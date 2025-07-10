import React from "react";

export default function Sidebar({ active, setActive }) {
  const tabs = [
    "NetworkRecon",
    "EngageOps",
    "PacketForge",
    "TargetPlanner",
    "AIAssistant",
    "Backups",
  ];

  return (
    <div className="sidebar">
      {tabs.map((t) => (
        <button
          key={t}
          className={active === t ? "active" : ""}
          onClick={() => setActive(t)}
        >
          {t}
        </button>
      ))}
    </div>
  );
}
