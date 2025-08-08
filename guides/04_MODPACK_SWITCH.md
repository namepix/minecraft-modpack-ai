# 🔄 모드팩 전환 가이드 (개요)

현재 버전은 NeoForge 모드 중심이며, 서버 재시작을 포함한 전환 자동화는 차기 버전에서 제공합니다.

## 수동 전환 절차 (권장 수순)
1) 현재 서버 정상 종료
2) 대상 모드팩 디렉토리로 이동 (예: `~/enigmatica_10`)
3) 서버 시작 스크립트 또는 서버스타터로 구동
4) 로그에서 오류 여부 확인 (`logs/latest.log`)

## 관련 API (간소화)
- POST `/api/modpack/switch`
  - body: `{ "modpack_name": "Enigmatica 10", "modpack_version": "x.y.z", "modpack_path": "/home/user/enigmatica_10" }`
  - 설명: 현재는 분석 메타데이터를 반환하는 수준으로 동작 (스크립트 연동용)

## 차기 계획
- 서버 프로세스 안전 종료/기동 자동화
- 전환 이력 기록 및 롤백
- 전환 실패 자동 복구