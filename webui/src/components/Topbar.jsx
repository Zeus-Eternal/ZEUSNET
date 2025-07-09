import React from "react";

export default function Topbar({ onSettings }) {
  return (
    <div className="topbar">
      <h1>ZeusNet Control Core</h1>
      <button onClick={onSettings}>⚙️</button>
    </div>
  );
}
