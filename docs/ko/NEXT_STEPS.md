# Session Handoff

이 파일은 이 저장소의 새 Codex 세션에 대한 재개 지점입니다.

## 이력서 프롬프트

repo 루트에서 Codex를 시작한 후 이 프롬프트를 사용하십시오.

```text
Read Agents.md, NEXT_STEPS.md, MAS_ARCHITECTURE.md, and README.md, inspect the latest commits, and continue from the next logical step.
```

## 현재 상태

- 저장소 루트: `/Users/theokim/Documents/github/kyunghee/Borg-Agent-Orchestrator`
- 1차 브랜치: `main`
- 원시 데이터 위치: `~/Documents/borg_data`
- 처리된 데이터 위치 : `~/Documents/borg_processed`
- Advanced XGBoost workspace: `~/Documents/borg_xgboost_workspace`
- 고급 런타임: repo-local `.venv`이 준비되고 `polars 1.39.3` 및 `xgboost 2.1.4`으로 확인됩니다.
- 기본 작업 클러스터: `b`, `c`, `d`, `e`, `f`, `g`
- 기본적으로 제외됨: `a`, `h`

## 파이프라인 상태

Advanced XGBoost 트랙 상태:

- 고급 작업공간 루트: `~/Documents/borg_xgboost_workspace`
- 이제 고급 런타임 래퍼가 `~/Documents/borg_xgboost_workspace/runtime/logs` 아래에 타임스탬프가 있는 단계 로그를 작성합니다.
- 최근 성공한 Advanced flatten 로그: `~/Documents/borg_xgboost_workspace/runtime/logs/20260331031358_advanced_flatten.log`
- 최근 가입 로그 : `~/Documents/borg_xgboost_workspace/runtime/logs/20260331035719_advanced_join_resumable.log`
- 최신 Advanced feature 빌드 로그: `~/Documents/borg_xgboost_workspace/runtime/logs/20260331040043_advanced_feature_build.log`
- 최신 고급 열차 기록 : `~/Documents/borg_xgboost_workspace/runtime/logs/20260331041159_advanced_train_resumable.log`
- 최신 튜닝 리포트 : `~/Documents/borg_xgboost_workspace/reports/202603311104_advanced_xgboost_tuning.json`
- 상세 이벤트 복구 로그 : `~/Documents/borg_xgboost_workspace/runtime/logs/20260331151302_advanced_event_repair_detailed.log`
- 복구된 cluster에 대한 자세한 가입-재실행 로그: `~/Documents/borg_xgboost_workspace/runtime/logs/20260331152055_advanced_join_resumable_detailed.log`
- 복구된 cluster에 대한 자세한 기능 재실행 로그: `~/Documents/borg_xgboost_workspace/runtime/logs/20260331152830_advanced_feature_build_resumable_detailed.log`
- 현재 tuned retrain 로그: `~/Documents/borg_xgboost_workspace/runtime/logs/20260331153419_advanced_train_resumable_detailed.log`
- 손상되고 실패한 사용 쪽 parquet 샤드를 재생성한 후 고정 샤드 고급 세트에 대해 현재 완료된 Advanced flatten
- 현재 flatten된 고급 샤드 수: `186` 비`.DS_Store` parquet 파일
- 현재 Advanced flatten 구성: `BORG_FLATTEN_WORKERS=8`, `BORG_FLATTEN_HEARTBEAT_SECONDS=10`
- Advanced flatten는 이제 `scan_ndjson(...).sink_parquet(...)`을 사용하여 샤드 처리 및 로그 `started ...`, `done ...` 및 `heartbeat completed=...`을(를) 사용합니다.
- 조인 단계 스키마 불일치는 연결 전에 각 샤드를 느리게 정규화하여 `scripts/make_dataset.py`에서 수정되었으므로 혼합 샤드 스키마가 더 이상 `scan_parquet` 충돌하지 않습니다.
- 문자열 지원 ID/타임스탬프에 `schema_overrides`을 사용하는 대신 스캔 후 인용된 숫자 NDJSON 필드를 캐스팅하여 `scripts/data_flattener.py`에서 고급 사용 flatten 버그가 수정되었습니다.
- 이제 `b`에서 `g`까지 클러스터에 대한 Advanced join 재실행이 완료되었습니다.
- 이제 `b`에서 `g`까지 클러스터에 대한 Advanced feature 구축이 완료되었습니다.
- 이제 재개 가능한 목표별 실행기 아래 구성된 모든 horizon에 대한 고급 훈련이 완료되었습니다.
- 최근 조인된 행 수:
  - `b`: `62,116,886`
  - `c` : `66,758,768`
  - `d`: `64,764,425`
  - `e`: `58,784,525`
  - `f`: `71,298,784`
  - `g`: `61,083,781`
- 현재 feature build 레이블 합계:
  - `b`: 구성된 모든 horizon에 대해 0이 아닌 양수
  - `c`: 구성된 모든 horizon에 대해 0이 아닌 양수
  - `d`: 구성된 모든 horizon에 대해 0이 아닌 양수
  - `e`: `5m=129,553`, `15m=175,699`, `30m=200,677`, `45m=220,331`, `60m=233,409`
  - `f`: `5m=48,677`, `15m=93,644`, `30m=148,814`, `45m=194,633`, `60m=240,144`
  - `g`: `5m=39,509`, `15m=60,618`, `30m=81,189`, `45m=97,625`, `60m=111,570`
- 최종 훈련 Summary:
  - `target_failure_5m`: 평균 정밀도 `0.9810528429`, 정밀도@1% `0.9940523790`, 재현율@1% `0.3911846272`
  - `target_failure_15m`: 평균 정밀도 `0.9726464046`, 정밀도@1% `0.9951022040`, 재현율@1% `0.3226700374`
  - `target_failure_30m`: 평균 정밀도 `0.9720370948`, 정밀도@1% `0.9954522739`, 재현율@1% `0.2821028481`
  - `target_failure_45m`: 평균 정밀도 `0.9659209812`, 정밀도@1% `0.9960021988`, 재현율@1% `0.2523550266`
  - `target_failure_60m`: 평균 정밀도 `0.9595348583`, 정밀도@1% `0.9960519740`, 재현율@1% `0.2326268120`
- 튜닝 상태:
  - 파일럿 스윕 우승자: `regularized_balanced`
  - 우승자 매개변수: `max_depth=6`, `learning_rate=0.03`, `n_estimators=1600`, `subsample=0.9`, `colsample_bytree=0.7`, `min_child_weight=8`, `reg_alpha=0.2`, `reg_lambda=2.0`, `early_stopping_rounds=80`
  - 이전 `xgboost_failure_risk_tuned_v1` 실행은 `e/f/g` 이벤트 키 복구 전에 시작되었고 복구된 레이블을 반영하지 않기 때문에 더 이상 사용되지 않습니다.
  - 현재 repaired label의 Tuned Retrain은 모델명 `xgboost_failure_risk_tuned_v2_repaired_labels`으로 실행 중입니다.
  - 현재 라이브 진행중인 과정은 `./scripts/run_advanced_train_resumable_detailed.sh` + `scripts/train_advanced_xgboost.py` 입니다.
  - 이제 세부 교육 래퍼가 명시적인 CLI 하이퍼파라미터 override를 유지하고 각 대상 시작 시 이를 에코합니다.
  - 세부 훈련 로그는 현재 `target_failure_5m`에서 시작하며 사전 처리가 완료되면 적합 중에 XGBoost 상세 평가 라인을 내보내야 합니다.

완료된 단계:

1. 원시 Borg 샤드 다운로드 스크립트
2. 클러스터별 parquet로 평탄화되는 원시 추적
3. 결합된 사용량/이벤트/머신 데이터 세트 빌더
4. 예측 라벨 데이터 세트 빌더
5. 최초의 Polars 전용 예측자 기본 트레이너
6. 예측자 검사 아티팩트 내보내기
7. 예측자 시간적 특징 생성 및 프로필 평가
8. Borg 이외의 어댑터에 대한 정식 예측 스키마 내보내기

구현된 스크립트:

- `scripts/download_shards.sh`
- `scripts/data_flattener.py`
- `scripts/make_dataset.py`
- `scripts/make_forecaster_dataset.py`
- `scripts/export_common_forecaster_dataset.py`
- `scripts/build_local_common_forecaster_dataset.py`
- `scripts/train_forecaster_baseline.py`

지원 문서:

- `Agents.md` 저장소 워크플로 지침
- MAS 설계의 경우 `MAS_ARCHITECTURE.md`
- 사용자 지향 워크플로의 경우 `README.md`
- `reports/202603191933_milestone.md` 최신 마일스톤 체크포인트

## 최근 검증된 출력

결합된 데이터세트:

- `b` ~ @@PLH0126@@@ 클러스터용으로 성공적으로 구축되었습니다.
- 위치 : `~/Documents/borg_processed/datasets`

예측자 데이터세트:

- `g`을 통해 `b` 클러스터용으로 성공적으로 구축되었습니다.
- 위치 : `~/Documents/borg_processed/datasets/forecaster`

표준 예측 데이터세트:

- `b` ~ @@PLH0132@@@ 클러스터용으로 성공적으로 구축되었습니다.
- 위치 : `~/Documents/borg_processed/datasets/forecaster/common_forecaster`
- Purpose: 향후 로컬 클라우드 어댑터를 위한 안정적인 워크로드/노드/기간 스키마

로컬 클라우드 어댑터 상태:

- JSON 열 매핑을 사용하여 parquet/CSV 원격 측정을 위해 일반 어댑터 스크립트가 추가되었습니다.
- 매핑 파일 예시: `config/local_common_forecaster.example.json`
- 합성 로컬 원격 측정 샘플로 확인되었으며 정식 parquet을 성공적으로 작성했습니다.

지역 parquet 문서 상태:

- `~/Documents/borg_processed` 아래 생성된 parquet 및 아티팩트 디렉터리 옆에 스키마 및 아티팩트 설명 파일이 추가되었습니다.
- 미래의 parquet 작업은 이 규칙을 계속해야 합니다.

기준 아티팩트:

- 위치 : `~/Documents/borg_processed/datasets/forecaster/baseline`
- 파일:
  - `metrics.json`
  - `weights.json`
  - `cluster_metrics.json`
  - `feature_ranking.json`
  - `validation_predictions.parquet`
  - `top_risk_alerts.parquet`

최신 전체 기준선 실행 Summary:

- 총 행 수: `24,052,784`
- 유효성 검사 행: `4,810,777`
- 검증 긍정: `1,448`
- 검증 긍정률 : `0.0301%`
- 평균 정밀도: `0.0074076`
- 정밀도@0.1%: `0.0122661`
- 회상@0.1%: `0.0407459`
- 정밀도@1%: `0.0070676`
- 리콜@1%: `0.2348066`

대체 롤링 프로필 실행 Summary:

- 프로필 : `base_plus_roll`
- artifact 위치 : `~/Documents/borg_processed/datasets/forecaster/baseline_base_plus_roll`
- 평균 정밀도: `0.0071694`
- 정밀도@0.1%: `0.0222453`
- 회상@0.1%: `0.0738950`
- 정밀도@1%: `0.0069013`
- 리콜@1%: `0.2292818`

## 중요한 결정

- 항상 작고 별도의 논리적 커밋을 만들고 푸시하세요.
- 관심사와 파일 클래스별로 커밋을 공격적으로 분할합니다. 별도로 커밋할 수 있는 코드, 문서, 핸드오프, 구성 및 정책 변경 사항을 함께 묶지 마십시오.
- Git이 커밋하고 푸시하기 전에 허가를 요청하지 마세요.
- 대용량 데이터를 저장소 외부에 보관하세요.
- 첫 번째 기본 ML 작업은 `~/Documents/borg_data` 및 `~/Documents/borg_processed` 아래에 유지하고, 새로운 고급/XGBoost 작업은 `~/Documents/borg_xgboost_workspace` 아래에 완전히 격리된 상태로 유지합니다.
- `a` 및 `h`은 기본 그룹과 사용 스키마가 다르기 때문에 기본적으로 제외되도록 유지합니다.
- 명시적인 사용자 프롬프트를 기다리지 않고 다음 구현 단계를 계속하는 것이 좋습니다.
- `reports/` 형식으로 KST 타임스탬프가 앞에 붙은 파일 이름을 `YYYYMMDDHHMM_*` 형식으로 사용하세요.
- 사용자가 `milestone`을 입력하는 경우 세션을 종료하기 전에 완료된 작업에 대한 저장소 메모리 파일을 업데이트하십시오.
- `~/Documents/borg_processed` 아래에 새 parquet 유형 또는 아티팩트 디렉터리가 생성되면 동일한 디렉터리에 스키마 또는 아티팩트 설명 파일을 배치합니다.
- 다중 샤드 원시 Borg 다운로드는 클러스터당 하나의 원시 parquet 파일로 열심히 병합하는 대신 `~/Documents/borg_processed/flat_shards`을 통해 처리되어야 합니다.

## 저장소 메모리

새 Codex 세션이 일관되게 작동하려면 이러한 파일을 최신 상태로 유지해야 합니다.

- `Agents.md` 지속 가능한 워크플로 규칙 및 `milestone`과 같은 트리거 용어의 경우
- `NEXT_STEPS.md` 현재 상태, 다음 단계 및 연속성 참고사항
- `README.md` 사용자 대상 워크플로 및 사용 변경 사항
- 타임스탬프가 지정된 평가, 스키마 및 마일스톤 스타일 세션 기록을 위한 `reports/`

최신 마일스톤 체크포인트:

- `reports/202603271632_milestone.md`
- 새로운 Codex 컨텍스트에서 재개할 때 `Agents.md` 및 이 파일과 함께 사용하십시오.
- 최신 고급 핸드오프 스냅샷: `reports/202603310315_advanced_pipeline_handoff.md`

## 즉시 다음 단계

이제 즉각적인 다음 엔지니어링 작업은 Advanced flatten 실행을 완료하도록 하거나 완료가 너무 느린 경우 추가로 tuning한 다음 격리된 Advanced XGBoost 파이프라인을 엔드 투 엔드로 계속하는 것입니다.

권장되는 다음 순서:

1. `./scripts/run_advanced_xgboost_pipeline.sh`이 `~/Documents/borg_xgboost_workspace/runtime/logs/20260331021002_advanced_flatten.log`에서 현재 flatten 실행을 계속하도록 합니다.
2. 활성 `xgboost_failure_risk_tuned_v2_repaired_labels` retrain이 완료되도록 하고 repaired label tuning 지표를 기준 생산 모델 기간과 비교합니다.
3. 복구된 레이블 tuning `5m` 실행이 아티팩트나 자세한 평가 줄을 내보내지 않고 비정상적으로 오랫동안 멈춰 있는 경우 전처리 메모리 압력을 검사한 다음 행 한도 또는 추정기 예산을 줄이고 동일한 모델 이름에서 다시 시작합니다.
4. 현재 기준선을 초과하는 경우 승리한 repaired label tuning 모델에서 이중 언어 평가 보고서를 재생성합니다.
5. 트레이너 출력의 평균 정밀도/PR-AUC 옆에 명시적인 ROC-AUC를 추가하고 영어/한국어 보고서를 새로 고쳐서 비ML 독자에 대해 메트릭이 일관되게 레이블이 지정되도록 합니다.
6. `e/f/g`이 다시 긍정적인 영향을 미쳤으므로 이제 고급 원시 샤드 깊이를 늘려 보정 및 희귀 이벤트 적용 horizon를 더욱 향상할지 결정합니다.

현재 원시 데이터 확장 참고사항:

- 다운로더는 `sample`, `target_bytes`, `all` 모드를 지원합니다.
- `target_bytes`는 이제 클러스터의 사용량 샤드를 추가하기 전에 클러스터에 대한 시스템 및 이벤트 컨텍스트를 완료하여 일관된 클러스터 슬라이스를 구축합니다.
- 이제 고급 환경은 `BORG_DOWNLOAD_SHARD_COUNT=15`과 함께 `fixed_shards`으로 기본 설정됩니다. 이는 `b`에서 `g`에 대한 클러스터당 첫 번째 `15` 이벤트 및 사용 샤드를 의미합니다.
- 추가 업스트림 샤드를 다운로드하여 현재 `6.91 GB` 기준선에서 `100 GB` 원시 대상에 도달할 수 있습니다.
- 클러스터 `b` 단독의 경우 업스트림에는 `49` `instance_events` 샤드 및 `1,463` `instance_usage` 샤드가 포함됩니다.
- 허용 가능한 중지 창은 `BORG_TARGET_TOLERANCE_BYTES`을 사용하여 넓힐 수 있습니다. 예를 들어 `100 GB` 목표와 실제 `50–150 GB` Result horizon에 대한 `50 GB` 허용 오차를 더합니다.
- 고급 트랙 디렉터리 루트는 이제 `~/Documents/borg_xgboost_workspace`이며 XGBoost/raw 확장 작업에서는 원래 기준 디렉터리가 아닌 해당 루트를 사용해야 합니다.
- `scripts/run_advanced_download.sh`은 이제 고급 env 파일을 자동 로드하고 일관된 다운로더를 격리된 고급 workspace으로 실행하는 단일 명령 진입점을 제공합니다.
- 고급 모델 소스 트리는 이제 전용 스크립트 `scripts/build_advanced_xgboost_dataset.py`, `scripts/train_advanced_xgboost.py` 및 `scripts/run_advanced_xgboost_pipeline.sh`을 사용하여 `src/advanced_xgboost` 아래로 분리됩니다.
- Advanced XGBoost 누락 데이터 정책은 이제 레이블이 유효한 행을 유지하고, XGBoost에 숫자 Null을 보존하고, 조인된 전체 행을 삭제하는 대신 명시적인 누락 표시기 기능을 추가합니다.
- 이제 격리된 Advanced pipeline(`scripts/run_advanced_flatten.sh`, `scripts/run_advanced_join.sh`, `scripts/run_advanced_feature_build.sh`, `scripts/run_advanced_train.sh` 및 전체 체인 `scripts/run_advanced_xgboost_pipeline.sh`에 대한 단계 래퍼가 존재합니다.
- Advanced feature parquet은 이제 기본 horizon `5m`, `15m`, `30m`, `45m` 및 `60m`에 대해 여러 대상 열을 전달하며 트레이너는 별도의 조인된 데이터 세트 없이 대상 열당 하나의 XGBoost 모델을 맞춥니다.
- `scripts/setup_advanced_runtime.sh`은 이제 repo-local `.venv`을 준비하고 고급 래퍼는 해당 해석기와 `PYTHONPATH`을 사용하므로 다운로드가 완료된 후 격리된 파이프라인이 즉시 실행될 수 있습니다.
- macOS의 고급 런타임 종속성 문제는 `libomp`을 설치하여 해결되었으며 이제 `xgboost`은 repo-local `.venv`에서 성공적으로 가져옵니다.
- 혼합 스키마 고급 parquet 샤드는 이제 연결 전에 파일별로 조이너에서 정규화되어 이전 샤드가 문자열 유형 ID/타임스탬프로 기록되었을 때 `polars.exceptions.SchemaError`을 방지합니다.
- 고급 NDJSON flatten는 이제 스캔 후 인용된 숫자 스칼라 필드를 캐스팅합니다. `scan_ndjson(..., schema_overrides=Int64)`이 고정 샤드 고급 세트에 대한 사용 ID/타임스탬프를 널링했기 때문입니다.
- 고급 조이너에는 이제 재개 가능한 한 번에 클러스터 래퍼 `scripts/run_advanced_join_resumable.sh`이 있으며, 이벤트/머신 집계에서 전역 사전 그룹 정렬을 제거하면 전체 Advanced join이 성공적으로 완료될 만큼 조인 벽 시간이 단축되었습니다.
- Advanced feature 및 교육 단계에는 이제 재개 가능한 래퍼(`scripts/run_advanced_feature_build_resumable.sh` 및 `scripts/run_advanced_train_resumable.sh`도 포함됩니다.
- 고급 트레이너는 더 이상 전체 기능 저장소를 메모리에 열심히 연결하지 않습니다. 이제 parquet parquet를 느리게 스캔하고, 모든 포지티브를 유지하고, 네거티브를 제한된 열차/검증 행 캡으로 결정론적으로 다운샘플링하므로 다중 클러스터 훈련이 로컬 시스템에 적합합니다.
- 이제 이전 스크립트를 교체하지 않고 세부적인 재실행을 위한 새로운 추가 단계 래퍼가 존재합니다: `scripts/data_flattener_detailed.py`, `scripts/run_advanced_event_repair_detailed.sh`, `scripts/run_advanced_join_resumable_detailed.sh`, `scripts/run_advanced_feature_build_resumable_detailed.sh` 및 `scripts/run_advanced_train_resumable_detailed.sh`.
- detailed wrapper는 클러스터별 감사 라인을 내보내고, 명시적인 런타임 override를 유지하고, 이전 기준 래퍼 옆에 전용 타임스탬프 로그를 작성하므로 장기 실행 복구 및 retrain 작업을 위한 것입니다.

## 다음 세션에 권장되는 커밋 샤드

예측 개선을 계속하는 경우 작업을 다음과 같은 커밋으로 분할하세요.

1. 다음 예측 모델 구현 추가
2. 로컬-클라우드 예시 매핑을 실제 플랫폼 매핑으로 교체
3. 모델 비교 아티팩트 유지
4. 클러스터 수준 보정 및 순위 지정 동작 비교
5. 성공적인 예측자 프로필/모델을 문서화합니다.
6. 스케줄러 데이터세트 구축 시작

## 최근 커밋 랜드마크

- `e8f06d6` 핸드오프 시 parquet 스키마-노트 규칙 기록
- `f599a15` 현지 parquet 스키마 메모 필요
- `7e426f2` 마일스톤 핸드오프 상태 새로 고침
- `fd9e0cf` 마일스톤 체크포인트 보고서 추가
- `7a70556` 핸드오프 연속성 메모 업데이트
- `e25f5e8` 기록 마일스톤 지속성 워크플로
- `be8a3e8` KST 타임스탬프가 포함된 보고서 파일 이름 접두사

## 실행 명령

권장 재개 명령:

```bash
cd /Users/theokim/Documents/github/kyunghee/Borg-Agent-Orchestrator
codex -a never --sandbox danger-full-access --network-access enabled
```