export async function sendAttack({ mode, target, channel }) {
  const res = await fetch("/api/nic/attack", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode, target, channel }),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Unknown error");
  }

  return await res.json();
}
