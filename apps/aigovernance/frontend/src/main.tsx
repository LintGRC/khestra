import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import AuthProvider from "./auth/AuthProvider";
import { initAppearance } from "./theme";
import "./styles.css";
import "./lintgrc-brand.css";
import "./aigov.css";
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
