from flask import Blueprint, render_template, request
from app.models import Project, Shift, Organization

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Показываем только проекты подтвержденных организаций и со статусом open
    featured_projects = Project.query.join(Organization).filter(
        Organization.is_verified == True,
        Project.status == 'open'
    ).order_by(Project.created_at.desc()).limit(6).all()

    # Статистика для лендинга
    stats = {
        'projects_count': Project.query.count(),
        'orgs_count': Organization.query.filter_by(is_verified=True).count(),
        'shifts_count': Shift.query.count()
    }
    return render_template('index.html', projects=featured_projects, stats=stats)

@main_bp.route('/catalog')
def catalog():
    query = Project.query.join(Organization).filter(
        Organization.is_verified == True,
        Project.status == 'open'
    )

    category = request.args.get('category')
    city = request.args.get('city')
    search = request.args.get('q')

    if category:
        query = query.filter(Project.category == category)
    if city:
        query = query.filter(Project.city.ilike(f'%{city}%'))
    if search:
        query = query.filter(Project.title.ilike(f'%{search}%') | Project.description.ilike(f'%{search}%'))

    projects = query.order_by(Project.created_at.desc()).all()

    categories = ['Животные', 'Экология', 'Социальное', 'Дети', 'Культура', 'Спорт']
    return render_template('catalog.html', projects=projects, categories=categories,
                           selected_category=category, selected_city=city, search=search)

@main_bp.route('/project/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project_detail.html', project=project)
