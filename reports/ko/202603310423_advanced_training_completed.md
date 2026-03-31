# Advanced Training 완료

타임스탬프: `2026-03-31 04:23 KST`

## Result

- 구성된 모든 horizon에 대해 Advanced XGBoost 교육 단계가 완료되었습니다.
  - `5m`
  - `15m`
  - `30m`
  - `45m`
  - `60m`
- 최종 열차 기록:
  - `~/Documents/borg_xgboost_workspace/runtime/logs/20260331041159_advanced_train_resumable.log`

## 교육 구성

- 런타임 래퍼:
  - `scripts/run_advanced_train_resumable.sh`
- 스레드:
  - `BORG_XGB_N_JOBS=10`
- 결정론적 제한 샘플링:
  - 트레인 캡: `8,000,000` 행
  - 검증 한도: `2,000,000` 행
- 긍정적인 예는 각 분할 내에서 전체가 보존되었습니다.
- 네거티브는 해시된 행 ID를 통해 결정적으로 샘플링되었습니다.

## 측정항목 Summary

- `target_failure_5m`
  - 평균 정밀도: `0.9810528429`
  - 정밀도@1%: `0.9940523790`
  - 회상@1%: `0.3911846272`
- `target_failure_15m`
  - 평균 정밀도: `0.9726464046`
  - 정밀도@1%: `0.9951022040`
  - 회상@1%: `0.3226700374`
- `target_failure_30m`
  - 평균 정밀도: `0.9720370948`
  - 정밀도@1%: `0.9954522739`
  - 회상@1%: `0.2821028481`
- `target_failure_45m`
  - 평균 정밀도: `0.9659209812`
  - 정밀도@1%: `0.9960021988`
  - 회상@1%: `0.2523550266`
- `target_failure_60m`
  - 평균 정밀도: `0.9595348583`
  - 정밀도@1%: `0.9960519740`
  - 회상@1%: `0.2326268120`

## artifact

- 모델 루트:
  - `~/Documents/borg_xgboost_workspace/models/xgboost`
- 이제 각 horizon에는 다음이 포함됩니다.
  - `model.json`
  - `model_config.json`
  - `metrics.json`
  - `feature_importance.json`
  - `validation_predictions.parquet`

## 중요 참고 사항

- 전체 기능 저장소는 `b`부터 `g`까지 모든 클러스터에 걸쳐 있지만 현재 고정 샤드 슬라이스는 `e`, `f` 및 `g` 클러스터에 대해 긍정적인 레이블을 생성하지 않았습니다.
- 현재 긍정적인 훈련 신호는 `b`, `c` 및 `d` 클러스터에서 나옵니다.
- 다음으로 유용한 조사는 고급 원시 샤드 깊이를 늘리거나 다른 샤드 창을 선택하여 `e`, `f` 및 `g`에 대한 긍정적인 예를 복원하는지 여부입니다.