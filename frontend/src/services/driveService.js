import axios from "axios";

const API_BASE = "http://127.0.0.1:5000/api";

const getHeaders = () => {
  const token = localStorage.getItem("token");
  return {
    headers: {
      Authorization: token ? `Bearer ${token}` : "",
      "Content-Type": "application/json"
    }
  };
};

export const createDrive = async (driveData) => {
  const response = await axios.post(`${API_BASE}/company/drives`, driveData, getHeaders());
  return response.data;
};

export const getCompanyDrives = async () => {
  const response = await axios.get(`${API_BASE}/company/drives`, getHeaders());
  return response.data;
};

export const getAdminDrives = async (status = "") => {
  const url = status ? `${API_BASE}/admin/drives?status=${status}` : `${API_BASE}/admin/drives`;
  const response = await axios.get(url, getHeaders());
  return response.data;
};

export const updateDriveStatus = async (driveId, status) => {
  const response = await axios.patch(`${API_BASE}/admin/drives/${driveId}`, { status }, getHeaders());
  return response.data;
};

export const getStudentDrives = async () => {
  const response = await axios.get(`${API_BASE}/student/drives`, getHeaders());
  return response.data;
};

export const closeDrive = async (driveId) => {
  const response = await axios.patch(`${API_BASE}/company/drives/${driveId}/close`, {}, getHeaders());
  return response.data;
};

export const getStudentProfile = async () => {
  const response = await axios.get(`${API_BASE}/student/profile`, getHeaders());
  return response.data;
};

export const updateStudentProfile = async (profileData) => {
  const response = await axios.patch(`${API_BASE}/student/profile`, profileData, getHeaders());
  return response.data;
};

export const applyForDrive = async (driveId) => {
  const response = await axios.post(`${API_BASE}/student/applications`, { drive_id: driveId }, getHeaders());
  return response.data;
};

export const getStudentApplications = async () => {
  const response = await axios.get(`${API_BASE}/student/applications`, getHeaders());
  return response.data;
};

export const getDriveApplicants = async (driveId) => {
  const response = await axios.get(`${API_BASE}/company/drives/${driveId}/applications`, getHeaders());
  return response.data;
};

export const scheduleInterview = async (data) => {
  const response = await axios.post(`${API_BASE}/company/interviews`, data, getHeaders());
  return response.data;
};

export const getDriveResults = async (driveId) => {
  const response = await axios.get(`${API_BASE}/company/drives/${driveId}/results`, getHeaders());
  return response.data;
};

export const updateApplicationResult = async (applicationId, result) => {
  const response = await axios.patch(`${API_BASE}/company/applications/${applicationId}/result`, { result }, getHeaders());
  return response.data;
};

export const getCompanyDashboardStats = async () => {
  const response = await axios.get(`${API_BASE}/company/dashboard`, getHeaders());
  return response.data;
};

export const getStudentDashboardStats = async () => {
  const response = await axios.get(`${API_BASE}/student/dashboard`, getHeaders());
  return response.data;
};

