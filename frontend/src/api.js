import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000/api';

export const getProjects = async () => {
  const res = await axios.get(`${API_URL}/projects`);
  return res.data;
};

export const createProject = async (project) => {
  const res = await axios.post(`${API_URL}/projects`, project);
  return res.data;
};