"""High-level memory API used by the agent.

- remember(text): store a durable fact (embedded for semantic search).
- recall(query): fetch the facts most relevant to the current query.
- save_message / load_history: persist and reload conversation turns.
- add_note / list_notes, add_reminder / list_reminders / due_reminders.
- observe(): optional automatic fact-extraction (off by default).
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
import json
from typing import Any

from sqlalchemy import delete, func, select

from purple import documents, focus
from purple.config import settings
from purple.memory import extract
from purple.memory.db import async_session
from purple.memory.models import (
    AutomationRule,
    Chunk,
    Document,
    Entity,
    Fact,
    Message,
    Note,
    ProfileEntry,
    Reminder,
    SessionSummary,
)
from purple.triggers.rules import Rule
from purple.utils.logging import get_logger

log = get_logger("memory")


class Memory:
    def __init__(self, llm: Any) -> None:
        # llm provides .embed(text) -> list[float]
        self.llm = llm

    async def remember(self, fact_text: str, kind: str = "fact") -> None:
        vec = await self.llm.embed(fact_text)
        async with async_session() as s:
            s.add(Fact(text=fact_text, kind=kind, embedding=vec))
            await s.commit()
        log.info("remembered", kind=kind)

    async def recall(self, query: str, limit: int = 6) -> list[str]:
        vec = await self.llm.embed(query)
        async with async_session() as s:
            rows = await s.execute(
                select(Fact).order_by(Fact.embedding.cosine_distance(vec)).limit(limit)
            )
            return [r.text for r in rows.scalars().all()]

    async def save_message(self, session_id: str, role: str, content: str) -> None:
        async with async_session() as s:
            s.add(Message(session_id=session_id, role=role, content=content))
            await s.commit()

    async def load_history(self, session_id: str, limit: int = 20) -> list[dict[str, str]]:
        async with async_session() as s:
            rows = await s.execute(
                select(Message)
                .where(Message.session_id == session_id)
                .order_by(Message.created_at.desc())
                .limit(limit)
            )
            msgs = list(rows.scalars().all())[::-1]
            return [{"role": m.role, "content": m.content} for m in msgs]

    async def observe(self, user_text: str, assistant_text: str) -> None:
        """Auto-learn durable facts from a turn — extract (tuned by mode), categorize,
        and dedup against what's already known (update a near-duplicate instead of piling
        on copies). Skips when the GPU is busy (gaming/rendering) so it never competes."""
        if not settings.auto_memory:
            return
        if focus.should_yield_gpu():  # don't tax the GPU mid-game; we'll learn later
            return
        mode = extract.normalize_mode(settings.auto_memory_mode)
        prompt = extract.extraction_prompt(mode, user_text, assistant_text)
        try:
            msg = await self.llm.chat([{"role": "user", "content": prompt}])
            items = json.loads((msg.get("content") or "[]").strip())
        except Exception as exc:
            log.warning("auto_memory_failed", error=str(exc))
            return
        for item in items if isinstance(items, list) else []:
            text = (item.get("text") or "").strip() if isinstance(item, dict) else ""
            if not text:
                continue
            category = extract.normalize_category(item.get("category", "fact"))
            try:
                await self._remember_dedup(text, category)
            except Exception as exc:
                log.warning("auto_memory_store_failed", error=str(exc))

    async def _remember_dedup(self, text: str, category: str) -> str:
        """Insert a fact, or update the nearest existing one if it's a near-duplicate."""
        vec = await self.llm.embed(text)
        dist = Fact.embedding.cosine_distance(vec)
        async with async_session() as s:
            hit = (await s.execute(select(Fact, dist).order_by(dist).limit(1))).first()
            if hit and extract.is_duplicate(1 - float(hit[1])):
                fact = hit[0]
                fact.text, fact.kind, fact.embedding = text, category, vec
                await s.commit()
                return "updated"
            s.add(Fact(text=text, kind=category, embedding=vec))
            await s.commit()
            return "added"

    # --- Structured profile + entities ---
    async def set_profile(self, key: str, value: str) -> None:
        async with async_session() as s:
            row = (
                await s.execute(select(ProfileEntry).where(ProfileEntry.key == key))
            ).scalar_one_or_none()
            if row:
                row.value = value
            else:
                s.add(ProfileEntry(key=key, value=value))
            await s.commit()

    async def get_profile(self) -> dict[str, str]:
        async with async_session() as s:
            rows = await s.execute(select(ProfileEntry))
            return {p.key: p.value for p in rows.scalars().all()}

    async def profile_summary(self) -> str:
        return extract.profile_summary(await self.get_profile())

    async def add_entity(
        self,
        kind: str,
        name: str,
        relation: str = "",
        aliases: list[str] | None = None,
        notes: str = "",
    ) -> int:
        async with async_session() as s:
            ent = Entity(
                kind=kind,
                name=name,
                relation=relation,
                aliases=",".join(aliases or []),
                notes=notes,
            )
            s.add(ent)
            await s.commit()
            return ent.id

    async def list_entities(self, kind: str | None = None) -> list[dict[str, Any]]:
        async with async_session() as s:
            stmt = select(Entity)
            if kind:
                stmt = stmt.where(Entity.kind == kind)
            rows = await s.execute(stmt.order_by(Entity.name))
            return [_entity_to_dict(e) for e in rows.scalars().all()]

    async def delete_entity(self, entity_id: int) -> bool:
        async with async_session() as s:
            ent = await s.get(Entity, entity_id)
            if ent is None:
                return False
            await s.delete(ent)
            await s.commit()
            return True

    async def forget_fact(self, fact_id: int) -> bool:
        async with async_session() as s:
            fact = await s.get(Fact, fact_id)
            if fact is None:
                return False
            await s.delete(fact)
            await s.commit()
            return True

    async def list_facts(self, limit: int = 50, category: str | None = None) -> list[dict[str, Any]]:
        async with async_session() as s:
            stmt = select(Fact)
            if category:
                stmt = stmt.where(Fact.kind == category)
            rows = await s.execute(stmt.order_by(Fact.created_at.desc()).limit(limit))
            return [_fact_to_dict(f) for f in rows.scalars().all()]

    async def search_facts(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        vec = await self.llm.embed(query)
        async with async_session() as s:
            rows = await s.execute(
                select(Fact).order_by(Fact.embedding.cosine_distance(vec)).limit(limit)
            )
            return [_fact_to_dict(f) for f in rows.scalars().all()]

    async def update_fact(self, fact_id: int, text: str) -> bool:
        vec = await self.llm.embed(text)
        async with async_session() as s:
            fact = await s.get(Fact, fact_id)
            if fact is None:
                return False
            fact.text, fact.embedding = text, vec
            await s.commit()
            return True

    # --- Episodic session summaries ---
    async def summarize_session(self, session_id: str) -> str | None:
        """(Re)build the rolling summary for a session. GPU-gated; best-effort."""
        if focus.should_yield_gpu():
            return None
        history = await self.load_history(session_id, limit=100)
        if not history:
            return None
        convo = "\n".join(f"{m['role']}: {m['content']}" for m in history)
        try:
            msg = await self.llm.chat([{"role": "user", "content": extract.summarize_prompt(convo)}])
            text = (msg.get("content") or "").strip()
        except Exception as exc:
            log.warning("summarize_failed", error=str(exc))
            return None
        if not text:
            return None
        vec = await self.llm.embed(text)
        async with async_session() as s:
            row = (
                await s.execute(select(SessionSummary).where(SessionSummary.session_id == session_id))
            ).scalar_one_or_none()
            if row:
                row.text, row.embedding = text, vec
            else:
                s.add(SessionSummary(session_id=session_id, text=text, embedding=vec))
            await s.commit()
        return text

    async def maybe_summarize(self, session_id: str, every: int | None = None) -> None:
        """Refresh the session summary every N messages (cheap count check first)."""
        every = every or settings.session_summarize_every
        async with async_session() as s:
            count = (
                await s.execute(
                    select(func.count()).select_from(Message).where(Message.session_id == session_id)
                )
            ).scalar() or 0
        if extract.should_summarize(int(count), every):
            await self.summarize_session(session_id)

    async def get_session_summary(self, session_id: str) -> str | None:
        async with async_session() as s:
            row = (
                await s.execute(select(SessionSummary).where(SessionSummary.session_id == session_id))
            ).scalar_one_or_none()
            return row.text if row else None

    async def search_summaries(self, query: str, limit: int = 2) -> list[str]:
        vec = await self.llm.embed(query)
        async with async_session() as s:
            rows = await s.execute(
                select(SessionSummary).order_by(SessionSummary.embedding.cosine_distance(vec)).limit(limit)
            )
            return [r.text for r in rows.scalars().all()]

    # --- Consolidation (tidy memory: merge near-duplicate facts, keep newest wording) ---
    async def consolidate(self, threshold: float | None = None) -> int:
        thr = threshold if threshold is not None else 0.92
        async with async_session() as s:
            facts = list(
                (await s.execute(select(Fact).order_by(Fact.created_at.desc()))).scalars().all()
            )
            kept: list[Fact] = []
            removed = 0
            for f in facts:
                emb = list(f.embedding) if f.embedding is not None else []
                if any(extract.cosine(emb, list(k.embedding)) >= thr for k in kept):
                    await s.delete(f)  # older duplicate of one we're keeping
                    removed += 1
                else:
                    kept.append(f)
            if removed:
                await s.commit()
            return removed

    async def decay_facts(self, max_age_days: int | None = None) -> int:
        """Forget plain 'fact' memories older than the cutoff (off when the setting is 0).
        Preferences / people / projects / routines are never decayed."""
        days = settings.memory_decay_days if max_age_days is None else max_age_days
        if days <= 0:
            return 0
        from datetime import timedelta

        cutoff = datetime.now(UTC) - timedelta(days=days)
        async with async_session() as s:
            rows = await s.execute(
                select(Fact).where(Fact.kind == "fact", Fact.created_at < cutoff)
            )
            facts = list(rows.scalars().all())
            for f in facts:
                await s.delete(f)
            if facts:
                await s.commit()
            return len(facts)

    # --- Documents / knowledge base (RAG) ---
    async def ingest_file(self, path: str, force: bool = False) -> dict[str, Any]:
        """Parse → chunk → embed → store one file. Idempotent: skips unchanged files."""
        from pathlib import Path

        p = Path(path).expanduser()
        if not p.is_file():
            return {"ok": False, "error": f"not a file: {p}"}
        if not documents.is_supported(p):
            return {"ok": False, "error": f"unsupported type: {p.suffix}"}
        key = str(p.resolve())
        sha = await asyncio.to_thread(documents.file_sha, p)
        async with async_session() as s:
            doc = (
                await s.execute(select(Document).where(Document.path == key))
            ).scalar_one_or_none()
            if doc and doc.sha == sha and not force:
                return {"ok": True, "skipped": True, "document": doc.title, "chunks": doc.n_chunks}

        text = await asyncio.to_thread(documents.extract_text, p)
        pieces = documents.chunk_text(text)
        if not pieces:
            return {"ok": False, "error": "no readable text"}
        embeddings = [await self.llm.embed(c) for c in pieces]
        title = documents.title_for(p)
        async with async_session() as s:
            doc = (
                await s.execute(select(Document).where(Document.path == key))
            ).scalar_one_or_none()
            if doc:  # changed file: drop old chunks, refresh
                await s.execute(delete(Chunk).where(Chunk.document_id == doc.id))
                doc.sha, doc.title, doc.n_chunks = sha, title, len(pieces)
            else:
                doc = Document(path=key, title=title, sha=sha, n_chunks=len(pieces))
                s.add(doc)
                await s.flush()
            for i, (chunk, vec) in enumerate(zip(pieces, embeddings, strict=False)):
                s.add(Chunk(document_id=doc.id, ordinal=i, text=chunk, embedding=vec))
            await s.commit()
            log.info("ingested", path=key, chunks=len(pieces))
            return {"ok": True, "document": title, "chunks": len(pieces)}

    async def ingest_folder(self, path: str, force: bool = False) -> dict[str, Any]:
        from pathlib import Path

        d = Path(path).expanduser()
        if not d.is_dir():
            return {"ok": False, "error": f"not a folder: {d}"}
        files = [p for p in sorted(d.rglob("*")) if p.is_file() and documents.is_supported(p)]
        ingested = skipped = chunks = 0
        for p in files:
            res = await self.ingest_file(str(p), force=force)
            if not res.get("ok"):
                continue
            if res.get("skipped"):
                skipped += 1
            else:
                ingested += 1
                chunks += res.get("chunks", 0)
        return {"ok": True, "files": len(files), "ingested": ingested, "skipped": skipped,
                "chunks": chunks}

    async def list_documents(self) -> list[dict[str, Any]]:
        async with async_session() as s:
            rows = await s.execute(select(Document).order_by(Document.updated_at.desc()))
            return [
                {"id": d.id, "title": d.title, "path": d.path, "chunks": d.n_chunks}
                for d in rows.scalars().all()
            ]

    async def remove_document(self, doc_id: int) -> bool:
        async with async_session() as s:
            doc = await s.get(Document, doc_id)
            if doc is None:
                return False
            await s.execute(delete(Chunk).where(Chunk.document_id == doc_id))
            await s.delete(doc)
            await s.commit()
            return True

    async def search_documents(self, query: str, k: int = 5) -> list[dict[str, Any]]:
        """Top matching passages with their source document title."""
        vec = await self.llm.embed(query)
        async with async_session() as s:
            rows = await s.execute(
                select(Chunk, Document.title)
                .join(Document, Document.id == Chunk.document_id)
                .order_by(Chunk.embedding.cosine_distance(vec))
                .limit(k)
            )
            return [{"source": title, "text": chunk.text} for chunk, title in rows.all()]

    # --- Notes ---
    async def add_note(self, text: str) -> int:
        async with async_session() as s:
            note = Note(text=text)
            s.add(note)
            await s.commit()
            return note.id

    async def list_notes(self, limit: int = 10) -> list[str]:
        async with async_session() as s:
            rows = await s.execute(select(Note).order_by(Note.created_at.desc()).limit(limit))
            return [n.text for n in rows.scalars().all()]

    # --- Reminders ---
    async def add_reminder(self, text: str, due_at: datetime | None = None) -> int:
        async with async_session() as s:
            rem = Reminder(text=text, due_at=due_at)
            s.add(rem)
            await s.commit()
            return rem.id

    async def list_reminders(self, include_done: bool = False) -> list[dict[str, Any]]:
        async with async_session() as s:
            stmt = select(Reminder).order_by(Reminder.due_at.is_(None), Reminder.due_at)
            if not include_done:
                stmt = stmt.where(Reminder.done.is_(False))
            rows = await s.execute(stmt)
            return [
                {"id": r.id, "text": r.text, "due_at": r.due_at.isoformat() if r.due_at else None}
                for r in rows.scalars().all()
            ]

    async def due_reminders(self) -> list[str]:
        now = datetime.now(UTC)
        async with async_session() as s:
            rows = await s.execute(
                select(Reminder)
                .where(
                    Reminder.done.is_(False),
                    Reminder.due_at.is_not(None),
                    Reminder.due_at <= now,
                )
                .order_by(Reminder.due_at)
            )
            return [r.text for r in rows.scalars().all()]

    # --- Automation rules ---
    async def add_rule(
        self,
        name: str,
        keywords: list[str] | None = None,
        source: str = "",
        min_priority: str = "normal",
        effect: str = "notify",
        action: str = "",
        action_args: dict[str, Any] | None = None,
    ) -> int:
        async with async_session() as s:
            rule = AutomationRule(
                name=name,
                keywords=",".join(keywords or []),
                source=source,
                min_priority=min_priority,
                effect=effect,
                action=action,
                action_args=json.dumps(action_args or {}),
            )
            s.add(rule)
            await s.commit()
            return rule.id

    async def list_rules_raw(self) -> list[dict[str, Any]]:
        """All rules as plain dicts (for the UI / tools), newest first."""
        async with async_session() as s:
            rows = await s.execute(
                select(AutomationRule).order_by(AutomationRule.created_at.desc())
            )
            return [_rule_to_dict(r) for r in rows.scalars().all()]

    async def get_rules(self) -> list[Rule]:
        """Enabled + disabled rules as domain objects for the trigger engine."""
        async with async_session() as s:
            rows = await s.execute(select(AutomationRule))
            return [_rule_to_domain(r) for r in rows.scalars().all()]

    async def set_rule_enabled(self, rule_id: int, enabled: bool) -> bool:
        async with async_session() as s:
            rule = await s.get(AutomationRule, rule_id)
            if rule is None:
                return False
            rule.enabled = enabled
            await s.commit()
            return True

    async def delete_rule(self, rule_id: int) -> bool:
        async with async_session() as s:
            rule = await s.get(AutomationRule, rule_id)
            if rule is None:
                return False
            await s.delete(rule)
            await s.commit()
            return True


def _fact_to_dict(f: Fact) -> dict[str, Any]:
    return {
        "id": f.id,
        "text": f.text,
        "category": f.kind,
        "created_at": f.created_at.isoformat() if f.created_at else None,
    }


def _entity_to_dict(e: Entity) -> dict[str, Any]:
    return {
        "id": e.id,
        "kind": e.kind,
        "name": e.name,
        "relation": e.relation,
        "aliases": extract.split_aliases(e.aliases),
        "notes": e.notes,
    }


def _split_keywords(raw: str) -> list[str]:
    return [k.strip() for k in (raw or "").split(",") if k.strip()]


def _load_args(raw: str) -> dict[str, Any]:
    try:
        val = json.loads(raw or "{}")
        return val if isinstance(val, dict) else {}
    except (ValueError, TypeError):
        return {}


def _rule_to_dict(r: AutomationRule) -> dict[str, Any]:
    return {
        "id": r.id,
        "name": r.name,
        "keywords": _split_keywords(r.keywords),
        "source": r.source,
        "min_priority": r.min_priority,
        "effect": r.effect,
        "enabled": r.enabled,
        "action": r.action,
        "action_args": _load_args(r.action_args),
    }


def _rule_to_domain(r: AutomationRule) -> Rule:
    return Rule(
        name=r.name,
        keywords=_split_keywords(r.keywords),
        source=r.source,
        min_priority=r.min_priority,
        effect=r.effect,
        enabled=r.enabled,
        action=r.action,
        action_args=_load_args(r.action_args),
    )
