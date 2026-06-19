import os
import sys
import unittest
import json
from datetime import datetime, date

# Add the backend directory to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from extensions import db
from app.models.admin import Admin
from app.models.company import Company
from app.models.student import Student
from app.models.placement_drive import PlacementDrive
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

class PlacementDrivesTestCase(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["JWT_SECRET_KEY"] = "test-jwt-secret-key"
        
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            self.seed_test_data()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def seed_test_data(self):
        # 1. Create Admin
        self.admin = Admin(
            name="Test Admin",
            email="admin@test.com",
            password_hash=generate_password_hash("admin123")
        )
        db.session.add(self.admin)
        
        # 2. Create Company A (Approved/Active)
        self.company_a = Company(
            name="Company A",
            email="comp_a@test.com",
            password_hash=generate_password_hash("comp123"),
            hr_contact="1234567890",
            website="http://comp-a.com",
            industry="Software",
            description="Company A Description",
            approval_status="approved",
            is_active=True
        )
        db.session.add(self.company_a)
        
        # 3. Create Company B (Approved/Active)
        self.company_b = Company(
            name="Company B",
            email="comp_b@test.com",
            password_hash=generate_password_hash("comp123"),
            hr_contact="0987654321",
            website="http://comp-b.com",
            industry="Hardware",
            description="Company B Description",
            approval_status="approved",
            is_active=True
        )
        db.session.add(self.company_b)

        # 4. Create Students (Eligible/Ineligible)
        self.student_cse = Student(
            name="CSE Student",
            email="student_cse@test.com",
            password_hash=generate_password_hash("stud123"),
            roll_number="CSE001",
            branch="CSE",
            cgpa=9.0,
            graduation_year=2026,
            is_active=True
        )
        self.student_ece = Student(
            name="ECE Student",
            email="student_ece@test.com",
            password_hash=generate_password_hash("stud123"),
            roll_number="ECE001",
            branch="ECE",
            cgpa=6.5,
            graduation_year=2026,
            is_active=True
        )
        db.session.add(self.student_cse)
        db.session.add(self.student_ece)
        
        db.session.commit()

        # Generate JWT Tokens
        self.admin_headers = {
            "Authorization": f"Bearer {create_access_token(identity=str(self.admin.id), additional_claims={'role': 'admin'})}"
        }
        self.comp_a_headers = {
            "Authorization": f"Bearer {create_access_token(identity=str(self.company_a.id), additional_claims={'role': 'company'})}"
        }
        self.comp_b_headers = {
            "Authorization": f"Bearer {create_access_token(identity=str(self.company_b.id), additional_claims={'role': 'company'})}"
        }
        self.student_cse_headers = {
            "Authorization": f"Bearer {create_access_token(identity=str(self.student_cse.id), additional_claims={'role': 'student'})}"
        }
        self.student_ece_headers = {
            "Authorization": f"Bearer {create_access_token(identity=str(self.student_ece.id), additional_claims={'role': 'student'})}"
        }

    # 1. Test Drive Creation & Date Verification
    def test_create_drive_success(self):
        drive_data = {
            "job_title": "Software Engineer Intern",
            "job_description": "Work on cutting-edge systems.",
            "eligibility_cgpa": 8.0,
            "eligible_branches": ["CSE", "IT"],
            "application_deadline": "2026-12-31",
            "package_lpa": 12.0
        }
        response = self.client.post(
            "/api/company/drives",
            data=json.dumps(drive_data),
            headers=self.comp_a_headers,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["drive"]["status"], "pending")
        
        # Verify in DB
        with self.app.app_context():
            drive = PlacementDrive.query.get(data["drive"]["id"])
            self.assertIsNotNone(drive)
            self.assertEqual(drive.job_title, "Software Engineer Intern")
            self.assertEqual(drive.eligible_branches, "CSE, IT")
            self.assertEqual(drive.application_deadline, date(2026, 12, 31))

    def test_create_drive_malformed_date(self):
        drive_data = {
            "job_title": "Software Engineer Intern",
            "job_description": "Work on cutting-edge systems.",
            "eligibility_cgpa": 8.0,
            "eligible_branches": ["CSE", "IT"],
            "application_deadline": "31-12-2026",  # Malformed date (should be YYYY-MM-DD)
            "package_lpa": 12.0
        }
        response = self.client.post(
            "/api/company/drives",
            data=json.dumps(drive_data),
            headers=self.comp_a_headers,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("application_deadline must be in YYYY-MM-DD format", data["message"])

    def test_create_drive_unauthorized_role(self):
        drive_data = {
            "job_title": "Software Engineer",
            "job_description": "Desc",
            "eligibility_cgpa": 7.0,
            "eligible_branches": ["CSE"],
            "application_deadline": "2026-12-31",
            "package_lpa": 8.5
        }
        # Attempt as student
        response = self.client.post(
            "/api/company/drives",
            data=json.dumps(drive_data),
            headers=self.student_cse_headers,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

    # 2. Test Admin List Pending Drives (Join validation)
    def test_admin_list_pending_drives(self):
        # Create a drive manually
        with self.app.app_context():
            d1 = PlacementDrive(
                company_id=self.company_a.id,
                job_title="Dev A",
                job_description="Desc",
                eligibility_cgpa=7.0,
                eligible_branches="CSE",
                application_deadline=date(2026, 12, 31),
                package_lpa=8.0,
                status="pending"
            )
            db.session.add(d1)
            db.session.commit()

        response = self.client.get(
            "/api/admin/drives?status=pending",
            headers=self.admin_headers
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["job_title"], "Dev A")
        self.assertEqual(data[0]["company"]["name"], "Company A")
        self.assertEqual(data[0]["company"]["website"], "http://comp-a.com")

    # 3. Test Admin Action & State Transition Guards
    def test_admin_approve_drive_success(self):
        with self.app.app_context():
            d1 = PlacementDrive(
                company_id=self.company_a.id,
                job_title="Dev A",
                job_description="Desc",
                eligibility_cgpa=7.0,
                eligible_branches="CSE",
                application_deadline=date(2026, 12, 31),
                package_lpa=8.0,
                status="pending"
            )
            db.session.add(d1)
            db.session.commit()
            drive_id = d1.id

        response = self.client.patch(
            f"/api/admin/drives/{drive_id}",
            data=json.dumps({"status": "approved"}),
            headers=self.admin_headers,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["drive"]["status"], "approved")

    def test_admin_state_transition_guard_already_approved(self):
        with self.app.app_context():
            d1 = PlacementDrive(
                company_id=self.company_a.id,
                job_title="Dev A",
                job_description="Desc",
                eligibility_cgpa=7.0,
                eligible_branches="CSE",
                application_deadline=date(2026, 12, 31),
                package_lpa=8.0,
                status="approved"  # Already Approved
            )
            db.session.add(d1)
            db.session.commit()
            drive_id = d1.id

        # Try to approve again or reject
        response = self.client.patch(
            f"/api/admin/drives/{drive_id}",
            data=json.dumps({"status": "rejected"}),
            headers=self.admin_headers,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Cannot modify status of a drive that is already 'approved'", data["message"])

    def test_company_approve_own_drive_mismatch(self):
        with self.app.app_context():
            d1 = PlacementDrive(
                company_id=self.company_a.id,
                job_title="Dev A",
                job_description="Desc",
                eligibility_cgpa=7.0,
                eligible_branches="CSE",
                application_deadline=date(2026, 12, 31),
                package_lpa=8.0,
                status="pending"
            )
            db.session.add(d1)
            db.session.commit()
            drive_id = d1.id

        # Company attempts to approve its own drive (Role check should fail)
        response = self.client.patch(
            f"/api/admin/drives/{drive_id}",
            data=json.dumps({"status": "approved"}),
            headers=self.comp_a_headers,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

    # 4. Test Student List and Eligibility (CGPA / Branch checks)
    def test_student_browse_and_eligibility(self):
        with self.app.app_context():
            # Drive requires CSE and CGPA >= 8.0
            d1 = PlacementDrive(
                company_id=self.company_a.id,
                job_title="SDE CSE",
                job_description="Desc",
                eligibility_cgpa=8.0,
                eligible_branches="CSE, IT",
                application_deadline=date(2026, 12, 31),
                package_lpa=15.0,
                status="approved"
            )
            db.session.add(d1)
            db.session.commit()

        # 4a. Verify CSE Student (CGPA = 9.0, Branch = CSE) is fully eligible
        response_cse = self.client.get(
            "/api/student/drives",
            headers=self.student_cse_headers
        )
        self.assertEqual(response_cse.status_code, 200)
        data_cse = json.loads(response_cse.data)
        self.assertEqual(len(data_cse), 1)
        self.assertTrue(data_cse[0]["cgpa_check"])
        self.assertTrue(data_cse[0]["branch_check"])
        self.assertTrue(data_cse[0]["is_eligible"])
        self.assertEqual(data_cse[0]["eligible_branches"], ["CSE", "IT"])

        # 4b. Verify ECE Student (CGPA = 6.5, Branch = ECE) is not eligible
        response_ece = self.client.get(
            "/api/student/drives",
            headers=self.student_ece_headers
        )
        self.assertEqual(response_ece.status_code, 200)
        data_ece = json.loads(response_ece.data)
        self.assertEqual(len(data_ece), 1)
        self.assertFalse(data_ece[0]["cgpa_check"])
        self.assertFalse(data_ece[0]["branch_check"])
        self.assertFalse(data_ece[0]["is_eligible"])

    # 5. Test Company Drive Close & Security / Guard checks
    def test_company_close_drive_success(self):
        with self.app.app_context():
            d1 = PlacementDrive(
                company_id=self.company_a.id,
                job_title="Dev Live",
                job_description="Desc",
                eligibility_cgpa=7.0,
                eligible_branches="CSE",
                application_deadline=date(2026, 12, 31),
                package_lpa=8.0,
                status="approved"  # Must be approved to be closed
            )
            db.session.add(d1)
            db.session.commit()
            drive_id = d1.id

        response = self.client.patch(
            f"/api/company/drives/{drive_id}/close",
            headers=self.comp_a_headers
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["drive"]["status"], "closed")

    def test_company_close_ownership_violation(self):
        with self.app.app_context():
            d1 = PlacementDrive(
                company_id=self.company_a.id,
                job_title="Dev Live A",
                job_description="Desc",
                eligibility_cgpa=7.0,
                eligible_branches="CSE",
                application_deadline=date(2026, 12, 31),
                package_lpa=8.0,
                status="approved"
            )
            db.session.add(d1)
            db.session.commit()
            drive_id = d1.id

        # Company B tries to close Company A's drive
        response = self.client.patch(
            f"/api/company/drives/{drive_id}/close",
            headers=self.comp_b_headers
        )
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertIn("Forbidden: You do not own this placement drive", data["message"])

    def test_company_close_drive_invalid_state_guard(self):
        with self.app.app_context():
            d1 = PlacementDrive(
                company_id=self.company_a.id,
                job_title="Dev Pending",
                job_description="Desc",
                eligibility_cgpa=7.0,
                eligible_branches="CSE",
                application_deadline=date(2026, 12, 31),
                package_lpa=8.0,
                status="pending"  # Pending drive cannot be closed
            )
            db.session.add(d1)
            db.session.commit()
            drive_id = d1.id

        response = self.client.patch(
            f"/api/company/drives/{drive_id}/close",
            headers=self.comp_a_headers
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Cannot close a drive that is currently 'pending'", data["message"])

if __name__ == "__main__":
    unittest.main()
