// src/services/api/solutions.ts
import axios from "axios";

const api = axios.create({
  baseURL: "http://rocketloud.ru:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

export default {
  async sendSolution(token, payload) {
    const res = await api.post("/solutions/", payload, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return res.data;
  },
};
