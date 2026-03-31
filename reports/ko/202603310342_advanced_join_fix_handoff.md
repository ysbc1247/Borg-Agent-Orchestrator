# Advanced Join Fix Handoff

타임스탬프: `2026-03-31 03:42 KST`

## 수정된 사항

- `scripts/make_dataset.py`은 더 이상 혼합 스키마 고급 parquet 조각을 직접 glob 스캔하지 않습니다.
- 이제 조이너는 각 샤드를 느리게 스캔하고 샤드별로 예상되는 스키마로 캐스팅한 다음 정규화된 게으른 프레임을 연결합니다.
- 이는 이전의 Advanced join 충돌을 수정합니다.

```text
polars.exceptions.SchemaError: data type mismatch for column time: incoming: Int64 != target: String
```

- `scripts/data_flattener.py`은 인용된 숫자 스칼라 필드에 대해 더 이상 `scan_ndjson(..., schema_overrides=Int64)`에 의존하지 않습니다.
- 이제 병합기는 해당 필드를 허용적으로 스캔하고 `with_columns(...)`에서 `strict=False`을 사용하여 캐스팅합니다.
- 이는 `start_time`, `end_time`, `collection_id`, `instance_index` 및 `machine_id`이 클러스터 `b`, `d`에 대해 모두 null로 작성된 고급 사용 샤드 버그를 수정합니다. `e`, `f`, `g`

## 확인

- `b_usage-000000000000.json.gz`에 대한 원시 고급 사용 샘플 확인이 이제 `Int64`으로 올바르게 캐스팅됩니다.
- `~/Documents/borg_xgboost_workspace/processed/flat_shards/usage` 아래의 모든 고급 사용 샤드 parquet가 삭제되고 성공적으로 재생성되었습니다.
- 재생성 후 사용 키 검증에서는 이제 `b`, `c`, `d`, `e`, `f` 및 `g` 클러스터의 행 수와 동일한 null이 아닌 개수를 표시합니다.
- 현재 가입 재실행 로그 : `~/Documents/borg_xgboost_workspace/runtime/logs/20260331033021_advanced_join.log`
- 지금까지 확인된 결합 출력:
  - `b_dataset.parquet`: `62,116,886` 행

## 현재 상태

- `./scripts/run_advanced_join.sh`은 `20260331033021` 로그에서 계속 실행 중입니다.
- 수정 후 새로운 가입 오류가 나타나지 않았습니다.
- 재실행 중에 `b` 클러스터가 성공적으로 완료되었습니다.
- 가입 완료 후 다음 단계는 여전히 `./scripts/run_advanced_feature_build.sh`, `./scripts/run_advanced_train.sh`입니다.