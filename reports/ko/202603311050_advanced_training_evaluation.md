# Advanced XGBoost 평가 보고서 (한국어)

생성 시각 `2026-03-31 10:50 KST`

## 핵심 Summary

- 운영용 horizon `5m`, `15m`, `30m`, `45m`, `60m` 학습이 모두 완료되었습니다.
- 평균 정밀도(AP)가 가장 높은 horizon은 `5m` 이며 값은 `0.981053` 입니다.
- 운영 alert budget인 `1%` 기준 재현율이 가장 높은 horizon도 `5m` 이며 값은 `0.391185` 입니다.
- 예측 창이 길어질수록 성능이 점진적으로 하락합니다. 이는 더 긴 horizon일수록 실패 직전 상태와 애매한 중간 상태가 함께 섞이기 때문에 자연스러운 현상입니다.
- 그럼에도 `60m` 에서도 `precision@1%` 는 `0.996` 이상을 유지하고 있습니다.

## Horizon 비교

| Horizon | AP | Precision@0.1% | Recall@0.1% | Precision@1% | Recall@1% | Valid Positives | Sampled Valid Rows |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 5m | 0.981053 | 0.995502 | 0.039179 | 0.994052 | 0.391185 | 50,843 | 2,000,796 |
| 15m | 0.972646 | 0.998001 | 0.032363 | 0.995102 | 0.322670 | 61,707 | 2,000,815 |
| 30m | 0.972037 | 0.996502 | 0.028240 | 0.995452 | 0.282103 | 70,609 | 2,000,972 |
| 45m | 0.965921 | 0.998501 | 0.025310 | 0.996002 | 0.252355 | 78,980 | 2,001,067 |
| 60m | 0.959535 | 0.998501 | 0.023320 | 0.996052 | 0.232627 | 85,678 | 2,000,920 |

## 해석

- `5m` 은 가장 선명한 탐지 구간입니다. 실패 시점과 가장 가까운 구간이므로 분리도가 가장 좋고 AP와 재현율이 모두 최고입니다.
- `15m`, `30m` 구간도 여전히 매우 강합니다. 정밀도는 거의 유지되지만 positive 정의가 넓어지면서 재현율이 점차 낮아집니다.
- `45m`, `60m` 에서는 예상대로 AP와 재현율이 더 떨어집니다. 하지만 상위 위험 순위 구간의 정밀도는 여전히 매우 높습니다.
- 모든 horizon의 ranking 품질이 매우 높게 보이는데, 이는 실제 신호가 강한 부분도 있지만 모든 positive을 유지하고 negative을 결정론적으로 다운샘플링한 평가 설계의 영향도 함께 받습니다.

## 샘플링 및 평가 방식

- horizon별 원본 학습 행 수: 약 `307.8M`
- horizon별 원본 검증 행 수: 약 `77.0M`
- horizon별 샘플링된 학습 행 수: 약 `8.0M`
- horizon별 샘플링된 검증 행 수: 약 `2.0M`
- positive 데이터는 모두 유지했습니다.
- negative 데이터는 해시 기반 결정론적 샘플링으로 축소했습니다.
- 검증 분할은 랜덤 셔플이 아니라 `end_time` 기준 시간 분할입니다.

이 방식은 `24 GB` 노트북에서도 학습을 가능하게 만들지만, 현재 precision 수치는 전체 원본 negative 분포를 그대로 통과시킨 운영 환경과 완전히 동일한 의미는 아닙니다.

## 중요 피처 관찰

- `task_age_us` 는 `5`개 horizon의 top-10 중요도 목록에 반복적으로 등장했습니다.
- `event_count` 는 `5`개 horizon의 top-10 중요도 목록에 반복적으로 등장했습니다.
- `observed_failure_by_window` 는 `5`개 horizon의 top-10 중요도 목록에 반복적으로 등장했습니다.
- `scheduling_class` 는 `5`개 horizon의 top-10 중요도 목록에 반복적으로 등장했습니다.
- `collection_recent_failure_count_12` 는 `5`개 horizon의 top-10 중요도 목록에 반복적으로 등장했습니다.
- `collection_recent_terminal_count_12` 는 `5`개 horizon의 top-10 중요도 목록에 반복적으로 등장했습니다.
- `priority` 는 `4`개 horizon의 top-10 중요도 목록에 반복적으로 등장했습니다.
- `usage_window` 는 `4`개 horizon의 top-10 중요도 목록에 반복적으로 등장했습니다.
- `req_cpu` 는 `4`개 horizon의 top-10 중요도 목록에 반복적으로 등장했습니다.
- `avg_mem_to_request_ratio` 는 `3`개 horizon의 top-10 중요도 목록에 반복적으로 등장했습니다.
- `max_mem_to_request_ratio` 는 `2`개 horizon의 top-10 중요도 목록에 반복적으로 등장했습니다.
- `collection_window_avg_cpu_sum` 는 `1`개 horizon의 top-10 중요도 목록에 반복적으로 등장했습니다.

반복적으로 상위에 나타나는 피처들은 현재 모델의 안정적인 핵심 신호로 볼 수 있습니다. 실제로는 보통 다음 범주의 정보가 섞여 있습니다.

- 직접적인 자원 사용량과 utilization
- 태스크 단위의 시간적 변화량
- 머신 단위 집계 부하
- 최근 실패/종료 이력
- 구조적으로 취약한 관측치를 표시하는 missingness indicator

## 남아 있는 리스크

- 현재 fixed-shard slice에서는 `e`, `f`, `g` 클러스터에서 positive 라벨이 전혀 생성되지 않았습니다. 따라서 현재 positive 학습 신호는 사실상 `b`, `c`, `d` 에서만 옵니다.
- 시간 분할 검증은 적절하지만, 여전히 같은 shard 선택 정책 안에서의 평가입니다. 더 깊은 shard 구간이나 다른 기간에 대한 일반화는 아직 검증되지 않았습니다.
- negative 샘플링이 들어가 있으므로 현재 precision 값은 전체 운영 이벤트 스트림에서의 절대 정밀도로 바로 해석하면 안 됩니다.
- 더 긴 horizon에서는 모델 복잡도를 무리하게 올릴 경우 과적합 위험이 커질 수 있습니다.
- 현재 보고서는 calibration curve, cluster holdout, 완전한 교차-클러스터 일반화 검증까지는 포함하지 않습니다.

## 다음 권장 작업

- 현재 진행 중인 early stopping 기반 하이퍼파라미터 탐색을 계속 진행합니다.
- `e`, `f`, `g` 에서 positive이 0개가 된 원인을 shard depth 확대나 다른 shard 선택으로 확인합니다.
- 클러스터별 holdout 비교와 calibration 분석을 추가합니다.
- 튜닝 승자 설정과 현재 운영 설정을 비교한 뒤 기본 파라미터를 승격합니다.

## 참고 아티팩트

- 모델 경로: `~/Documents/borg_xgboost_workspace/models/xgboost`
- 학습 로그: `~/Documents/borg_xgboost_workspace/runtime/logs/20260331041159_advanced_train_resumable.log`
- 현재 핸드오프: `reports/202603310423_advanced_training_completed.md`
