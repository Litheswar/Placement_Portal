const getStatusBadgeClass = (status) => {
  switch (status) {
    case "selected":
      return "bg-success text-white";
    case "rejected":
      return "bg-danger text-white";
    case "shortlisted":
      return "bg-warning text-dark";
    default:
      return "bg-info text-white";
  }
};

const getResultBadgeClass = (result) => {
  switch (result) {
    case "selected":
      return "bg-success";
    case "rejected":
      return "bg-danger";
    case "waiting":
      return "bg-warning text-dark";
    default:
      return "bg-secondary";
  }
};

const formatDate = (dateString) => {
  if (!dateString) return "N/A";
  try {
    return new Date(dateString).toLocaleDateString();
  } catch {
    return dateString;
  }
};

const formatDateTime = (dateString) => {
  if (!dateString) return "Not Scheduled";
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      day: '2-digit', 
      month: 'short', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  } catch {
    return dateString;
  }
};

function ApplicationsTab({ applications }) {
  return (
    <div>
      {applications.length === 0 ? (
        <div className="text-center py-5 bg-white rounded border shadow-sm">
          <h5 className="text-muted">You haven't applied to any drives yet.</h5>
          <p className="text-muted small">Go to the 'Browse Drives' tab to get started.</p>
        </div>
      ) : (
        <div className="table-responsive bg-white rounded border shadow-sm">
          <table className="table table-hover align-middle mb-0">
            <thead className="table-light">
             <tr>
                  <th className="ps-4">Company</th>
                  <th>Job Title</th>
                  <th>Status</th>
                  <th>Interview Date</th>
                  <th>Mode</th>
                  <th>Location / Link</th>
                  <th>Interview Status</th>
                  <th>Result</th>
              </tr>
            </thead>
            <tbody>
  {applications.map((app) => (
    <tr key={app.id}>
      <td className="ps-4 fw-semibold">
        {app.drive.company_name}
      </td>

      <td>
        {app.drive.job_title}
      </td>

      <td>
        <span
          className={`badge px-3 py-2 text-capitalize ${getStatusBadgeClass(
            app.status
          )}`}
        >
          {app.status}
        </span>
      </td>

      <td>
        {app.interview ? formatDateTime(app.interview.interview_date) : "Not Scheduled"}
      </td>

      <td>
        {app.interview ? app.interview.interview_mode : "-"}
      </td>

      <td>
        {app.interview && app.interview.location_or_link ? (
          app.interview.location_or_link.length > 30 ? 
            <a href={app.interview.location_or_link} target="_blank" rel="noopener noreferrer" className="text-decoration-none">
              {app.interview.location_or_link.substring(0, 30)}...
            </a> :
            <a href={app.interview.location_or_link} target="_blank" rel="noopener noreferrer" className="text-decoration-none">
              {app.interview.location_or_link}
            </a>
        ) : "-"}
      </td>

      <td>
        {app.interview ? (
          <span className="badge bg-primary">
            Scheduled
          </span>
        ) : (
          <span className="badge bg-secondary">
            Not Scheduled
          </span>
        )}
      </td>

      <td>
        {!app.result ? (
          <span className={`badge ${getResultBadgeClass(null)}`}>
            Pending
          </span>
        ) : app.result === "selected" ? (
          <span className={`badge ${getResultBadgeClass("selected")}`}>
            Selected
          </span>
        ) : app.result === "rejected" ? (
          <span className={`badge ${getResultBadgeClass("rejected")}`}>
            Rejected
          </span>
        ) : (
          <span className={`badge ${getResultBadgeClass("waiting")}`}>
            Waiting List
          </span>
        )}
      </td>
    </tr>
  ))}
</tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default ApplicationsTab;
