/* 헤더 시간 */
function updateTime() {
    const now = new Date();
    const options = { month: 'long', day: 'numeric' };
    const formattedDate = now.toLocaleDateString('en-US', options);
    document.getElementById('current-time').textContent = formattedDate;
}
updateTime();
setInterval(updateTime, 60000); // 1분마다 갱신

/* 로그인 폼 */
function LoginDialog() {
    document.getElementById('loginDialog').style.display = 'block';
}

function closeDialog() {
    document.getElementById('loginDialog').style.display = 'none';
    document.getElementById('logoutDialog').style.display = 'none';
}

// 로그인 여부 확인 
let isLoggedIn = false;

// 페이지 로드 시 로그인 상태 확인
window.onload = function () {
    const storedUsername = localStorage.getItem('username');
    if (storedUsername) {
        isLoggedIn = true;
        document.getElementById('profile-id').textContent = storedUsername; // 유저 이름 스토리지 저장
        fetchProjects(storedUsername); // 프로젝트 정보 스토리지 저장
    } else {
        isLoggedIn = false;
        document.getElementById('profile-id').textContent = '로그인을 해주세요.';
    }
};

function openDialog() {
    if (isLoggedIn) {
        // 사용자가 로그인 한 경우 (로그아웃 다이얼로그 열기)
        document.getElementById('logoutDialog').style.display = 'block';
    } else {
        document.getElementById('loginDialog').style.display = 'block';
    }
}

/* 로그인 액션 */
function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // AJAX 요청을 통해 서버에 로그인 정보 전송
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username: username, password: password })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('로그인 성공!');
                // 로그인한 아이디를 넣음.
                document.getElementById('profile-id').textContent = username;
                // 로그인 상태 업데이트
                isLoggedIn = true;
                // 입력 폼 초기화
                document.getElementById('username').value = '';
                document.getElementById('password').value = '';

                // 로그인 세션 유지
                localStorage.setItem('username', username);
                closeDialog();

                // 프로젝트 블럭
                projectBlock(data.projects);
            } else {
                alert('로그인 실패: ' + data.message);
                document.getElementById('username').value = '';
                document.getElementById('password').value = '';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('서버 오류가 발생했습니다.');
        });
}

/* 로그아웃 액션 */
function logout() {
    // 프로필 초기화
    document.getElementById('profile-id').textContent = '로그인을 해주세요.';
    //로그인 상태 초기화
    isLoggedIn = false;
    // Local Storage에서 사용자 정보 제거
    localStorage.removeItem('username');
    closeDialog();
    alert('로그아웃 되었습니다.');

    location.reload();
}

/* 프로젝트 블럭 */
function projectBlock(projects) {
    const projectBoxWrapper = document.querySelector('.project-box-wrapper'); // 프로젝트 박스 래퍼

    // 기존 프로젝트 박스 초기화
    projectBoxWrapper.innerHTML = '';

    projects.forEach(project => {
        const projectBox = document.createElement('div');
        projectBox.className = 'project-box';
        projectBox.style.backgroundColor = '#fee4cb';
        
        projectBox.innerHTML = `
            <div class="project-box-header">
                <span class="project-box-time">${formatDate(project.time)}</span>
                <div class="more-wrapper">
                    <button class="project-btn-more">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
                             viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                             stroke-linecap="round" stroke-linejoin="round"
                             class="feather feather-more-vertical">
                            <circle cx="12" cy="12" r="1" />
                            <circle cx="12" cy="5" r="1" />
                            <circle cx="12" cy="19" r="1" />
                        </svg>
                    </button>
                </div>
            </div>
            <div class="project-box-content-header">
                <p class="box-content-header">
                    <a href="/test" class="project-box-title" style="text-decoration: none; color: inherit;">${project.name}</a>
                </p>
                <p class="box-content-subheader">
                    <a class="box-content-des" style="text-decoration: none; color: inherit;">${project.description}</a>
                </p>
            </div>
            <div class="box-progress-wrapper">
                <p class="box-progress-header">진행 상태</p>
                <div class="box-progress-bar">
                    <span class="box-progress" style="width: 60%; background-color: #ff942e"></span>
                </div>
                <p class="box-progress-percentage">60%</p>
            </div>
        `;

        projectBoxWrapper.appendChild(projectBox);
        
    });
   
}

// 날짜 포맷팅 함수
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', options);
}

let hasRefreshed = false;
function fetchProjects(username) {
    fetch(`/get_projects?username=${username}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                projectBlock(data.projects);
            } else {
                console.error('프로젝트 정보를 가져오는 데 실패했습니다.');
            }
        })
        .catch(error => {
            console.error('Error fetching projects:', error);
        });
}

/* 프로젝트 생성 다이얼로그 열기 */
function projectopenDlg() {
    document.getElementById('popenDlg').style.display = 'block';
}
function closepopenDlg() {
    document.getElementById('popenDlg').style.display = 'none';
}


/* 프로젝트 다이얼로그에서 값 서버로 전송 */
function submitProject(){
    const projectName = document.getElementById('projectName').value;
    const projectDes = document.getElementById('projectDescription').value;

    fetch('/add_project', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: projectName,
            description: projectDes
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.success){
            alert('프로젝트가 성공적으로 생성되었습니다.');
            closepopenDlg();
            location.reload(); // 새로고침
        }else{
            alert('오류: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}