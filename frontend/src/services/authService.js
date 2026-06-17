import axios from "axios";

const API_URL = "http://127.0.0.1:5000/api/auth";

export const loginUser = async (
  role,
  email,
  password
) => {

  const response = await axios.post(
    `${API_URL}/${role}/login`,
    {
      email,
      password,
    }
  );

  return response.data;
};

export const registerStudent = async (studentData) => {

  const response = await axios.post(
    `${API_URL}/student/register`,
    studentData
  );

  return response.data;
};


export const registerCompany = async (companyData) => {

  const response = await axios.post(
    `${API_URL}/company/register`,
    companyData
  );

  return response.data;
};


