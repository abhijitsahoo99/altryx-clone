"use client";

import { useEffect, useState } from "react";

export function useDarkMode() {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("altryx-dark-mode");
    if (stored === "true") {
      setIsDark(true);
      document.documentElement.classList.add("dark");
    }
  }, []);

  const toggle = () => {
    const next = !isDark;
    setIsDark(next);
    if (next) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("altryx-dark-mode", "true");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("altryx-dark-mode", "false");
    }
  };

  return { isDark, toggle };
}
