// Light / Dark / Windows(system) theme. The palette is defined as CSS variables in
// App.css for `.light` and `.dark`; we just toggle the class on <html>. "system" follows
// the OS (Windows) setting via prefers-color-scheme, and updates live when it changes.

export type Theme = "light" | "dark" | "system";

const KEY = "purple-theme";

export function getTheme(): Theme {
  try {
    const t = localStorage.getItem(KEY);
    if (t === "light" || t === "dark" || t === "system") return t;
  } catch {
    /* localStorage unavailable — fall through */
  }
  return "system";
}

export function resolve(theme: Theme): "light" | "dark" {
  if (theme === "system") {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  return theme;
}

export function apply(theme: Theme): void {
  const mode = resolve(theme);
  const root = document.documentElement;
  root.classList.remove("light", "dark");
  root.classList.add(mode);
}

export function setTheme(theme: Theme): void {
  try {
    localStorage.setItem(KEY, theme);
  } catch {
    /* ignore */
  }
  apply(theme);
}

// Re-apply when the OS theme changes, but only while we're in "system" mode.
export function watchSystem(onChange: () => void): () => void {
  const mq = window.matchMedia("(prefers-color-scheme: dark)");
  const handler = () => {
    if (getTheme() === "system") {
      apply("system");
      onChange();
    }
  };
  mq.addEventListener("change", handler);
  return () => mq.removeEventListener("change", handler);
}
