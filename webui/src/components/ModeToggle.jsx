import { useState } from "react";

export default function ModeToggle({ mode, setMode }) {
  return (
    <div className="toggle-container">
      <label>Mode:</label>
      <select value={mode} onChange={(e) => setMode(e.target.value)}>
        <option value="SAFE">SAFE</option>
        <option value="AGGRESSIVE">AGGRESSIVE</option>
      </select>
    </div>
  );
}
