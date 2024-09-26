from flask import Flask

app = Flask(__name__)

# blue print
from views.main_views import main_bp
from views.pro_admin_views import p_ad_bp
from views.test_views import test_bp

app.register_blueprint(main_bp)
app.register_blueprint(p_ad_bp)
app.register_blueprint(test_bp)
app.secret_key = '1234'  # 비밀 키 설정

if __name__ == '__main__':
    app.run(debug=True)

    #December 10, 2020