import apiClient from "./apiClient";

export async function sendAttack({ mode, target, channel }) {
  const { data } = await apiClient.post("/nic/attack", {
    mode,
    target,
    channel,
  });
  return data;
}

export async function fetchSettings() {
  const { data } = await apiClient.get("/settings");
  return data;
}

export async function updateMode(mode) {
  const { data } = await apiClient.post("/settings", { mode });
  localStorage.setItem("ZEUSNET_MODE", data.mode);
  return data;
}
