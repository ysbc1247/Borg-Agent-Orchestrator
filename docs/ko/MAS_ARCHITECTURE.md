# Multi-Agent System Architecture

이 문서는 Borg 클러스터 환경을 관리하는 세 개의 자율 에이전트에 대한 전문적인 역할, 관찰 공간 및 보상 기능을 정의합니다.

## 1. 예측 에이전트("예측자")

**목표:** 과거 시계열 데이터를 분석하여 리소스 급증이나 OOM 또는 작업 손실과 같은 임박한 작업 실패를 예측합니다.

**모델 유형:** LSTM 또는 TFT(Temporal Fusion Transformer).

**입력(상태):**

- `avg_cpu`, `max_cpu`, `avg_mem`, `max_mem`의 창 `[T-30, T]`
- `priority`
- `scheduling_class`

**출력(작업):** 다음 15분 동안 실패할 확률을 나타내는 위험 점수 `P in [0, 1]`입니다.

**보상 기능:**

```text
R_f = -(Actual_Failure - Predicted_Failure)^2
```

이는 실패 예측에 대한 평균 제곱 오차 또는 로그 손실로 최적화될 수 있습니다.

## 2. 배치 에이전트("스케줄러")

**목표:** 수신 작업을 물리적 시스템(`machine_id`)에 매핑하여 핫 노드를 방지하면서 패킹 밀도를 최대화합니다.

**모델 유형:** 전체 노드를 무시하기 위해 마스크된 소프트맥스가 있는 DQN(Deep Q-Network) 또는 PPO.

**입력(상태):**

- 과제 `req_cpu`, `req_mem`
- `machine_id` 현재 활용도에 따른 매트릭스로서의 글로벌 클러스터 상태
- 후보 노드의 기존 작업에 대한 예측 위험 점수

**출력(작업):** 배치를 위한 `machine_id` 인덱스입니다.

**보상 기능:**

```text
R_p = w1(Cluster_Density) - w2(Node_Fragmentation) - w3(Placement_Latency)
```

## 3. 퇴거 에이전트("센티넬")

**목표:** 안전 밸브 역할을 합니다. 노드가 과도하게 커밋되어 계단식 오류가 발생할 위험이 있는 경우 이 에이전트는 종료할 영향이 가장 적은 작업을 선택합니다.

**모델 유형:** 규칙 기반 정책 또는 배우 평론가.

**입력(상태):**

- 노드당 실시간 `max_cpu` 및 `max_mem`
- 스트레스를 받은 노드의 활성 작업
- 과제 `priority`

**출력(작업):** 종료하려면 `task_id`, 아무것도 하지 않으려면 `null`입니다.

**보상 기능:**

```text
R_e = Node_Health_Regained - (Priority_of_Terminated_Task * SLA_Penalty)
```

## 에이전트 상호 작용 논리

제어 루프는 다음과 같습니다.

1. Forecaster는 실행 중인 모든 작업의 위험 프로필을 지속적으로 업데이트합니다.
2. 배치자는 이러한 위험 프로필을 사용하여 고위험 작업이 급증할 가능성이 있는 노드에 새 작업을 배치하는 것을 방지합니다.
3. Evictor는 노드 압력을 모니터링하고 예측이 스파이크를 놓치고 노드가 불안정해지면 개입합니다.

## 데이터 스키마 참조(평탄화 후)

| 칼럼 | 에이전트 | Purpose |
| --- | --- | --- |
| `avg_cpu` / `max_cpu` | Forecaster | 기본 시계열 기능 |
| `req_cpu` / `req_mem` | 사금 | 빈 패킹 제약 |
| `priority` | 퇴거자 | 작업 종료에 대한 기본 결정 가중치 |
| `machine_cpu` | 모두 | 정규화의 상한 |