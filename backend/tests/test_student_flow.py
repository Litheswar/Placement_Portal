import os
import sys
import unittest
import json
from datetime import datetime, date, timedelta

# Add the backend directory to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from extensions import db
from app.models.company import Company
from app.models.student import Student
from app.models.placement_drive import PlacementDrive
from app.models.application import Application
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

class StudentFlowTestCase(unittest.TestCase):
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
        # 1. Create Company
        self.company = Company(
            name="SuperTech Corp",
            email="hr@supertech.com",
            password_hash=generate_password_hash("password123"),
            hr_contact="9999999999",
            website="http://supertech.com",
            industry="IT",
            description="Leading software firm",
            approval_status="approved",
            is_active=True
        )
        db.session.add(self.company)
        
        # 2. Create Students
        self.student_cse = Student(
            name="John Doe",
            email="john@test.com",
            password_hash=generate_password_hash("password123"),
            roll_number="CSE001",
            branch="CSE",
            cgpa=9.0,
            graduation_year=2026,
            resume_url=None,
            is_active=True,
            is_blacklisted=False
        )
        self.student_blacklisted = Student(
            name="Blacklisted Student",
            email="blacklist@test.com",
            password_hash=generate_password_hash("password123"),
            roll_number="CSE002",
            branch="CSE",
            cgpa=8.5,
            graduation_year=2026,
            resume_url="http://resume.com/b",
            is_active=True,
            is_blacklisted=True
        )
        self.student_ece = Student(
            name="Jane Doe",
            email="jane@test.com",
            password_hash=generate_password_hash("password123"),
            roll_number="ECE001",
            branch="ECE",
            cgpa=6.5,
            graduation_year=2026,
            resume_url="http://resume.com/jane",
            is_active=True,
            is_blacklisted=False
        )
        db.session.add(self.student_cse)
        db.session.add(self.student_blacklisted)
        db.session.add(self.student_ece)
        
        # 3. Create Placement Drives
        self.drive_cse = PlacementDrive(
            company_id=1,
            job_title="Software Developer",
            job_description="Write awesome Python code",
            eligibility_cgpa=8.0,
            eligible_branches="CSE",
            application_deadline=date.today() + timedelta(days=1),
            package_lpa=12.0,
            status="approved"
        )
        self.drive_pending = PlacementDrive(
            company_id=1,
            job_title="Intern",
            job_description="Database updates",
            eligibility_cgpa=6.0,
            eligible_branches="CSE, ECE",
            application_deadline=date.today() + timedelta(days=5),
            package_lpa=5.0,
            status="pending"
        )
        self.drive_expired = PlacementDrive(
            company_id=1,
            job_title="QA Engineer",
            job_description="Test scripts",
            eligibility_cgpa=7.0,
            eligible_branches="CSE",
            application_deadline=date.today() - timedelta(days=1),
            package_lpa=8.0,
            status="approved"
        )
        db.session.add(self.drive_cse)
        db.session.add(self.drive_pending)
        db.session.add(self.drive_expired)
        
        db.session.commit()

        # Fix company_id reference
        self.drive_cse.company_id = self.company.id
        self.drive_pending.company_id = self.company.id
        self.drive_expired.company_id = self.company.id
        db.session.commit()

        # Store critical values/IDs to prevent DetachedInstanceErrors
        self.company_id = self.company.id
        self.student_cse_id = self.student_cse.id
        self.student_ece_id = self.student_ece.id
        self.student_blacklisted_id = self.student_blacklisted.id
        self.drive_cse_id = self.drive_cse.id
        self.drive_pending_id = self.drive_pending.id
        self.drive_expired_id = self.drive_expired.id

        # Generate tokens
        self.cse_token = create_access_token(identity=str(self.student_cse_id), additional_claims={"role": "student"})
        self.ece_token = create_access_token(identity=str(self.student_ece_id), additional_claims={"role": "student"})
        self.blacklist_token = create_access_token(identity=str(self.student_blacklisted_id), additional_claims={"role": "student"})

    def get_auth_headers(self, token):
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def test_get_student_profile(self):
        response = self.client.get("/api/student/profile", headers=self.get_auth_headers(self.cse_token))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["name"], "John Doe")
        self.assertEqual(data["email"], "john@test.com")
        self.assertEqual(data["roll_number"], "CSE001")
        self.assertEqual(data["branch"], "CSE")
        self.assertEqual(data["cgpa"], 9.0)
        self.assertEqual(data["graduation_year"], 2026)
        self.assertIsNone(data["resume_url"])
        self.assertEqual(data["completeness_percentage"], 86)

    def test_patch_student_profile(self):
        payload = {
            "roll_number": "CSE001_MOD",
            "resume_url": "https://googledrive.com/myresume"
        }
        response = self.client.patch(
            "/api/student/profile",
            headers=self.get_auth_headers(self.cse_token),
            data=json.dumps(payload)
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Profile updated successfully")
        self.assertEqual(data["student"]["roll_number"], "CSE001_MOD")
        self.assertEqual(data["student"]["resume_url"], "https://googledrive.com/myresume")
        self.assertEqual(data["student"]["completeness_percentage"], 100)

        # Unique constraint on roll_number
        payload_duplicate = {
            "roll_number": "ECE001"
        }
        response_dup = self.client.patch(
            "/api/student/profile",
            headers=self.get_auth_headers(self.cse_token),
            data=json.dumps(payload_duplicate)
        )
        self.assertEqual(response_dup.status_code, 400)
        data_dup = json.loads(response_dup.data)
        self.assertIn("already registered", data_dup["message"])

        # Invalid CGPA
        payload_invalid_cgpa = {
            "cgpa": 12.0
        }
        response_invalid = self.client.patch(
            "/api/student/profile",
            headers=self.get_auth_headers(self.cse_token),
            data=json.dumps(payload_invalid_cgpa)
        )
        self.assertEqual(response_invalid.status_code, 400)

    def test_student_list_drives_with_eligibility(self):
        response = self.client.get("/api/student/drives", headers=self.get_auth_headers(self.cse_token))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(len(data), 2)
        
        drive_map = {d["id"]: d for d in data}
        
        cse_drive_res = drive_map[self.drive_cse_id]
        self.assertTrue(cse_drive_res["cgpa_check"])
        self.assertTrue(cse_drive_res["branch_check"])
        self.assertTrue(cse_drive_res["is_eligible"])
        self.assertFalse(cse_drive_res["has_applied"])

        response_ece = self.client.get("/api/student/drives", headers=self.get_auth_headers(self.ece_token))
        self.assertEqual(response_ece.status_code, 200)
        data_ece = json.loads(response_ece.data)
        drive_map_ece = {d["id"]: d for d in data_ece}
        
        ece_drive_res = drive_map_ece[self.drive_cse_id]
        self.assertFalse(ece_drive_res["cgpa_check"])
        self.assertFalse(ece_drive_res["branch_check"])
        self.assertFalse(ece_drive_res["is_eligible"])

    def test_apply_for_drive_success_and_duplicate(self):
        payload = {"drive_id": self.drive_cse_id}
        response = self.client.post(
            "/api/student/applications",
            headers=self.get_auth_headers(self.cse_token),
            data=json.dumps(payload)
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Application submitted successfully")
        self.assertEqual(data["application"]["status"], "applied")

        response_list = self.client.get("/api/student/drives", headers=self.get_auth_headers(self.cse_token))
        data_list = json.loads(response_list.data)
        drive_map = {d["id"]: d for d in data_list}
        self.assertTrue(drive_map[self.drive_cse_id]["has_applied"])

        # Apply again
        response_dup = self.client.post(
            "/api/student/applications",
            headers=self.get_auth_headers(self.cse_token),
            data=json.dumps(payload)
        )
        self.assertEqual(response_dup.status_code, 400)
        data_dup = json.loads(response_dup.data)
        self.assertIn("already applied", data_dup["message"])

    def test_apply_for_drive_failures(self):
        # 1. Ineligible CGPA
        payload = {"drive_id": self.drive_cse_id}
        response = self.client.post(
            "/api/student/applications",
            headers=self.get_auth_headers(self.ece_token),
            data=json.dumps(payload)
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("CGPA criteria not met", json.loads(response.data)["message"])

        # 2. Blacklisted student applies
        response_bl = self.client.post(
            "/api/student/applications",
            headers=self.get_auth_headers(self.blacklist_token),
            data=json.dumps(payload)
        )
        self.assertEqual(response_bl.status_code, 403)
        self.assertIn("blacklisted", json.loads(response_bl.data)["message"])

        # 3. Expired deadline drive
        payload_exp = {"drive_id": self.drive_expired_id}
        response_exp = self.client.post(
            "/api/student/applications",
            headers=self.get_auth_headers(self.cse_token),
            data=json.dumps(payload_exp)
        )
        self.assertEqual(response_exp.status_code, 400)
        self.assertIn("deadline has passed", json.loads(response_exp.data)["message"])

        # 4. Pending drive
        payload_pend = {"drive_id": self.drive_pending_id}
        response_pend = self.client.post(
            "/api/student/applications",
            headers=self.get_auth_headers(self.cse_token),
            data=json.dumps(payload_pend)
        )
        self.assertEqual(response_pend.status_code, 400)
        self.assertIn("not approved", json.loads(response_pend.data)["message"])

    def test_get_student_applications(self):
        response_empty = self.client.get("/api/student/applications", headers=self.get_auth_headers(self.cse_token))
        self.assertEqual(response_empty.status_code, 200)
        self.assertEqual(len(json.loads(response_empty.data)), 0)

        payload = {"drive_id": self.drive_cse_id}
        self.client.post(
            "/api/student/applications",
            headers=self.get_auth_headers(self.cse_token),
            data=json.dumps(payload)
        )

        response = self.client.get("/api/student/applications", headers=self.get_auth_headers(self.cse_token))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["status"], "applied")
        self.assertEqual(data[0]["drive"]["job_title"], "Software Developer")
        self.assertEqual(data[0]["drive"]["company_name"], "SuperTech Corp")

if __name__ == "__main__":
    unittest.main()
