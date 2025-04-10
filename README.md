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
+ TypeScript
+ NEXT.js
+ React
+ TailwindCSS, shadcn/ui
+ Zustand
+ Axios, SWR
+ Draft.js / Quill
+ Naver Cloud Platform / Vercel
+ GitHub Actions
+ React Hook Form
+ Zod
+ JWT, OAuth2
+ VScode, Cursor

💚 Back End
+ FastAPI
+ PostgreSQL
+ swagger(자동 API 문서)
+ Docker
+ Pre-commit
+ CI/CD: black, isort
+ Nginx
+ Redis
+ Tortoise orm
+ GitHub Actions
+ JWT, OAuth2
+ Bycrpt
+ Pydantic
+ Asyncio, Uvicorn

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
# 📚 핵심 기능 요약 

# ✅ 회원 가입
- 일반 회원과 기업 회원을 구분하여 회원 가입을 진행합니다.
- 일반 회원: 구직 상태 여부 / 관심 분야 선택, 소셜(카카오, 네이버)을 이용한 회원 가입 및 로그인 가능
- 기업 회원: 사업자등록번호와 담당자의 전화번호와 이메일을 입력
- 유효성 검사 및 중복 검사 기능 제공

# 📝 공고 등록 및 관리
- 기업 회원 혹은 어드민만 작성이 가능
- 고용 형태 (공공/일반) 선택
- 구인 형태 (정규직/계약직/일용직/프리랜서) 선택

# 📋 이력서 등록
- 구직 상태에 따른 이력서 공개 여부 선택
- 희망 근무 지역 등록
- 추가 제출용 서류 필드 제공

# 👤 마이 페이지

---
# ⚙️ 사용 방법
