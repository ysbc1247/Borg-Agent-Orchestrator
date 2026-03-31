# Repaired Label 재실행 현황

## Summary

- 이전 스크립트를 교체하는 대신 새로운 추가 detailed wrapper로 고급 이벤트 flat shard를 복구했습니다.
- `b`부터 `g`까지 cluster에서 join key가 정상적으로 채워진 Advanced event parquet을 다시 생성했습니다.
- 복구된 cluster `e`, `f`, `g`에 대해 Advanced join을 다시 실행했습니다.
- 복구된 cluster `e`, `f`, `g`에 대해 Advanced feature build를 다시 실행했습니다.
- `e`, `f`, `g`이 더 이상 positive label이 0이 아닌 것으로 확인되었습니다.
- repaired label 이전에 시작된 old tuning run과 분리하기 위해, 새 model name으로 tuned XGBoost training을 다시 시작했습니다.

## 자세한 로그

- 이벤트 복구 : `~/Documents/borg_xgboost_workspace/runtime/logs/20260331151302_advanced_event_repair_detailed.log`
- join 재실행 로그 : `~/Documents/borg_xgboost_workspace/runtime/logs/20260331152055_advanced_join_resumable_detailed.log`
- feature 재실행 로그 : `~/Documents/borg_xgboost_workspace/runtime/logs/20260331152830_advanced_feature_build_resumable_detailed.log`
- live training 재실행 로그: `~/Documents/borg_xgboost_workspace/runtime/logs/20260331153419_advanced_train_resumable_detailed.log`

## 복구된 Join 결과

- `e`: `58,784,525` 행, `22,553,673` 이벤트 레이블이 지정된 행
- `f`: `71,298,784` 행, `54,306,159` 이벤트 레이블이 지정된 행
- `g`: `61,083,781` 행, `20,708,106` 이벤트 레이블이 지정된 행

## 복구된 Feature Label 합계

- `b`: `5m=65,537`, `15m=78,359`, `30m=91,387`, `45m=96,116`, `60m=99,303`
- `c`: `5m=152,711`, `15m=182,451`, `30m=200,980`, `45m=212,647`, `60m=222,296`
- `d`: `5m=27,307`, `15m=35,422`, `30m=42,821`, `45m=48,111`, `60m=52,288`
- `e`: `5m=129,553`, `15m=175,699`, `30m=200,677`, `45m=220,331`, `60m=233,409`
- `f`: `5m=48,677`, `15m=93,644`, `30m=148,814`, `45m=194,633`, `60m=240,144`
- `g`: `5m=39,509`, `15m=60,618`, `30m=81,189`, `45m=97,625`, `60m=111,570`

## 훈련 재실행

- 더 이상 사용하지 않는 tuning run: `xgboost_failure_risk_tuned_v1`
  - 이 run은 `e/f/g` repair 이전에 시작됐기 때문에 최종 tuned 후보로 보면 안 됩니다.
- 현재 tuned run: `xgboost_failure_risk_tuned_v2_repaired_labels`
- 재시작 시점의 현재 target: `target_failure_5m`
- tuned parameter:
  - `n_estimators=1600`
  - `max_depth=6`
  - `learning_rate=0.03`
  - `subsample=0.9`
  - `colsample_bytree=0.7`
  - `min_child_weight=8`
  - `reg_alpha=0.2`
  - `reg_lambda=2.0`
  - `early_stopping_rounds=80`
  - `verbose_eval=25`

## 재실행 중 적용되는 수정 사항

- 첫 번째 detailed tuned retrain 시도에서는 명시적으로 넣은 hyperparameter override가 env file 기본값으로 되돌아가는 문제가 있었습니다.
- 원인: `scripts/run_advanced_train_resumable_detailed.sh`가 model name과 horizon override만 유지하고, 나머지 `BORG_XGB_*` override는 유지하지 않았기 때문입니다.
- 수정: `advanced_env.sh`를 source하기 전에 training 관련 runtime override를 모두 보존하고, source 이후 다시 복원하도록 바꿨습니다.
- 커밋: `5f66e48` (`Preserve tuned train overrides in detailed wrapper`)

## 다음 작업

- `xgboost_failure_risk_tuned_v2_repaired_labels`가 모든 horizon을 끝낼 때까지 계속 진행합니다.
- repaired label tuned metric을 baseline trained model과 비교합니다.
- repaired label winner 기준으로 English/Korean evaluation report를 다시 생성합니다.
