// Purple backend client: WebSocket chat (confirmations + live activity), health,
// and config read/write. Copy into the scaffolded app's src/ folder.

export type ConfirmRequest = {
  type: "confirm_request";
  tool: string;
  args: Record<string, unknown>;
};
export type ReplyMsg = { type: "reply"; reply: string };
export type ReplyChunkMsg = { type: "reply_chunk"; text: string };
export type StatusMsg = { type: "status"; state: string };
export type VoiceMsg = {
  type: "voice";
  state: "listening" | "woke" | "heard" | "reply";
  text?: string;
};
export type ToolMsg = { type: "tool"; name: string };
export type ServerMsg =
  | ConfirmRequest
  | ReplyMsg
  | ReplyChunkMsg
  | StatusMsg
  | VoiceMsg
  | ToolMsg;
export type Activity = StatusMsg | VoiceMsg | ToolMsg;

export type Health = {
  ok: boolean;
  ollama: boolean;
  model: string;
  database: boolean;
  speech_provider: string;
  vision_model: string;
  wake_enabled: boolean;
  scheduler_enabled: boolean;
  tools: number;
  tool_names: string[];
};

export type Automation = {
  id: number;
  name: string;
  keywords: string[];
  source: string;
  min_priority: string;
  effect: string;
  enabled: boolean;
  action?: string;
  action_args?: Record<string, unknown>;
};

export type MemoryFact = { id: number; text: string; category: string; created_at: string | null };
export type Person = {
  id: number;
  name: string;
  relation: string;
  aliases: string[];
  notes: string;
};
export type MemoryOverview = {
  profile: Record<string, string>;
  people: Person[];
  facts: MemoryFact[];
  auto_memory: boolean;
  auto_memory_mode: string;
};

export type KbDocument = { id: number; title: string; path: string; chunks: number };

export type MissionStep = {
  id: number;
  ordinal: number;
  title: string;
  status: string;
  result: string;
};
export type MissionSummary = { id: number; goal: string; status: string };
export type MissionDetail = MissionSummary & { steps: MissionStep[] };

const HTTP_BASE = "http://127.0.0.1:8765";
const WS_URL = "ws://127.0.0.1:8765/ws";

export class PurpleClient {
  private ws: WebSocket | null = null;

  onReply: (text: string) => void = () => {};
  onReplyChunk: (text: string) => void = () => {};
  onStatus: (connected: boolean) => void = () => {};
  onActivity: (msg: Activity) => void = () => {};
  onConfirm: (req: ConfirmRequest) => Promise<boolean> = async () => false;

  connect(): void {
    const ws = new WebSocket(WS_URL);
    this.ws = ws;
    ws.onopen = () => this.onStatus(true);
    ws.onclose = () => {
      this.onStatus(false);
      setTimeout(() => this.connect(), 2000);
    };
    ws.onmessage = async (e) => {
      const msg: ServerMsg = JSON.parse(e.data);
      switch (msg.type) {
        case "confirm_request":
          ws.send(JSON.stringify({ approved: await this.onConfirm(msg) }));
          break;
        case "reply":
          this.onReply(msg.reply);
          break;
        case "reply_chunk":
          this.onReplyChunk(msg.text);
          break;
        case "status":
        case "voice":
        case "tool":
          this.onActivity(msg);
          break;
      }
    };
  }

  send(message: string): void {
    this.ws?.send(JSON.stringify({ message }));
  }

  async health(): Promise<Health> {
    return (await fetch(`${HTTP_BASE}/health`)).json();
  }

  async metricsSummary(): Promise<Record<string, any>> {
    return (await fetch(`${HTTP_BASE}/metrics/summary`)).json();
  }

  async logs(n = 120): Promise<{ lines: string[] }> {
    return (await fetch(`${HTTP_BASE}/logs?n=${n}`)).json();
  }

  async status(): Promise<Record<string, any>> {
    return (await fetch(`${HTTP_BASE}/status`)).json();
  }

  async system(): Promise<{ cpu: number; ram: number; gpu: number; vram: number }> {
    return (await fetch(`${HTTP_BASE}/system`)).json();
  }

  async setFocus(on: boolean): Promise<Record<string, any>> {
    return (
      await fetch(`${HTTP_BASE}/focus`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ on }),
      })
    ).json();
  }

  async getObserve(): Promise<{ observing: boolean; auto_off_hours: number }> {
    return (await fetch(`${HTTP_BASE}/observe`)).json();
  }

  async setObserve(on: boolean): Promise<{ observing: boolean }> {
    return (
      await fetch(`${HTTP_BASE}/observe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ on }),
      })
    ).json();
  }

  async getConfig(): Promise<Record<string, unknown>> {
    return (await fetch(`${HTTP_BASE}/config`)).json();
  }

  async saveConfig(
    updates: Record<string, unknown>
  ): Promise<{ applied: string[]; restart_needed: string[] }> {
    const r = await fetch(`${HTTP_BASE}/config`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updates),
    });
    return r.json();
  }

  async listAutomations(): Promise<{ rules: Automation[] }> {
    return (await fetch(`${HTTP_BASE}/automations`)).json();
  }

  async addAutomation(rule: Partial<Automation>): Promise<{ id: number }> {
    return (
      await fetch(`${HTTP_BASE}/automations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(rule),
      })
    ).json();
  }

  async toggleAutomation(id: number, enabled: boolean): Promise<{ ok: boolean }> {
    return (
      await fetch(`${HTTP_BASE}/automations/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enabled }),
      })
    ).json();
  }

  async removeAutomation(id: number): Promise<{ ok: boolean }> {
    return (await fetch(`${HTTP_BASE}/automations/${id}`, { method: "DELETE" })).json();
  }

  async memory(): Promise<MemoryOverview> {
    return (await fetch(`${HTTP_BASE}/memory`)).json();
  }

  async memorySearch(q: string): Promise<{ facts: MemoryFact[] }> {
    return (await fetch(`${HTTP_BASE}/memory/search?q=${encodeURIComponent(q)}`)).json();
  }

  async addFact(text: string, category = "fact"): Promise<{ ok: boolean }> {
    return (
      await fetch(`${HTTP_BASE}/memory/fact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, category }),
      })
    ).json();
  }

  async deleteFact(id: number): Promise<{ ok: boolean }> {
    return (await fetch(`${HTTP_BASE}/memory/fact/${id}`, { method: "DELETE" })).json();
  }

  async setProfileField(key: string, value: string): Promise<{ ok: boolean }> {
    return (
      await fetch(`${HTTP_BASE}/memory/profile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key, value }),
      })
    ).json();
  }

  async deletePerson(id: number): Promise<{ ok: boolean }> {
    return (await fetch(`${HTTP_BASE}/memory/person/${id}`, { method: "DELETE" })).json();
  }

  async documents(): Promise<{ documents: KbDocument[] }> {
    return (await fetch(`${HTTP_BASE}/documents`)).json();
  }

  async ingestDocuments(path: string): Promise<Record<string, unknown>> {
    return (
      await fetch(`${HTTP_BASE}/documents/ingest`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path }),
      })
    ).json();
  }

  async removeDocument(id: number): Promise<{ ok: boolean }> {
    return (await fetch(`${HTTP_BASE}/documents/${id}`, { method: "DELETE" })).json();
  }

  async voices(): Promise<{ voices: string[]; available: boolean; enforced: boolean }> {
    return (await fetch(`${HTTP_BASE}/voice/voices`)).json();
  }

  async enrollVoice(name: string, audio: Blob): Promise<Record<string, unknown>> {
    const fd = new FormData();
    fd.append("name", name);
    fd.append("file", audio, "enroll.webm");
    return (await fetch(`${HTTP_BASE}/voice/enroll`, { method: "POST", body: fd })).json();
  }

  async removeVoice(name: string): Promise<{ ok: boolean }> {
    return (await fetch(`${HTTP_BASE}/voice/voices/${encodeURIComponent(name)}`, { method: "DELETE" })).json();
  }

  async missions(): Promise<{ missions: MissionSummary[] }> {
    return (await fetch(`${HTTP_BASE}/missions`)).json();
  }

  async mission(id: number): Promise<MissionDetail> {
    return (await fetch(`${HTTP_BASE}/missions/${id}`)).json();
  }

  async startMission(goal: string): Promise<Record<string, unknown>> {
    return (
      await fetch(`${HTTP_BASE}/missions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ goal }),
      })
    ).json();
  }

  async cancelMission(id: number): Promise<{ ok: boolean }> {
    return (await fetch(`${HTTP_BASE}/missions/${id}`, { method: "DELETE" })).json();
  }

  async resumeMission(id: number): Promise<{ ok: boolean }> {
    return (await fetch(`${HTTP_BASE}/missions/${id}/resume`, { method: "POST" })).json();
  }

  async sendVoice(
    audio: Blob
  ): Promise<{ transcript: string; reply: string; audio_base64: string }> {
    const fd = new FormData();
    fd.append("file", audio, "speech.webm");
    return (await fetch(`${HTTP_BASE}/voice`, { method: "POST", body: fd })).json();
  }
}
