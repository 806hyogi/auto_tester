from flask import Blueprint, render_template

p_ad_bp = Blueprint('pro_admin', __name__)

@p_ad_bp.route('/pro_admin')
def index():
    return render_template('pro_admin_page/pro_admin_views.html')
