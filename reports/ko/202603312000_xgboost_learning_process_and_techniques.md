# XGBoost 학습 과정과 사용한 기법

Timestamp: `2026-03-31 20:00 KST`

## Purpose

이 보고서는 초기 test model 이후 이 프로젝트에서 실제로 사용한 XGBoost 학습 과정을 설명합니다. non-ML developer도 어떤 ML 기법을 썼는지, 왜 썼는지, 어떤 tradeoff가 있었는지를 이해할 수 있도록 정리했습니다.

## Test Model 이후에 한 일

smoke test model로 isolated Advanced XGBoost pipeline이 end-to-end로 동작한다는 것을 확인한 뒤, 실제 ML workflow는 다음 순서로 진행됐습니다.

1. joined dataset 생성
2. feature store 구축
3. multi-horizon failure label 생성
4. baseline XGBoost model 학습
5. hyperparameter candidate tuning
6. `e/f/g`의 broken label repair
7. repaired data 기준으로 tuned retrain 재시작

## 핵심 ML 기법

### 1. Multi-horizon learning

이 프로젝트는 미래 failure를 예측하는 model 하나만 학습한 것이 아닙니다.

대신 prediction window마다 별도 model을 학습했습니다.

- `5m`
- `15m`
- `30m`
- `45m`
- `60m`

즉 model마다 질문이 조금씩 다릅니다.

- "이 task가 앞으로 5분 안에 fail할까?"
- "이 task가 앞으로 60분 안에 fail할까?"

짧은 horizon과 긴 horizon은 필요한 signal이 다르기 때문에 이런 방식이 유용합니다.

### 2. Feature engineering

model은 raw Borg field를 그대로 학습하지 않았습니다.

대신 이런 engineered feature를 사용했습니다.

- CPU / memory usage 요약값
- request 대비 usage ratio
- machine-level / collection-level load
- task age
- 최근 failure history
- lag / delta / rolling 통계
- missingness flag

즉 raw log 자체보다 operational pattern을 학습하도록 만든 것입니다.

### 3. Time-based split

train/validation split은 random sampling이 아니라 time 기준으로 나눴습니다.

즉:

- 과거 window는 train
- 더 최근 window는 validation

이 방식은 실제 production 상황과 더 가깝습니다. model은 항상 과거를 보고 미래를 예측해야 하기 때문입니다.

### 4. Negative downsampling

failure는 rare event라서 negative row가 positive row보다 훨씬 많습니다.

local machine에서 학습이 가능하도록:

- positive row는 전부 유지
- negative row는 일부만 유지

이 방식은 train과 validation 둘 다에 적용되었습니다.

장점:

- memory와 runtime을 크게 줄일 수 있음
- tuning과 iteration이 빨라짐
- local training이 현실적으로 가능해짐

주의점:

- sampled validation에서 계산한 PR-AUC나 precision은 production보다 optimistic하게 보일 수 있음

### 5. Lazy parquet scanning

feature store 전체를 한 번에 거대한 in-memory table로 올리지 않았습니다.

대신 lazy parquet scan과 bounded sampling을 사용했습니다. 이것은 순수 ML algorithm이라기보다는 systems technique에 가깝지만, 이 machine에서 workflow를 실제로 돌리기 위해 매우 중요했습니다.

### 6. `scale_pos_weight`

positive가 rare하기 때문에, trainer는 XGBoost에 class-balance weight를 계산해서 넣습니다.

즉:

- positive는 상대적으로 더 중요하게 보고
- negative는 상대적으로 덜 지배적으로 보게 만듭니다

이렇게 해야 model이 "대부분 정상"만 예측하는 쪽으로 무너지는 것을 줄일 수 있습니다.

### 7. Early stopping

tuned run에서는 `early_stopping_rounds`를 사용했습니다.

의미는:

- validation `aucpr`가 좋아지는 동안은 tree를 계속 추가
- 일정 round 동안 validation `aucpr`가 더 좋아지지 않으면 학습 중단

이 기법은 overfitting을 줄이고, 더 이상 도움이 안 되는 tree를 쌓느라 시간을 낭비하지 않게 해줍니다.

### 8. Regularization

tuned candidate들은 아래와 같은 regularization 관련 control을 사용했습니다.

- 더 낮은 `max_depth`
- 더 높은 `min_child_weight`
- `reg_alpha`
- `reg_lambda`
- `subsample`
- `colsample_bytree`

이 값들은 model이 training set의 noise나 너무 특수한 pattern을 외우는 위험을 낮춥니다.

### 9. Hyperparameter tuning

전체 tuned retrain을 돌리기 전에, representative horizon 기준으로 pilot tuning sweep을 먼저 돌렸습니다.

candidate family는 다음과 같았습니다.

- `baseline_es`
- `regularized_balanced`
- `shallow_conservative`
- `wider_regularized`

이건 standard ML practice입니다.

- 몇 개의 coherent model family를 비교하고
- 가장 promising한 profile을 고른 다음
- 그 다음에 full retrain에 시간을 쓰는 방식입니다

### 10. Feature importance export

학습이 끝난 뒤에는 feature importance file도 export했습니다.

이것이 causality를 증명해 주는 것은 아니지만, 적어도 다음 질문에는 답할 수 있습니다.

- model이 무엇에 의존하는가
- window별로 어떤 signal이 지배적인가
- operationally 말이 되는 feature를 보고 있는가

### 11. Validation prediction export

validation prediction도 저장했습니다.

그래서 나중에 다음을 분석할 수 있습니다.

- ranking behavior
- top-risk row
- threshold effect
- 추가 reporting과 debugging

### 12. Resumable wrapper

join, feature build, training처럼 오래 걸리는 단계는 resumable script로 감쌌습니다.

이것 자체는 ML algorithm은 아니지만, local workstation에서 long-running ML workflow를 운영하는 데 매우 중요한 production engineering technique입니다.

## `regularized_balanced`가 의미하는 것

`regularized_balanced`는 pilot tuning sweep에서 winner가 된 tuning profile입니다.

parameter는 다음과 같습니다.

- `n_estimators=1600`
- `max_depth=6`
- `learning_rate=0.03`
- `subsample=0.9`
- `colsample_bytree=0.7`
- `min_child_weight=8`
- `reg_alpha=0.2`
- `reg_lambda=2.0`
- `early_stopping_rounds=80`

이 profile이 유망했던 이유:

- `learning_rate`가 낮아서 비교적 안정적으로 학습함
- tree 수는 충분해서 ensemble 표현력은 확보함
- regularization이 들어가 있어 공격적인 overfitting을 줄여줌
- 너무 shallow하고 conservative해서 signal을 잃는 수준은 아님

쉽게 말하면 "강하지만 조심스러운" 후보였습니다.

## Data Repair도 ML Process의 일부였다

이 프로젝트에서 가장 중요한 발견 중 하나는 `e/f/g`에 positive가 0이었던 이유가 model 성능 문제가 아니라 upstream event join key 문제였다는 점입니다.

이것이 의미하는 바는 아주 단순합니다.

- label pipeline이 틀리면 metric이 좋아 보여도 의미가 없다

즉 이 프로젝트의 ML process는 단순히

- train
- tune
- compare

가 아니라, 다음도 포함했습니다.

- label quality audit
- upstream data repair
- feature rebuild
- corrected label 기준 retraining

## 실무적으로 배운 점

non-ML developer 관점에서 가장 중요한 교훈은 다음입니다.

- data pipeline이 신뢰 가능해져야 model도 신뢰 가능해진다
- validation metric이 높다고 해서 곧바로 production 성능이 보장되지는 않는다
- regularization과 early stopping은 overfitting 방지용 guardrail이지, overfitting이 절대 없다는 증거는 아니다
- tuning의 목적은 단순히 점수를 키우는 것이 아니라, 더 안정적으로 generalize하는 profile을 찾는 것이다
- feature importance와 validation prediction export는 ML workflow를 설명 가능하고 debug 가능하게 만든다

## 다음 ML 단계

다음으로 가장 가치 있는 단계는 production-style evaluation입니다.

- 가능하면 unsampled holdout에서 평가
- PR-AUC / average precision 옆에 ROC-AUC도 명시
- 실제 class imbalance에 가까운 threshold behavior 비교
- target local cloud 환경에서도 같은 feature logic이 유지되는지 검증
