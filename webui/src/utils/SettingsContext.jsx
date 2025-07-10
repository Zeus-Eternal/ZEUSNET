import { createContext, useContext, useEffect, useState } from "react";
import { fetchSettings, updateMode } from "./api";

const SettingsContext = createContext();

export function SettingsProvider({ children }) {
  const [settings, setSettings] = useState({ mode: "SAFE" });
  useEffect(() => {
    fetchSettings().then((data) => {
      setSettings(data);
      localStorage.setItem("ZEUSNET_MODE", data.mode);
    });
  }, []);

  const setMode = async (mode) => {
    const data = await updateMode(mode);
    setSettings((s) => ({ ...s, mode: data.mode }));
  };

  return (
    <SettingsContext.Provider value={{ settings, setMode }}>
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings() {
  return useContext(SettingsContext);
}
