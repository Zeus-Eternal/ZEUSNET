import React from "react";
import { useSettings } from "../utils/SettingsContext";

export default function Topbar({ onSettings }) {
  const { settings } = useSettings();
  return (
    <div className="topbar">
      <h1>ZeusNet Control Core</h1>
      <div>
        <span className="mode">{settings.mode}</span>
        <button onClick={onSettings}>⚙️</button>
      </div>
    </div>
  );
}
