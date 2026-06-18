import * as Tooltip from "@radix-ui/react-tooltip";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./App.css";
import { apply, getTheme } from "./theme";

apply(getTheme()); // set light/dark/system before first paint (no flash)

const el = document.getElementById("root");
if (el) {
  createRoot(el).render(
    <StrictMode>
      <Tooltip.Provider delayDuration={300}>
        <App />
      </Tooltip.Provider>
    </StrictMode>
  );
}
