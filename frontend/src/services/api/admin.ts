// src/services/api/admin.ts
import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://rocketloud.ru:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

export default {
  async getAdminTasks() {
    const token = localStorage.getItem("token");
    const res = await apiClient.get("/admin/tasks/list", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return res.data;
  },

  async approveSolution(teamId, taskId) {
    const token = localStorage.getItem("token");
    const res = await apiClient.post(
      "/admin/tasks/answers/approve",
      {
        team_id: teamId,
        task_id: taskId,
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      }
    );
    return res.data;
  },

  async rejectSolution(teamId, taskId) {
    const token = localStorage.getItem("token");
    const res = await apiClient.post(
      "/admin/tasks/answers/reject",
      {
        team_id: teamId,
        task_id: taskId,
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      }
    );
    return res.data;
  },

  async createTask(task) {
    const token = localStorage.getItem("token");
    const res = await apiClient.post("/admin/tasks/load", task, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return res.data;
  },

  async removeTask(taskId) {
    const token = localStorage.getItem("token");
    const res = await apiClient.delete(
      `/admin/tasks/remove?task_id=${taskId}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return res.data;
  },

  async getTeamSolutions(teamId) {
    const token = localStorage.getItem("token");
    const res = await apiClient.get(
      `/admin/tasks/team_solutions?team_id=${teamId}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return res.data;
  },

  async getTaskSolutions(taskId) {
    const token = localStorage.getItem("token");
    const res = await apiClient.get(
      `/admin/tasks/task_solutions?task_id=${taskId}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return res.data;
  },
};
