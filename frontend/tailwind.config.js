/** @type {import('tailwindcss').Config} */
const c = (v) => `rgb(var(${v}) / <alpha-value>)`;

export default {
  content: ["./index.html", "./ui-src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      // Theme-aware via CSS variables (see App.css). Switching .light/.dark on <html>
      // re-colors the whole UI; opacity modifiers like text-muted/70 still work.
      colors: {
        ink: c("--c-ink"), // app background
        panel: c("--c-panel"), // cards / surfaces
        edge: c("--c-edge"), // borders
        muted: c("--c-muted"), // secondary text
        cloud: c("--c-cloud"), // primary text
        accent: c("--c-accent"), // purple
        up: c("--c-up"), // good / connected
        down: c("--c-down"), // bad / error
        userbubble: c("--c-userbubble"), // user chat bubble
      },
    },
  },
  plugins: [],
};
