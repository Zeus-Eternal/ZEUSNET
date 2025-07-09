import React from "react";
import AttackForm from "../AttackForm";

export default function EngageOps({ log }) {
  return (
    <div>
      <h2>Engage Ops</h2>
      <AttackForm log={log} />
    </div>
  );
}
