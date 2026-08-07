#!/usr/bin/env python
"""Test script to verify SQLAlchemy models configure correctly"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from app import create_app
from app.models import Student, Application, PlacementDrive, InterviewSchedule

app = create_app()

with app.app_context():
    # Try to query Student - this was failing before
    try:
        students = Student.query.all()
        print("✓ Student.query executed successfully")
        print(f"  Found {len(students)} students")
    except Exception as e:
        print(f"✗ Student.query failed: {e}")
        sys.exit(1)
    
    # Test other models
    try:
        applications = Application.query.all()
        print(f"✓ Application.query executed successfully ({len(applications)} records)")
    except Exception as e:
        print(f"✗ Application.query failed: {e}")
        sys.exit(1)
    
    try:
        drives = PlacementDrive.query.all()
        print(f"✓ PlacementDrive.query executed successfully ({len(drives)} records)")
    except Exception as e:
        print(f"✗ PlacementDrive.query failed: {e}")
        sys.exit(1)
    
    try:
        schedules = InterviewSchedule.query.all()
        print(f"✓ InterviewSchedule.query executed successfully ({len(schedules)} records)")
    except Exception as e:
        print(f"✗ InterviewSchedule.query failed: {e}")
        sys.exit(1)

print("\n✓ All SQLAlchemy models configured correctly - no mapper errors!")
