import { useState, useEffect } from "react";
import { getAdminDrives, updateDriveStatus } from "../services/driveService";
import { getAdminCompanies, updateCompanyStatus } from "../services/companyService";

function AdminDashboard() {
  const [activeTab, setActiveTab] = useState("companies"); // companies or drives
  const [drives, setDrives] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [filterStatus, setFilterStatus] = useState("pending"); // pending, approved, rejected, or all

  const fetchDrives = async () => {
    try {
      setLoading(true);
      const data = await getAdminDrives(filterStatus === "all" ? "" : filterStatus);
      setDrives(data);
      setError("");
    } catch (err) {
      setError(err.response?.data?.message || "Failed to fetch placement drives");
    } finally {
      setLoading(false);
    }
  };

  const fetchCompanies = async () => {
    try {
      setLoading(true);
      const data = await getAdminCompanies(filterStatus === "all" ? "" : filterStatus);
      setCompanies(data);
      setError("");
    } catch (err) {
      console.error("Error fetching companies:", err);
      const errorMsg = err.response?.data?.message || err.message || "Failed to fetch companies";
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === "companies") {
      fetchCompanies();
    } else {
      fetchDrives();
    }
  }, [activeTab, filterStatus]);

  const handleUpdateStatus = async (driveId, status) => {
    setError("");
    setSuccess("");
    const actionText = status === "approved" ? "approve" : "reject";
    if (!window.confirm(`Are you sure you want to ${actionText} this placement drive?`)) {
      return;
    }

    try {
      await updateDriveStatus(driveId, status);
      setSuccess(`Placement drive has been successfully ${status}.`);
      fetchDrives();
      setTimeout(() => setSuccess(""), 5000);
    } catch (err) {
      setError(err.response?.data?.message || `Failed to ${actionText} placement drive`);
    }
  };

  const handleUpdateCompanyStatus = async (companyId, status) => {
    setError("");
    setSuccess("");
    const actionText = status === "approved" ? "approve" : "reject";
    if (!window.confirm(`Are you sure you want to ${actionText} this company?`)) {
      return;
    }

    try {
      await updateCompanyStatus(companyId, status);
      setSuccess(`Company has been successfully ${status}.`);
      fetchCompanies();
      setTimeout(() => setSuccess(""), 5000);
    } catch (err) {
      setError(err.response?.data?.message || `Failed to ${actionText} company`);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    window.location.href = "/login";
  };

  return (
    <div className="container py-5">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="fw-bold text-primary">Admin Dashboard</h1>
          <p className="text-muted">Review, approve, and manage company registrations and placement drives</p>
        </div>
        <button className="btn btn-outline-danger" onClick={handleLogout}>
          Logout
        </button>
      </div>

      {error && <div className="alert alert-danger alert-dismissible fade show" role="alert">{error}</div>}
      {success && <div className="alert alert-success alert-dismissible fade show" role="alert">{success}</div>}

      {/* Main Tab Switcher */}
      <div className="card border-0 bg-light p-2 mb-4">
        <div className="nav nav-pills nav-fill">
          <button 
            className={`nav-link fw-semibold py-2 ${activeTab === "companies" ? "active bg-primary text-white" : "text-dark"}`}
            onClick={() => { setActiveTab("companies"); setFilterStatus("pending"); }}
          >
            Company Approvals
          </button>
          <button 
            className={`nav-link fw-semibold py-2 ${activeTab === "drives" ? "active bg-primary text-white" : "text-dark"}`}
            onClick={() => { setActiveTab("drives"); setFilterStatus("pending"); }}
          >
            Placement Drives
          </button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="card border-0 bg-light p-2 mb-4">
        <div className="nav nav-pills nav-fill">
          <button 
            className={`nav-link fw-semibold py-2 ${filterStatus === "pending" ? "active bg-warning text-dark" : "text-dark"}`}
            onClick={() => setFilterStatus("pending")}
          >
            Pending Review
          </button>
          <button 
            className={`nav-link fw-semibold py-2 ${filterStatus === "approved" ? "active bg-success text-white" : "text-dark"}`}
            onClick={() => setFilterStatus("approved")}
          >
            Approved
          </button>
          <button 
            className={`nav-link fw-semibold py-2 ${filterStatus === "rejected" ? "active bg-danger text-white" : "text-dark"}`}
            onClick={() => setFilterStatus("rejected")}
          >
            Rejected
          </button>
          <button 
            className={`nav-link fw-semibold py-2 ${filterStatus === "all" ? "active bg-secondary text-white" : "text-dark"}`}
            onClick={() => setFilterStatus("all")}
          >
            All
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : activeTab === "companies" ? (
        companies.length === 0 ? (
          <div className="text-center py-5 bg-white rounded border border-light shadow-sm">
            <h5 className="text-muted">No companies found for status '{filterStatus}'</h5>
          </div>
        ) : (
          <div className="row g-4">
            {companies.map((company) => (
              <div className="col-12" key={company.id}>
                <div className="card shadow-sm border-0 h-100">
                  <div className="card-body p-4">
                    <div className="row g-4">
                      <div className="col-lg-8">
                        <div className="d-flex justify-content-between align-items-start mb-3">
                          <h4 className="fw-bold text-dark mb-0">{company.name}</h4>
                          {company.status === "pending" && <span className="badge bg-warning text-dark px-3 py-2">Pending Review</span>}
                          {company.status === "approved" && <span className="badge bg-success px-3 py-2">Approved</span>}
                          {company.status === "rejected" && <span className="badge bg-danger px-3 py-2">Rejected</span>}
                        </div>
                        
                        <div className="row g-3 mb-3">
                          <div className="col-md-6">
                            <span className="text-muted d-block small">EMAIL</span>
                            <span className="fw-bold text-dark">{company.email}</span>
                          </div>
                          <div className="col-md-6">
                            <span className="text-muted d-block small">HR CONTACT</span>
                            <span className="fw-bold text-dark">{company.hr_contact}</span>
                          </div>
                          {company.website && (
                            <div className="col-md-6">
                              <span className="text-muted d-block small">WEBSITE</span>
                              <a href={company.website} target="_blank" rel="noopener noreferrer" className="fw-bold text-primary text-decoration-none">
                                {company.website}
                              </a>
                            </div>
                          )}
                          {company.industry && (
                            <div className="col-md-6">
                              <span className="text-muted d-block small">INDUSTRY</span>
                              <span className="fw-bold text-dark">{company.industry}</span>
                            </div>
                          )}
                        </div>
                        
                        {company.description && (
                          <div className="mb-3">
                            <span className="text-muted d-block small mb-1">DESCRIPTION</span>
                            <p className="text-muted mb-0" style={{ whiteSpace: "pre-line" }}>{company.description}</p>
                          </div>
                        )}
                        
                        <div className="small text-muted">
                          <strong>Registered:</strong> {company.created_at}
                        </div>
                      </div>

                      <div className="col-lg-4 d-flex flex-column justify-content-between">
                        {company.status === "pending" && (
                          <div className="d-flex flex-column gap-2">
                            <button 
                              className="btn btn-success py-2 fw-semibold"
                              onClick={() => handleUpdateCompanyStatus(company.id, "approved")}
                            >
                              Approve Company
                            </button>
                            <button 
                              className="btn btn-outline-danger py-2 fw-semibold"
                              onClick={() => handleUpdateCompanyStatus(company.id, "rejected")}
                            >
                              Reject Company
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )
      ) : drives.length === 0 ? (
        <div className="text-center py-5 bg-white rounded border border-light shadow-sm">
          <h5 className="text-muted">No placement drives found for status '{filterStatus}'</h5>
        </div>
      ) : (
        <div className="row g-4">
          {drives.map((drive) => (
            <div className="col-12" key={drive.id}>
              <div className="card shadow-sm border-0 h-100">
                <div className="card-body p-4">
                  <div className="row g-4">
                    {/* Placement Drive Details */}
                    <div className="col-lg-7 border-end-lg">
                      <div className="d-flex justify-content-between align-items-start mb-2">
                        <h4 className="fw-bold text-dark mb-0">{drive.job_title}</h4>
                        {drive.status === "pending" && <span className="badge bg-warning text-dark px-3 py-2">Pending Review</span>}
                        {drive.status === "approved" && <span className="badge bg-success px-3 py-2">Approved</span>}
                        {drive.status === "rejected" && <span className="badge bg-danger px-3 py-2">Rejected</span>}
                        {drive.status === "closed" && <span className="badge bg-dark px-3 py-2">Closed</span>}
                      </div>
                      
                      <p className="text-muted mb-4" style={{ whiteSpace: "pre-line" }}>{drive.job_description}</p>
                      
                      <div className="row g-3">
                        <div className="col-md-6 col-12">
                          <span className="text-muted d-block small">PACKAGE (LPA)</span>
                          <span className="fw-bold fs-5 text-primary">{drive.package_lpa} LPA</span>
                        </div>
                        <div className="col-md-6 col-12">
                          <span className="text-muted d-block small">REQUIRED CGPA</span>
                          <span className="fw-bold fs-5 text-dark">{drive.eligibility_cgpa}</span>
                        </div>
                        <div className="col-md-6 col-12">
                          <span className="text-muted d-block small">APPLICATION DEADLINE</span>
                          <span className="fw-bold text-dark">{drive.application_deadline}</span>
                        </div>
                        <div className="col-md-6 col-12">
                          <span className="text-muted d-block small">ELIGIBLE BRANCHES</span>
                          <div>
                            {drive.eligible_branches.map((b, idx) => (
                              <span className="badge bg-light text-dark border me-1 mb-1" key={idx}>{b}</span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Company Profile Column */}
                    <div className="col-lg-5 ps-lg-4 d-flex flex-column justify-content-between">
                      <div>
                        <span className="text-muted d-block small mb-1">SUBMITTING COMPANY</span>
                        <h5 className="fw-bold text-dark mb-1">{drive.company.name}</h5>
                        {drive.company.website && (
                          <a href={drive.company.website} target="_blank" rel="noopener noreferrer" className="small text-decoration-none d-block mb-3">
                            {drive.company.website}
                          </a>
                        )}
                        <div className="mb-3 small">
                          <strong>Industry:</strong> {drive.company.industry || "Not Specified"}
                        </div>
                        <p className="text-muted small mb-0" style={{ display: "-webkit-box", WebkitLineClamp: "4", WebkitBoxOrient: "vertical", overflow: "hidden" }}>
                          {drive.company.description || "No company description provided."}
                        </p>
                      </div>

                      {/* Admin Actions */}
                      {drive.status === "pending" && (
                        <div className="d-flex gap-2 mt-4 pt-3 border-top">
                          <button 
                            className="btn btn-success flex-grow-1 py-2 fw-semibold"
                            onClick={() => handleUpdateStatus(drive.id, "approved")}
                          >
                            Approve Drive
                          </button>
                          <button 
                            className="btn btn-outline-danger flex-grow-1 py-2 fw-semibold"
                            onClick={() => handleUpdateStatus(drive.id, "rejected")}
                          >
                            Reject Drive
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default AdminDashboard;