from typing import List, Tuple

from schema import Vehicle, Job
from state import NETWORK


class Dispatcher:
	"""
	Job Queue와 idle Vehicle을 매칭하는 정책 컴포넌트
	"""
	def assign(self, jobs: List[Job], idle_vehicles: List[Vehicle]) -> List[Tuple[Job, Vehicle]]:
		"""
		nearest-idle-vehicle: 각 job의 pickup_node에서 shortest_path 기준
		가장 가까운(실제 거리 기준) idle vehicle에 배정.
		한 차량이 여러 job에 동시 배정되지 않도록 배정된 차량은 후보에서 제외한다.
		TODO: 여러 차량이 있을 때 job priority 기반으로 배정 순서 조정
		"""
		matches = []
		available = list(idle_vehicles)

		for job in jobs:
			if not available:
				break  # 남은 idle 차량이 없으면 이번 배정 사이클에서는 대기

			closest_vehicle = None
			min_distance = float('inf')
			for vehicle in available:
				path = NETWORK.shortest_path(job.pickup_node, vehicle.current_node)
				if not path:
					continue  # 도달 불가능한 차량은 후보에서 제외
				distance = NETWORK.path_distance(path)
				if distance < min_distance:
					min_distance = distance
					closest_vehicle = vehicle

			if closest_vehicle is None:
				continue  # 이 job에 배정 가능한 차량이 없음

			closest_vehicle.assigned_job = job.id
			available.remove(closest_vehicle)
			matches.append((job, closest_vehicle))

		return matches
