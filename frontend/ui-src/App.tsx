import * as Dialog from "@radix-ui/react-dialog";
import {
  CheckIcon,
  ChevronDownIcon,
  DesktopIcon,
  EyeOpenIcon,
  MoonIcon,
  PaperPlaneIcon,
  SunIcon,
  TrashIcon,
} from "@radix-ui/react-icons";
import * as RSelect from "@radix-ui/react-select";
import * as RSwitch from "@radix-ui/react-switch";
import * as Tabs from "@radix-ui/react-tabs";
import * as Tooltip from "@radix-ui/react-tooltip";
import { type ReactNode, useEffect, useRef, useState } from "react";
import {
  Activity,
  Automation,
  ConfirmRequest,
  Health,
  KbDocument,
  MemoryOverview,
  MissionDetail,
  MissionSummary,
  PurpleClient,
} from "./purple";
import { type Theme, getTheme, setTheme, watchSystem } from "./theme";
import "./App.css";

type Msg = { role: "user" | "purple"; text: string };
type Pending = { req: ConfirmRequest; resolve: (ok: boolean) => void };
type TabKey = "chat" | "monitor" | "automations" | "memory" | "missions" | "settings";
const TABS: TabKey[] = ["chat", "monitor", "automations", "memory", "missions", "settings"];

const client = new PurpleClient();

// --- small styled primitives (Radix behavior + Tailwind looks) ---
const BTN = {
  primary: "inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-semibold bg-accent text-ink hover:opacity-90 transition disabled:opacity-50",
  good: "inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-semibold bg-up text-ink hover:opacity-90 transition disabled:opacity-50",
  outline: "inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm border border-edge text-cloud hover:bg-panel transition disabled:opacity-50",
  ghost: "inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-sm text-muted hover:bg-panel transition",
};
const FIELD = "w-full px-3 py-2 rounded-lg bg-panel border border-edge text-cloud text-sm outline-none focus:border-accent placeholder:text-muted/70";

function Btn({ variant = "primary", className = "", ...p }: { variant?: keyof typeof BTN } & React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return <button className={`${BTN[variant]} ${className}`} {...p} />;
}
function Field(p: React.InputHTMLAttributes<HTMLInputElement>) {
  return <input className={FIELD} {...p} />;
}
function IconBtn(p: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return <button className="p-1.5 rounded-lg text-down hover:bg-panel transition" {...p} />;
}
function Chip({ tone = "muted", children }: { tone?: "muted" | "up" | "down" | "accent"; children: ReactNode }) {
  const tones = {
    muted: "border border-edge text-muted",
    up: "border border-up text-up",
    down: "border border-down text-down",
    accent: "bg-accent text-ink",
  };
  return <span className={`text-xs px-2 py-0.5 rounded-full whitespace-nowrap ${tones[tone]}`}>{children}</span>;
}
function Panel({ children }: { children: ReactNode }) {
  return (
    <div className="flex-1 overflow-y-auto p-4">
      <div className="mx-auto flex max-w-3xl flex-col gap-3">{children}</div>
    </div>
  );
}
function Section({ children }: { children: ReactNode }) {
  return <h3 className="text-sm font-semibold text-cloud mt-1">{children}</h3>;
}
function Feed({ lines, empty }: { lines: string[]; empty: string }) {
  return (
    <div className="rounded-xl border border-edge bg-[#120e24] p-3">
      {lines.length ? (
        <div className="flex flex-col gap-1">
          {lines.map((l, i) => (
            <span key={i} className="font-mono text-xs text-muted">
              {l}
            </span>
          ))}
        </div>
      ) : (
        <span className="text-xs italic text-muted">{empty}</span>
      )}
    </div>
  );
}
function Row({ children }: { children: ReactNode }) {
  return <div className="flex items-center justify-between gap-3 rounded-xl border border-edge p-2.5">{children}</div>;
}
function Sel({ value, onChange, options }: { value: string; onChange: (v: string) => void; options: { value: string; label: string }[] }) {
  return (
    <RSelect.Root value={value} onValueChange={onChange}>
      <RSelect.Trigger className="inline-flex min-w-[130px] items-center justify-between gap-2 rounded-lg border border-edge bg-panel px-3 py-2 text-sm text-cloud outline-none">
        <RSelect.Value />
        <RSelect.Icon>
          <ChevronDownIcon />
        </RSelect.Icon>
      </RSelect.Trigger>
      <RSelect.Portal>
        <RSelect.Content className="radix-surface z-50 overflow-hidden">
          <RSelect.Viewport className="p-1">
            {options.map((o) => (
              <RSelect.Item
                key={o.value}
                value={o.value}
                className="relative cursor-pointer select-none rounded px-6 py-1.5 text-sm outline-none data-[highlighted]:bg-accent data-[highlighted]:text-ink"
              >
                <RSelect.ItemIndicator className="absolute left-1.5">
                  <CheckIcon />
                </RSelect.ItemIndicator>
                <RSelect.ItemText>{o.label}</RSelect.ItemText>
              </RSelect.Item>
            ))}
          </RSelect.Viewport>
        </RSelect.Content>
      </RSelect.Portal>
    </RSelect.Root>
  );
}
function Sw({ checked, onChange }: { checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <RSwitch.Root
      checked={checked}
      onCheckedChange={onChange}
      className="relative h-6 w-11 rounded-full bg-edge transition-colors data-[state=checked]:bg-accent"
    >
      <RSwitch.Thumb className="block h-5 w-5 translate-x-0.5 rounded-full bg-cloud transition-transform data-[state=checked]:translate-x-[22px]" />
    </RSwitch.Root>
  );
}

function ThemeToggle() {
  const [theme, setThemeState] = useState<Theme>(getTheme());
  useEffect(() => watchSystem(() => {}), []); // re-apply on OS change while in "system"
  const opts: { value: Theme; icon: ReactNode; label: string }[] = [
    { value: "light", icon: <SunIcon />, label: "Light" },
    { value: "dark", icon: <MoonIcon />, label: "Dark" },
    { value: "system", icon: <DesktopIcon />, label: "Windows (system)" },
  ];
  return (
    <div className="flex items-center overflow-hidden rounded-full border border-edge">
      {opts.map((o) => (
        <Tooltip.Root key={o.value}>
          <Tooltip.Trigger asChild>
            <button
              aria-label={o.label}
              onClick={() => {
                setTheme(o.value);
                setThemeState(o.value);
              }}
              className={`px-2 py-1.5 text-xs transition ${theme === o.value ? "bg-accent text-ink" : "text-muted hover:bg-panel"}`}
            >
              {o.icon}
            </button>
          </Tooltip.Trigger>
          <Tooltip.Portal>
            <Tooltip.Content sideOffset={6} className="radix-surface z-50 px-2 py-1 text-xs">
              {o.label}
              <Tooltip.Arrow className="fill-edge" />
            </Tooltip.Content>
          </Tooltip.Portal>
        </Tooltip.Root>
      ))}
    </div>
  );
}

export default function App() {
  const [tab, setTab] = useState<TabKey>("chat");
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

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, activity, streaming]);

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

  const args = pending?.req.args as Record<string, unknown> | undefined;
  const shot = args && typeof args.screenshot_b64 === "string" ? (args.screenshot_b64 as string) : "";

  return (
    <div className="flex h-screen flex-col bg-ink text-cloud">
      <header className="flex items-center gap-3 border-b border-edge px-4 py-3">
        <span className={`h-2.5 w-2.5 rounded-full ${connected ? "bg-up" : "bg-down"}`} />
        <h1 className="text-lg font-semibold tracking-wide">Purple</h1>
        {model && <Chip>{model}</Chip>}
        <div className="flex-1" />
        <Tooltip.Root>
          <Tooltip.Trigger asChild>
            <button
              onClick={toggleObserve}
              className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs transition ${
                observing ? "bg-up text-ink" : "border border-edge text-muted hover:bg-panel"
              }`}
            >
              <EyeOpenIcon /> {observing ? "Observing" : "Observe off"}
            </button>
          </Tooltip.Trigger>
          <Tooltip.Portal>
            <Tooltip.Content sideOffset={6} className="radix-surface z-50 max-w-[260px] px-2 py-1 text-xs">
              When on, Purple can see your active window title to ground vague requests. Off by default; auto-stops after a few hours.
              <Tooltip.Arrow className="fill-edge" />
            </Tooltip.Content>
          </Tooltip.Portal>
        </Tooltip.Root>
        <ThemeToggle />
        <a className="rounded-full border border-edge px-3 py-1.5 text-xs text-muted hover:bg-panel" href="/docs" target="_blank" rel="noreferrer">
          API
        </a>
      </header>

      <Tabs.Root value={tab} onValueChange={(v) => setTab(v as TabKey)} className="flex min-h-0 flex-1 flex-col">
        <Tabs.List className="flex gap-1 border-b border-edge px-3">
          {TABS.map((t) => (
            <Tabs.Trigger
              key={t}
              value={t}
              className="border-b-2 border-transparent px-3 py-2 text-sm capitalize text-muted transition hover:text-cloud data-[state=active]:border-accent data-[state=active]:text-cloud"
            >
              {t}
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        <Tabs.Content value="chat" className="flex min-h-0 flex-1 flex-col data-[state=inactive]:hidden">
          <div className="flex flex-1 flex-col gap-2 overflow-y-auto p-4">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`max-w-[78%] whitespace-pre-wrap rounded-2xl px-3.5 py-2.5 ${
                  m.role === "user" ? "self-end bg-userbubble" : "self-start border border-edge bg-panel"
                }`}
              >
                {m.text}
              </div>
            ))}
            {streaming && <div className="max-w-[78%] self-start whitespace-pre-wrap rounded-2xl border border-edge bg-panel px-3.5 py-2.5">{streaming}</div>}
            {activity && <span className="self-start text-xs italic text-muted">{activity}</span>}
            <div ref={endRef} />
          </div>
          <div className="flex gap-2 border-t border-edge p-3">
            <Field
              placeholder="Ask Purple anything…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendText()}
            />
            <Btn variant={recording ? "good" : "outline"} onClick={toggleMic}>
              {recording ? "Stop" : "Mic"}
            </Btn>
            <Btn variant="primary" onClick={sendText}>
              Send <PaperPlaneIcon />
            </Btn>
          </div>
        </Tabs.Content>

        <Tabs.Content value="monitor" className="min-h-0 flex-1 data-[state=inactive]:hidden">
          <MonitorPanel feed={feed} />
        </Tabs.Content>
        <Tabs.Content value="automations" className="min-h-0 flex-1 data-[state=inactive]:hidden">
          <AutomationsPanel />
        </Tabs.Content>
        <Tabs.Content value="memory" className="min-h-0 flex-1 data-[state=inactive]:hidden">
          <MemoryPanel />
        </Tabs.Content>
        <Tabs.Content value="missions" className="min-h-0 flex-1 data-[state=inactive]:hidden">
          <MissionsPanel />
        </Tabs.Content>
        <Tabs.Content value="settings" className="min-h-0 flex-1 data-[state=inactive]:hidden">
          <SettingsPanel />
        </Tabs.Content>
      </Tabs.Root>

      <Dialog.Root open={!!pending} onOpenChange={(o) => !o && resolveConfirm(false)}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 z-40 bg-black/60" />
          <Dialog.Content className="radix-surface fixed left-1/2 top-1/2 z-50 w-[460px] max-w-[90vw] -translate-x-1/2 -translate-y-1/2 p-5">
            <Dialog.Title className="mb-2 text-lg font-semibold">Confirm action</Dialog.Title>
            <Dialog.Description className="mb-2 text-sm text-muted">
              Purple wants to run <b className="text-cloud">{pending?.req.tool}</b>:
            </Dialog.Description>
            <pre className="overflow-x-auto rounded-lg bg-ink p-2 font-mono text-xs text-muted">
              {pending &&
                JSON.stringify(Object.fromEntries(Object.entries(pending.req.args).filter(([k]) => k !== "screenshot_b64")))}
            </pre>
            {shot && <img className="mt-3 max-w-full rounded-lg" src={"data:image/png;base64," + shot} alt="screen" />}
            <div className="mt-4 flex justify-end gap-2">
              <Btn variant="ghost" onClick={() => resolveConfirm(false)}>
                Cancel
              </Btn>
              <Btn variant="good" onClick={() => resolveConfirm(true)}>
                Allow
              </Btn>
            </div>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
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

  return (
    <Panel>
      {h ? (
        <div className="flex flex-wrap gap-1.5">
          <Chip tone={h.ollama ? "up" : "down"}>Ollama</Chip>
          <Chip tone={h.database ? "up" : "down"}>Database</Chip>
          <Chip>{h.tools} tools</Chip>
          <Chip>brain: {h.model}</Chip>
          <Chip>eyes: {h.vision_model}</Chip>
          <Chip>wake: {h.wake_enabled ? "on" : "off"}</Chip>
          <Chip>scheduler: {h.scheduler_enabled ? "on" : "off"}</Chip>
          {st && <Chip>up {Math.round((st.uptime_seconds || 0) / 60)}m</Chip>}
          {st?.focus && <Chip tone={st.focus.yielding ? "down" : "up"}>{st.focus.yielding ? "GPU: yielding" : "GPU: free"}</Chip>}
        </div>
      ) : (
        <span className="text-sm text-muted">Connecting…</span>
      )}

      {st?.focus && (
        <Btn variant="outline" className="self-start" onClick={() => client.setFocus(!st.focus.manual).then((f) => setSt({ ...st, focus: f }))}>
          {st.focus.manual ? "Focus mode: ON — release the GPU" : "Focus mode: OFF — pause GPU work"}
        </Btn>
      )}

      {m && m.enabled && (
        <div className="flex flex-wrap gap-2">
          {[
            [m.turns, "turns"],
            [m.llm_calls, "LLM calls"],
            [`${m.llm_avg_ms} ms`, "avg LLM"],
            [m.tool_calls, "tool calls"],
            [`${m.tool_avg_ms} ms`, "avg tool"],
          ].map(([v, label], i) => (
            <div key={i} className="min-w-[96px] rounded-xl border border-edge bg-panel px-3 py-2">
              <div className="text-lg font-semibold">{v}</div>
              <div className="text-xs text-muted">{label}</div>
            </div>
          ))}
        </div>
      )}

      {m && m.tools && m.tools.length > 0 && (
        <>
          <Section>Tool usage</Section>
          <Feed lines={m.tools.map((t: any) => `${t.tool} (${t.ok === "true" ? "ok" : "fail"}): ${t.count}`)} empty="—" />
        </>
      )}

      <Section>Live activity</Section>
      <Feed lines={feed.slice().reverse()} empty="quiet…" />

      <Section>Recent logs</Section>
      <Feed lines={logs.slice().reverse()} empty="no logs yet…" />
    </Panel>
  );
}

function AutomationsPanel() {
  const empty = { name: "", effect: "speak", keywords: "", source: "any", min_priority: "normal", action: "" };
  const [rules, setRules] = useState<Automation[]>([]);
  const [draft, setDraft] = useState(empty);
  const [msg, setMsg] = useState("");

  const load = () => client.listAutomations().then((r) => setRules(r.rules || [])).catch(() => {});
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
      source: draft.source === "any" ? "" : draft.source,
      min_priority: draft.min_priority,
      action: draft.action.trim(),
    });
    setDraft(empty);
    setMsg("Rule added.");
    load();
  }

  return (
    <Panel>
      <p className="text-sm text-muted">
        Rules shape what Purple tells you — <b className="text-cloud">speak</b> gives a gentle nudge even mid-game,{" "}
        <b className="text-cloud">mute</b> stays silent, <b className="text-cloud">notify</b> is normal. They only change
        notifications; they never run actions on their own.
      </p>

      <div className="flex flex-col gap-2 rounded-xl border border-edge bg-panel p-3">
        <Field placeholder="Rule name (e.g. Hear my boss)" value={draft.name} onChange={(e) => setDraft({ ...draft, name: e.target.value })} />
        <Field placeholder="keywords, comma-separated (blank = any)" value={draft.keywords} onChange={(e) => setDraft({ ...draft, keywords: e.target.value })} />
        <div className="flex flex-wrap gap-2">
          <Sel
            value={draft.source}
            onChange={(v) => setDraft({ ...draft, source: v })}
            options={[
              { value: "any", label: "any source" },
              ...["email", "call", "message", "calendar", "system"].map((s) => ({ value: s, label: s })),
            ]}
          />
          <Sel
            value={draft.min_priority}
            onChange={(v) => setDraft({ ...draft, min_priority: v })}
            options={["low", "normal", "important"].map((p) => ({ value: p, label: `≥ ${p}` }))}
          />
          <Sel value={draft.effect} onChange={(v) => setDraft({ ...draft, effect: v })} options={["speak", "mute", "notify"].map((x) => ({ value: x, label: x }))} />
        </div>
        <Field placeholder="run a tool (optional)" value={draft.action} onChange={(e) => setDraft({ ...draft, action: e.target.value })} />
        <Btn variant="primary" className="self-start" onClick={add}>
          Add rule
        </Btn>
      </div>
      <span className="text-xs text-muted">
        {msg || "Actions run under the autonomy setting (Settings → autonomy: notify / confirm / act)."}
      </span>

      {rules.length === 0 && <span className="text-xs text-muted">No automations yet — add one above.</span>}
      {rules.map((r) => (
        <Row key={r.id}>
          <div className={r.enabled ? "" : "opacity-50"}>
            <div className="font-semibold">{r.name}</div>
            <div className="mt-1 flex flex-wrap gap-1">
              <Chip tone={r.effect === "mute" ? "muted" : "accent"}>{r.effect}</Chip>
              <Chip>{r.source || "any source"}</Chip>
              <Chip>≥ {r.min_priority}</Chip>
              {r.keywords.length > 0 && <Chip>{r.keywords.join(", ")}</Chip>}
              {r.action && <Chip tone="accent">▶ {r.action}</Chip>}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Btn variant="outline" onClick={() => client.toggleAutomation(r.id, !r.enabled).then(load)}>
              {r.enabled ? "On" : "Off"}
            </Btn>
            <IconBtn onClick={() => client.removeAutomation(r.id).then(load)}>
              <TrashIcon />
            </IconBtn>
          </div>
        </Row>
      ))}
    </Panel>
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

  if (!mem)
    return (
      <Panel>
        <span className="text-sm text-muted">Loading…</span>
      </Panel>
    );
  const facts = results ?? mem.facts;

  return (
    <Panel>
      <Section>What Purple knows</Section>
      <div className="flex items-center gap-2">
        <Chip>auto-learn: {mem.auto_memory ? mem.auto_memory_mode : "off"}</Chip>
        <Sel
          value={mem.auto_memory_mode}
          onChange={async (v) => {
            await client.saveConfig({ auto_memory_mode: v });
            setMem({ ...mem, auto_memory_mode: v });
          }}
          options={["moderate", "high", "aggressive"].map((x) => ({ value: x, label: `learn: ${x}` }))}
        />
      </div>

      <Section>Profile</Section>
      <div className="flex flex-col gap-2">
        {Object.entries(mem.profile).map(([k, v]) => (
          <label key={k} className="flex items-center gap-3">
            <span className="w-32 text-sm text-muted">{k.replace(/_/g, " ")}</span>
            <Field defaultValue={v} onBlur={(e) => client.setProfileField(k, e.target.value).then(load)} />
          </label>
        ))}
        <div className="flex flex-wrap gap-2">
          <Field placeholder="field (e.g. location)" value={newKey} onChange={(e) => setNewKey(e.target.value)} />
          <Field placeholder="value" value={newVal} onChange={(e) => setNewVal(e.target.value)} />
          <Btn
            variant="outline"
            onClick={async () => {
              if (!newKey.trim()) return;
              await client.setProfileField(newKey.trim(), newVal.trim());
              setNewKey("");
              setNewVal("");
              load();
            }}
          >
            Set field
          </Btn>
        </div>
      </div>

      {mem.people.length > 0 && (
        <>
          <Section>People</Section>
          {mem.people.map((p) => (
            <Row key={p.id}>
              <div>
                <div className="font-semibold">{p.name}</div>
                <div className="mt-1 flex flex-wrap gap-1">
                  {p.relation && <Chip>{p.relation}</Chip>}
                  {p.aliases.length > 0 && <Chip>{p.aliases.join(", ")}</Chip>}
                </div>
              </div>
              <IconBtn onClick={() => client.deletePerson(p.id).then(load)}>
                <TrashIcon />
              </IconBtn>
            </Row>
          ))}
        </>
      )}

      <Section>Knowledge (documents)</Section>
      <div className="flex flex-wrap gap-2">
        <div className="min-w-[220px] flex-1">
          <Field
            placeholder="file or folder path to learn…"
            value={ingestPath}
            onChange={(e) => setIngestPath(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && ingest()}
          />
        </div>
        <Btn variant="outline" onClick={ingest}>
          Learn
        </Btn>
      </div>
      {ingestMsg && <span className="text-xs text-muted">{ingestMsg}</span>}
      {docs.length === 0 && <span className="text-xs text-muted">No documents learned yet.</span>}
      {docs.map((d) => (
        <Row key={d.id}>
          <div>
            <div className="font-semibold">{d.title}</div>
            <div className="mt-1 flex flex-wrap gap-1">
              <Chip>{d.chunks} passages</Chip>
              <Chip>{d.path}</Chip>
            </div>
          </div>
          <IconBtn onClick={() => client.removeDocument(d.id).then(loadDocs)}>
            <TrashIcon />
          </IconBtn>
        </Row>
      ))}

      <Section>Facts</Section>
      <div className="flex flex-wrap gap-2">
        <div className="min-w-[220px] flex-1">
          <Field
            placeholder="search what Purple knows…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && search()}
          />
        </div>
        <Btn variant="outline" onClick={search}>
          Search
        </Btn>
        {results !== null && (
          <Btn
            variant="ghost"
            onClick={() => {
              setResults(null);
              setQuery("");
            }}
          >
            Clear
          </Btn>
        )}
      </div>
      <div className="flex flex-wrap gap-2">
        <div className="min-w-[220px] flex-1">
          <Field placeholder="teach Purple a fact…" value={newFact} onChange={(e) => setNewFact(e.target.value)} />
        </div>
        <Btn
          variant="outline"
          onClick={async () => {
            if (!newFact.trim()) return;
            await client.addFact(newFact.trim());
            setNewFact("");
            load();
          }}
        >
          Add fact
        </Btn>
      </div>
      {facts.length === 0 && <span className="text-xs text-muted">Nothing yet.</span>}
      {facts.map((f) => (
        <Row key={f.id}>
          <div>
            <div>{f.text}</div>
            <div className="mt-1">
              <Chip>{f.category}</Chip>
            </div>
          </div>
          <IconBtn
            onClick={() =>
              client.deleteFact(f.id).then(() => {
                setResults(null);
                load();
              })
            }
          >
            <TrashIcon />
          </IconBtn>
        </Row>
      ))}
    </Panel>
  );
}

function VoiceEnroll() {
  const [voices, setVoices] = useState<string[]>([]);
  const [info, setInfo] = useState<{ available: boolean; enforced: boolean }>({ available: false, enforced: false });
  const [name, setName] = useState("");
  const [status, setStatus] = useState("");
  const [recording, setRecording] = useState(false);

  const load = () =>
    client
      .voices()
      .then((r) => {
        setVoices(r.voices || []);
        setInfo({ available: r.available, enforced: r.enforced });
      })
      .catch(() => {});
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
    <div className="flex flex-col gap-2">
      <Section>Voice access</Section>
      <div className="flex flex-wrap gap-1.5">
        <Chip tone={info.enforced ? "up" : "muted"}>{info.enforced ? "locked: only enrolled voices" : "not enforced yet"}</Chip>
        {!info.available && <Chip tone="down">speaker model not installed</Chip>}
      </div>
      <div className="flex flex-wrap gap-2">
        <Field placeholder="your name" value={name} onChange={(e) => setName(e.target.value)} />
        <Btn variant="outline" onClick={record} disabled={recording || !info.available}>
          {recording ? "Recording…" : "Enroll (record 4s)"}
        </Btn>
      </div>
      {status && <span className="text-xs text-muted">{status}</span>}
      {voices.length === 0 && <span className="text-xs text-muted">No voices enrolled yet.</span>}
      {voices.map((v) => (
        <Row key={v}>
          <div className="font-semibold">{v}</div>
          <IconBtn onClick={() => client.removeVoice(v).then(load)}>
            <TrashIcon />
          </IconBtn>
        </Row>
      ))}
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
    <Panel>
      <Section>Missions</Section>
      <div className="flex flex-wrap gap-2">
        <div className="min-w-[240px] flex-1">
          <Field
            placeholder="give Purple a goal to carry out…"
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && start()}
          />
        </div>
        <Btn variant="primary" onClick={start}>
          Start mission
        </Btn>
      </div>
      <span className="text-xs text-muted">She plans + works it in the background; risky steps pause for your approval.</span>

      {missions.length === 0 && <span className="text-xs text-muted">No missions yet.</span>}
      {missions.map((m) => (
        <div key={m.id} className="rounded-xl border border-edge p-2.5">
          <div className="flex justify-between gap-3">
            <div>
              <div className="cursor-pointer font-semibold" onClick={() => toggle(m.id)}>
                #{m.id} {m.goal}
              </div>
              <div className="mt-1">
                <Chip tone={m.status === "blocked" ? "down" : "muted"}>{m.status}</Chip>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {m.status === "blocked" && (
                <Btn variant="outline" onClick={() => client.resumeMission(m.id).then(load)}>
                  Approve
                </Btn>
              )}
              {(m.status === "running" || m.status === "blocked" || m.status === "planned") && (
                <Btn variant="ghost" onClick={() => client.cancelMission(m.id).then(load)}>
                  Cancel
                </Btn>
              )}
              <Btn variant="ghost" onClick={() => toggle(m.id)}>
                {open[m.id] ? "Hide" : "Steps"}
              </Btn>
            </div>
          </div>
          {open[m.id] && (
            <div className="mt-2">
              <Feed lines={open[m.id].steps.map((s) => `[${s.status}] ${s.title}${s.result ? ` — ${s.result.slice(0, 120)}` : ""}`)} empty="—" />
            </div>
          )}
        </div>
      ))}
    </Panel>
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

  if (!cfg)
    return (
      <Panel>
        <span className="text-sm text-muted">Loading…</span>
      </Panel>
    );
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
    setMsg(`Saved: ${r.applied.join(", ")}.` + (r.restart_needed.length ? ` Restart needed for: ${r.restart_needed.join(", ")}.` : ""));
    setCfg({ ...cfg, ...updates });
  }

  return (
    <Panel>
      <VoiceEnroll />
      <Section>Configuration</Section>
      <div className="flex flex-col gap-2">
        {fields.map((k) => (
          <label key={k} className="flex items-center justify-between gap-3">
            <span className="text-sm text-muted">{k}</span>
            {typeof cfg![k] === "boolean" ? (
              <Sw checked={!!draft[k]} onChange={(v) => set(k, v)} />
            ) : typeof cfg![k] === "number" ? (
              <input className={`${FIELD} max-w-[200px]`} type="number" value={draft[k]} onChange={(e) => set(k, Number(e.target.value))} />
            ) : (
              <input className={`${FIELD} max-w-[260px]`} type="text" value={draft[k] ?? ""} onChange={(e) => set(k, e.target.value)} />
            )}
          </label>
        ))}
      </div>
      <div className="flex items-center gap-3">
        <Btn variant="primary" onClick={save}>
          Save
        </Btn>
        {msg && <span className="text-xs text-muted">{msg}</span>}
      </div>
    </Panel>
  );
}
