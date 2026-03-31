# Baseline 과 XGBoost 보고서의 Precision 차이가 큰 이유

Timestamp: `2026-03-31 15:03 KST`

## 짧은 Summary

차이가 크게 보이는 가장 큰 이유는 **모델 공식이 틀렸다기보다, 평가에 사용된 데이터 집단이 다르기 때문**입니다.

- 예전 baseline 보고서는 **전체 validation set** 위에서 평가되었습니다.
- 현재 XGBoost 보고서는 **샘플링된 validation set** 위에서 평가되었습니다.
  - positive는 전부 유지
  - negative는 상당수 제거

Precision은 "선택한 것 중 진짜 positive이 얼마나 되는가"를 보는 지표이기 때문에, negative를 많이 제거하면 수치가 훨씬 좋아 보이게 됩니다.

즉:

- 두 학습 모두 precision / recall 계산식 자체는 대체로 정상입니다.
- 하지만 두 보고서는 **그대로 직접 비교하면 안 됩니다.**

## "Positive는 kept, Negative는 not kept"가 무슨 뜻인가

비ML 개발자 관점에서 쉽게 비유하면 스팸 메일 분류와 비슷합니다.

- `positive`: 반드시 찾아야 하는 중요한 메일
- `negative`: 일반 메일

이제 두 가지 평가 방식을 생각해 보겠습니다.

### 방식 A: 전체 메일함

모든 메일을 그대로 평가합니다.

- 중요한 메일 10개
- 일반 메일 99,990개

이것이 실제 운영 분포에 가깝습니다.

### 방식 B: 줄여진 메일함

중요한 메일 10개는 모두 남겨두고, 일반 메일 99,990개 중에서는 2,500개만 남깁니다.

그러면 평가 세트는:

- 중요한 메일 10개
- 일반 메일 2,500개

이렇게 됩니다.

이 경우 모델은 훨씬 더 좋아 보이기 쉽습니다. 왜냐하면 경쟁해야 할 negative가 훨씬 적기 때문입니다.

현재 XGBoost 평가가 정확히 이런 구조입니다.

- validation positive는 모두 유지
- validation negative는 일부만 남김

그래서 validation set 안의 positive 밀도가 원래 데이터보다 훨씬 높아집니다.

## 왜 Precision이 이렇게 달라지나

Precision은 다음 질문입니다.

> 모델이 위험하다고 고른 것들 중에서, 실제 positive은 몇 개였는가?

negative가 적게 남아 있으면, 상위 risk 구간에 positive가 차지하는 비율이 자연스럽게 높아집니다.

그래서 XGBoost 보고서의:

- `precision@1% ≈ 0.995`

와 예전 baseline 보고서의:

- `precision@1% ≈ 0.007`

를 그대로 놓고 "모델이 100배 좋아졌다"고 보면 안 됩니다.

## 저장소 안의 실제 숫자로 보면

### 예전 baseline 보고서

[`reports/202603191915_forecaster_evaluation.md`](/Users/theokim/Documents/github/kyunghee/Borg-Agent-Orchestrator/reports/202603191915_forecaster_evaluation.md) 기준:

- validation rows: `4,810,777`
- validation positives: `1,448`
- validation positive rate: `0.0301%`
- precision@1%: `0.0070676`
- recall@1%: `0.2348066`

이 의미는:

- validation set 대부분이 negative였고
- positive 비율이 `0.03%` 수준으로 매우 낮았기 때문에
- 절대 precision 값이 낮게 나오는 것이 자연스러웠습니다.

### XGBoost 15분 보고서

`~/Documents/borg_xgboost_workspace/models/xgboost/xgboost_failure_risk_target_failure_15m/metrics.json` 기준:

- source validation rows: `76,991,970`
- sampled validation rows: `2,000,815`
- validation positives: `61,707`
- validation negative keep fraction: `0.025195...`
- precision@1%: `0.995102...`
- recall@1%: `0.322670...`

핵심 해석:

- 원래 validation은 약 `7,700만` 행이었고
- 그 중 negative는 약 `2.5%`만 남겼고
- positive는 전부 남겼습니다.

즉, 지금 보고된 precision은 **원본 전체 validation 분포 위의 precision이 아닙니다.**

## 계산식이 틀린 것인가

### Baseline 쪽

Baseline의 계산 방식은 일반적인 ranking metric 방식입니다.

- precision@k:
  - `risk_score`로 정렬
  - 상위 `k`개 선택
  - positive 수 / 선택 수
- recall@k:
  - 상위 `k`개 선택
  - 선택된 positive 수 / 전체 positive 수
- average precision:
  - rank 기반 average precision

### XGBoost 쪽

XGBoost 쪽도 수식 자체는 일반적인 방식입니다.

- precision@k는 샘플링된 validation frame 위에서 계산
- recall@k도 샘플링된 validation frame 위에서 계산
- average precision도 샘플링된 validation frame 위에서 계산

즉, **주된 문제는 공식 오류가 아니라 평가 대상의 차이**입니다.

## 진짜 문제는 무엇인가

핵심 문제는 **evaluation population mismatch** 입니다.

두 보고서는 서로 다른 질문에 답하고 있습니다.

### Baseline이 답하는 질문

> 전체 validation population을 그대로 놓고 정렬했을 때, 상위 1%의 precision은 얼마인가?

### XGBoost가 답하는 질문

> positive은 모두 유지하고 negative는 많이 제거한 validation population에서, 상위 1%의 precision은 얼마인가?

이 둘은 같은 실험이 아닙니다.

## Recall도 왜 직접 비교하면 안 되나

Recall은 precision보다 negative downsampling의 영향을 덜 받는 편이지만, 여전히 동일 비교는 아닙니다.

이유:

- recall@k는 상위 구간에서 몇 개의 positive를 회수했는지를 봅니다.
- 그런데 그 상위 구간의 크기 `k` 자체가 샘플링된 validation 크기를 기준으로 정해집니다.

validation set이 negative 제거 때문에 훨씬 작아졌다면:

- top `1%`가 포함하는 총 row 수 자체가 달라지고
- positive 밀도도 높아집니다.

따라서 recall도 같은 모집단 위 평가가 아니면 직접 비교가 왜곡됩니다.

## 그래도 XGBoost가 실제로 더 좋을 가능성은 높다

이 비교 문제가 있다고 해서 XGBoost의 개선이 전부 착시라는 뜻은 아닙니다.

왜냐하면:

- XGBoost는 예전 선형형 baseline보다 훨씬 강한 모델 계열이고
- feature interaction을 더 잘 사용할 수 있으며
- temporal feature, missingness indicator 등을 더 유연하게 반영하고
- 학습 데이터 규모도 훨씬 큽니다.

즉 다음 두 문장은 동시에 참일 수 있습니다.

- XGBoost가 실제 ranking 품질은 더 좋다.
- 현재 보고된 precision 증가는 evaluation sampling 때문에 과장되어 있다.

## 지금 가장 안전한 해석

가장 안전한 결론은 다음과 같습니다.

1. XGBoost는 baseline보다 더 좋은 ranking을 학습했을 가능성이 높습니다.
2. 하지만 현재 XGBoost의 precision / average precision은 샘플링된 validation set 때문에 **낙관적(optimistic)** 입니다.
3. 따라서 예전 `0.7%` precision과 현재 `99%` precision을 숫자 그대로 비교하면 안 됩니다.

## 다음에 꼭 해야 할 것

공정 비교를 위해서는:

1. 학습은 필요하면 지금처럼 sampled negative를 써도 됩니다.
2. 그러나 평가는 **full unsampled validation set** 위에서 해야 합니다.
3. 그 위에서 다시 계산해야 합니다:
   - precision@0.1%
   - recall@0.1%
   - precision@1%
   - recall@1%
   - PR-AUC / average precision
   - ROC-AUC
4. 그 다음에 baseline vs XGBoost를 비교해야 진짜 운영 의미가 있습니다.

그 질문은 결국 이것입니다.

> 실제 원본 클래스 불균형 환경에서도 XGBoost가 정말 더 잘 동작하는가?

## 남아 있는 리스크

- 현재 XGBoost 지표는 예전 baseline 보고서와 apples-to-apples 비교가 아닙니다.
- 현재 fixed-shard advanced slice에서는 `e`, `f`, `g` 클러스터의 positive가 0개입니다.
- sampled validation은 실험을 가능하게 해 주지만, 최종 운영형 평가로 바로 쓰기에는 한계가 있습니다.
- 현재 bilingual evaluation report도 XGBoost Result를 잘 정리하고는 있지만, full-population evaluation이 추가되면 다시 갱신하는 것이 맞습니다.

## 결론

예전 precision이 낮았다고 해서 예전 모델 계산이 틀렸다는 뜻은 아닙니다.

낮게 나온 주된 이유는:

- validation population이 극단적으로 불균형했고
- 전체 분포 그대로 평가했기 때문입니다.

현재 XGBoost precision도 공식상 "잘못 계산"된 것은 아닐 가능성이 높습니다.

하지만 그대로 비교하면 안 되는 이유는:

- positive는 모두 남기고
- negative는 많이 제거한 상태에서 평가했기 때문입니다.

따라서 현재 가장 정확한 결론은:

- 계산식 자체보다
- **평가에 사용된 모집단이 다르다**는 점이 핵심입니다.
