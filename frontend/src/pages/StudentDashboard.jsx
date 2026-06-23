import { useState, useEffect, useRef } from "react";
import { 
  getStudentDrives, 
  getStudentProfile, 
  updateStudentProfile, 
  applyForDrive, 
  getStudentApplications 
} from "../services/driveService";
import DrivesTab from "../components/student/DrivesTab";
import ApplicationsTab from "../components/student/ApplicationsTab";
import ProfileTab from "../components/student/ProfileTab";

function StudentDashboard() {
  const [activeTab, setActiveTab] = useState("drives");
  const [drives, setDrives] = useState([]);
  const [applications, setApplications] = useState([]);
  const [profile, setProfile] = useState(null);
  
  // Form State
  const [profileForm, setProfileForm] = useState({
    roll_number: "",
    branch: "",
    cgpa: "",
    graduation_year: "",
    resume_url: ""
  });

  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  
  // Ref to track timeout for cleanup on unmount
  const successTimeoutRef = useRef(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError("");
      
      const profileData = await getStudentProfile();
      setProfile(profileData);
      setProfileForm({
        roll_number: profileData.roll_number || "",
        branch: profileData.branch || "",
        cgpa: profileData.cgpa !== null && profileData.cgpa !== undefined ? String(profileData.cgpa) : "",
        graduation_year: profileData.graduation_year !== null && profileData.graduation_year !== undefined ? String(profileData.graduation_year) : "",
        resume_url: profileData.resume_url || ""
      });

      const drivesData = await getStudentDrives();
      setDrives(drivesData);

      const appsData = await getStudentApplications();
      setApplications(appsData);
    } catch (err) {
      setError(err.response?.data?.message || "Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Cleanup timeout on unmount to prevent setSuccess calls after component unmounts
  useEffect(() => {
    return () => {
      if (successTimeoutRef.current) {
        clearTimeout(successTimeoutRef.current);
        successTimeoutRef.current = null;
      }
    };
  }, []);

  const handleProfileChange = (e) => {
    setProfileForm({
      ...profileForm,
      [e.target.name]: e.target.value
    });
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    
    // Prevent double-submit on rapid clicks
    if (actionLoading) {
      return;
    }

    setError("");
    setSuccess("");
    setActionLoading(true);

    try {
      // Validate CGPA and Graduation Year before parsing and submitting
      const parsedCgpa = profileForm.cgpa ? parseFloat(profileForm.cgpa) : 0.0;
      const parsedGradYear = profileForm.graduation_year ? parseInt(profileForm.graduation_year, 10) : 0;

      // Check for NaN values
      if (profileForm.cgpa && isNaN(parsedCgpa)) {
        setError("CGPA must be a valid number");
        setActionLoading(false);
        return;
      }
      if (profileForm.graduation_year && isNaN(parsedGradYear)) {
        setError("Graduation Year must be a valid number");
        setActionLoading(false);
        return;
      }

      const response = await updateStudentProfile({
        roll_number: profileForm.roll_number,
        branch: profileForm.branch,
        cgpa: parsedCgpa,
        graduation_year: parsedGradYear,
        resume_url: profileForm.resume_url
      });

      setProfile(response.student);
      setSuccess("Profile updated successfully!");
      
      // Refresh drives list in case eligibility flags changed
      const drivesData = await getStudentDrives();
      setDrives(drivesData);

      // Clear success message after 5 seconds (with ref tracking for cleanup)
      successTimeoutRef.current = setTimeout(() => setSuccess(""), 5000);
    } catch (err) {
      setError(err.response?.data?.message || "Failed to update profile");
    } finally {
      setActionLoading(false);
    }
  };

  const handleApply = async (driveId, jobTitle) => {
    // Prevent double-submit on rapid clicks
    if (actionLoading) {
      return;
    }

    setError("");
    setSuccess("");
    
    if (!window.confirm(`Are you sure you want to apply for "${jobTitle}"?`)) {
      return;
    }

    // Set actionLoading immediately after confirmation to prevent double-submit
    setActionLoading(true);

    try {
      await applyForDrive(driveId);
      setSuccess(`Applied to "${jobTitle}" successfully!`);
      
      // Refresh drives and applications list
      const drivesData = await getStudentDrives();
      setDrives(drivesData);
      
      const appsData = await getStudentApplications();
      setApplications(appsData);

      // Clear success message after 5 seconds (with ref tracking for cleanup)
      successTimeoutRef.current = setTimeout(() => setSuccess(""), 5000);
    } catch (err) {
      setError(err.response?.data?.message || `Failed to apply for ${jobTitle}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    window.location.href = "/login";
  };

  return (
    <div className="container py-5">
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="fw-bold text-primary">Student Portal</h1>
          <p className="text-muted">Browse drives, apply, and monitor your application status</p>
        </div>
        <button className="btn btn-outline-danger px-4" onClick={handleLogout}>
          Logout
        </button>
      </div>

      {/* Profile summary card with progress bar */}
      {profile && (
        <div className="card shadow-sm border-0 mb-4 bg-light">
          <div className="card-body p-4">
            <div className="row align-items-center">
              <div className="col-md-8">
                <h4 className="fw-bold text-dark mb-1">Welcome, {profile.name}</h4>
                <p className="text-muted mb-3 mb-md-0">{profile.email} • Branch: {profile.branch || "N/A"}</p>
              </div>
              <div className="col-md-4 text-md-end">
                <span className="small fw-semibold text-muted d-block mb-1">PROFILE COMPLETENESS</span>
                <div className="progress mb-1" style={{ height: "10px" }}>
                  <div 
                    className="progress-bar bg-success progress-bar-striped progress-bar-animated" 
                    role="progressbar" 
                    style={{ width: `${profile.completeness_percentage}%` }} 
                    aria-valuenow={profile.completeness_percentage} 
                    aria-valuemin="0" 
                    aria-valuemax="100"
                  ></div>
                </div>
                <span className="fw-bold text-success">{profile.completeness_percentage}% Complete</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {error && <div className="alert alert-danger alert-dismissible fade show shadow-sm" role="alert">{error}</div>}
      {success && <div className="alert alert-success alert-dismissible fade show shadow-sm" role="alert">{success}</div>}

      {/* Tabs Navigation */}
      <div className="card border-0 bg-light p-2 mb-4">
        <ul className="nav nav-pills nav-fill">
          <li className="nav-item">
            <button 
              className={`nav-link fw-semibold py-2 ${activeTab === "drives" ? "active bg-primary text-white" : "text-dark"}`}
              onClick={() => setActiveTab("drives")}
            >
              Browse Drives
            </button>
          </li>
          <li className="nav-item">
            <button 
              className={`nav-link fw-semibold py-2 ${activeTab === "applications" ? "active bg-primary text-white" : "text-dark"}`}
              onClick={() => setActiveTab("applications")}
            >
              My Applications ({applications.length})
            </button>
          </li>
          <li className="nav-item">
            <button 
              className={`nav-link fw-semibold py-2 ${activeTab === "profile" ? "active bg-primary text-white" : "text-dark"}`}
              onClick={() => setActiveTab("profile")}
            >
              Edit Profile
            </button>
          </li>
        </ul>
      </div>

      {loading ? (
        <div className="text-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : (
        <>
          {/* Tab 1: Drives */}
          {activeTab === "drives" && (
            <DrivesTab 
              drives={drives} 
              profile={profile} 
              actionLoading={actionLoading} 
              onApply={handleApply} 
            />
          )}

          {/* Tab 2: Applications */}
          {activeTab === "applications" && (
            <ApplicationsTab applications={applications} />
          )}

          {/* Tab 3: Profile */}
          {activeTab === "profile" && (
            <ProfileTab 
              profile={profile} 
              profileForm={profileForm} 
              actionLoading={actionLoading} 
              onProfileChange={handleProfileChange} 
              onSubmit={handleUpdateProfile} 
            />
          )}
        </>
      )}
    </div>
  );
}

export default StudentDashboard;