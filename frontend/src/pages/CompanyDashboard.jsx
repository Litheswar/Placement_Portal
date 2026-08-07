import { useState, useEffect } from "react";
import { getCompanyDrives, createDrive, closeDrive, getDriveApplicants, scheduleInterview, getDriveResults, updateApplicationResult, getCompanyDashboardStats } from "../services/driveService";
import { Pie, Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
} from "chart.js";

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title
);

function CompanyDashboard() {
  const [drives, setDrives] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Dashboard Stats
  const [stats, setStats] = useState(null);
  const [loadingStats, setLoadingStats] = useState(true);

  // Applicants State
  const [applicants, setApplicants] = useState([]);
  const [selectedDrive, setSelectedDrive] = useState(null);
  const [selectedApplicant, setSelectedApplicant] = useState(null);
  const [loadingApplicants, setLoadingApplicants] = useState(false);

  // Interview Form State
  const [interviewDate, setInterviewDate] = useState("");
  const [interviewMode, setInterviewMode] = useState("Online");
  const [locationOrLink, setLocationOrLink] = useState("");
  const [notes, setNotes] = useState("");
  const [schedulingInterview, setSchedulingInterview] = useState(false);

  // Results State
  const [results, setResults] = useState([]);
  const [loadingResults, setLoadingResults] = useState(false);

  // Form State
  const [jobTitle, setJobTitle] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [eligibilityCgpa, setEligibilityCgpa] = useState("");
  const [packageLpa, setPackageLpa] = useState("");
  const [applicationDeadline, setApplicationDeadline] = useState("");
  const [selectedBranches, setSelectedBranches] = useState([]);

  const [submitting, setSubmitting] = useState(false);

  const availableBranches = ["CSE", "ECE", "EEE", "MECH", "CIVIL", "IT", "CHEMICAL"];

  const fetchDrives = async () => {
    try {
      setLoading(true);
      const data = await getCompanyDrives();
      setDrives(data);
      setError("");
    } catch (err) {
      setError(err.response?.data?.message || "Failed to load placement drives");
    } finally {
      setLoading(false);
    }
  };

  const fetchDashboardStats = async () => {
    try {
      setLoadingStats(true);
      const data = await getCompanyDashboardStats();
      setStats(data);
    } catch (err) {
      console.error("Error fetching dashboard stats:", err);
      setError("Failed to load dashboard statistics");
    } finally {
      setLoadingStats(false);
    }
  };

  useEffect(() => {
    fetchDrives();
    fetchDashboardStats();
  }, []);

  const handleBranchChange = (branch) => {
    if (selectedBranches.includes(branch)) {
      setSelectedBranches(selectedBranches.filter((b) => b !== branch));
    } else {
      setSelectedBranches([...selectedBranches, branch]);
    }
  };

  const handleCreateDrive = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!jobTitle.trim() || !jobDescription.trim() || !eligibilityCgpa || !packageLpa || !applicationDeadline) {
      setError("Please fill in all fields.");
      return;
    }

    if (selectedBranches.length === 0) {
      setError("Please select at least one eligible branch.");
      return;
    }

    // Validate CGPA between 0 and 10
    const cgpaValue = parseFloat(eligibilityCgpa);
    if (isNaN(cgpaValue) || cgpaValue < 0 || cgpaValue > 10) {
      setError("Eligibility CGPA must be between 0 and 10.");
      return;
    }

    // Validate package > 0
    const packageValue = parseFloat(packageLpa);
    if (isNaN(packageValue) || packageValue <= 0) {
      setError("Package (LPA) must be greater than 0.");
      return;
    }

    // Validate deadline not in the past
    const deadlineDate = new Date(applicationDeadline);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if (deadlineDate < today) {
      setError("Application deadline cannot be in the past.");
      return;
    }

    try {
      setSubmitting(true);
      await createDrive({
        job_title: jobTitle,
        job_description: jobDescription,
        eligibility_cgpa: cgpaValue,
        package_lpa: packageValue,
        application_deadline: applicationDeadline,
        eligible_branches: selectedBranches
      });

      setSuccess("Placement drive created successfully! It is now pending admin approval.");

      // Reset form
      setJobTitle("");
      setJobDescription("");
      setEligibilityCgpa("");
      setPackageLpa("");
      setApplicationDeadline("");
      setSelectedBranches([]);

      // Refresh data first
      await fetchDrives();
      await fetchDashboardStats();

      // Then close modal after data is refreshed
      const modalElement = document.getElementById("createDriveModal");
      const modalInstance = window.bootstrap?.Modal.getInstance(modalElement);
      if (modalInstance) {
        modalInstance.hide();
      }

      // Clear success message after 5 seconds
      setTimeout(() => setSuccess(""), 5000);
    } catch (err) {
      setError(err.response?.data?.message || "Failed to create placement drive");
    } finally {
      setSubmitting(false);
    }
  };

const handleCloseDrive = async (driveId) => {
  setError("");
  setSuccess("");
  if (!window.confirm("Are you sure you want to close this placement drive? This action is manual and final.")) {
    return;
  }

  try {
    await closeDrive(driveId);
    setSuccess("Placement drive closed successfully.");
    fetchDrives();
    setTimeout(() => setSuccess(""), 5000);
  } catch (err) {
    setError(err.response?.data?.message || "Failed to close placement drive");
  }
};

const handleViewApplicants = async (driveId) => {
  setError("");
  setSelectedDrive(driveId);
  try {
    setLoadingApplicants(true);
    const data = await getDriveApplicants(driveId);
    setApplicants(data);
  } catch (err) {
    setError(err.response?.data?.message || "Failed to fetch applicants");
  } finally {
    setLoadingApplicants(false);
  }
};

const handleScheduleInterviewClick = (applicant) => {
  setSelectedApplicant(applicant);
  setInterviewDate("");
  setInterviewMode("Online");
  setLocationOrLink("");
  setNotes("");
};

const handleScheduleInterview = async (e) => {
  e.preventDefault();
  setError("");
  setSuccess("");

  if (!interviewDate || !locationOrLink) {
    setError("Please fill in all required fields.");
    return;
  }

  try {
    setSchedulingInterview(true);
    await scheduleInterview({
      application_id: selectedApplicant.application_id,
      interview_date: interviewDate,
      interview_mode: interviewMode,
      location_or_link: locationOrLink,
      notes: notes
    });

    setSuccess("Interview scheduled successfully!");

    // Close modal
    const modalElement = document.getElementById("scheduleInterviewModal");
    const modalInstance = window.bootstrap?.Modal.getInstance(modalElement);
    if (modalInstance) {
      modalInstance.hide();
    }

    // Refresh applicants
    handleViewApplicants(selectedDrive);

    // Refresh dashboard stats
    fetchDashboardStats();

    setTimeout(() => setSuccess(""), 5000);
  } catch (err) {
    setError(err.response?.data?.message || "Failed to schedule interview");
  } finally {
    setSchedulingInterview(false);
  }
};

const handleManageResults = async (driveId) => {
  setError("");
  setSelectedDrive(driveId);
  try {
    setLoadingResults(true);
    const data = await getDriveResults(driveId);
    setResults(data);
  } catch (err) {
    setError(err.response?.data?.message || "Failed to fetch results");
  } finally {
    setLoadingResults(false);
  }
};

const handleUpdateResult = async (applicationId, result) => {
  setError("");
  try {
    await updateApplicationResult(applicationId, result);
    setSuccess("Result updated successfully!");

    // Update local state without refresh
    setResults(results.map(r =>
      r.application_id === applicationId ? { ...r, result } : r
    ));

    // Refresh dashboard stats
    fetchDashboardStats();

    setTimeout(() => setSuccess(""), 5000);
  } catch (err) {
    setError(err.response?.data?.message || "Failed to update result");
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
        <h1 className="fw-bold text-primary">Company Dashboard</h1>
        <p className="text-muted">Manage your placement drives and recruit students</p>
      </div>
      <button className="btn btn-outline-danger" onClick={handleLogout}>
        Logout
      </button>
    </div>

    {error && <div className="alert alert-danger alert-dismissible fade show" role="alert">{error}</div>}
    {success && <div className="alert alert-success alert-dismissible fade show" role="alert">{success}</div>}

    {/* Dashboard Stats Cards */}
    {loadingStats ? (
      <div className="text-center py-4 mb-4">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading stats...</span>
        </div>
      </div>
    ) : stats && (
      <>
        <div className="row g-4 mb-4">
          <div className="col-md-6 col-lg-2">
            <div className="card border-0 shadow-sm h-100">
              <div className="card-body p-4">
                <div className="d-flex align-items-center">
                  <div className="flex-grow-1">
                    <h6 className="text-muted mb-1">Total Drives</h6>
                    <h3 className="fw-bold text-primary mb-0">{stats.total_drives}</h3>
                  </div>
                  <div className="ms-3">
                    <div className="bg-primary bg-opacity-10 rounded-circle p-3">
                      <i className="bi bi-briefcase-fill text-primary fs-4"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="col-md-6 col-lg-2">
            <div className="card border-0 shadow-sm h-100">
              <div className="card-body p-4">
                <div className="d-flex align-items-center">
                  <div className="flex-grow-1">
                    <h6 className="text-muted mb-1">Applications</h6>
                    <h3 className="fw-bold text-info mb-0">{stats.total_applications}</h3>
                  </div>
                  <div className="ms-3">
                    <div className="bg-info bg-opacity-10 rounded-circle p-3">
                      <i className="bi bi-file-earmark-text-fill text-info fs-4"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="col-md-6 col-lg-2">
            <div className="card border-0 shadow-sm h-100">
              <div className="card-body p-4">
                <div className="d-flex align-items-center">
                  <div className="flex-grow-1">
                    <h6 className="text-muted mb-1">Interviews</h6>
                    <h3 className="fw-bold text-secondary mb-0">{stats.interviews_scheduled}</h3>
                  </div>
                  <div className="ms-3">
                    <div className="bg-secondary bg-opacity-10 rounded-circle p-3">
                      <i className="bi bi-calendar-check-fill text-secondary fs-4"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="col-md-6 col-lg-2">
            <div className="card border-0 shadow-sm h-100">
              <div className="card-body p-4">
                <div className="d-flex align-items-center">
                  <div className="flex-grow-1">
                    <h6 className="text-muted mb-1">Selected</h6>
                    <h3 className="fw-bold text-success mb-0">{stats.selected_students}</h3>
                  </div>
                  <div className="ms-3">
                    <div className="bg-success bg-opacity-10 rounded-circle p-3">
                      <i className="bi bi-check-circle-fill text-success fs-4"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="col-md-6 col-lg-2">
            <div className="card border-0 shadow-sm h-100">
              <div className="card-body p-4">
                <div className="d-flex align-items-center">
                  <div className="flex-grow-1">
                    <h6 className="text-muted mb-1">Rejected</h6>
                    <h3 className="fw-bold text-danger mb-0">{stats.rejected_students}</h3>
                  </div>
                  <div className="ms-3">
                    <div className="bg-danger bg-opacity-10 rounded-circle p-3">
                      <i className="bi bi-x-circle-fill text-danger fs-4"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="col-md-6 col-lg-2">
            <div className="card border-0 shadow-sm h-100">
              <div className="card-body p-4">
                <div className="d-flex align-items-center">
                  <div className="flex-grow-1">
                    <h6 className="text-muted mb-1">Waiting</h6>
                    <h3 className="fw-bold text-warning mb-0">{stats.waiting_students}</h3>
                  </div>
                  <div className="ms-3">
                    <div className="bg-warning bg-opacity-10 rounded-circle p-3">
                      <i className="bi bi-clock-fill text-warning fs-4"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="row g-4 mb-4">
          <div className="col-md-6">
            <div className="card border-0 shadow-sm h-100">
              <div className="card-header bg-white py-3">
                <h5 className="card-title fw-bold mb-0">Drive Status</h5>
              </div>
              <div className="card-body p-4">
                <Pie
                  data={{
                    labels: ['Approved', 'Pending', 'Closed'],
                    datasets: [{
                      data: [stats.approved_drives, stats.pending_drives, stats.closed_drives],
                      backgroundColor: ['#28a745', '#ffc107', '#6c757d'],
                      borderWidth: 2,
                      borderColor: '#ffffff'
                    }]
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                      legend: {
                        position: 'bottom'
                      }
                    }
                  }}
                />
              </div>
            </div>
          </div>
          <div className="col-md-6">
            <div className="card border-0 shadow-sm h-100">
              <div className="card-header bg-white py-3">
                <h5 className="card-title fw-bold mb-0">Student Results</h5>
              </div>
              <div className="card-body p-4">
                <Bar
                  data={{
                    labels: ['Selected', 'Rejected', 'Waiting'],
                    datasets: [{
                      label: 'Students',
                      data: [stats.selected_students, stats.rejected_students, stats.waiting_students],
                      backgroundColor: ['#28a745', '#dc3545', '#ffc107'],
                      borderWidth: 1,
                      borderColor: ['#28a745', '#dc3545', '#ffc107']
                    }]
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                      legend: {
                        display: false
                      }
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                        ticks: {
                          stepSize: 1
                        }
                      }
                    }
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      </>
    )}

    <div className="row mb-4">
      <div className="col-12 text-end">
        <button
          className="btn btn-primary btn-lg shadow-sm"
          data-bs-toggle="modal"
          data-bs-target="#createDriveModal"
        >
          + Create New Drive
        </button>
      </div>
    </div>

    <div className="card shadow-sm border-0">
      <div className="card-header bg-white py-3 border-0">
        <h3 className="card-title fw-bold mb-0">Your Placement Drives</h3>
      </div>
      <div className="card-body p-0">
        {loading ? (
          <div className="text-center py-5">
            <div className="spinner-border text-primary" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
          </div>
        ) : drives.length === 0 ? (
          <div className="text-center py-5 text-muted">
            <h5>No placement drives created yet.</h5>
            <p>Click the "+ Create New Drive" button above to get started.</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="table table-hover align-middle mb-0">
              <thead className="table-light">
                <tr>
                  <th className="ps-4">Job Title</th>
                  <th>Package (LPA)</th>
                  <th>Required CGPA</th>
                  <th>Eligible Branches</th>
                  <th>Deadline</th>
                  <th>Status</th>
                  <th className="pe-4 text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                {drives.map((drive) => (
                  <tr key={drive.id}>
                    <td className="ps-4 fw-semibold text-dark">{drive.job_title}</td>
                    <td>{drive.package_lpa} LPA</td>
                    <td>{drive.eligibility_cgpa}</td>
                    <td>
                      {drive.eligible_branches.map((branch, idx) => (
                        <span key={idx} className="badge bg-secondary me-1">{branch}</span>
                      ))}
                    </td>
                    <td>{drive.application_deadline}</td>
                    <td>
                      {drive.status === "pending" && <span className="badge bg-warning text-dark px-3 py-2">Pending Approval</span>}
                      {drive.status === "approved" && <span className="badge bg-success px-3 py-2">Approved & Live</span>}
                      {drive.status === "rejected" && <span className="badge bg-danger px-3 py-2">Rejected</span>}
                      {drive.status === "closed" && <span className="badge bg-dark px-3 py-2">Closed</span>}
                    </td>
                    <td className="pe-4 text-end">
                      {drive.status === "approved" && (
                        <div className="d-flex gap-2 justify-content-end">
                          <button
                            className="btn btn-primary btn-sm"
                            onClick={() => handleViewApplicants(drive.id)}
                            data-bs-toggle="modal"
                            data-bs-target="#applicantsModal"
                          >
                            View Applicants
                          </button>
                          <button
                            className="btn btn-success btn-sm"
                            onClick={() => handleManageResults(drive.id)}
                            data-bs-toggle="modal"
                            data-bs-target="#resultsModal"
                          >
                            Manage Results
                          </button>
                          <button
                            className="btn btn-outline-danger btn-sm"
                            onClick={() => handleCloseDrive(drive.id)}
                          >
                            Close Drive
                          </button>
                        </div>
                      )}
                      {drive.status !== "approved" && (
                        <button className="btn btn-outline-secondary btn-sm" disabled>
                          No Actions
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>

    {/* Create Drive Modal */}
    <div
      className="modal fade"
      id="createDriveModal"
      tabIndex="-1"
      aria-labelledby="createDriveModalLabel"
      aria-hidden="true"
    >
      <div className="modal-dialog modal-lg modal-dialog-centered">
        <div className="modal-content border-0 shadow-lg">
          <div className="modal-header bg-primary text-white py-3">
            <h5 className="modal-title fw-bold" id="createDriveModalLabel">Create Placement Drive</h5>
            <button type="button" className="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <form onSubmit={handleCreateDrive}>
            <div className="modal-body p-4">
              <div className="row g-3">
                <div className="col-md-12">
                  <label className="form-label fw-semibold">Job Title</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="e.g. Software Development Engineer"
                    value={jobTitle}
                    onChange={(e) => setJobTitle(e.target.value)}
                    required
                  />
                </div>
                <div className="col-md-12">
                  <label className="form-label fw-semibold">Job Description</label>
                  <textarea
                    className="form-control"
                    rows="4"
                    placeholder="Detail the roles, responsibilities, skills, and expectations..."
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                    required
                  ></textarea>
                </div>
                <div className="col-md-6">
                  <label className="form-label fw-semibold">Package (LPA)</label>
                  <input
                    type="number"
                    step="0.01"
                    className="form-control"
                    placeholder="e.g. 12.5"
                    value={packageLpa}
                    onChange={(e) => setPackageLpa(e.target.value)}
                    required
                  />
                </div>
                <div className="col-md-6">
                  <label className="form-label fw-semibold">Eligibility CGPA (0.0 to 10.0)</label>
                  <input
                    type="number"
                    step="0.01"
                    className="form-control"
                    placeholder="e.g. 8.0"
                    value={eligibilityCgpa}
                    onChange={(e) => setEligibilityCgpa(e.target.value)}
                    required
                  />
                </div>
                <div className="col-md-6">
                  <label className="form-label fw-semibold">Application Deadline</label>
                  <input
                    type="date"
                    className="form-control"
                    value={applicationDeadline}
                    onChange={(e) => setApplicationDeadline(e.target.value)}
                    required
                  />
                </div>
                <div className="col-md-12">
                  <label className="form-label fw-semibold d-block">Eligible Branches</label>
                  <div className="card p-3 bg-light border-0">
                    <div className="row">
                      {availableBranches.map((branch) => (
                        <div className="col-md-4 col-6 mb-2" key={branch}>
                          <div className="form-check">
                            <input
                              className="form-check-input"
                              type="checkbox"
                              id={`branch-${branch}`}
                              checked={selectedBranches.includes(branch)}
                              onChange={() => handleBranchChange(branch)}
                            />
                            <label className="form-check-label fw-medium" htmlFor={`branch-${branch}`}>
                              {branch}
                            </label>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="modal-footer p-3 bg-light border-0">
              <button type="button" className="btn btn-outline-secondary px-4" data-bs-dismiss="modal">Cancel</button>
              <button
                type="submit"
                className="btn btn-primary px-4"
                disabled={submitting}

              >
                {submitting ? "Submitting..." : "Submit Drive"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    {/* Applicants Modal */}
    <div
      className="modal fade"
      id="applicantsModal"
      tabIndex="-1"
      aria-labelledby="applicantsModalLabel"
      aria-hidden="true"
    >
      <div className="modal-dialog modal-lg modal-dialog-centered">
        <div className="modal-content border-0 shadow-lg">
          <div className="modal-header bg-primary text-white py-3">
            <h5 className="modal-title fw-bold" id="applicantsModalLabel">Applicants for Drive</h5>
            <button type="button" className="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div className="modal-body p-4">
            {loadingApplicants ? (
              <div className="text-center py-5">
                <div className="spinner-border text-primary" role="status">
                  <span className="visually-hidden">Loading...</span>
                </div>
              </div>
            ) : applicants.length === 0 ? (
              <div className="text-center py-5 text-muted">
                <h5>No applicants yet.</h5>
              </div>
            ) : (
              <div className="table-responsive">
                <table className="table table-hover align-middle mb-0">
                  <thead className="table-light">
                    <tr>
                      <th>Student Name</th>
                      <th>Email</th>
                      <th>Roll Number</th>
                      <th>Branch</th>
                      <th>CGPA</th>
                      <th>Status</th>
                      <th className="text-end">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {applicants.map((applicant) => (
                      <tr key={applicant.application_id}>
                        <td className="fw-semibold">{applicant.student_name}</td>
                        <td>{applicant.email}</td>
                        <td>{applicant.roll_number}</td>
                        <td>{applicant.branch}</td>
                        <td>{applicant.cgpa}</td>
                        <td>
                          <span className="badge bg-secondary">{applicant.status}</span>
                        </td>
                        <td className="text-end">
                          <button
                            className="btn btn-success btn-sm"
                            onClick={() => handleScheduleInterviewClick(applicant)}
                            data-bs-toggle="modal"
                            data-bs-target="#scheduleInterviewModal"
                          >
                            Schedule Interview
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>

    {/* Schedule Interview Modal */}
    <div
      className="modal fade"
      id="scheduleInterviewModal"
      tabIndex="-1"
      aria-labelledby="scheduleInterviewModalLabel"
      aria-hidden="true"
    >
      <div className="modal-dialog modal-dialog-centered">
        <div className="modal-content border-0 shadow-lg">
          <div className="modal-header bg-success text-white py-3">
            <h5 className="modal-title fw-bold" id="scheduleInterviewModalLabel">Schedule Interview</h5>
            <button type="button" className="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <form onSubmit={handleScheduleInterview}>
            <div className="modal-body p-4">
              {selectedApplicant && (
                <div className="alert alert-info mb-3">
                  <strong>Student:</strong> {selectedApplicant.student_name}<br />
                  <strong>Email:</strong> {selectedApplicant.email}
                </div>
              )}
              <div className="mb-3">
                <label className="form-label fw-semibold">Interview Date & Time</label>
                <input
                  type="datetime-local"
                  className="form-control"
                  value={interviewDate}
                  onChange={(e) => setInterviewDate(e.target.value)}
                  required
                />
              </div>
              <div className="mb-3">
                <label className="form-label fw-semibold">Interview Mode</label>
                <select
                  className="form-select"
                  value={interviewMode}
                  onChange={(e) => setInterviewMode(e.target.value)}
                  required
                >
                  <option value="Online">Online</option>
                  <option value="Offline">Offline</option>
                </select>
              </div>
              <div className="mb-3">
                <label className="form-label fw-semibold">Location / Meeting Link</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="e.g. https://meet.google.com/abc or Room 101"
                  value={locationOrLink}
                  onChange={(e) => setLocationOrLink(e.target.value)}
                  required
                />
              </div>
              <div className="mb-3">
                <label className="form-label fw-semibold">Notes</label>
                <textarea
                  className="form-control"
                  rows="3"
                  placeholder="e.g. Technical Round, HR Round, etc."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                ></textarea>
              </div>
            </div>
            <div className="modal-footer p-3 bg-light border-0">
              <button type="button" className="btn btn-outline-secondary px-4" data-bs-dismiss="modal">Cancel</button>
              <button
                type="submit"
                className="btn btn-success px-4"
                disabled={schedulingInterview}
              >
                {schedulingInterview ? "Scheduling..." : "Save Interview"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    {/* Results Management Modal */}
    <div
      className="modal fade"
      id="resultsModal"
      tabIndex="-1"
      aria-labelledby="resultsModalLabel"
      aria-hidden="true"
    >
      <div className="modal-dialog modal-xl modal-dialog-centered">
        <div className="modal-content border-0 shadow-lg">
          <div className="modal-header bg-success text-white py-3">
            <h5 className="modal-title fw-bold" id="resultsModalLabel">Manage Interview Results</h5>
            <button type="button" className="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div className="modal-body p-4">
            {loadingResults ? (
              <div className="text-center py-5">
                <div className="spinner-border text-success" role="status">
                  <span className="visually-hidden">Loading...</span>
                </div>
              </div>
            ) : results.length === 0 ? (
              <div className="text-center py-5 text-muted">
                <h5>No interview results to manage yet.</h5>
                <p>Schedule interviews first to update results.</p>
              </div>
            ) : (
              <div className="table-responsive">
                <table className="table table-hover align-middle mb-0">
                  <thead className="table-light">
                    <tr>
                      <th>Student Name</th>
                      <th>Email</th>
                      <th>Branch</th>
                      <th>CGPA</th>
                      <th>Interview Date</th>
                      <th>Interview Mode</th>
                      <th>Current Result</th>
                      <th className="text-end">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((item) => (
                      <tr key={item.application_id}>
                        <td className="fw-semibold">{item.student_name}</td>
                        <td>{item.email}</td>
                        <td>{item.branch}</td>
                        <td>{item.cgpa}</td>
                        <td>
                          {item.interview ? item.interview.interview_date : "-"}
                        </td>
                        <td>
                          {item.interview ? item.interview.interview_mode : "-"}
                        </td>
                        <td>
                          {!item.result ? (
                            <span className="badge bg-secondary">Pending</span>
                          ) : item.result === "selected" ? (
                            <span className="badge bg-success">Selected</span>
                          ) : item.result === "rejected" ? (
                            <span className="badge bg-danger">Rejected</span>
                          ) : (
                            <span className="badge bg-warning text-dark">Waiting List</span>
                          )}
                        </td>
                        <td className="text-end">
                          {item.interview && (
                            <div className="btn-group" role="group">
                              <button
                                className={`btn btn-sm ${item.result === "selected" ? "btn-success" : "btn-outline-success"}`}
                                onClick={() => handleUpdateResult(item.application_id, "selected")}
                              >
                                Selected
                              </button>
                              <button
                                className={`btn btn-sm ${item.result === "rejected" ? "btn-danger" : "btn-outline-danger"}`}
                                onClick={() => handleUpdateResult(item.application_id, "rejected")}
                              >
                                Rejected
                              </button>
                              <button
                                className={`btn btn-sm ${item.result === "waiting" ? "btn-warning text-dark" : "btn-outline-warning text-dark"}`}
                                onClick={() => handleUpdateResult(item.application_id, "waiting")}
                              >
                                Waiting List
                              </button>
                            </div>
                          )}
                          {!item.interview && (
                            <span className="text-muted small">No interview scheduled</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  </div>
);
}

export default CompanyDashboard;