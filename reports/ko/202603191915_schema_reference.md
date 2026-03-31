# 스키마 참조

이 파일은 처리된 Borg parquet parquet 출력에서 관찰된 스키마 및 유형 정보와 분석 중에 필요한 관련 메모를 기록합니다.

## 처리된 이벤트 Parquet 스키마

확인된 소스: `~/Documents/borg_processed/b_events.parquet`

열 및 유형:

- `time`: `String`
- `type`: `String`
- `collection_id`: `String`
- `scheduling_class`: `String`
- `missing_type`: `String`
- `collection_type`: `String`
- `priority`: `String`
- `alloc_collection_id`: `String`
- `instance_index`: `String`
- `machine_id` : `String`
- `alloc_instance_index` : `String`
- `req_cpu` : `Float64`
- `req_mem`: `Float64`

참고:

- 많은 이벤트 필드가 처리된 Parquet에 `String`으로 저장되지만 다운스트림 데이터 세트 빌더는 모델링하기 전에 그 중 일부를 정수 유형으로 변환합니다.

## 이벤트 `type` 의미

`type` 필드는 `CollectionEvent` 및 `InstanceEvent`에 사용되는 Borg 스케줄러 이벤트 열거형입니다.

- `0` : `SUBMIT`
- `1`: `QUEUE`
- `2`: `ENABLE`
- `3`: `SCHEDULE`
- `4` : `EVICT`
- `5`: `FAIL`
- `6`: `FINISH`
- `7`: `KILL`
- `8`: `LOST`
- `9` : `UPDATE_PENDING`
- `10`: `UPDATE_RUNNING`

## 일부 이벤트가 `time` 값이 `0`인 이유

Borg 추적은 `time`을 추적 시작 이후의 마이크로초로 정의합니다.

`time = 0`의 해석:

- 워크로드의 실제 생성 시간이 아닌 관찰 기간의 시작을 표시하는 경우가 많습니다.
- 추적이 시작될 때 워크로드 또는 인스턴스가 이미 존재했음을 나타낼 수 있습니다.
- 추적에 초기 관찰 상태가 포함되어 있지만 해당 상태를 생성한 이전 전환이 포함되어 있지 않은 경우에도 나타날 수 있습니다.

실제적인 의미:

- `time = 0`이 자동으로 실제 제출 또는 생성 순간으로 해석되어서는 안 됩니다.
- 이러한 행은 초기 관찰 상태 기록으로 더 잘 처리되는 경우가 많습니다.

## 처리된 사용량 Parquet 스키마

확인된 소스: `~/Documents/borg_processed/b_usage.parquet`

열 및 유형:

- `start_time` : `String`
- `end_time` : `String`
- `collection_id`: `String`
- `instance_index` : `String`
- `machine_id` : `String`
- `alloc_collection_id` : `String`
- `alloc_instance_index` : `String`
- `collection_type` : `String`
- `random_sample_usage` : `Struct({'cpus': Float64})`
- `assigned_memory` : `Float64`
- `page_cache_memory` : `Float64`
- `memory_accesses_per_instruction`: `Float64`
- `sample_rate` : `Float64`
- `cpu_usage_distribution` : `List(Float64)`
- `tail_cpu_usage_distribution` : `List(Float64)`
- `avg_cpu` : `Float64`
- `avg_mem` : `Float64`
- `max_cpu`: `Float64`
- `max_mem`: `Float64`
- `cluster_id` : `String`

## 처리된 기계 Parquet 스키마

확인된 소스: `~/Documents/borg_processed/b_machines.parquet`

열 및 유형:

- `time` : `String`
- `machine_id` : `String`
- `type`: `String`
- `switch_id` : `String`
- `platform_id` : `String`
- `machine_cpu`: `Float64`
- `machine_mem`: `Float64`

## 모델링 노트

원시 처리된 parquet parquet 스키마는 모델링 스키마와 동일하지 않습니다.
학습 파이프라인은 결합된 데이터 세트와 예측 데이터 세트를 구축하기 전에 이러한 열을 숫자 특성으로 캐스팅하고 재구성합니다.