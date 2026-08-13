"""
AMHS 시뮬레이터 - Step 1: 최소 동작 예시

<<<<<<< HEAD
노드 3개, 차량 1대, job 1개를 하드코딩해서
"시뮬레이션이 한 바퀴 도는지"만 확인하는 것이 이 파일의 유일한 목표입니다.
일반화(그래프 파일 읽기, job 자동 생성, 차량 여러 대, dispatcher)는 다음 단계에서 합니다.
"""

import simpy

# ---- 1. Rail Network (하드코딩된 최소 그래프) ----
# 노드: STOCKER(시작점), TOOL_A, TOOL_B
# 값은 편의상 "이동 시간(분)"으로 취급합니다.
DISTANCES = {
    ("STOCKER", "TOOL_A"): 3,
    ("TOOL_A", "STOCKER"): 3,
    ("STOCKER", "TOOL_B"): 5,
    ("TOOL_B", "STOCKER"): 5,
    ("TOOL_A", "TOOL_B"): 4,
    ("TOOL_B", "TOOL_A"): 4,
}


def travel_time(a, b):
    return DISTANCES[(a, b)]


# ---- 2. Job (하드코딩된 요청 1건) ----
job = {
    "id": "JOB-001",
    "pickup": "TOOL_A",
    "dropoff": "TOOL_B",
}


# ---- 3. Vehicle (상태 머신을 SimPy 프로세스로 표현) ----
def vehicle_process(env, name, start_node, job):
    """
    상태 전이: IDLE -> MOVING_TO_PICKUP -> LOADING
             -> MOVING_TO_DROPOFF -> UNLOADING -> IDLE
    """
    current_node = start_node
    print(f"[t={env.now:>5.1f}] {name}: IDLE at {current_node}")

    print(f"[t={env.now:>5.1f}] {name}: ASSIGNED {job['id']} "
          f"(pickup={job['pickup']}, dropoff={job['dropoff']})")

    move_time = travel_time(current_node, job["pickup"])
    print(f"[t={env.now:>5.1f}] {name}: MOVING_TO_PICKUP "
          f"({current_node} -> {job['pickup']}, {move_time}분)")
    yield env.timeout(move_time)
    current_node = job["pickup"]

    print(f"[t={env.now:>5.1f}] {name}: LOADING at {current_node}")
    yield env.timeout(1)

    move_time = travel_time(current_node, job["dropoff"])
    print(f"[t={env.now:>5.1f}] {name}: MOVING_TO_DROPOFF "
          f"({current_node} -> {job['dropoff']}, {move_time}분)")
    yield env.timeout(move_time)
    current_node = job["dropoff"]

    print(f"[t={env.now:>5.1f}] {name}: UNLOADING at {current_node}")
    yield env.timeout(1)

    print(f"[t={env.now:>5.1f}] {name}: IDLE at {current_node} "
          f"({job['id']} 완료)")


# ---- 4. 시뮬레이션 실행 ----
if __name__ == "__main__":
    env = simpy.Environment()
    env.process(vehicle_process(env, "OHT-1", "STOCKER", job))
    env.run()
    print("\n시뮬레이션 종료.")