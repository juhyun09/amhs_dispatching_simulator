import simpy

from job_generator import JobGenerator
from dispatcher import Dispatcher
from vehicle import VehicleManager
from metrics_collector import MetricsCollector

from state import NETWORK
from schema import Vehicle


SIM_DURATION = 200  # 시뮬레이션 총 실행 시간 (분 단위, 임의값)


def build_scenario(num_jobs: int = 2, num_vehicles: int = 2):
	"""
	이번 주 범위의 시나리오 구성:
	- 고정 12노드 레퍼런스 레이아웃 사용 (재현 가능해야 디버깅이 쉬움)
	- job은 하드코딩성 랜덤 생성(포아송 자동생성은 다음 단계로 미룸)
	- vehicle 2대를 서로 다른 STOCKER에서 시작
	"""
	NETWORK.build_reference_layout()

	job_gen = JobGenerator()
	jobs = job_gen.generate_random_jobs(NETWORK, num_jobs=num_jobs)

	vehicle_mgr = VehicleManager()
	stocker_ids = [n.id for n in NETWORK.nodes.values() if n.type == "STOCKER"]
	for i in range(num_vehicles):
		start_node = stocker_ids[i % len(stocker_ids)]
		vehicle_mgr.add_vehicle(Vehicle(id=f"OHT-{i+1}", current_node=start_node))

	return jobs, vehicle_mgr


if __name__ == "__main__":
	env = simpy.Environment()

	jobs, vehicle_mgr = build_scenario(num_jobs=2, num_vehicles=2)

	print("=== Rail Network ===")
	NETWORK.print_network()

	print("\n=== Jobs ===")
	for job in jobs:
		print(f"  {job.id}: {job.pickup_node} -> {job.dropoff_node} (priority={job.priority})")

	print("\n=== Vehicles ===")
	for v in vehicle_mgr.vehicles.values():
		print(f"  {v.id} at {v.current_node}")

	dispatcher = Dispatcher()
	metrics = MetricsCollector()

	assignments = dispatcher.assign(jobs, vehicle_mgr.get_idle_vehicles())
	print(f"\n=== Dispatch 결과 ({len(assignments)}건 배정) ===")
	for job, vehicle in assignments:
		print(f"  {job.id} -> {vehicle.id}")

	print("\n=== 시뮬레이션 시작 ===")
	vehicle_mgr.start_all(env, assignments, metrics=metrics)
	env.run(until=SIM_DURATION)

	print("\n시뮬레이션 종료.")
	metrics.print_summary(SIM_DURATION)
