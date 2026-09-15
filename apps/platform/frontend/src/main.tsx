import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import AuthProvider from "@cmmc/auth/AuthProvider";
import { initAppearance } from "@cmmc/theme";
import "@cmmc/styles.css";
import "@cmmc/lintgrc-brand.css";
import "@soc2/soc2.css";
import "@iso27001/iso27001.css";
import "@shared/platform.css";
import "@shared/filter-bar/filter-bar.css";

initAppearance();

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
