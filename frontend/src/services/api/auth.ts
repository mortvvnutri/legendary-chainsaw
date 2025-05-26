import axios from "axios";
import apiClient from "../http";

export default {
  async login(credentials) {
    const response = await apiClient.post("/auth/login", credentials);
    return {
      token: response.data.token,
    };
  },

  async adminLogin(credentials) {
    const res = await apiClient.post("/auth/login/admin", credentials);
    return res.data;
  },
};
