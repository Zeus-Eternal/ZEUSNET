import { useState } from "react";
import ModeToggle from "./components/ModeToggle";
import AttackForm from "./components/AttackForm";
import TerminalLog from "./components/TerminalLog";

export default function App() {
  const [mode, setMode] = useState("SAFE");
  const [logLines, setLogLines] = useState([]);

  const log = (msg) =>
    setLogLines((lines) => [...lines, `[${new Date().toLocaleTimeString()}] ${msg}`]);

  return (
    <div className="dashboard">
      <h1>ZeusNet Control Center</h1>
      <ModeToggle mode={mode} setMode={setMode} />
      <AttackForm log={log} />
      <TerminalLog lines={logLines} />
    </div>
  );
}
