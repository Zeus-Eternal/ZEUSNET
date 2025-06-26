import { useEffect, useRef } from "react";

export default function TerminalLog({ lines }) {
  const endRef = useRef();

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [lines]);

  return (
    <div className="terminal">
      {lines.map((line, i) => (
        <div key={i}>{line}</div>
      ))}
      <div ref={endRef} />
    </div>
  );
}
