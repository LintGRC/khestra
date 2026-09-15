export type ThemeChoice = "light" | "dark" | "system";
export type BrandChoice = "classic" | "lintgrc";

const THEME_KEY = "cmmc_theme";
const BRAND_KEY = "cmmc_brand";

export function getStoredTheme(): ThemeChoice {
  const v = localStorage.getItem(THEME_KEY);
  if (v === "light" || v === "dark" || v === "system") return v;
  return "system";
}

export function getStoredBrand(): BrandChoice {
  const v = localStorage.getItem(BRAND_KEY);
  if (v === "classic") return "classic";
  if (v === "lintgrc") return "lintgrc";
  return "lintgrc";
}

export function resolveTheme(choice: ThemeChoice): "light" | "dark" {
  if (choice === "system") {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  return choice;
}

export function applyTheme(choice: ThemeChoice) {
  localStorage.setItem(THEME_KEY, choice);
  document.documentElement.setAttribute("data-theme", resolveTheme(choice));
}

export function applyBrand(choice: BrandChoice) {
  localStorage.setItem(BRAND_KEY, choice);
  if (choice === "lintgrc") {
    document.documentElement.setAttribute("data-brand", "lintgrc");
  } else {
    document.documentElement.removeAttribute("data-brand");
  }
}

export function initTheme() {
  applyTheme(getStoredTheme());
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
    if (getStoredTheme() === "system") {
      applyTheme("system");
    }
  });
}

export function initBrand() {
  applyBrand(getStoredBrand());
}

/** Theme + LintGRC brand skin (default). Classic available in workspace settings. */
export function initAppearance() {
  initTheme();
  initBrand();
}
