function DrivesTab({ drives, profile, actionLoading, onApply }) {
  return (
    <div>
      {profile?.is_blacklisted && (
        <div className="alert alert-danger" role="alert">
          <strong>Warning:</strong> You are currently blacklisted and cannot apply to any placement drives.
        </div>
      )}
      {drives.length === 0 ? (
        <div className="text-center py-5 bg-white rounded border shadow-sm">
          <h5 className="text-muted">No placement drives are active at the moment.</h5>
          <p className="text-muted small">Please verify later.</p>
        </div>
      ) : (
        <div className="row g-4">
          {drives.map((drive) => {
            const branches = Array.isArray(drive.eligible_branches) ? drive.eligible_branches : [];
            return (
              <div className="col-md-6 col-12" key={drive.id}>
                <div className="card shadow-sm border-0 h-100 d-flex flex-column justify-content-between">
                  <div className="card-body p-4">
                    <div className="mb-3">
                      <span className="badge bg-primary mb-2">{drive.company.name}</span>
                      <h4 className="fw-bold text-dark mb-1">{drive.job_title}</h4>
                      <span className="text-muted small d-block">Published: {drive.created_at || "N/A"}</span>
                    </div>

                    <p className="text-muted small mb-4" style={{ display: "-webkit-box", WebkitLineClamp: "3", WebkitBoxOrient: "vertical", overflow: "hidden" }}>
                      {drive.job_description}
                    </p>

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

                    {/* Eligibility Section */}
                    <div className="mb-3">
                      <h6 className="fw-bold text-dark small mb-2">ELIGIBILITY STATUS</h6>
                      <div className="d-flex flex-wrap gap-2">
                        {drive.is_eligible ? (
                          <span className="badge bg-success-subtle text-success border border-success px-3 py-2 fw-semibold">
                            ✓ Eligible to Apply
                          </span>
                        ) : (
                          <span className="badge bg-danger-subtle text-danger border border-danger px-3 py-2 fw-semibold">
                            ✗ Ineligible
                          </span>
                        )}

                        {drive.cgpa_check ? (
                          <span className="badge bg-light text-success border me-1">CGPA Criteria Passed (Required: {drive.eligibility_cgpa})</span>
                        ) : (
                          <span className="badge bg-light text-danger border me-1">CGPA too low (Required: {drive.eligibility_cgpa})</span>
                        )}

                        {drive.branch_check ? (
                          <span className="badge bg-light text-success border">Branch Eligible</span>
                        ) : (
                          <span className="badge bg-light text-danger border">Branch Ineligible</span>
                        )}
                      </div>
                    </div>

                    <div className="mb-2">
                      <span className="text-muted small d-block mb-1">Eligible Branches:</span>
                      <div>
                        {branches.map((b, idx) => (
                          <span className="badge bg-light text-dark border me-1 mb-1 small" key={idx}>{b}</span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="card-footer bg-white border-0 p-4 pt-0">
                    {drive.has_applied ? (
                      <button className="btn btn-secondary w-100 py-2 fw-bold" disabled>
                        Applied
                      </button>
                    ) : (
                      <button 
                        className={`btn w-100 py-2 fw-bold ${drive.is_eligible && !profile?.is_blacklisted ? "btn-primary" : "btn-secondary"}`}
                        disabled={!drive.is_eligible || profile?.is_blacklisted || actionLoading}
                        onClick={() => onApply(drive.id, drive.job_title)}
                      >
                        {profile?.is_blacklisted 
                          ? "Disabled (Blacklisted)" 
                          : drive.is_eligible 
                            ? "Apply Now" 
                            : "Eligibility Required"}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default DrivesTab;
