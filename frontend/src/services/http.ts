// src/services/http.ts
import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://rocketloud.ru:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

export default apiClient;
