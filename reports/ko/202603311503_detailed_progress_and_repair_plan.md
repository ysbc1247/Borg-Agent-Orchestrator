# 자세한 진행상황 및 수리계획

타임스탬프: `2026-03-31 15:03 KST`

## 새로운 추가 스크립트가 추가된 이유

- 기존 고급 래퍼는 일괄 실행에는 충분했지만 장기 실행 수리 및 retrain 작업에는 너무 부족했습니다.
- 이전 작업 흐름과 보고서가 그대로 유지되도록 이전 스크립트를 교체하는 대신 새 스크립트가 추가되었습니다.
- 목표는 다음과 같습니다.
  - 더 자세한 라이브 로그
  - 클러스터별 및 종류별 체크포인트
  - 수리 실행 후 감사 Summary
  - 손상된 이벤트 샤드에 대한 명시적인 재실행 경로

## 새로운 스크립트

- `scripts/data_flattener_detailed.py`
  - `BORG_FLATTEN_KINDS` 지원
  - 대기열 수, 하트비트 속도, ETA 및 실행 후 감사를 기록합니다.
- `scripts/run_advanced_event_repair_detailed.sh`
  - 선택한 고급 이벤트 parquet 조각을 삭제합니다.
  - 세부 평탄화 기능을 사용하여 선택한 이벤트 샤드만 재생성합니다.
- `scripts/run_advanced_join_resumable_detailed.sh`
  - 클러스터별로 조인을 다시 실행하고 Result 행 수 및 이벤트 레이블이 지정된 행을 기록합니다.
- `scripts/run_advanced_feature_build_resumable_detailed.sh`
  - 클러스터별로 기능 parquet parquet를 재구축하고 수평선당 포지티브 라벨 합계를 기록합니다.

## 즉시수리 대상

- 클러스터 `e`, `f` 및 `g`
- 현재 문제:
  - 이벤트 flat shard가 존재합니다.
  - 그러나 이벤트 조인 키 열은 기존 parquet 파일에서 모두 null입니다.
  - 따라서 결합된 데이터세트에는 이벤트 라벨이 없습니다.
  - 따라서 기능 세트에는 모든 horizon에 대해 긍정적인 요소가 없습니다.

## 수리 순서

1. 현재 실행 중인 tuned retrain을 중지하여 머신 리소스를 확보합니다.
2. 고급 작업 영역에서 `e/f/g` 이벤트 파켓 샤드만 삭제합니다.
3. `run_advanced_event_repair_detailed.sh`이 포함된 이벤트 샤드만 재생성합니다.
4. `run_advanced_join_resumable_detailed.sh`을 사용하여 `e/f/g`에 대한 조인을 다시 실행합니다.
5. `run_advanced_feature_build_resumable_detailed.sh`을 사용하여 `e/f/g`에 대한 feature build를 다시 실행합니다.
6. 이제 긍정적인 라벨이 존재하는지 확인하세요.
7. 복구된 데이터세트에 대한 모델 훈련 재개