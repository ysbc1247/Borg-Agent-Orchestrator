# Tuning 및 Tuned Retrain 현황

타임스탬프: `2026-03-31 11:20 KST`

## Tuning 결과

- 파일럿 튜닝 스윕 보고서:
  - `~/Documents/borg_xgboost_workspace/reports/202603311104_advanced_xgboost_tuning.json`
- 선정된 winner:
  - `regularized_balanced`
- winner parameter set:
  - `n_estimators=1600`
  - `max_depth=6`
  - `learning_rate=0.03`
  - `subsample=0.9`
  - `colsample_bytree=0.7`
  - `min_child_weight=8`
  - `reg_alpha=0.2`
  - `reg_lambda=2.0`
  - `early_stopping_rounds=80`

## 이 candidate가 winner가 된 이유

- 파일럿 `5m` 튜닝 스윕에서 `regularized_balanced`은 결합 선택 점수에서 조기 중지 기준선을 약간 능가했습니다.
- 파일럿 샘플에서 재현율을 효과적으로 변경하지 않고 유지하면서 고정 운영 예산에서 약간 더 높은 정밀도에서 주요 이득을 얻었습니다.
- 후보는 또한 원래 생산 설정보다 더 보수적이므로 과적합 위험을 줄이는 데 바람직합니다.

## 현재 활동 중인 작업

- 완전히 tuned retrain은 다음에서 실행됩니다.
  - 모델명 : `xgboost_failure_risk_tuned_v1`
  - 로그 : `~/Documents/borg_xgboost_workspace/runtime/logs/20260331111307_advanced_train_resumable.log`
- tuned retrain은 사과 대 사과 비교를 위한 기준과 동일한 전체 생산 샘플링 한도를 사용합니다.
  - 트레인캡 : `8,000,000`
  - 검증 한도: `2,000,000`

## 다음 결정

- tuned retrain이 완료되면 tuned 측정항목을 모든 horizon에 대한 현재 기준선과 비교합니다.
- 튜닝된 모델이 더 좋거나 더 안정적인 경우 튜닝된 아티팩트를 사용하여 영어/한국어 평가 보고서를 재생성하고 튜닝된 구성을 홍보합니다.
