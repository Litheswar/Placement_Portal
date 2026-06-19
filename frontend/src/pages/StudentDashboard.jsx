import { useState, useEffect } from "react";
import { getStudentDrives } from "../services/driveService";

function StudentDashboard() {
  const [drives, setDrives] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchDrives = async () => {
    try {
      setLoading(true);
      const data = await getStudentDrives();
      setDrives(data);
      setError("");
    } catch (err) {
      setError(err.response?.data?.message || "Failed to load placement drives");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDrives();
  }, []);

  const handleApplyPlaceholder = (jobTitle) => {
    alert(`Application flow for "${jobTitle}" will be enabled in Milestone 5!`);
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
          <h1 className="fw-bold text-primary">Student Dashboard</h1>
          <p className="text-muted">Browse available placement drives and track your eligibility</p>
        </div>
        <button className="btn btn-outline-danger" onClick={handleLogout}>
          Logout
        </button>
      </div>

      {error && <div className="alert alert-danger alert-dismissible fade show" role="alert">{error}</div>}

      {loading ? (
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : drives.length === 0 ? (
        <div className="text-center py-5 bg-white rounded border border-light shadow-sm">
          <h5 className="text-muted">No live placement drives are currently available.</h5>
          <p className="text-muted small">Please check back later.</p>
        </div>
      ) : (
        <div className="row g-4">
          {drives.map((drive) => (
            <div className="col-md-6 col-12" key={drive.id}>
              <div className="card shadow-sm border-0 h-100 d-flex flex-column justify-content-between">
                <div className="card-body p-4">
                  {/* Title & Company */}
                  <div className="mb-3">
                    <span className="badge bg-primary mb-2">{drive.company.name}</span>
                    <h4 className="fw-bold text-dark mb-1">{drive.job_title}</h4>
                    <span className="text-muted small d-block">Published: {drive.created_at || "N/A"}</span>
                  </div>

                  {/* Description */}
                  <p className="text-muted small mb-4" style={{ display: "-webkit-box", WebkitLineClamp: "3", WebkitBoxOrient: "vertical", overflow: "hidden" }}>
                    {drive.job_description}
                  </p>

                  {/* Drive Metadata */}
                  <div className="row g-2 mb-4 bg-light p-3 rounded">
                    <div className="col-6">
                      <span className="text-muted d-block small">PACKAGE</span>
                      <span className="fw-bold text-dark">{drive.package_lpa} LPA</span>
                    </div>
                    <div className="col-6">
                      <span className="text-muted d-block small">DEADLINE</span>
                      <span className="fw-bold text-danger">{drive.application_deadline}</span>
                    </div>
                  </div>

                  {/* Eligibility Status Cards */}
                  <div className="mb-3">
                    <h6 className="fw-bold text-dark small mb-2">ELIGIBILITY STATUS</h6>
                    <div className="d-flex flex-wrap gap-2">
                      {/* Overall status */}
                      {drive.is_eligible ? (
                        <span className="badge bg-success-subtle text-success border border-success px-3 py-2 fw-semibold">
                          ✓ Eligible to Apply
                        </span>
                      ) : (
                        <span className="badge bg-danger-subtle text-danger border border-danger px-3 py-2 fw-semibold">
                          ✗ Ineligible
                        </span>
                      )}

                      {/* CGPA check */}
                      {drive.cgpa_check ? (
                        <span className="badge bg-light text-success border me-1">CGPA Criteria Passed (Required: {drive.eligibility_cgpa})</span>
                      ) : (
                        <span className="badge bg-light text-danger border me-1">CGPA too low (Required: {drive.eligibility_cgpa})</span>
                      )}

                      {/* Branch check */}
                      {drive.branch_check ? (
                        <span className="badge bg-light text-success border">Branch Eligible</span>
                      ) : (
                        <span className="badge bg-light text-danger border">Branch Ineligible</span>
                      )}
                    </div>
                  </div>

                  {/* Branches */}
                  <div className="mb-2">
                    <span className="text-muted small d-block mb-1">Eligible Branches:</span>
                    <div>
                      {drive.eligible_branches.map((b, idx) => (
                        <span className="badge bg-light text-dark border me-1 mb-1 small" key={idx}>{b}</span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Footer/Action */}
                <div className="card-footer bg-white border-0 p-4 pt-0">
                  <button 
                    className={`btn w-100 py-2 fw-bold ${drive.is_eligible ? "btn-primary" : "btn-secondary"}`}
                    disabled={!drive.is_eligible}
                    onClick={() => handleApplyPlaceholder(drive.job_title)}
                  >
                    {drive.is_eligible ? "Apply Now" : "Eligibility Required"}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default StudentDashboard;