# AMHS 시뮬레이터 아키텍처 설계 문서 (v1)

## 개요

이산 사건 시뮬레이션(SimPy 기반)으로 팹 내 OHT 반송을 재현한다. 5개 컴포넌트가
느슨하게 결합되며, 각 컴포넌트는 독립적으로 교체·테스트 가능하도록 설계한다.

## 컴포넌트 정의

### 1. Rail Network

| 항목 | 내용 |
|---|---|
| 역할 | 팹 레이아웃을 그래프로 표현. 노드=스토커/툴 포트/분기점, 엣지=레일 구간 |
| 데이터 모델 | `Node(id, type, x, y)` / `Edge(from_id, to_id, distance, travel_time)` |
| 제공 기능 | `shortest_path(a, b) -> List[node_id]`, `neighbors(node_id)` |
| 설계 결정 | v1은 단일 트랙 링 + 지선 구조, 방향성 없는 그래프로 단순화. 트랙 점유 충돌(교착) 처리는 v1에서 제외하고 스트레치 목표로 분리 |

### 2. Job Generator

| 항목 | 내용 |
|---|---|
| 역할 | 반송 요청(job)을 시간에 따라 생성 |
| 데이터 모델 | `Job(id, pickup_node, dropoff_node, created_at, priority=NORMAL)` |
| 생성 방식 | 포아송 프로세스, `arrival_rate`(jobs/min) 파라미터로 제어. pickup/dropoff는 노드 중 랜덤 샘플링(가중치 조정 가능) |
| 설계 결정 | `priority` 필드를 처음부터 넣어두어, 이후 hot lot 우선순위 기능을 스키마 변경 없이 확장 가능하게 함 |

### 3. Vehicle (OHT)

| 항목 | 내용 |
|---|---|
| 역할 | 상태 머신으로 동작하는 반송 차량 에이전트 |
| 상태 전이 | `IDLE → ASSIGNED → MOVING_TO_PICKUP → LOADING → MOVING_TO_DROPOFF → UNLOADING → IDLE` |
| 데이터 모델 | `Vehicle(id, current_node, status, assigned_job, speed)` |
| 설계 결정 | 상태 전이는 SimPy 프로세스(제너레이터)로 구현. 각 전이마다 `yield env.timeout(duration)`으로 시간 경과를 표현하고, 전이 시점에 Metrics Collector에 이벤트 전달 |

### 4. Dispatcher

| 항목 | 내용 |
|---|---|
| 역할 | Job Queue와 idle Vehicle을 매칭하는 정책 컴포넌트 |
| 인터페이스 | `assign(jobs: List[Job], idle_vehicles: List[Vehicle]) -> List[Tuple[Job, Vehicle]]` |
| v1 알고리즘 | nearest-idle-vehicle: 각 job의 pickup_node에서 `shortest_path` 기준 가장 가까운 idle vehicle에 배정 |
| 설계 결정 | 전략 패턴으로 분리(`Dispatcher` 인터페이스 + 구현체 교체)해서, 이후 zone-based(v2)나 priority-aware 알고리즘을 기존 코드 변경 없이 추가 가능하게 함 |

### 5. Metrics Collector

| 항목 | 내용 |
|---|---|
| 역할 | 시뮬레이션 이벤트를 관찰해 성능 지표를 계산 |
| 수집 지표 | 처리량(moves/hour), 평균 반송 시간, 차량 가동률(idle 대비 이동 시간 비율), 정시 배송률 |
| 수집 방식 | Observer 패턴: `job_completed`, `vehicle_state_changed` 등 이벤트 발생 시 콜백으로 기록 → 시뮬레이션 종료 후 집계 함수로 지표 산출 |
| 설계 결정 | 원시 이벤트 로그를 먼저 모두 저장하고, 지표 계산은 별도 후처리 단계로 분리해 새로운 지표를 나중에 추가하기 쉽게 함 |

## 컴포넌트 상호작용 흐름

1. **Job Generator**가 포아송 간격으로 Job을 생성해 Job Queue에 추가
2. **Dispatcher**가 주기적(또는 이벤트 트리거) 으로 Job Queue와 idle Vehicle 목록을 확인해 매칭
3. 매칭된 **Vehicle**이 **Rail Network**의 `shortest_path`로 경로를 계산하고 상태 전이를 시작
4. 상태가 전이될 때마다 **Metrics Collector**가 이벤트를 기록
5. Job이 완료(UNLOADING → IDLE)되면 반송 소요 시간이 확정되어 지표에 반영

```
Job Generator ──▶ Job Queue ──▶ Dispatcher ──▶ Vehicle (FSM)
                                    │                │
                                    ▼                ▼
                             Rail Network      Metrics Collector
                             (경로 계산)         (이벤트 관찰/집계)
```

## v1 범위에서 의도적으로 제외한 것

- 단일 트랙 구간 충돌/교착 방지 (segment locking) → 스트레치 목표
- 우선순위 job(hot lot)의 실제 우선 배차 로직 → 스키마만 준비, 로직은 v2 이후
- AI 에이전트 개입 → 별도 MCP 서버 컴포넌트로 이후 단계에서 연결
