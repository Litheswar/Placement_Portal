function ProfileTab({ profile, profileForm, actionLoading, onProfileChange, onSubmit }) {
  return (
    <div className="card shadow-sm border-0">
      <div className="card-header bg-white py-3 border-0">
        <h3 className="card-title fw-bold mb-0">Edit Profile Information</h3>
      </div>
      <div className="card-body p-4">
        <form onSubmit={onSubmit}>
          <div className="row g-3">
            <div className="col-md-6">
              <label htmlFor="profile-name" className="form-label fw-semibold">Name (from register)</label>
              <input 
                id="profile-name"
                type="text" 
                className="form-control bg-light" 
                value={profile?.name || ""} 
                disabled 
              />
            </div>
            <div className="col-md-6">
              <label htmlFor="profile-email" className="form-label fw-semibold">Email (from register)</label>
              <input 
                id="profile-email"
                type="email" 
                className="form-control bg-light" 
                value={profile?.email || ""} 
                disabled 
              />
            </div>
            <div className="col-md-6">
              <label htmlFor="profile-roll-number" className="form-label fw-semibold">Roll Number</label>
              <input 
                id="profile-roll-number"
                type="text" 
                name="roll_number" 
                className="form-control" 
                value={profileForm.roll_number} 
                onChange={onProfileChange}
                placeholder="e.g. CS2023001"
                required
              />
            </div>
            <div className="col-md-6">
              <label htmlFor="profile-branch" className="form-label fw-semibold">Branch</label>
              <input 
                id="profile-branch"
                type="text" 
                name="branch" 
                className="form-control" 
                value={profileForm.branch} 
                onChange={onProfileChange}
                placeholder="e.g. CSE"
                required
              />
            </div>
            <div className="col-md-6">
              <label htmlFor="profile-cgpa" className="form-label fw-semibold">CGPA (0.0 to 10.0)</label>
              <input 
                id="profile-cgpa"
                type="number" 
                step="0.01"
                min="0"
                max="10"
                name="cgpa" 
                className="form-control" 
                value={profileForm.cgpa} 
                onChange={onProfileChange}
                placeholder="e.g. 8.5"
                required
              />
            </div>
            <div className="col-md-6">
              <label htmlFor="profile-graduation-year" className="form-label fw-semibold">Graduation Year</label>
              <input 
                id="profile-graduation-year"
                type="number"
                min="2020"
                max="2035"
                name="graduation_year" 
                className="form-control" 
                value={profileForm.graduation_year} 
                onChange={onProfileChange}
                placeholder="e.g. 2024"
                required
              />
            </div>
            <div className="col-md-12">
              <label htmlFor="profile-resume-url" className="form-label fw-semibold">Resume URL</label>
              <input 
                id="profile-resume-url"
                type="url" 
                name="resume_url" 
                className="form-control" 
                value={profileForm.resume_url} 
                onChange={onProfileChange}
                placeholder="e.g. https://drive.google.com/your-resume-link"
              />
              <div className="form-text">Provide a link to your hosted resume (e.g. Google Drive, Dropbox).</div>
            </div>
          </div>
          <div className="mt-4 text-end">
            <button 
              type="submit" 
              className="btn btn-primary px-5 py-2 fw-semibold"
              disabled={actionLoading}
            >
              {actionLoading ? "Saving..." : "Save Profile"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ProfileTab;
