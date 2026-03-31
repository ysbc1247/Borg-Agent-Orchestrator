# Window별 Feature Importance 평가

## Scope

이 보고서는 완료된 baseline Advanced XGBoost model들에 대해 저장된 `feature_importance.json` artifact를 정리합니다.

- `xgboost_failure_risk_target_failure_5m`
- `xgboost_failure_risk_target_failure_15m`
- `xgboost_failure_risk_target_failure_30m`
- `xgboost_failure_risk_target_failure_45m`
- `xgboost_failure_risk_target_failure_60m`

여기서 쓰는 importance 값은 각 prediction window별로 model이 export한 XGBoost feature importance입니다. 어떤 input을 많이 참고했는지 보는 데는 유용하지만, causal explanation은 아닙니다.

## 주요 Findings

### 1. 모든 window를 지배하는 두 가지 feature

5개 창 모두에서 모델은 다음 사항에 의해 지배됩니다.

- `task_age_us`
- `event_count`

창 전체의 평균 중요도:

| Feature | 평균 중요도 |
| --- | ---: |
| `task_age_us` | `0.688633` |
| `event_count` | `0.130892` |

해석:

- `task_age_us`은 모든 모델에서 매우 큰 차이로 가장 강력한 신호입니다.
- `event_count`은 모든 모델에서 두 번째로 강한 신호입니다.
- 함께, 그들은 모델의 총 중요도 질량의 대부분을 차지합니다.

즉 baseline Advanced model은 단기 failure risk를 추정할 때 task maturity와 event-history density를 매우 강하게 보고 있다는 뜻입니다.

## 안정적인 핵심 기능

이러한 기능은 대부분 또는 모든 창에서 여전히 중요합니다.

| 기능 | 평균 중요도 | 패턴 |
| --- | ---: | --- |
| `task_age_us` | `0.688633` | 모든 horizon에서 지배적이며 horizon 길이가 증가함에 따라 약간 감소합니다 |
| `event_count` | `0.130892` | 모든 영역에 걸쳐 강력하고 안정적인 두 번째 기능 |
| `observed_failure_by_window` | `0.015891` | 안정적인 사전 고장 신호 |
| `scheduling_class` | `0.015795` | 안정적인 스케줄링 정책 신호 |
| `priority` | `0.015499` | 짧은 창에서는 강하고 나중에는 약함 |
| `collection_recent_failure_count_12` | `0.008749` | 모든 창에서 중요하며, 긴 창에서 더 강력함 |
| `collection_recent_terminal_count_12` | `0.006563` | 안정적인 과거 터미널 이벤트 신호 |
| `usage_window` | `0.006031` | 지속적으로 유용하지만 부차적인 |
| `collection_window_avg_mem_sum` | `0.005524` | 안정적인 작업 부하 수준의 부하 신호 |
| `machine_recent_terminal_count_12` | `0.005028` | 안정적인 기계 이력 신호 |

## 창별 상위 10가지 기능

### 5분 모델

1. `task_age_us` `0.717560`
2. `event_count` `0.134272`
3. `priority` `0.024799`
4. `observed_failure_by_window` `0.014286`
5. `scheduling_class` `0.012484`
6. `collection_recent_failure_count_12` `0.006880`
7. `avg_mem_to_request_ratio` `0.006291`
8. `usage_window` `0.006038`
9. `collection_window_avg_cpu_sum` `0.005629`
10. `collection_recent_terminal_count_12` `0.005353`

### 15분 모델

1. `task_age_us` `0.705644`
2. `event_count` `0.127874`
3. `priority` `0.025674`
4. `observed_failure_by_window` `0.015609`
5. `scheduling_class` `0.015569`
6. `collection_recent_failure_count_12` `0.008486`
7. `collection_recent_terminal_count_12` `0.006029`
8. `usage_window` `0.005710`
9. `collection_window_avg_mem_sum` `0.005257`
10. `req_cpu` `0.004991`

### 30분 모델

1. `task_age_us` `0.688073`
2. `event_count` `0.130745`
3. `scheduling_class` `0.016288`
4. `observed_failure_by_window` `0.015926`
5. `priority` `0.014835`
6. `req_cpu` `0.012222`
7. `collection_recent_failure_count_12` `0.007948`
8. `usage_window` `0.006907`
9. `collection_recent_terminal_count_12` `0.006522`
10. `max_mem_to_request_ratio` `0.006485`

### 45분 모델

1. `task_age_us` `0.675809`
2. `event_count` `0.128991`
3. `req_cpu` `0.019481`
4. `scheduling_class` `0.017011`
5. `observed_failure_by_window` `0.016949`
6. `collection_recent_failure_count_12` `0.008659`
7. `avg_mem_to_request_ratio` `0.007975`
8. `collection_recent_terminal_count_12` `0.007345`
9. `max_mem_to_request_ratio` `0.006408`
10. `usage_window` `0.006111`

### 60분 모델

1. `task_age_us` `0.656080`
2. `event_count` `0.132580`
3. `avg_mem_to_request_ratio` `0.018261`
4. `scheduling_class` `0.017623`
5. `req_cpu` `0.017073`
6. `observed_failure_by_window` `0.016685`
7. `collection_recent_failure_count_12` `0.011769`
8. `collection_recent_terminal_count_12` `0.007565`
9. `cpu_request_ratio` `0.007500`
10. `priority` `0.006286`

## 교차 창 동향

### 짧은 기간 모델은 워크플로 메타데이터에 더 많이 의존합니다.

`5m` 및 `15m` 모델은 다음에 상대적으로 더 많은 비중을 둡니다.

- `priority`
- `scheduling_class`
- 즉각적인 역사적 실패 지표

해석:

- 매우 짧은 기간 예측의 경우 모델은 작업의 긴급성, 일정 컨텍스트 및 작업에 이미 문제의 징후가 보이는지 여부에 더 의존합니다.

### 더 긴 기간 모델은 리소스 형태에 더 많이 의존합니다.

`30m` ~ `60m` 모델은 다음에 상대적으로 더 많은 비중을 둡니다.

- `req_cpu`
- `avg_mem_to_request_ratio`
- `cpu_request_ratio`
- `max_mem_to_request_ratio`
- `req_mem`

해석:

- 장기적인 예측은 작업이 요청된 리소스 및 기계 용량과 구조적으로 일치하지 않는지 여부에 더 의존합니다.
- 이는 합리적인 패턴입니다. 향후 위험은 즉각적인 실패에 가까운 증상보다는 지속적인 자원 압박과 관련되는 경우가 많습니다.

### horizon이 커질수록 기록 기능이 더욱 중요해집니다.

다음과 같은 기능:

- `collection_recent_failure_count_12`
- `collection_recent_terminal_count_12`
- `machine_recent_terminal_count_12`

기간이 길수록 더욱 중요해집니다.

해석:

- 예측 horizon가 멀수록 모델은 작업의 더 넓은 맥락에서 누적된 불안정 기록을 더 많이 사용합니다.

## 중요성이 거의 0에 가까운 기능

많은 누락 플래그는 저장된 기준 모델, 특히 `5m` 모델에서 중요도가 0입니다.

해석:

- 이 훈련 슬라이스에서 해당 소스 열이 거의 누락되지 않거나
- 원시 특성 값은 이미 유용한 신호를 캡처하므로 누락 표시기가 거의 추가되지 않습니다.

이는 실종 플래그가 실수였다는 의미는 아닙니다. 이는 현재 교육 데이터에서 사용률이 낮은 안전 기능임을 의미합니다.

## 운영 읽기

높은 수준에서 기본 Advanced XGBoost 모델은 주로 네 가지 증거 그룹을 사용합니다.

1. 수명주기 상태
   - `task_age_us`
   - `usage_window`

2. 사건 이력 밀도와 사전 불안정성
   - `event_count`
   - `observed_failure_by_window`
   - 최근 실패/단말기 카운터

3. 스케줄링 및 작업 정책
   - `priority`
   - `scheduling_class`

4. 자원 적합성과 압박감
   - `req_cpu`, `req_mem`
   - 요청 비율
   - 메모리 대 요청 비율
   - 수집 및 기계 창 부하 합계

이는 실패 예측에 있어 방향적으로 합리적입니다. 모델은 "작업이 얼마나 오래되었는지", "이미 문제의 징후를 보였습니까?", "어떤 일정 체제에 있는지", "자원 동작이 환경과 일치하지 않는 것처럼 보입니까?"를 결합하는 것으로 보입니다.

## 위험과 한계

- 이러한 중요성은 아직 실행 중인 repaired label tuning retrain이 아닌 저장된 기준 모델에서 비롯됩니다.
- 중요성은 인과관계를 의미하지 않습니다.
- 두 기능의 상관 관계가 높으면 중요도가 둘 사이에 고르지 않게 분할될 수 있습니다.
- 모델은 샘플링된 검증 세트에서 평가되었으므로 강력한 중요도 순위 자체가 강력한 생산 일반화를 입증하지는 않습니다.
- `task_age_us`의 지배력이 매우 크다는 것은 모델이 수명 주기 효과에 크게 의존할 수 있음을 의미합니다. 로컬 클라우드 환경으로 이동할 때 주의 깊게 확인해야 할 사항입니다.

## 최종 마일스톤에 대한 권장 사항

로컬 클라우드 환경에 배포하기 전에 다음과 같은 동일한 주요 기능이 여전히 지배적인지 비교하십시오.

- repaired 라벨 tuning 모델에 대한 교육
- 샘플링되지 않은 홀드아웃을 평가합니다.
- 로컬 클라우드 형태의 데이터 검증

동일한 기능이 안정적으로 유지된다면 이는 이전 가능성이 있다는 좋은 신호입니다. 급격하게 변화하는 경우 Borg 기반 모델은 내구성 있는 작동 신호보다는 데이터 세트별 지름길에 의존할 수 있습니다.
