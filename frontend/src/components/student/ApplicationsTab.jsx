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

const formatDate = (dateString) => {
  if (!dateString) return "N/A";
  try {
    return new Date(dateString).toLocaleDateString();
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
        {app.interview_date
          ? formatDate(app.interview_date)
          : "Not Scheduled"}
      </td>

      <td>
        {app.interview_mode || "-"}
      </td>

      <td>
        {app.location_or_link || "-"}
      </td>

      <td>
        {app.result ? (
          app.result === "selected" ? (
            <span className="badge bg-success">
              Selected
            </span>
          ) : (
            <span className="badge bg-danger">
              Rejected
            </span>
          )
        ) : (
          <span className="badge bg-secondary">
            Pending
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
