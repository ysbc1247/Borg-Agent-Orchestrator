# Advanced Pipeline Handoff

타임스탬프: `2026-03-31 03:15 KST`

## 현재 stage

- `~/Documents/borg_xgboost_workspace/processed/flat_shards` 아래의 고정 샤드 고급 세트에 대해 Advanced flatten가 완료되었습니다.
- 현재 비`.DS_Store` 플랫샤드 parquet 개수: `186`
- 최근 성공한 Advanced flatten 로그: `~/Documents/borg_xgboost_workspace/runtime/logs/20260331031358_advanced_flatten.log`

## flatten 수정 사항이 적용되었습니다.

- `scan_ndjson(...).sink_parquet(...)`을 사용하여 이전 Eager 샤드 경로를 지연 스트리밍 경로로 대체했습니다.
- 다음에 대한 객체 지원 중첩 구문 분석을 기본 구조체 스키마로 대체했습니다.
  - `events.resource_request`
  - `usage.average_usage`
  - `usage.maximum_usage`
  - `machines.capacity`
- `20`-작업자 실행이 비효율적인 것으로 판명된 후 `BORG_FLATTEN_WORKERS`을 다시 `8`로 축소했습니다.
- 실패한 사용량 샤드를 다시 생성할 수 있도록 평탄화에서 불안정한 선택적 사용량 측정항목 `memory_accesses_per_instruction`을 제거했습니다.

## parquet parquet 수리 작업

- 이전 조인 시도에서는 중단된 기록 쓰기로 인해 손상된 `b` 사용 쪽 parquet 파일 6개가 노출되었습니다.
  - `b_usage-000000000005.parquet`
  - `b_usage-000000000008.parquet`
  - `b_usage-000000000009.parquet`
  - `b_usage-000000000010.parquet`
  - `b_usage-000000000012.parquet`
  - `b_usage-000000000013.parquet`
- 해당 파일이 성공적으로 제거되고 다시 생성되었습니다.
- `e`, `f` 및 `g`에 대해 이전에 실패한 추가 사용 샤드도 불안정한 필드가 제거된 후 성공적으로 재생성되었습니다.

## 현재 차단기

- 다운스트림 조인 단계가 여전히 차단되어 있습니다.
- 최근 가입 로그 : `~/Documents/borg_xgboost_workspace/runtime/logs/20260331031434_advanced_join.log`
- 현재 오류:

```text
polars.exceptions.SchemaError: data type mismatch for column time: incoming: Int64 != target: String
```

- `~/Documents/borg_xgboost_workspace/processed/datasets` 아래에는 아직 조인된 고급 데이터 세트 parquet가 작성되지 않았습니다.

## 다음 작업

1. 이벤트 관련 `time` 열 및 기타 혼합 유형 열에 대한 flat shard 파켓 스키마를 검사합니다.
2. `scripts/make_dataset.py`에서 또는 flatten 시간에 해당 열을 정규화하여 `scan_parquet`에서 안정적인 스키마를 확인합니다.
3. 조인 다시 실행
4. Advanced feature 구축 및 XGBoost 교육을 계속합니다.