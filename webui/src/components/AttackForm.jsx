import { useState } from "react";
import { sendAttack } from "../utils/api";

export default function AttackForm({ log }) {
  const [mode, setMode] = useState("deauth");
  const [target, setTarget] = useState("");
  const [channel, setChannel] = useState(6);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    log(`Firing ${mode.toUpperCase()} on ${target} @ ch ${channel}`);

    try {
      const res = await sendAttack({ mode, target, channel });
      log(JSON.stringify(res, null, 2));
    } catch (err) {
      log(`❌ ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>Attack Type</label>
      <select value={mode} onChange={(e) => setMode(e.target.value)}>
        <option value="deauth">Deauth</option>
        <option value="pmkid">PMKID Capture</option>
        <option value="rogue_ap">Rogue AP</option>
      </select>

      {(mode === "deauth" || mode === "rogue_ap") && (
        <>
          <label>Target MAC</label>
          <input
            type="text"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            required={mode === "deauth"}
          />
        </>
      )}

      <label>Channel</label>
      <input
        type="number"
        value={channel}
        onChange={(e) => setChannel(e.target.value)}
      />

      <button disabled={loading}>{loading ? "Deploying..." : "Launch Attack"}</button>
    </form>
  );
}
