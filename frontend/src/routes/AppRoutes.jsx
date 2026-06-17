import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";

import Login from "../pages/Login";
import StudentRegister from "../pages/StudentRegister";
import CompanyRegister from "../pages/CompanyRegister";

import ProtectedRoute from "../components/ProtectedRoute";

import AdminDashboard from "../pages/AdminDashboard";
import StudentDashboard from "../pages/StudentDashboard";
import CompanyDashboard from "../pages/CompanyDashboard";
function AppRoutes() {
  return (
    <BrowserRouter>

      <Routes>

        <Route
          path="/"
          element={<Login />}
        />

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/register/student"
          element={<StudentRegister />}
        />

        <Route
          path="/register/company"
          element={<CompanyRegister />}
        />
        <Route
  path="/admin/dashboard"
  element={
    <ProtectedRoute allowedRole="admin">
      <AdminDashboard />
    </ProtectedRoute>
  }
/>

<Route
  path="/student/dashboard"
  element={
    <ProtectedRoute allowedRole="student">
      <StudentDashboard />
    </ProtectedRoute>
  }
/>

<Route
  path="/company/dashboard"
  element={
    <ProtectedRoute allowedRole="company">
      <CompanyDashboard />
    </ProtectedRoute>
  }
/>
      </Routes>

    </BrowserRouter>
  );
}

export default AppRoutes;