import paramiko
import re
import time
import json
import shutil
from pathlib import Path
from robot.api.deco import keyword

class remote:
    def __init__(self):
        self.ssh_client = None
        self.sftp_client = None
    
    @keyword
    def get_host_info(self):
        #ip, port, 업로드할 경로 가져오기
        with open('./set_global.cfg', 'r') as global_cfg:
            host_info = json.load(global_cfg)
        lsim = host_info['L-SIM']
        rsim = host_info['R-SIM']
        
        return lsim, rsim
    
    @keyword
    def open_connection(self, host, port, user, password):
        #ssh port 오픈
        if self.ssh_client:
            self.close_connection()
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.load_system_host_keys()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(host, port=port, username=user, password=password)
    
    @keyword
    def close_sftp_connection(self):
        if self.sftp_client:
            self.sftp_client.close()
            self.sftp_client = None
    
    @keyword
    def open_sftp_connection(self):
        #ssh 포트를 연 후, 추가로 sftp 포트가 필요할때 사용
        if not self.ssh_client:
            raise Exception("SSH connection is not open. Open SSH connection first.")
        if self.sftp_client:
            self.close_sftp_connection()
        self.sftp_client = self.ssh_client.open_sftp()
    
    @keyword
    def close_connection(self):
        if self.sftp_client:
            self.close_sftp_connection()
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None

    @keyword
    def exec_sipp(self, command):
        #sipp 실행
        if not self.ssh_client:
            raise RuntimeError("Connection not open.")
        #커맨드 실행 후 프로세스 번호 가져오기
        _, stdout, stderr = self.ssh_client.exec_command(command + '; echo $!')
        result = stdout.read().decode('utf-8')
        error = stderr.read().decode()

        #echo에서 번호만 추출
        pid_match = re.search(r'\d+', result)
        if pid_match:
            result = pid_match.group(0)
        else:
            result = None
        #번호와 에러내용이 있다면 에러내용도 반환
        return result, error

    @keyword
    def check_end(self, pid):
        #프로세스가 살아있는지 5초마다 한번 체크
        if not self.ssh_client:
            raise RuntimeError("Connection not open.")
        if pid == None:
            return
        while True:
            _, stdout, stderr = self.ssh_client.exec_command(f'ps -p {pid}')
            result = stdout.read().decode('utf-8')
            if pid not in result:
                break
            else:
                time.sleep(5)
        
        return
    
    @keyword
    def get_xml_files(self, dir):
        if not self.ssh_client:
            raise RuntimeError("Connection not open.")
        _, stdout, stderr = self.ssh_client.exec_command(f'cd {dir}; ls *.xml')
        files = stdout.read().decode().splitlines()
        
        return files
    
    @keyword
    def scenario_list(self,dir):
        #테스트할 시나리오 리스트의 목록을 가져옴
        scenario_lst=[]
        with open(dir, 'r', encoding='utf-8') as list:
            for scenario in list:
                scenario_lst.append(scenario.strip())
        
        return scenario_lst
    
    @keyword
    def scenario_file(self, dir, type):
        dir = Path(dir)
        # 서버 또는 클라이언트 타입에 따른 파일 패턴 설정
        file_pattern = '*_s.xml' if type == "server" else '*_c.xml'
        
        # 파일 검색
        files = list(dir.glob(file_pattern))
        
        # 파일이 하나도 없을 때 예외 처리
        if not files:
            raise FileNotFoundError(f"No matching {type} XML file found in directory: {dir}")
        
        # 첫 번째 파일의 전체 경로 및 파일 이름 반환
        full_path = str(files[0].as_posix())
        file_name = str(files[0].name)
        
        return full_path, file_name
        
    @keyword
    def upload_file(self, loacl_path, remote_path):
        #로컬 -> VM    파일 옮기기
        if not self.sftp_client:
            raise RuntimeError("Connection not open.")
        
        self.sftp_client.put(loacl_path, remote_path)

    @keyword
    def download_file(self, remote_path, local_path):
        #VM -> 로컬    파일 옮기기
        if not self.sftp_client:
            raise RuntimeError("Connection not open.")
        file_name = str(Path(remote_path).name)
        local_path = local_path+'/'+file_name
        self.sftp_client.get(remote_path, local_path)

    @keyword
    def input_cmd(self, cmd):
        #아무커맨드 입력하고 결과받아오기
        if not self.ssh_client:
            raise RuntimeError("Connection not open.")
        _, stdout, stderr = self.ssh_client.exec_command(cmd)
        files = stdout.read().decode().splitlines()
        error = stderr.read().decode()
        
        return files, error
    
    @keyword
    def make_dir(self, dir, time_now):
        #로그를 기록할 디렉토리 만들기
        dir = Path(dir)
        
        log_dir = dir / time_now
        log_dir.mkdir(exist_ok=True)
        
        s_log_dir = log_dir / "s"
        c_log_dir = log_dir / "c"
        s_log_dir.mkdir(exist_ok=True)
        c_log_dir.mkdir(exist_ok=True)
    
    @keyword
    def check_directory(self, dir):
        if not self.ssh_client:
            raise RuntimeError("Connection not open.")
        _, stdout, stderr = self.ssh_client.exec_command(f'ls {dir}log/')
        files = stdout.read().decode()
        error = stderr.read().decode()
        return files, error
    
    @keyword
    def get_remote_log_file(self, dir, type):
        #로그파일 다운로드 하기전에 로그파일 목록 가져옴
        log_files=[]
        if not self.ssh_client:
            raise RuntimeError("Connection not open.")
        _, stdout, stderr = self.ssh_client.exec_command(f'ls {dir}*{type}.log')
        files = stdout.read().decode().splitlines()
        
        for file in files:
            log_files.append(file)
        
        return log_files

    @keyword
    def get_local_log_file(self, dir, type):
        log_files=[]
        dir = Path(dir)
        files = list(dir.glob(f'*{type}.log'))
        for file in files:
            log_files.append(str(file))
        
        return log_files
    
    @keyword
    def make_received_log(self,dir):
        idx = 0
        capturing = False
        captured_lines = []
        dir_path = Path(dir)
        directory = str(dir_path.parent.as_posix())
        filename = str(dir_path.stem)
        log_file_name = directory + '/' + filename + '_recv_only.log'

        with open(dir, 'r') as remote_file:
            for line in remote_file:
                line = line.strip()
                if line.startswith('UDP message received'):
                    captured_lines.append(f'index[{idx}]')
                    idx += 1
                    capturing = True
                    continue
                
                elif line.startswith('-') and capturing:
                    capturing = False  
                    continue
                
                if capturing:
                    captured_lines.append(line)
        
        with open(log_file_name, 'w') as receive_only_file:
            for line in captured_lines:
                receive_only_file.write(line + '\n')
    
    
    @keyword
    def check_rules(self, dir, type):
        header_blocks = {}
        validation_headers = {}
        path = Path(dir)
        
        #서버/클라이언트의 rule파일이 있는 상위디렉토리 가져오기
        cfg_dir = path.parents[1]
        #서버/클라이언트에 따른 룰 파일과 recv_only 로그 가져오기
        if type=="server":
            with open(f"{cfg_dir}/s.cfg", 'r') as rules:
                rule_data = json.load(rules)
            log_dir = Path(dir + '/s')
            
        if type=="client":
            with open(f"{cfg_dir}/c.cfg", 'r') as rules:
                rule_data = json.load(rules)
            log_dir = Path(dir + '/c')

        files = list(log_dir.glob('*recv_only.log'))
        file_dir = str(files[0].as_posix())
        
        #recv_only로그 열어서 index단위로 나누기
        with open(file_dir, 'r') as recv_only_log:
            blocks = recv_only_log.read().split('index')
            for block in blocks:
                if block.strip():
                    # 비교를 위한 index번호 추출
                    index = block[1]
                    #index:block(header) 형태로 딕셔너리 만들기    
                    header_blocks[index] = block
        #헤더와 룰을 비교
        for rule_key, rule_values in rule_data.items():
            #룰의 index가 블럭에 있다면
            if rule_key in header_blocks:
                with open(file_dir[:-22]+'summary.log', 'a') as summary_file:
                    summary_file.write(f'index[{rule_key}]\n')
                #블럭을 라인으로 쪼개고, key:value형식의 딕셔너리로 만듦
                headers = header_blocks[rule_key].splitlines()
                for header in headers[1:]:
                    #:, =, ' '(공백)중 처음만나는 기준으로 헤더/밸류로 나눔
                    match = re.split(r'[:= ]', header, maxsplit=1)
                    if match:
                        if len(match) == 2:
                            key, value = match
                            validation_headers[key.strip()] = value.strip()
            # 룰의 속성(inc, only)에 따른 헤더와 룰의 비교
            for rule_header, rule_header_value in rule_values.items():
                if rule_header in validation_headers:
                    for key, value in rule_header_value.items():
                        if validation_header(validation_headers[rule_header], value, key):
                            result=(f'RULE      = {value}\nLOG_VALUE = {validation_headers[rule_header]} - PASS\n')
                        else:
                            result=(f'RULE      = {value}\nLOG_VALUE = {validation_headers[rule_header]} - FAIL\n')
                    with open(file_dir[:-22]+'summary.log', 'a') as summary_file:
                        summary_file.write(result)
            with open(file_dir[:-22]+'summary.log', 'a') as summary_file:
                summary_file.write('\n')
    
    @keyword
    def create_recent_log(self, dir):
        path = Path(dir)
        testcase_dir = path.parents[1]
        testcase_name = testcase_dir.name
        s_summary_dir = Path(dir+'/s')
        c_summary_dir = Path(dir+'/c')
        s_summary_name = str(testcase_dir.as_posix()) + '/' + testcase_name + '_s_lastest.log'
        c_summary_name = str(testcase_dir.as_posix()) + '/' + testcase_name + '_c_lastest.log'
        s_file = list(s_summary_dir.glob('*summary.log'))
        c_file = list(c_summary_dir.glob('*summary.log'))
        shutil.copy(s_file[0], s_summary_name)
        shutil.copy(c_file[0], c_summary_name)

#헤더 검사용 함수
def validation_header(header, rules, type):
    if type == 'inc':
        return all(rule in header for rule in rules) if isinstance(rules, list) else rules in header
    elif type == 'only':
        return True if rules == header else False
