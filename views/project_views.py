from flask import Blueprint, render_template

project_bp = Blueprint('project', __name__, template_folder="templates")

@project_bp.route('/')
def project_ready():
    return render_template('project_page/project_views.html', project_name= "기본")

@project_bp.route('/<project_name>')
def project_get(project_name):
    return render_template('project_page/project_views.html', project_name = project_name)
