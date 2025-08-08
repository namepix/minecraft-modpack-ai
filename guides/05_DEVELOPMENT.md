# 🛠️ 개발자 가이드 (NeoForge 모드 + Flask 백엔드)

## 요구사항
- Java 17+, Gradle 8+
- Python 3.9+

## 모드 빌드
```bash
cd minecraft_mod
# gradle 래퍼가 있으면 우선 사용, 없으면 시스템 gradle 사용
[ -x ./gradlew ] && ./gradlew clean build || gradle clean build
```

## 백엔드 실행 (개발 모드)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## 통합 테스트
```bash
cd backend
python -m pytest -q
```

## 코드 위치
- NeoForge 모드: `minecraft_mod/src/main/java/com/modpackai/`
- Flask 백엔드: `backend/`
- 가이드 문서: `guides/`

## 릴리스 체크리스트
- 모드 빌드 산출물 확인: `minecraft_mod/build/libs/modpackai-*.jar`
- 백엔드 `/health` 응답 확인
- `guides/01_ADMIN_SETUP.md`의 자동/단계별 설치 흐름 검증
- README의 저장소 링크 최신화