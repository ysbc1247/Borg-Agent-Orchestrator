# Model Directory Registry 및 ML Evolution

## Purpose

이 보고서는 다음 XGBoost model artifact directory들을 설명합니다.

- `~/Documents/borg_xgboost_workspace/models/xgboost`

핵심 질문은 두 가지입니다.

1. 각 디렉토리가 나타내는 것
2. 시간이 지남에 따라 머신러닝 프로세스가 어떻게 발전했나요?

## Directory 계열

### 1. smoke test 계열

- `xgboost_smoke_target_failure_5m`

의미:

- 이것은 isolated Advanced XGBoost pipeline이 실제로 end-to-end로 도는지 확인한 초기 smoke run입니다.
- 목적은 최종 model quality가 아니라 pipeline plumbing 검증이었습니다.

존재 이유:

- full training 전에 더 작고 단순한 실험을 먼저 돌려서 다음이 실제로 되는지 확인하는 것은 standard practice입니다.
  - feature loading
  - training
  - artifact export
  - metric export

### 2. 베이스라인 풀 어드밴스드 제품군

- `xgboost_failure_risk_target_failure_5m`
- `xgboost_failure_risk_target_failure_15m`
- `xgboost_failure_risk_target_failure_30m`
- `xgboost_failure_risk_target_failure_45m`
- `xgboost_failure_risk_target_failure_60m`

의미:

- 이는 최초의 완전한 다중 수평 Advanced XGBoost 모델입니다.
- 고급 트랙의 기본 제품군을 형성합니다.

연기 실행과 비교하여 변경된 사항:

- 더 많은 데이터
- 다중 클러스터 기능 저장소
- 다중 수평 훈련
- 전체 아티팩트 내보내기
- 전체 기능 - 중요 내보내기

### 3. 파일럿 튜닝 제품군

- `xgboost_tune_baseline_es_target_failure_5m`
- `xgboost_tune_regularized_balanced_target_failure_5m`
- `xgboost_tune_shallow_conservative_target_failure_5m`
- `xgboost_tune_wider_regularized_target_failure_5m`

의미:

- `5m` 수평선에만 사용되는 제어된 튜닝 후보입니다.
- 모든 창에 걸쳐 완전히 tuned retrain에 시간을 보내기 전에 매개변수 계열을 비교하기 위해 만들어졌습니다.

이 단계가 정상적인 이유:

- 모든 horizon을 즉시 tuning하는 것은 비용이 많이 듭니다.
- 일반적인 관행은 하나의 대표적인 horizon을 선택하고, 여러 후보 구성을 실행하고, 성공적인 프로필을 선택하는 것입니다.

Result:

- `regularized_balanced`이 파일럿 스윕에서 승리했으며 나중에 완전히 tuned retrain 시도의 기초가 되었습니다.

### 4. 완전 tuned 가족 retrain

- `xgboost_failure_risk_tuned_v1_target_failure_5m`
- `xgboost_failure_risk_tuned_v2_repaired_labels_target_failure_5m`

의미:

- 이 디렉토리는 튜닝 승자를 완전히 튜닝된 모델 계보로 바꾸려는 시도를 나타냅니다.

둘 사이의 차이점:

- `tuned_v1`
  - 첫 번째 완전 tuning 시도
  - `e/f/g` repaired 라벨 수정 이전에 시작됨
  - 구식
- `tuned_v2_repaired_labels`
  - 올바른 후속 실행
  - repaired `e/f/g` 라벨 포함
  - 현재 tuned 분기를 시청할 수 있습니다.

## ML 프로세스의 진화

학습 과정은 다음 순서로 진행되었습니다.

### 1단계. 파이프라인 검증

목표:

- 격리된 Advanced XGBoost 파이프라인이 엔드 투 엔드로 작동했음을 증명

artifact:

- `xgboost_smoke_target_failure_5m`

팀이 배운 내용:

- 기능 로딩, 훈련, 점수 매기기 및 아티팩트 저장을 위한 코드 경로가 작동 중이었습니다.

### 2단계. 첫 번째 전체 기준 모델링

목표:

- 여러 실패 horizon에 대한 심각한 기준 모델 계열을 훈련합니다.

artifact:

- `xgboost_failure_risk_target_failure_5m`
- `xgboost_failure_risk_target_failure_15m`
- `xgboost_failure_risk_target_failure_30m`
- `xgboost_failure_risk_target_failure_45m`
- `xgboost_failure_risk_target_failure_60m`

변경된 사항:

- 프로젝트가 "훈련할 수 있나요?"에서 옮겨졌습니다. "창 전체의 기준 신호는 무엇입니까?"

팀이 배운 내용:

- feature importance는 수명주기 및 이벤트 기록 기능에 의해 지배되었습니다.
- Advanced XGBoost 파이프라인은 강력한 내부 순위 지표를 생성할 수 있습니다.
- 서로 다른 창에서 단기 메타데이터와 장기적인 리소스 적합성 신호로 중요성이 이동했습니다.

### 3단계. 매개변수 튜닝

목표:

- 정규화 및 조기 중단을 통해 과적합을 제어하면서 더 나은 하이퍼파라미터로 기준선을 개선합니다.

artifact:

- `xgboost_tune_*` 디렉토리

변경된 사항:

- 팀은 "기본적인 기준선"에서 "매개변수 계열 비교"로 이동했습니다.
- 이는 전형적인 모델 선택 단계입니다.

팀이 배운 내용:

- `regularized_balanced` 최강의 파일럿 후보로 보임
- 튜닝 아티팩트는 샘플링된 검증 데이터에서 여전히 평가되었으므로 비교에는 유용했지만 최종 배포 증명은 아닙니다.

### 4단계. 라벨 품질 수정

목표:

- 클러스터 `e/f/g`의 숨겨진 데이터 문제를 해결합니다.

무엇이 잘못되었나요?

- `e/f/g`에 대한 이벤트 flat shard의 조인 키가 손상되었습니다.
- 따라서 조인된 데이터세트에는 이벤트 라벨이 없습니다.
- 따라서 기능 세트에는 `e/f/g`에 대한 긍정적인 내용이 없습니다.

변경된 사항:

- 이벤트 flat shard가 재생성되었습니다.
- `e/f/g` 조인이 다시 실행되었습니다.
- `e/f/g` 기능 세트가 다시 실행되었습니다.
- 긍정적인 라벨이 모든 창에 다시 나타납니다.

이것이 중요한 이유:

- 단순한 튜닝 변경이 아닙니다.
- 모델이 실제로 학습할 수 있는 내용을 변경하는 데이터 품질 수정입니다.

### 5단계. 수정된 라벨 tuning retrain

목표:

- 수정된 라벨에서 tuned 모델 계열을 다시 실행합니다.

artifact:

- `xgboost_failure_risk_tuned_v1_target_failure_5m`
- `xgboost_failure_risk_tuned_v2_repaired_labels_target_failure_5m`

해석:

- `tuned_v1`은 역사적으로 실패한 브랜치입니다.
- `tuned_v2_repaired_labels`은 의미 있는 후계자다.

## 중요한 프로세스 주의사항

현재 Advanced XGBoost 워크플로는 훈련과 검증 모두에서 네거티브 다운샘플링을 사용합니다. 이는 다음을 의미합니다.

- 저장된 아티팩트는 유효한 실험 아티팩트입니다.
- 측정항목은 모델 대 모델 비교에 유용합니다.
- 측정항목은 아직 최종 프로덕션 스타일 로컬 클라우드 수치가 아닙니다.

따라서 지금까지의 ML 프로세스는 다음과 같은 패턴으로 발전해 왔습니다.

1. 인프라 검증
2. 기준선 모델링
3. 튜닝
4. 데이터 복구
5. tuned retrain 수정
6. 로컬-클라우드 이전에 대한 프로덕션 스타일 평가 예정

## 최종 마일스톤에 추가해야 할 사항

로컬 클라우드 이정표의 경우 다음 진화는 다음과 같아야 합니다.

1. 샘플링되지 않은 홀드아웃에서 최종 후보 모델의 점수를 매깁니다.
2. PR-AUC/평균 정밀도 옆에 ROC-AUC를 추가합니다.
3. 현실적인 계급 불균형에 대한 임계값을 비교합니다.
4. Borg 스타일 기능을 로컬 클라우드 기능에 매핑
5. 전송 후에도 동일한 기능 논리가 여전히 모델을 구동하는지 확인합니다.

## 디렉터리 수준 문서

짧은 `README.md` 파일은 다음 모델-아티팩트 디렉터리 내부에 직접 추가되었습니다.

- `~/Documents/borg_xgboost_workspace/models/xgboost`

해당 로컬 파일은 각 디렉토리를 설명하므로 아티팩트 트리는 git 저장소 외부에서도 자체 설명됩니다.
