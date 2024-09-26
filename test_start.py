from robot import run

# Robot Framework 스크립트를 실행하는 함수
def run_robot_tests():
    # 테스트 스크립트 파일 경로
    robot_file = 'sipp.robot'
    
    # 로봇 테스트 실행
    run(robot_file)

if __name__ == "__main__":
    run_robot_tests()