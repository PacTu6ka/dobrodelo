from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models import db, Organization, Project, User, Application

admin_bp = Blueprint('admin', __name__)

def check_admin():
    if current_user.role != 'admin':
        abort(403)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    check_admin()
    pending_orgs = Organization.query.filter_by(is_verified=False).all()
    verified_orgs = Organization.query.filter_by(is_verified=True).all()
    
    stats = {
        'total_users': User.query.count(),
        'volunteers': User.query.filter_by(role='volunteer').count(),
        'coordinators': User.query.filter_by(role='coordinator').count(),
        'total_projects': Project.query.count(),
        'total_applications': Application.query.count()
    }
    
    return render_template('admin/dashboard.html', 
                           pending_orgs=pending_orgs, 
                           verified_orgs=verified_orgs,
                           stats=stats)

@admin_bp.route('/verify-org/<int:org_id>', methods=['POST'])
@login_required
def verify_organization(org_id):
    check_admin()
    org = Organization.query.get_or_404(org_id)
    org.is_verified = True
    db.session.commit()
    flash(f'Организация «{org.name}» успешно верифицирована! Теперь ее проекты доступны в общем каталоге.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/block-org/<int:org_id>', methods=['POST'])
@login_required
def block_organization(org_id):
    check_admin()
    org = Organization.query.get_or_404(org_id)
    org.is_verified = False
    db.session.commit()
    flash(f'Организация «{org.name}» деактивирована.', 'warning')
    return redirect(url_for('admin.dashboard'))
