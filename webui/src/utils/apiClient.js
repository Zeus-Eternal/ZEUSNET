import axios from "axios";

const apiClient = axios.create({
  baseURL: "/api",
});

apiClient.interceptors.request.use((config) => {
  const mode = localStorage.getItem("ZEUSNET_MODE") || "SAFE";
  config.headers["ZEUSNET-MODE"] = mode;
  return config;
});

apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    const message = err.response?.data?.detail || err.message;
    return Promise.reject(new Error(message));
  }
);

export default apiClient;
