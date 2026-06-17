import { useEffect, useRef, useState } from "react";
import {
  PurpleClient,
  ConfirmRequest,
  Activity,
  Health,
  Automation,
  MemoryOverview,
  KbDocument,
  MissionSummary,
  MissionDetail,
} from "./purple";
import "./App.css";

type Msg = { role: "user" | "purple"; text: string };
type Pending = { req: ConfirmRequest; resolve: (ok: boolean) => void };
type Tab = "chat" | "monitor" | "automations" | "memory" | "missions" | "settings";

const client = new PurpleClient();

export default function App() {
  const [tab, setTab] = useState<Tab>("chat");
  const [connected, setConnected] = useState(false);
  const [model, setModel] = useState("");
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [activity, setActivity] = useState("");
  const [feed, setFeed] = useState<string[]>([]);
  const [pending, setPending] = useState<Pending | null>(null);
  const [recording, setRecording] = useState(false);
  const [streaming, setStreaming] = useState("");
  const [observing, setObserving] = useState(false);

  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const endRef = useRef<HTMLDivElement | null>(null);

  function addMsg(role: Msg["role"], text: string) {
    if (text) setMessages((m) => [...m, { role, text }]);
  }
  function pushFeed(line: string) {
    setFeed((f) => [...f.slice(-49), `${new Date().toLocaleTimeString()}  ${line}`]);
  }

  function onActivity(msg: Activity) {
    if (msg.type === "status" && msg.state === "thinking") {
      setActivity("Thinking…");
      pushFeed("thinking…");
    } else if (msg.type === "tool") {
      pushFeed(`tool → ${msg.name}`);
    } else if (msg.type === "voice") {
      if (msg.state === "listening") setActivity("Listening for the wake word…");
      else if (msg.state === "woke") {
        setActivity("Yes? I'm listening…");
        pushFeed("woke");
      } else if (msg.state === "heard") {
        addMsg("user", msg.text || "");
        pushFeed(`heard: ${msg.text || ""}`);
        setActivity("Thinking…");
      } else if (msg.state === "reply") {
        addMsg("purple", msg.text || "");
        setActivity("");
      }
    }
  }

  useEffect(() => {
    client.onStatus = (c) => {
      setConnected(c);
      if (c) client.health().then((h) => setModel(h.model)).catch(() => {});
    };
    client.onReply = (t) => {
      addMsg("purple", t);
      setStreaming("");
      setActivity("");
    };
    client.onReplyChunk = (c) => setStreaming((s) => s + c);
    client.onActivity = onActivity;
    client.onConfirm = (req) => new Promise<boolean>((resolve) => setPending({ req, resolve }));
    client.connect();
    client.getObserve().then((o) => setObserving(!!o.observing)).catch(() => {});
  }, []);

  async function toggleObserve() {
    const next = !observing;
    setObserving(next);
    try {
      const o = await client.setObserve(next);
      setObserving(!!o.observing);
      pushFeed(next ? "observing screen context (on)" : "stopped observing");
    } catch {
      setObserving(!next);
    }
  }

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, activity, streaming]);

  function sendText() {
    const t = input.trim();
    if (!t) return;
    addMsg("user", t);
    client.send(t);
    setInput("");
  }

  function resolveConfirm(ok: boolean) {
    pending?.resolve(ok);
    setPending(null);
  }

  async function toggleMic() {
    if (recording) {
      recorderRef.current?.stop();
      setRecording(false);
      return;
    }
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const rec = new MediaRecorder(stream);
    chunksRef.current = [];
    rec.ondataavailable = (e) => chunksRef.current.push(e.data);
    rec.onstop = async () => {
      stream.getTracks().forEach((t) => t.stop());
      setActivity("Thinking…");
      const res = await client.sendVoice(new Blob(chunksRef.current, { type: "audio/webm" }));
      addMsg("user", res.transcript);
      addMsg("purple", res.reply);
      setActivity("");
      if (res.audio_base64) new Audio("data:audio/wav;base64," + res.audio_base64).play();
    };
    recorderRef.current = rec;
    rec.start();
    setRecording(true);
  }

  return (
    <div className="app">
      <div className="header">
        <span className={"dot" + (connected ? " on" : "")} />
        <h1>Purple</h1>
        {model && <span className="model">{model}</span>}
        <button
          className={"observe" + (observing ? " on" : "")}
          onClick={toggleObserve}
          title="When on, Purple can see the title of your active window to ground vague requests. Off by default; auto-stops after a few hours."
        >
          {observing ? "👁 Observing" : "Observe off"}
        </button>
      </div>

      <div className="tabs">
        {(["chat", "monitor", "automations", "memory", "missions", "settings"] as Tab[]).map((t) => (
          <button key={t} className={tab === t ? "tab active" : "tab"} onClick={() => setTab(t)}>
            {t}
          </button>
        ))}
      </div>

      {tab === "chat" && (
        <>
          <div className="messages">
            {messages.map((m, i) => (
              <div key={i} className={"msg " + m.role}>
                {m.text}
              </div>
            ))}
            {streaming && <div className="msg purple">{streaming}</div>}
            {activity && <div className="activity">{activity}</div>}
            <div ref={endRef} />
          </div>
          <div className="composer">
            <input
              value={input}
              placeholder="Ask Purple anything…"
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendText()}
            />
            <button className={recording ? "rec" : ""} onClick={toggleMic}>
              {recording ? "Stop" : "Mic"}
            </button>
            <button onClick={sendText}>Send</button>
          </div>
        </>
      )}

      {tab === "monitor" && <MonitorPanel feed={feed} />}
      {tab === "automations" && <AutomationsPanel />}
      {tab === "memory" && <MemoryPanel />}
      {tab === "missions" && <MissionsPanel />}
      {tab === "settings" && <SettingsPanel />}

      {pending && (
        <div className="confirm">
          <div className="box">
            <h3>Confirm action</h3>
            <p>
              Purple wants to run <b>{pending.req.tool}</b>:
            </p>
            <code>
              {JSON.stringify(
                Object.fromEntries(
                  Object.entries(pending.req.args).filter(([k]) => k !== "screenshot_b64")
                )
              )}
            </code>
            {typeof (pending.req.args as any).screenshot_b64 === "string" && (
              <img
                className="shot"
                src={"data:image/png;base64," + (pending.req.args as any).screenshot_b64}
                alt="screen"
              />
            )}
            <div className="row">
              <button className="deny" onClick={() => resolveConfirm(false)}>
                Cancel
              </button>
              <button className="allow" onClick={() => resolveConfirm(true)}>
                Allow
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function MonitorPanel({ feed }: { feed: string[] }) {
  const [h, setH] = useState<Health | null>(null);
  const [m, setM] = useState<Record<string, any> | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [st, setSt] = useState<Record<string, any> | null>(null);
  useEffect(() => {
    let alive = true;
    const tick = () => {
      client.health().then((x) => alive && setH(x)).catch(() => {});
      client.metricsSummary().then((x) => alive && setM(x)).catch(() => {});
      client.logs(120).then((x) => alive && setLogs(x.lines || [])).catch(() => {});
      client.status().then((x) => alive && setSt(x)).catch(() => {});
    };
    tick();
    const id = setInterval(tick, 4000);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, []);
  const badge = (ok: boolean, label: string) => (
    <span className={"badge " + (ok ? "up" : "down")}>{label}</span>
  );
  return (
    <div className="panel">
      {h ? (
        <div className="status">
          {badge(h.ollama, "Ollama")}
          {badge(h.database, "Database")}
          <span className="badge info">{h.tools} tools</span>
          <span className="badge info">brain: {h.model}</span>
          <span className="badge info">eyes: {h.vision_model}</span>
          <span className="badge info">wake: {h.wake_enabled ? "on" : "off"}</span>
          <span className="badge info">scheduler: {h.scheduler_enabled ? "on" : "off"}</span>
          {st && <span className="badge info">up {Math.round((st.uptime_seconds || 0) / 60)}m</span>}
          {st?.focus && (
            <span className={"badge " + (st.focus.yielding ? "down" : "up")}>
              {st.focus.yielding ? "GPU: yielding" : "GPU: free"}
            </span>
          )}
        </div>
      ) : (
        <p>Connecting…</p>
      )}

      {st?.focus && (
        <div className="status">
          <button
            className="tab"
            onClick={() => client.setFocus(!st.focus.manual).then((f) => setSt({ ...st, focus: f }))}
          >
            {st.focus.manual
              ? "Focus mode: ON — click to release the GPU"
              : "Focus mode: OFF — click to pause GPU work"}
          </button>
        </div>
      )}

      {m && m.enabled && (
        <div className="metrics">
          <div className="card"><b>{m.turns}</b><span>turns</span></div>
          <div className="card"><b>{m.llm_calls}</b><span>LLM calls</span></div>
          <div className="card"><b>{m.llm_avg_ms} ms</b><span>avg LLM</span></div>
          <div className="card"><b>{m.tool_calls}</b><span>tool calls</span></div>
          <div className="card"><b>{m.tool_avg_ms} ms</b><span>avg tool</span></div>
        </div>
      )}

      {m && m.tools && m.tools.length > 0 && (
        <>
          <h3>Tool usage</h3>
          <div className="feed">
            {m.tools.map((t: any, i: number) => (
              <div key={i}>
                {t.tool} ({t.ok === "true" ? "ok" : "fail"}): {t.count}
              </div>
            ))}
          </div>
        </>
      )}

      <h3>Live activity</h3>
      <div className="feed">
        {feed.length ? feed.slice().reverse().map((l, i) => <div key={i}>{l}</div>) : <em>quiet…</em>}
      </div>

      <h3>Recent logs</h3>
      <div className="feed">
        {logs.length ? (
          logs.slice().reverse().map((l, i) => <div key={i}>{l}</div>)
        ) : (
          <em>no logs yet…</em>
        )}
      </div>
    </div>
  );
}

function AutomationsPanel() {
  const empty = {
    name: "",
    effect: "speak",
    keywords: "",
    source: "",
    min_priority: "normal",
    action: "",
  };
  const [rules, setRules] = useState<Automation[]>([]);
  const [draft, setDraft] = useState(empty);
  const [msg, setMsg] = useState("");

  const load = () =>
    client.listAutomations().then((r) => setRules(r.rules || [])).catch(() => {});
  useEffect(() => {
    load();
  }, []);

  async function add() {
    if (!draft.name.trim()) {
      setMsg("Give the rule a name.");
      return;
    }
    await client.addAutomation({
      name: draft.name.trim(),
      effect: draft.effect,
      keywords: draft.keywords.split(",").map((s) => s.trim()).filter(Boolean),
      source: draft.source.trim(),
      min_priority: draft.min_priority,
      action: draft.action.trim(),
    });
    setDraft(empty);
    setMsg("Rule added.");
    load();
  }

  return (
    <div className="panel">
      <p className="hint">
        Rules shape what Purple tells you — <b>speak</b> gives a gentle nudge even mid-game,{" "}
        <b>mute</b> stays silent, <b>notify</b> is normal. They only change notifications; they
        never run actions on their own.
      </p>

      <div className="addform">
        <input
          placeholder="Rule name (e.g. Hear my boss)"
          value={draft.name}
          onChange={(e) => setDraft({ ...draft, name: e.target.value })}
        />
        <input
          placeholder="keywords, comma-separated (blank = any)"
          value={draft.keywords}
          onChange={(e) => setDraft({ ...draft, keywords: e.target.value })}
        />
        <select value={draft.source} onChange={(e) => setDraft({ ...draft, source: e.target.value })}>
          <option value="">any source</option>
          {["email", "call", "message", "calendar", "system"].map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
        <select
          value={draft.min_priority}
          onChange={(e) => setDraft({ ...draft, min_priority: e.target.value })}
        >
          {["low", "normal", "important"].map((p) => (
            <option key={p} value={p}>
              ≥ {p}
            </option>
          ))}
        </select>
        <select value={draft.effect} onChange={(e) => setDraft({ ...draft, effect: e.target.value })}>
          {["speak", "mute", "notify"].map((x) => (
            <option key={x} value={x}>
              {x}
            </option>
          ))}
        </select>
        <input
          placeholder="run a tool (optional)"
          value={draft.action}
          onChange={(e) => setDraft({ ...draft, action: e.target.value })}
        />
        <button onClick={add}>Add rule</button>
      </div>
      <span className="hint">
        {msg || "Actions run under the autonomy setting (Settings → autonomy: notify / confirm / act)."}
      </span>

      <div className="rules">
        {rules.length === 0 && <em className="hint">No automations yet — add one above.</em>}
        {rules.map((r) => (
          <div key={r.id} className={"rule" + (r.enabled ? "" : " off")}>
            <div className="rule-main">
              <b>{r.name}</b>
              <div className="rule-meta">
                <span className={"badge eff-" + r.effect}>{r.effect}</span>
                <span className="badge info">{r.source || "any source"}</span>
                <span className="badge info">≥ {r.min_priority}</span>
                {r.keywords.length > 0 && (
                  <span className="badge info">{r.keywords.join(", ")}</span>
                )}
                {r.action && <span className="badge eff-speak">▶ {r.action}</span>}
              </div>
            </div>
            <div className="rule-actions">
              <button
                className="tab"
                onClick={() => client.toggleAutomation(r.id, !r.enabled).then(load)}
              >
                {r.enabled ? "On" : "Off"}
              </button>
              <button className="tab del" onClick={() => client.removeAutomation(r.id).then(load)}>
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function MemoryPanel() {
  const [mem, setMem] = useState<MemoryOverview | null>(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<MemoryOverview["facts"] | null>(null);
  const [newFact, setNewFact] = useState("");
  const [newKey, setNewKey] = useState("");
  const [newVal, setNewVal] = useState("");
  const [docs, setDocs] = useState<KbDocument[]>([]);
  const [ingestPath, setIngestPath] = useState("");
  const [ingestMsg, setIngestMsg] = useState("");

  const load = () => client.memory().then(setMem).catch(() => {});
  const loadDocs = () => client.documents().then((r) => setDocs(r.documents || [])).catch(() => {});
  useEffect(() => {
    load();
    loadDocs();
  }, []);

  async function ingest() {
    if (!ingestPath.trim()) return;
    setIngestMsg("Learning…");
    const r = await client.ingestDocuments(ingestPath.trim());
    setIngestMsg(
      r.ok === false
        ? `Couldn't: ${r.error || "failed"}`
        : (r.document as string)
          ? `Learned '${r.document}' (${r.chunks} passages).`
          : `Learned ${r.ingested ?? 0} file(s).`
    );
    setIngestPath("");
    loadDocs();
  }

  async function search() {
    if (!query.trim()) {
      setResults(null);
      return;
    }
    const r = await client.memorySearch(query.trim());
    setResults(r.facts || []);
  }

  if (!mem) return <div className="panel"><p>Loading…</p></div>;
  const facts = results ?? mem.facts;

  return (
    <div className="panel">
      <h3>What Purple knows</h3>
      <div className="status">
        <span className="badge info">auto-learn: {mem.auto_memory ? mem.auto_memory_mode : "off"}</span>
        <select
          value={mem.auto_memory_mode}
          onChange={async (e) => {
            await client.saveConfig({ auto_memory_mode: e.target.value });
            setMem({ ...mem, auto_memory_mode: e.target.value });
          }}
        >
          {["moderate", "high", "aggressive"].map((m) => (
            <option key={m} value={m}>
              learn: {m}
            </option>
          ))}
        </select>
      </div>

      <h3>Profile</h3>
      <div className="form">
        {Object.entries(mem.profile).map(([k, v]) => (
          <label key={k} className="frow">
            <span>{k.replace(/_/g, " ")}</span>
            <input
              type="text"
              defaultValue={v}
              onBlur={(e) => client.setProfileField(k, e.target.value).then(load)}
            />
          </label>
        ))}
      </div>
      <div className="addform">
        <input placeholder="field (e.g. location)" value={newKey} onChange={(e) => setNewKey(e.target.value)} />
        <input placeholder="value" value={newVal} onChange={(e) => setNewVal(e.target.value)} />
        <button
          onClick={async () => {
            if (!newKey.trim()) return;
            await client.setProfileField(newKey.trim(), newVal.trim());
            setNewKey("");
            setNewVal("");
            load();
          }}
        >
          Set field
        </button>
      </div>

      {mem.people.length > 0 && (
        <>
          <h3>People</h3>
          <div className="rules">
            {mem.people.map((p) => (
              <div key={p.id} className="rule">
                <div className="rule-main">
                  <b>{p.name}</b>
                  <div className="rule-meta">
                    {p.relation && <span className="badge info">{p.relation}</span>}
                    {p.aliases.length > 0 && <span className="badge info">{p.aliases.join(", ")}</span>}
                  </div>
                </div>
                <div className="rule-actions">
                  <button className="tab del" onClick={() => client.deletePerson(p.id).then(load)}>
                    Forget
                  </button>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      <h3>Knowledge (documents)</h3>
      <div className="addform">
        <input
          placeholder="file or folder path to learn…"
          value={ingestPath}
          onChange={(e) => setIngestPath(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && ingest()}
        />
        <button onClick={ingest}>Learn</button>
      </div>
      <span className="hint">{ingestMsg}</span>
      <div className="rules">
        {docs.length === 0 && <em className="hint">No documents learned yet.</em>}
        {docs.map((d) => (
          <div key={d.id} className="rule">
            <div className="rule-main">
              <b>{d.title}</b>
              <div className="rule-meta">
                <span className="badge info">{d.chunks} passages</span>
                <span className="badge info">{d.path}</span>
              </div>
            </div>
            <div className="rule-actions">
              <button className="tab del" onClick={() => client.removeDocument(d.id).then(loadDocs)}>
                Remove
              </button>
            </div>
          </div>
        ))}
      </div>

      <h3>Facts</h3>
      <div className="addform">
        <input
          placeholder="search what Purple knows…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && search()}
        />
        <button onClick={search}>Search</button>
        {results !== null && (
          <button
            className="tab"
            onClick={() => {
              setResults(null);
              setQuery("");
            }}
          >
            Clear
          </button>
        )}
      </div>
      <div className="addform">
        <input placeholder="teach Purple a fact…" value={newFact} onChange={(e) => setNewFact(e.target.value)} />
        <button
          onClick={async () => {
            if (!newFact.trim()) return;
            await client.addFact(newFact.trim());
            setNewFact("");
            load();
          }}
        >
          Add fact
        </button>
      </div>
      <div className="rules">
        {facts.length === 0 && <em className="hint">Nothing yet.</em>}
        {facts.map((f) => (
          <div key={f.id} className="rule">
            <div className="rule-main">
              <span>{f.text}</span>
              <div className="rule-meta">
                <span className="badge info">{f.category}</span>
              </div>
            </div>
            <div className="rule-actions">
              <button className="tab del" onClick={() => client.deleteFact(f.id).then(() => {
                setResults(null);
                load();
              })}>
                Forget
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function VoiceEnroll() {
  const [voices, setVoices] = useState<string[]>([]);
  const [info, setInfo] = useState<{ available: boolean; enforced: boolean }>({
    available: false,
    enforced: false,
  });
  const [name, setName] = useState("");
  const [status, setStatus] = useState("");
  const [recording, setRecording] = useState(false);

  const load = () =>
    client.voices().then((r) => {
      setVoices(r.voices || []);
      setInfo({ available: r.available, enforced: r.enforced });
    }).catch(() => {});
  useEffect(() => {
    load();
  }, []);

  async function record() {
    if (!name.trim()) {
      setStatus("Enter a name first.");
      return;
    }
    setRecording(true);
    setStatus("Recording 4 seconds — speak naturally…");
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const rec = new MediaRecorder(stream);
    const chunks: Blob[] = [];
    rec.ondataavailable = (e) => chunks.push(e.data);
    rec.onstop = async () => {
      stream.getTracks().forEach((t) => t.stop());
      const r = await client.enrollVoice(name.trim(), new Blob(chunks, { type: "audio/webm" }));
      setStatus(r.ok ? `Enrolled '${name.trim()}' (${r.samples} sample(s)).` : `Failed: ${r.error}`);
      setName("");
      setRecording(false);
      load();
    };
    rec.start();
    setTimeout(() => rec.stop(), 4000);
  }

  return (
    <div className="panel" style={{ padding: 0 }}>
      <h3>Voice access</h3>
      <div className="status">
        <span className={"badge " + (info.enforced ? "up" : "info")}>
          {info.enforced ? "locked: only enrolled voices" : "not enforced yet"}
        </span>
        {!info.available && <span className="badge down">speaker model not installed</span>}
      </div>
      <div className="addform">
        <input placeholder="your name" value={name} onChange={(e) => setName(e.target.value)} />
        <button onClick={record} disabled={recording || !info.available}>
          {recording ? "Recording…" : "Enroll (record 4s)"}
        </button>
      </div>
      <span className="hint">{status}</span>
      <div className="rules">
        {voices.length === 0 && <em className="hint">No voices enrolled yet.</em>}
        {voices.map((v) => (
          <div key={v} className="rule">
            <div className="rule-main"><b>{v}</b></div>
            <div className="rule-actions">
              <button className="tab del" onClick={() => client.removeVoice(v).then(load)}>
                Remove
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function MissionsPanel() {
  const [missions, setMissions] = useState<MissionSummary[]>([]);
  const [open, setOpen] = useState<Record<number, MissionDetail>>({});
  const [goal, setGoal] = useState("");

  const load = () => client.missions().then((r) => setMissions(r.missions || [])).catch(() => {});
  useEffect(() => {
    load();
    const id = setInterval(load, 4000);
    return () => clearInterval(id);
  }, []);

  async function toggle(id: number) {
    if (open[id]) {
      setOpen((o) => {
        const n = { ...o };
        delete n[id];
        return n;
      });
      return;
    }
    const d = await client.mission(id);
    setOpen((o) => ({ ...o, [id]: d }));
  }

  async function start() {
    if (!goal.trim()) return;
    await client.startMission(goal.trim());
    setGoal("");
    load();
  }

  return (
    <div className="panel">
      <h3>Missions</h3>
      <div className="addform">
        <input
          placeholder="give Purple a goal to carry out…"
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && start()}
        />
        <button onClick={start}>Start mission</button>
      </div>
      <span className="hint">
        She plans + works it in the background; risky steps pause for your approval.
      </span>

      <div className="rules">
        {missions.length === 0 && <em className="hint">No missions yet.</em>}
        {missions.map((m) => (
          <div key={m.id} className="rule" style={{ flexDirection: "column", alignItems: "stretch" }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
              <div className="rule-main">
                <b onClick={() => toggle(m.id)} style={{ cursor: "pointer" }}>
                  #{m.id} {m.goal}
                </b>
                <div className="rule-meta">
                  <span className={"badge " + (m.status === "blocked" ? "down" : "info")}>{m.status}</span>
                </div>
              </div>
              <div className="rule-actions">
                {m.status === "blocked" && (
                  <button className="tab" onClick={() => client.resumeMission(m.id).then(load)}>
                    Approve
                  </button>
                )}
                {(m.status === "running" || m.status === "blocked" || m.status === "planned") && (
                  <button className="tab del" onClick={() => client.cancelMission(m.id).then(load)}>
                    Cancel
                  </button>
                )}
                <button className="tab" onClick={() => toggle(m.id)}>
                  {open[m.id] ? "Hide" : "Steps"}
                </button>
              </div>
            </div>
            {open[m.id] && (
              <div className="feed" style={{ marginTop: 8 }}>
                {open[m.id].steps.map((s) => (
                  <div key={s.id}>
                    [{s.status}] {s.title}
                    {s.result ? ` — ${s.result.slice(0, 120)}` : ""}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function SettingsPanel() {
  const [cfg, setCfg] = useState<Record<string, any> | null>(null);
  const [draft, setDraft] = useState<Record<string, any>>({});
  const [msg, setMsg] = useState("");

  useEffect(() => {
    client.getConfig().then((c) => {
      setCfg(c);
      setDraft(c);
    });
  }, []);

  if (!cfg) return <div className="panel"><p>Loading…</p></div>;
  const fields = Object.keys(cfg).filter((k) => !k.endsWith("_set"));
  const set = (k: string, v: any) => setDraft((d) => ({ ...d, [k]: v }));

  async function save() {
    const updates: Record<string, any> = {};
    for (const k of fields) if (draft[k] !== cfg![k]) updates[k] = draft[k];
    if (!Object.keys(updates).length) {
      setMsg("No changes.");
      return;
    }
    const r = await client.saveConfig(updates);
    setMsg(
      `Saved: ${r.applied.join(", ")}.` +
        (r.restart_needed.length ? ` Restart needed for: ${r.restart_needed.join(", ")}.` : "")
    );
    setCfg({ ...cfg, ...updates });
  }

  return (
    <div className="panel">
      <VoiceEnroll />
      <h3>Configuration</h3>
      <div className="form">
        {fields.map((k) => (
          <label key={k} className="frow">
            <span>{k}</span>
            {typeof cfg![k] === "boolean" ? (
              <input
                type="checkbox"
                checked={!!draft[k]}
                onChange={(e) => set(k, e.target.checked)}
              />
            ) : typeof cfg![k] === "number" ? (
              <input
                type="number"
                value={draft[k]}
                onChange={(e) => set(k, Number(e.target.value))}
              />
            ) : (
              <input
                type="text"
                value={draft[k] ?? ""}
                onChange={(e) => set(k, e.target.value)}
              />
            )}
          </label>
        ))}
      </div>
      <div className="saverow">
        <button onClick={save}>Save</button>
        <span className="hint">{msg}</span>
      </div>
    </div>
  );
}
