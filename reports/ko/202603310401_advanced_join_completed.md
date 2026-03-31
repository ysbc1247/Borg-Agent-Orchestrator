# Advanced Join 완료

타임스탬프: `2026-03-31 04:01 KST`

## Result

- 이제 `b`, `c`, `d`, `e`, `f` 및 `g` 클러스터에 대한 Advanced join 데이터 세트 단계가 완료되었습니다.
- 최종 재개 가능한 가입 로그:
  - `~/Documents/borg_xgboost_workspace/runtime/logs/20260331035719_advanced_join_resumable.log`

## 최종 조인 행 수

- `b`: `62,116,886`
- `c`: `66,758,768`
- `d`: `64,764,425`
- `e`: `58,784,525`
- `f`: `71,298,784`
- `g`: `61,083,781`

## 완료를 가능하게 하는 중요한 수정 사항

- `scripts/data_flattener.py`
  - 인용된 숫자 사용 필드에 대해 `scan_ndjson(..., schema_overrides=Int64)`에 의존하는 것을 중지했습니다.
  - `strict=False`으로 스캔한 후 숫자 스칼라 필드를 캐스팅합니다.
- `scripts/make_dataset.py`
  - 연결하기 전에 각 혼합 스키마 parquet 조각을 정규화합니다.
  - 수집 전 최종 데이터 세트 전체 정렬을 제거했습니다.
  - 글로벌 이벤트/머신 사전 그룹 정렬을 그룹화된 `sort_by(...).last()` 집계로 대체했습니다.
- `scripts/run_advanced_join_resumable.sh`
  - 한 번에 하나의 클러스터를 실행하고 완료된 데이터 세트를 건너뛰므로 전체 단계를 다시 시작하는 대신 실패한 클러스터에서 실패를 다시 시도할 수 있습니다.

## 다음 단계

- `./scripts/run_advanced_feature_build.sh` 실행
- 그런 다음 `./scripts/run_advanced_train.sh`을 실행합니다.