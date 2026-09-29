import React, { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

import App from "./App";

const root = createRoot(document.getElementById("root"));
root.render(
  <StrictMode>
    <App />
  </StrictMode>
);

// PWA: registra el service worker només en producció (en dev interferiria amb HMR)
if (process.env.NODE_ENV === "production" && "serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    const base = process.env.PUBLIC_URL || "";
    navigator.serviceWorker
      .register(`${base}/sw.js`, { scope: `${base}/` })
      .catch((err) => console.warn("Service worker no registrat:", err));
  });
}
