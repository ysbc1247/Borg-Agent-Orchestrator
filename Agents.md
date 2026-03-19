# Multi-Agent System Architecture

This document defines the specialized roles, observation spaces, and reward functions for the three autonomous agents managing the Borg cluster environment.

## 1. The Forecaster Agent (the "Predictor")

**Goal:** Analyze historical time-series data to predict resource spikes or imminent task failures such as OOM or lost tasks.

**Model Type:** LSTM or Temporal Fusion Transformer (TFT).

**Input (State):**

- Window `[T-30, T]` of `avg_cpu`, `max_cpu`, `avg_mem`, `max_mem`
- `priority`
- `scheduling_class`

**Output (Action):** A risk score `P in [0, 1]` representing the probability of failure in the next 15 minutes.

**Reward Function:**

```text
R_f = -(Actual_Failure - Predicted_Failure)^2
```

This can be optimized with mean squared error or log-loss on the failure prediction.

## 2. The Placer Agent (the "Scheduler")

**Goal:** Map incoming tasks to physical machines (`machine_id`) to maximize packing density while avoiding hot nodes.

**Model Type:** Deep Q-Network (DQN) or PPO with masked softmax to ignore full nodes.

**Input (State):**

- Task `req_cpu`, `req_mem`
- Global cluster state as a matrix of per-`machine_id` current utilization
- Forecaster risk scores for existing tasks on candidate nodes

**Output (Action):** A `machine_id` index for placement.

**Reward Function:**

```text
R_p = w1(Cluster_Density) - w2(Node_Fragmentation) - w3(Placement_Latency)
```

## 3. The Evictor Agent (the "Sentinel")

**Goal:** Act as the safety valve. When a node is over-committed and risks a cascade failure, this agent selects the lowest-impact task to terminate.

**Model Type:** Rule-based policy or actor-critic.

**Input (State):**

- Real-time `max_cpu` and `max_mem` per node
- Active tasks on a stressed node
- Task `priority`

**Output (Action):** A `task_id` to terminate, or `null` to do nothing.

**Reward Function:**

```text
R_e = Node_Health_Regained - (Priority_of_Terminated_Task * SLA_Penalty)
```

## Agent Interaction Logic

The control loop is:

1. The Forecaster continuously updates the risk profile of every running task.
2. The Placer uses those risk profiles to avoid placing new tasks on nodes where high-risk tasks are likely to spike.
3. The Evictor monitors node pressure and intervenes if the forecast misses a spike and a node becomes unstable.

## Data Schema Reference (Post-Flattening)

| Column | Agent | Purpose |
| --- | --- | --- |
| `avg_cpu` / `max_cpu` | Forecaster | Primary time-series features |
| `req_cpu` / `req_mem` | Placer | Bin-packing constraints |
| `priority` | Evictor | Primary decision weight for task termination |
| `machine_cpu` | All | Upper bound for normalization |
