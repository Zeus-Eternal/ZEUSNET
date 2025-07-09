import React, { useState } from "react";

export default function SettingsDrawer({ open, onClose }) {
  const [iface, setIface] = useState("wlan0");
  const [mode, setMode] = useState("SAFE");
  const [retries, setRetries] = useState(3);

  if (!open) return null;

  return (
    <div className="drawer">
      <h3>Settings</h3>
      <label>Network Interface</label>
      <input value={iface} onChange={(e) => setIface(e.target.value)} />
      <label>Mode</label>
      <select value={mode} onChange={(e) => setMode(e.target.value)}>
        <option value="SAFE">SAFE</option>
        <option value="AGGRESSIVE">AGGRESSIVE</option>
      </select>
      <label>Retry Limit</label>
      <input
        type="number"
        value={retries}
        onChange={(e) => setRetries(e.target.value)}
      />
      <button onClick={onClose}>Close</button>
    </div>
  );
}
