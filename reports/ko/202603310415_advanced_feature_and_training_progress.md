# Advanced Feature 및 Training 진행

타임스탬프: `2026-03-31 04:15 KST`

## feature build 상태

- `b`, `c`, `d`, `e`, `f` 및 `g` 클러스터에 대한 Advanced feature parquet 생성이 완료되었습니다.
- 기능 저장소 디렉터리:
  - `~/Documents/borg_xgboost_workspace/processed/feature_store`
- 최신 feature build 로그:
  - `~/Documents/borg_xgboost_workspace/runtime/logs/20260331040043_advanced_feature_build.log`

## 기능 라벨 Summary

- `b`
  - `5m`, `15m`, `30m`, `45m`, `60m`에 대한 0이 아닌 긍정
- `c`
  - `5m`, `15m`, `30m`, `45m`, `60m`에 대한 0이 아닌 긍정
- `d`
  - `5m`, `15m`, `30m`, `45m`, `60m`에 대한 0이 아닌 긍정
- `e`
  - `5m`, `15m`, `30m`, `45m`, `60m`에 대한 positive label 없음
- `f`
  - `5m`, `15m`, `30m`, `45m`, `60m`에 대한 positive label 없음
- `g`
  - `5m`, `15m`, `30m`, `45m`, `60m`에 대한 positive label 없음

## 훈련 경로 변경 사항

- 고급 트레이너에 결정론적 경계 네거티브 샘플링을 추가하여 전체 열차/검증 행이 노트북 친화적인 한도 내에 유지되는 동안 모든 포지티브가 유지됩니다.
- 기본 한도는 다음과 같습니다.
  - 열차: `8,000,000` 행
  - 유효성 검사: `2,000,000` 행
- 재개 가능한 래퍼가 추가되었습니다.
  - `scripts/run_advanced_feature_build_resumable.sh`
  - `scripts/run_advanced_train_resumable.sh`

## 훈련 진행

- 재개 가능한 최신 훈련 로그:
  - `~/Documents/borg_xgboost_workspace/runtime/logs/20260331041159_advanced_train_resumable.log`
- 완성된 목표:
  - `target_failure_5m`
- 현재 실행 중인 목표:
  - `target_failure_15m`

## 5분 horizon 지표

- 모델 디렉토리:
  - `~/Documents/borg_xgboost_workspace/models/xgboost/xgboost_failure_risk_target_failure_5m`
- 측정항목 Summary:
  - 소스 트레인 행: `307,815,199`
  - 소스 검증 행: `76,991,970`
  - 샘플링된 열차 행: `8,003,074`
  - 샘플링된 유효성 검사 행: `2,000,796`
  - 검증 긍정: `50,843`
  - 평균 정밀도: `0.9810528429`
  - 정밀도@0.1%: `0.9955022489`
  - 재현율@0.1%: `0.0391794347`
  - 정밀도@1%: `0.9940523790`
  - 회상@1%: `0.3911846272`