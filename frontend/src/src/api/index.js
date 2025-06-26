// src/api/index.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000', // point to your FastAPI backend
});

export default api;
