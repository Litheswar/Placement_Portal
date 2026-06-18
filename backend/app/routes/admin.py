from flask import Blueprint, jsonify
from extensions import db

from app.models.company import Company
from app.decorators.roles import admin_required

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/api/admin"
)


@admin_bp.route("/pending-companies")
@admin_required
def get_pending_companies():

    companies = Company.query.filter_by(
        approval_status="pending"
    ).all()

    return jsonify([
        {
            "id": company.id,
            "name": company.name,
            "email": company.email,
            "industry": company.industry
        }
        for company in companies
    ])


@admin_bp.route(
    "/company/<int:company_id>/approve",
    methods=["PUT"]
)
@admin_required
def approve_company(company_id):

    company = Company.query.get_or_404(
        company_id
    )

    company.approval_status = "approved"

    db.session.commit()

    return jsonify({
        "message": "Company approved"
    })


@admin_bp.route(
    "/company/<int:company_id>/reject",
    methods=["PUT"]
)
@admin_required
def reject_company(company_id):

    company = Company.query.get_or_404(
        company_id
    )

    company.approval_status = "rejected"

    db.session.commit()

    return jsonify({
        "message": "Company rejected"
    })


@admin_bp.route("/companies")
@admin_required
def get_companies():

    companies = Company.query.all()

    return jsonify([
        {
            "id": company.id,
            "name": company.name,
            "email": company.email,
            "approval_status": company.approval_status,
            "is_active": company.is_active
        }
        for company in companies
    ])