#!/usr/bin/env python
"""Validate SQLAlchemy model relationships"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import Flask app
    from app import create_app
    
    # Create app to initialize SQLAlchemy
    app = create_app()
    
    # Try to import all models - this will trigger SQLAlchemy mapper configuration
    with app.app_context():
        from app.models import Student, Application, PlacementDrive, InterviewSchedule, Company, Admin
        
        print("✓ All models imported successfully")
        
        # Test that relationships are properly configured
        try:
            # This will fail if there are duplicate backrefs
            Student.query.all()
            print("✓ Student.query executed - no mapper errors")
        except Exception as e:
            print(f"✗ Student.query failed: {e}")
            sys.exit(1)
            
        try:
            Application.query.all()
            print("✓ Application.query executed - no mapper errors")
        except Exception as e:
            print(f"✗ Application.query failed: {e}")
            sys.exit(1)
            
        try:
            PlacementDrive.query.all()
            print("✓ PlacementDrive.query executed - no mapper errors")
        except Exception as e:
            print(f"✗ PlacementDrive.query failed: {e}")
            sys.exit(1)
            
        try:
            InterviewSchedule.query.all()
            print("✓ InterviewSchedule.query executed - no mapper errors")
        except Exception as e:
            print(f"✗ InterviewSchedule.query failed: {e}")
            sys.exit(1)
            
        try:
            Company.query.all()
            print("✓ Company.query executed - no mapper errors")
        except Exception as e:
            print(f"✗ Company.query failed: {e}")
            sys.exit(1)
            
        print("\n✓✓✓ ALL MODELS CONFIGURED CORRECTLY - NO DUPLICATE BACKREFS ✓✓✓")
        
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
