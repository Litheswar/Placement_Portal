import { useEffect, useState } from "react";
import axios from "axios";

function AdminDashboard() {

  const [companies, setCompanies] = useState([]);

  const token = localStorage.getItem("token");

  const fetchPendingCompanies = async () => {
    try {

      const response = await axios.get(
        "http://127.0.0.1:5000/api/admin/pending-companies",
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      setCompanies(response.data);

    } catch (error) {
      console.log(error);
    }
  };

  useEffect(() => {
    fetchPendingCompanies();
  }, []);

  const approveCompany = async (id) => {
    try {

      await axios.put(
        `http://127.0.0.1:5000/api/admin/company/${id}/approve`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      fetchPendingCompanies();

    } catch (error) {
      console.log(error);
    }
  };

  const rejectCompany = async (id) => {
    try {

      await axios.put(
        `http://127.0.0.1:5000/api/admin/company/${id}/reject`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      fetchPendingCompanies();

    } catch (error) {
      console.log(error);
    }
  };

  return (
    <div className="container mt-5">

      <h1>Admin Dashboard</h1>

      <div className="alert alert-primary mt-3">
        Welcome Admin
      </div>

      <h3 className="mt-4">
        Pending Companies
      </h3>

      <table className="table table-bordered mt-3">

        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Industry</th>
            <th>Actions</th>
          </tr>
        </thead>

        <tbody>

          {companies.length === 0 ? (
            <tr>
              <td colSpan="4" className="text-center">
                No Pending Companies
              </td>
            </tr>
          ) : (
            companies.map((company) => (
              <tr key={company.id}>
                <td>{company.name}</td>
                <td>{company.email}</td>
                <td>{company.industry}</td>

                <td>
                  <button
                    className="btn btn-success btn-sm me-2"
                    onClick={() =>
                      approveCompany(company.id)
                    }
                  >
                    Approve
                  </button>

                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() =>
                      rejectCompany(company.id)
                    }
                  >
                    Reject
                  </button>
                </td>

              </tr>
            ))
          )}

        </tbody>

      </table>

    </div>
  );
}

export default AdminDashboard;