# Implementation Plan - Student Application Flow & Eligibility Validation (M5)

This plan implements the student application process, student profile updates, and database-level eligibility validation (Milestone 5). Caching (M7) and Interview/Funnel/Stats flows (M6) are out of scope.

---

## User Review Required

> [!IMPORTANT]
> - **SQLite Queries Only**: No Redis caching will be used. All queries read from and write directly to SQLite.
> - **Application Constraints**: Applications will be validated on: CGPA, branch, student blacklist status, drive status/deadline, and duplicate submission checks.
> - **Profile Completeness**: Progress calculation based on 7 fields (name, email, roll_number, branch, cgpa, graduation_year, resume_url) is calculated and displayed on the UI, but does not block applications.

---

## Open Questions

None.

---

## Proposed Changes

### Backend Components

#### [MODIFY] [routes/drives.py](file:///c:/Users/keshav/Documents/Placement_Portal/backend/app/routes/drives.py)
* Add **`GET /api/student/profile`**:
  - Fetches the logged-in student's details.
  - Computes and returns the profile completeness percentage (based on name, email, roll_number, branch, cgpa, graduation_year, and resume_url being filled).
* Add **`PATCH /api/student/profile`**:
  - Accepts and updates student profile fields: `roll_number`, `branch`, `cgpa`, `graduation_year`, and `resume_url`.
* Update **`GET /api/student/drives`**:
  - Queries SQLite for approved drives.
  - Dynamically computes and attaches student-specific eligibility checks (`cgpa_check`, `branch_check`, `is_eligible`, `has_applied`) relative to the requesting student.
* Add **`POST /api/student/applications`**:
  - Validates constraints:
    - Student is not blacklisted (`is_blacklisted == False`).
    - Drive exists and its status is `"approved"`.
    - Drive deadline has not passed (`drive.application_deadline >= today`).
    - Student meets the CGPA requirement (`student.cgpa >= drive.eligibility_cgpa`).
    - Student's branch is in the drive's list of eligible branches.
    - No existing application exists for `(student_id, drive_id)`.
  - Creates a new application with status `"applied"`.
* Add **`GET /api/student/applications`**:
  - Fetches applications submitted by the logged-in student, including associated placement drive and company details.

---

### Frontend Components

#### [MODIFY] [driveService.js](file:///c:/Users/keshav/Documents/Placement_Portal/frontend/src/services/driveService.js)
* Implement service wrapper methods:
  - `getStudentProfile()`
  - `updateStudentProfile(data)`
  - `applyForDrive(driveId)`
  - `getStudentApplications()`

#### [MODIFY] [StudentDashboard.jsx](file:///c:/Users/keshav/Documents/Placement_Portal/frontend/src/pages/StudentDashboard.jsx)
* Add a tabbed layout inside the dashboard:
  - **Drives Tab**: Lists approved placement drives, showing eligibility and a clickable "Apply Now" button.
  - **My Applications Tab**: Tracks the status of submitted applications.
  - **Profile Tab**: Displays profile completeness progress bar (calculated out of the 7 profile fields) and form fields to edit and save details.

---

## Verification Plan

### Automated Tests
* Create `backend/tests/test_student_flow.py` asserting:
  - Profile PATCH validation and completeness percentage calculation.
  - Application eligibility enforcement (CGPA, branch, blacklist).
  - Deadline validation and duplicate submission rejection.
  - Success path of applying to a drive.

### Manual Verification
* Complete student profile, verify the completeness progress bar.
* Apply for a drive, check that status changes to "Applied", and verify it displays under the My Applications tab.
