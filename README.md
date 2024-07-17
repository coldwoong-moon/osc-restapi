## OSC RestAPI 사용 가이드
### 개발 환경
- Language : Python 3.11 FastAPI
    - 진입점 : [main.py](app/main.py)
- Environment
    - `OSC_BUILD_CONFIGURATION`: `dev` or `release`
    - `OSC_DEV_DB_USERNAME`: 데이터베이스 사용자 이름
    - `OSC_DEV_DB_PASSWORD`: 데이터베이스 사용자 비밀번호
    - `OSC_DEV_DB_HOST`: 데이터베이스 호스트 IP 또는 URL
    - `OSC_DEV_DB_NAME`: 데이터베이스 이름

### 각 디렉토리 및 파일의 역할:

- `app/`: 메인 애플리케이션 코드
- `app/main.py`: FastAPI 애플리케이션 및 라우터 설정
- `app/api/endpoints/`: API 엔드포인트 정의
- `app/core/`: 핵심 기능 (설정, 보안 등)
- `app/db/`: 데이터베이스 연결 및 세션 관리
- `app/models/`: 데이터베이스 모델 (ORM)
- `app/schemas/`: Pydantic 모델 (요청/응답 검증)
- `tests/`: 단위 테스트 및 통합 테스트

5. 프로젝트 관리 방식:

- 버전 관리: Git을 사용하여 코드 버전을 관리합니다.
- 의존성 관리: `requirements.txt`를 사용하거나 `poetry`를 도입하여 의존성을 관리합니다.
- 환경 변수: `.env` 파일을 사용하여 환경 변수를 관리하고, `python-dotenv`를 사용하여 로드합니다.
- 테스트: `pytest`를 사용하여 단위 테스트와 통합 테스트를 작성합니다.
- 문서화: FastAPI의 자동 문서 생성 기능을 활용하고, 필요한 경우 추가 문서를 작성합니다.
- 코드 스타일: `black`과 `flake8`을 사용하여 일관된 코드 스타일을 유지합니다.

이러한 구조와 관리 방식을 따르면 확장 가능하고 유지보수가 쉬운 RestAPI 서버를 개발할 수 있습니다. 필요에 따라 구조를 조정하고 추가 기능을 도입할 수 있습니다.

더 자세한 설명이나 특정 부분에 대해 더 알고 싶으신 점이 있다면 말씀해 주세요.