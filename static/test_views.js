/* 헤더 시간 */
function updateTime() {
  const now = new Date();
  const options = { month: 'long', day: 'numeric' };
  const formattedDate = now.toLocaleDateString('en-US', options);
  document.getElementById('current-time').textContent = formattedDate;
}
updateTime();
setInterval(updateTime, 60000); // 1분마다 갱신


/* 디렉터리 파일 */
const renderFileTree = (el, data) => {
  if (!el) {
    console.error('Element with id "tree" not found.');
    return;
  }
  if (!data || !Array.isArray(data.contents)) {
    console.error('Data is not in the expected format:', data);
    return;
  }

  let treeHtml = '';

  data.contents.forEach(item => {
    treeHtml += getFileTreeHtml(item);
  });

  el.innerHTML = treeHtml;

  const folderLinks = el.querySelectorAll('li.dir > a'); // 폴더 링크 선택
  folderLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const parentEl = e.currentTarget.parentNode; // 폴더 가져오기
      parentEl.classList.toggle('open'); // 폴더 열기
    });
  });

  const fileLinks = el.querySelectorAll('li.file > a'); // 파일 링크 선택
  fileLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const filename = e.currentTarget.dataset.path; // 상대 경로 가져오기
      fetchFileContent(filename); // 파일 내용 가져오기
    });
  });
};

// 파일 내용 가져오는 함수
const fetchFileContent = (filename) => {
  fetch(`/file_content?filename=${encodeURIComponent(filename)}`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json(); // 파일 내용을 json로 변환
    })
    .then(data => {
      // 파일 내용을 특정 div에 표시
      const contentDiv = document.querySelector('.projects-section-body-res');
      if(data.content){
        contentDiv.innerHTML = `<pre>${data.content}</pre>`; // 포맷 유지 pre 사용
      }else {
        contentDiv.innerHTML = `
        <div class="error-content">
          <img src="${window.location.origin}/static/image/pageerror.png" class="error-img" alt="Error Image" />
          <pre>${data.error}</pre>
        </div>` // 오류 처리
      }
    })
    .catch(error => console.error('Error:', error));  
};


// 파일 이름을 입력 받아서 확장자 반환
const getFileExtension = (filename) => {
  if (!filename || filename.indexOf('.') === -1) return 'unknown'
  const path = filename.toLowerCase().split('.')
  return path[path.length - 1]
}

// 디렉터리 & 파일 데이터 li 요소로 변환
const getFileTreeHtml = (data, parentPath='') => {
  let html = `<li class="${data.type}"><a href="#" data-path="${parentPath}${data.name}"><i class="icon ${data.type}"></i> ${data.name}</a>`;

  if (data.type === 'dir' && data.contents) {
    html += '<ul class="folder-items">';
    data.contents.forEach(content => {
      html += getFileTreeHtml(content, `${parentPath}${data.name}/`); // 재귀 호출
    });
    html += '</ul>';
  }
  html += '</li>';

  return html;
};


// 페이지 로드 후 디렉터리 구조를 가져옴.
document.addEventListener('DOMContentLoaded', () => {
  // 동적으로 tree 요소 생성
  const treeElement = document.createElement('ul');
  treeElement.id = 'tree'; // ID 설정
  document.body.appendChild(treeElement); // body에 추가

  fetchDirectoryStructure();
});

// flask 에서 디렉터리 읽음
const fetchDirectoryStructure = () => {
  fetch('/directory_structure')
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      console.log('Fetched data:', data); // 데이터 구조를 확인합니다.
      renderFileTree(document.getElementById('tree'), data); // 전체 데이터로 렌더링
    })
    .catch(error => console.error('Error:', error));
};


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
    document.getElementById('profile-id').textContent = storedUsername;
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
}



