import { useState } from "react";
import { useSettings } from "./utils/SettingsContext";
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";
import SettingsDrawer from "./components/SettingsDrawer";
import TerminalLog from "./components/TerminalLog";
import NetworkRecon from "./components/Tabs/NetworkRecon";
import EngageOps from "./components/Tabs/EngageOps";
import PacketForge from "./components/Tabs/PacketForge";
import TargetPlanner from "./components/Tabs/TargetPlanner";
import AIAssistant from "./components/Tabs/AIAssistant";
import Backups from "./components/Tabs/Backups";

export default function App() {
  const { settings } = useSettings();
  const [activeTab, setActiveTab] = useState("NetworkRecon");
  const [showSettings, setShowSettings] = useState(false);
  const [logLines, setLogLines] = useState([]);

  const log = (msg) =>
    setLogLines((lines) => [...lines, `[${new Date().toLocaleTimeString()}] ${msg}`]);

  const renderTab = () => {
    switch (activeTab) {
      case "NetworkRecon":
        return <NetworkRecon />;
      case "EngageOps":
        return <EngageOps log={log} />;
      case "PacketForge":
        return <PacketForge />;
      case "TargetPlanner":
        return <TargetPlanner />;
      case "AIAssistant":
        return <AIAssistant />;
      case "Backups":
        return <Backups />;
      default:
        return null;
    }
  };

  return (
    <div className="app">
      <Topbar onSettings={() => setShowSettings(true)} />
      <div className="main">
        <Sidebar active={activeTab} setActive={setActiveTab} />
        <div className="content">
          {renderTab()}
          <TerminalLog lines={logLines} />
        </div>
      </div>
      <SettingsDrawer
        open={showSettings}
        onClose={() => setShowSettings(false)}
      />
    </div>
  );
}
