# 🕺🏻 시니어 내일

시니어 세대를 위한 일자리 플랫폼
구직자는 이력서를 작성하고 원하는 일자리에 지원할 수 있으며, 기업은 공고를 통해 맞춤형 인재를 모집할 수 있습니다.

---
# 🧑🏻‍💻 팀원 소개

| 역할   | 팀장   | 팀원이름             |               
|--------|------| ------------------ |
| FE     | 나기태 | 김유주, 박민희, 박수정 |
| BE     | 김이준 | 김병학, 박미정, 황순해 |

---
## ⚒️ 기술 스택

💛 Front End
![image](https://github.com/user-attachments/assets/c07c91f7-da7a-4b29-bfb1-92ecc253a6ce)


💚 Back End
![image](https://github.com/user-attachments/assets/486a4508-f7dd-4469-85f0-34777194c66c)


---
# 📁 프로젝트 규칙

Pull Request
+ 리뷰어는 LGTM를 제외한 코멘트를 작성. 작성자는 해당 코멘트를 보고 수정 및 보충을 진행합니다.
+ 1인 이상의 승인이 있어야 머지를 진행할 수 있습니다.

CI
+ PR 진행시 자동으로 테스트 진행 (github action)
+ 테스트 결과 알림: PR 진행 시 CI 테스트 결과가 실패한 경우 팀 채널(Discord)로 알림이 가도록 설정

CD
+ docker hub + github action

Swagger
+ /docs 경로에서 자동 문서 제공

Kanvan Board
+ 깃 허브 내의 칸반 보드를 이용하여 ToDo 리스트 명확화, 중요도 배치, 진행도 확인

---
# 🖼️Infra Architecture
![image](https://github.com/user-attachments/assets/61d82d53-b22e-4a1f-b37b-4a0ddeda8874)

---
# 📁폴더 구조
```
co-pj-senior/  
├── app/                # API, 도메인 로직, 설정 등이 포함된 폴더  
│   ├── api/           # API 엔드포인트 관련 코드  
│   ├── core/          # 핵심 설정 및 구성 관련 코드  
│   ├── domain/        # 도메인 모델, 비즈니스 로직 등  
│   ├── exceptions/    # 사용자 정의 예외 처리 모듈  
│   ├── tests/         # 애플리케이션 테스트 코드  
│   ├── utils/         # 공용 유틸리티 함수 및 모듈  
│   └── main.py        # 애플리케이션 진입점  
├── .envs/              # 환경 변수 파일들이 위치한 폴더  
│   ├── .dev.env       # 개발 환경용 환경 변수 파일  
│   └── .env.test      # 테스트 환경용 환경 변수 파일  
├── .github/            # GitHub Actions 관련 워크플로우 설정  
├── nginx/               
│   └── conf.d/dev.conf  # 개발 환경용 Nginx 설정 파일  
├── docker-compose.dev.yml  # 개발용 Docker Compose 파일  
├── Dockerfile.dev          # 개발 환경용 Dockerfile  
├── pyproject.toml      # Python 프로젝트 및 의존성 설정 파일  
└── README.md           # 프로젝트 설명 및 문서  
```

---
# 📚 핵심 기능 요약 

# ✅ 회원 가입
- 일반 회원과 기업 회원을 구분하여 회원 가입을 진행합니다.
- 일반 회원: 구직 상태 여부 / 관심 분야 선택, 소셜(카카오, 네이버)을 이용한 회원 가입 및 로그인 가능
- 기업 회원: 사업자등록번호와 담당자의 전화번호와 이메일을 입력
- 유효성 검사 및 중복 검사 기능 제공

# 📝 공고 조회 및 관리
- 기업 회원 혹은 어드민만 작성 및 수정 가능
- 고용 형태 (공공/일반) 선택
- 구인 형태 (정규직/계약직/일용직/프리랜서) 선택
- 모든 유저 공고 조회 가능

# 📋 이력서 등록
- 구직 상태에 따른 이력서 공개 여부 선택
- 희망 근무 지역 등록
- 추가 제출용 서류 필드 제공

# 👤 마이 페이지
개인회원
- 작성된 이력서 열람
- 지원한 공고 열람
- 북마크한 공고 열람

기업회원
- 공고 작성
- 작성된 공고별 지원자 열람

---
# ⚙️ 사용 방법

docker-compose -f docker-compose.dev.yml up --build
