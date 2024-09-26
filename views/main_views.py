from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from flask import session
import json

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('main_views.html')

# 계정 정보
users = {
    "admin": "1234",
    "admin2": "1234"
}
# profile.cfg 경로 설정
PROFILE_PATH = './static/cfg/profile.cfg'

# 로그인 
@main_bp.route('/login', methods=["POST"])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    print("username: ", username)
    print("password: ", password)
    # 사용자 정보 확인
    if username in users and users[username] == password:
        # profile.cfg 읽기
        try:
            with open(PROFILE_PATH, 'r') as f:
                profile_data = json.load(f)
            user_projects = profile_data.get(username, {}).get('projects', []) # 프로젝트 정보 가져옴.
            
            session['username'] = username # 세션에 로그인 아이디 저장
            return jsonify(success=True, projects=user_projects)
        except Exception as e:
            return jsonify(success=False, message='프로필 파일을 읽는 중 오류가 발생했습니다.')
    else:
        return jsonify(success=False, message='사용자 이름 또는 비밀번호가 잘못되었습니다.')
    
# 프로젝트 정보 가져오는 엔드포인트
@main_bp.route('/get_projects', methods=["GET"])
def get_projects():
    username = request.args.get('username')
    
    try:
        with open(PROFILE_PATH, 'r') as f:
            profile_data = json.load(f)
        user_projects = profile_data.get(username, {}).get('projects', [])
        return jsonify(success=True, projects=user_projects)
    except Exception as e:
        return jsonify(success=False, message=f'프로필 파일을 읽는 중 오류가 발생했습니다. {str(e)}')

# 프로젝트 정보를 추가하는 엔드포인트
@main_bp.route('/add_project', methods=["POST"])
def add_project():
    username = session.get('username') # 세션에서 현재 로그인된 사용자 이름 가져오기
    data = request.get_json()
    project_name = data.get('name')
    project_des = data.get('description')

    # 현재 시간 가져오기
    current_time = datetime.now().strftime('%B %d, %Y')

    try:
        with open(PROFILE_PATH, 'r') as f:
            profile_data = json.load(f)

        # 사용자 프로젝트 추가
        if username not in profile_data:
            profile_data[username] = {'projects': []}

        profile_data[username]['projects'].append({
            'name': project_name,
            'description' : project_des,
            'time' : current_time
        })

        with open(PROFILE_PATH, 'w') as f:
            json.dump(profile_data, f, ensure_ascii=False, indent=4)

        return jsonify(success=True)
    
    except Exception as e:
        return jsonify(success=False, message=f'프로필 파일을 업데이트 하는 도중 오류가 발생했습니다. {str(e)}')
