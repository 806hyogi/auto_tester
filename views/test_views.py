from flask import Blueprint, render_template, jsonify, request, send_file
import os

test_bp = Blueprint('test', __name__)

@test_bp.route('/test')
def index():
    return render_template('test_page/test_views.html')

# 디렉터리의 구조를 읽음.
def get_directory_structure(dir_path):
    result = {
        "type": "dir",
        "name": os.path.basename(dir_path),
        "contents": []
    }

    # 디렉토리 내의 파일 및 하위 디렉토리 목록을 읽음
    for item in os.listdir(dir_path):
        full_path = os.path.join(dir_path, item)
        if os.path.isdir(full_path):
            result["contents"].append(get_directory_structure(full_path))
        else:
            result["contents"].append({"type": "file", "name": item})

    return result

@test_bp.route('/directory_structure', methods=['GET'])
def directory_structure():
    directory_path = './workspace'
    structure = get_directory_structure(directory_path)
    return jsonify(structure)

# 파일 내용을 반환
@test_bp.route('/file_content', methods=['GET'])
def file_content():
    filename = request.args.get('filename')
    directory_path = './workspace' # 파일 위치 디렉터리 경로
    full_path = os.path.join(directory_path, filename)

    if not os.path.isfile(full_path):
        return jsonify({"error": "File not found"}), 404
    
    try:
        with open(full_path, 'r') as file:
            content = file.read()
        return jsonify({"content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


