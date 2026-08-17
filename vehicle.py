import random

from typing import List, Tuple

from schema import Vehicle, Job
from state import NETWORK


class VehicleManager:
	"""
	여러 Vehicle을 보유/관리하는 컨테이너.
	(참고: schema.Vehicle은 차량 1대의 데이터, 이 클래스는 차량들의 모음을 다룸 -
	 이전 버전은 두 이름이 겹쳐서 import한 Vehicle을 이 클래스가 덮어쓰는 버그가 있었음)
	"""

	def __init__(self):
		self.vehicles: dict[str, Vehicle] = {}

	def add_vehicle(self, vehicle: Vehicle):
		self.vehicles[vehicle.id] = vehicle

	def get_idle_vehicles(self) -> list[Vehicle]:
		"""
		현재 상태가 IDLE인 Vehicle 리스트를 반환
		"""
		return [v for v in self.vehicles.values() if v.status == "IDLE"]

	def generate_random_vehicles(self, max_vehicles: int = 2):
		num_vehicles = random.randint(1, max_vehicles)
		occupied_nodes = set()
		for i in range(num_vehicles):
			vehicle_id = f"OHT-{i+1}"
			start_node = random.choice(list(set(NETWORK.nodes.keys()) - occupied_nodes))
			occupied_nodes.add(start_node)
			self.vehicles[vehicle_id] = Vehicle(id=vehicle_id, current_node=start_node)

	def vehicle_process(self, env, vehicle: Vehicle, job: Job, metrics=None):
		"""
		SimPy 프로세스: 차량 1대가 job 1건을 수행하는 상태 전이.
		IDLE -> MOVING_TO_PICKUP -> LOADING -> MOVING_TO_DROPOFF -> UNLOADING -> IDLE

		이동 시간 = 경로 총 거리 / 차량 속도 (Architecture.md 원칙:
		좌표(x,y)는 시각화 전용이며, 이동시간은 반드시 그래프 상 shortest_path의
		거리 합산으로 계산한다 - 직선거리/좌표 차이를 쓰지 않는다)
		"""
		vehicle.status = "IDLE"
		current_node = vehicle.current_node
		print(f"[t={env.now:>6.1f}] {vehicle.id}: IDLE at {current_node}")

		vehicle.assigned_job = job.id
		print(f"[t={env.now:>6.1f}] {vehicle.id}: ASSIGNED {job.id} "
			  f"(pickup={job.pickup_node}, dropoff={job.dropoff_node})")

		# --- MOVING_TO_PICKUP ---
		vehicle.status = "MOVING_TO_PICKUP"
		path_to_pickup = NETWORK.shortest_path(current_node, job.pickup_node)
		if not path_to_pickup:
			print(f"[t={env.now:>6.1f}] {vehicle.id}: ERROR - {current_node} -> "
				  f"{job.pickup_node} 경로 없음")
			return
		move_time = NETWORK.path_distance(path_to_pickup) / vehicle.speed
		print(f"[t={env.now:>6.1f}] {vehicle.id}: MOVING_TO_PICKUP "
			  f"({current_node} -> {job.pickup_node}, {move_time:.1f}분, 경로={path_to_pickup})")
		yield env.timeout(move_time)
		current_node = job.pickup_node
		vehicle.current_node = current_node

		# --- LOADING ---
		vehicle.status = "LOADING"
		print(f"[t={env.now:>6.1f}] {vehicle.id}: LOADING at {current_node}")
		yield env.timeout(1)

		# --- MOVING_TO_DROPOFF ---
		vehicle.status = "MOVING_TO_DROPOFF"
		path_to_dropoff = NETWORK.shortest_path(current_node, job.dropoff_node)
		if not path_to_dropoff:
			print(f"[t={env.now:>6.1f}] {vehicle.id}: ERROR - {current_node} -> "
				  f"{job.dropoff_node} 경로 없음")
			return
		move_time = NETWORK.path_distance(path_to_dropoff) / vehicle.speed
		print(f"[t={env.now:>6.1f}] {vehicle.id}: MOVING_TO_DROPOFF "
			  f"({current_node} -> {job.dropoff_node}, {move_time:.1f}분, 경로={path_to_dropoff})")
		yield env.timeout(move_time)
		current_node = job.dropoff_node
		vehicle.current_node = current_node

		# --- UNLOADING ---
		vehicle.status = "UNLOADING"
		print(f"[t={env.now:>6.1f}] {vehicle.id}: UNLOADING at {current_node}")
		yield env.timeout(1)

		# --- 완료, 다시 IDLE ---
		vehicle.status = "IDLE"
		vehicle.assigned_job = None
		print(f"[t={env.now:>6.1f}] {vehicle.id}: IDLE at {current_node} ({job.id} 완료)")

		if metrics is not None:
			metrics.record_job_completed(job, vehicle, env.now)

	def start_all(self, env, assignments: List[Tuple[Job, Vehicle]], metrics=None):
		"""
		dispatcher.assign()이 반환한 (job, vehicle) 매칭 리스트를 받아
		각각을 별도 SimPy 프로세스로 시작
		"""
		for job, vehicle in assignments:
			if not vehicle:
				continue
			env.process(self.vehicle_process(env, vehicle, job, metrics))
