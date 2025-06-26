import { useState } from "react";
import { sendAttack } from "../utils/api";

export default function NetworkOpsPanel({ log }) {
  const [operation, setOperation] = useState("signal_reset");
  const [targetId, setTargetId] = useState("");
  const [channel, setChannel] = useState(6);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    log(
      `\ud83d\udce1 Initiating ${operation.replace("_", " ").toUpperCase()} on ${targetId} (Ch ${channel})`
    );

    try {
      const res = await sendAttack({
        mode: operation,
        target: targetId,
        channel,
      });
      log(`\u2705 Response: ${JSON.stringify(res, null, 2)}`);
    } catch (err) {
      log(`\u274c Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>Operation Type</label>
      <select value={operation} onChange={(e) => setOperation(e.target.value)}>
        <option value="signal_reset">Signal Reset</option>
        <option value="pmkid_probe">PMKID Probe</option>
        <option value="link_simulation">Link Simulation</option>
      </select>

      {(operation === "signal_reset" || operation === "link_simulation") && (
        <>
          <label>Target Identifier</label>
          <input
            type="text"
            value={targetId}
            onChange={(e) => setTargetId(e.target.value)}
            placeholder="e.g. AA:BB:CC:DD:EE:FF"
            required
          />
        </>
      )}

      <label>Channel</label>
      <input
        type="number"
        value={channel}
        onChange={(e) => setChannel(e.target.value)}
        min={1}
        max={165}
      />

      <button disabled={loading}>
        {loading ? "Running Diagnostic..." : "Initiate"}
      </button>
    </form>
  );
}
