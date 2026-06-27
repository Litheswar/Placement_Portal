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

export const getAdminCompanies = async (status = "") => {
  const url = status ? `${API_BASE}/auth/admin/companies?status=${status}` : `${API_BASE}/auth/admin/companies`;
  const response = await axios.get(url, getHeaders());
  return response.data;
};

export const updateCompanyStatus = async (companyId, status) => {
  const response = await axios.patch(`${API_BASE}/auth/admin/companies/${companyId}`, { approval_status: status }, getHeaders());
  return response.data;
};
