# Advanced Flatten Handoff

타임스탬프: `2026-03-31 02:36 KST`

## horizon

이 보고서는 `~/Documents/borg_xgboost_workspace` 아래에 격리된 Advanced XGBoost 파이프라인의 현재 상태를 기록합니다.

## 현재 런타임 상태

- 라이브 파이프라인 진입점: `./scripts/run_advanced_xgboost_pipeline.sh`
- 라이브 파이프라인 로그: `~/Documents/borg_xgboost_workspace/runtime/logs/20260331021002_advanced_pipeline.log`
- 라이브 플랫화 로그: `~/Documents/borg_xgboost_workspace/runtime/logs/20260331021002_advanced_flatten.log`
- Advanced flatten 구성:
  - `BORG_FLATTEN_WORKERS=20`
  - `BORG_FLATTEN_HEARTBEAT_SECONDS=10`
- 현재 flatten된 고급 샤드 수: `56` 비`.DS_Store` `~/Documents/borg_xgboost_workspace/processed/flat_shards` 아래의 parquet 파일

## 최근 행동 변화

- 고급 단계 래퍼는 이제 타임스탬프가 있는 로그를 작성하고 `latest_advanced_*.log` 심볼릭 링크를 유지합니다.
- 이제 플래트너는 0에서 다시 시작하는 대신 기존 샤드 parquet 출력에서 ​​다시 시작됩니다.
- 이제 병합기가 다음을 기록합니다.
  - `started ...` 작업자가 샤드를 시작하는 경우
  - `done ...` 샤드 parquet를 쓴 경우
  - 장기 샤드 작업 중 `heartbeat completed=... running=... pending=...`
- 사용자 요청에 따라 고급 병합이 `8` 작업자에서 `10`로 푸시된 다음 `20`으로 푸시되었습니다.

## 현재 병목 현상

- 대규모 고급 `events` 샤드는 여전히 파이프라인에서 가장 느린 부분입니다.
- 예제 이벤트 샤드 크기는 각각 대략 `500 MB` 압축되어 있습니다.
- 현재 이벤트 flatten 경로는 `pl.Object`과 `map_elements(...)`을 통해 중첩된 `resource_request` 값을 추출하는데, 이는 기본 구조체 기반 경로보다 느립니다.
- 이는 로그에 `done ...` 줄이 자주 표시되지 않고 `heartbeat` 줄이 반복적으로 표시될 수 있는 주된 이유입니다.

## 현재 해석

- 로그에 `started ...`과 반복되는 `heartbeat completed=...` 행이 표시되면 샤드 완료가 드물더라도 병합이 활성화됩니다.
- 대규모 이벤트 샤드의 첫 번째 물결이 구문 분석되고 기록되는 동안 드물게 완료될 것으로 예상됩니다.
- 향후 세션에 더 많은 처리량이 필요한 경우 다음으로 중요한 최적화는 작업자 수를 더 늘리는 것보다 객체 지원 이벤트 중첩 추출 경로를 바꾸는 것입니다.

## 다음 작업

1. 현재 고급 평탄화 실행을 계속 진행합니다.
2. 완료가 너무 희박한 경우 `scripts/data_flattener.py`에서 이벤트 중첩 필드 추출을 최적화합니다.
3. flatten가 완료된 후 동일한 격리된 고급 workspace을 사용하여 조인, feature build 및 XGBoost 교육을 계속 진행합니다.