import random
import math
import datetime

from typing import get_args

from schema import Job
from rail_network import RailNetwork


class JobGenerator:
	"""
	Job을 생성하는 클래스. Job은 스토커에서 툴 포트로 이동하는 반송 작업 단위
	"""
	def __init__(self):
		self.job_queue: dict[str, Job] = {}

	def generate_random_jobs(self, network: RailNetwork, num_jobs: int = 5, created_at: float = 0.0) -> list[Job]:
		"""
		이번 주 범위의 기본 경로: pickup/dropoff를 STOCKER/PORT 노드 중에서만 뽑는다.
		Architecture.md 원칙 - JUNCTION은 통과 전용이지 job의 시작/끝이 될 수 없음.

		created_at은 시뮬레이션 시간(env.now)과 같은 축을 써야 한다.
		datetime.now().timestamp()(실제 시계 시각, 유닉스 초)를 쓰면 metrics에서
		duration = completed_at(env.now, 분 단위, 0부터 시작) - created_at(1970년 기준 초 단위)
		를 계산할 때 단위와 기준점이 완전히 어긋나 반송시간이 터무니없는 값이 됨.
		시뮬레이션 시작 시점에 한꺼번에 생성하는 경우 기본값 0.0이면 충분하고,
		실행 중간에 생성한다면 호출 시점의 env.now를 넘겨줘야 한다.
		"""
		if not network.nodes or not network.adjacency:
			raise ValueError("Network is empty. Please generate a network first.")

		valid_nodes = [n.id for n in network.nodes.values() if n.type in ("STOCKER", "PORT")]
		if len(valid_nodes) < 2:
			raise ValueError("STOCKER/PORT 노드가 2개 미만이라 job을 만들 수 없습니다.")

		for i in range(num_jobs):
			pickup, dropoff = random.sample(valid_nodes, 2)
			padding = int(math.log10(max(num_jobs, 1))) + 1

			job_id = f"JOB-{i+1:0{padding}d}"

			priority_options = get_args(Job.__annotations__['priority'])
			priority = random.choice(priority_options)

			job = Job(
				id=job_id,
				pickup_node=pickup,
				dropoff_node=dropoff,
				created_at=created_at,
				priority=priority,
			)
			self.job_queue[job_id] = job
		return list(self.job_queue.values())

	def generate_jobs(self, env, arrival_rate: float, network: RailNetwork):
		"""
		포아송 프로세스로 job을 순차 생성하는 SimPy 제너레이터.
		arrival_rate: 분당 평균 job 발생 건수.
		주의: 향후 단계(자동 생성) 구현이며, 이번 주 범위에서는 사용하지 않음.
		env.process(generate_jobs(...))로 등록해서 무한히 실행하는 프로세스이므로
		단독으로 호출하면 끝나지 않는다.
		"""
		if not network.nodes or not network.adjacency:
			raise ValueError("Network is empty. Please generate a network first.")

		valid_nodes = [n.id for n in network.nodes.values() if n.type in ("STOCKER", "PORT")]

		job_no = 0
		while True:
			interarrival = random.expovariate(arrival_rate)
			yield env.timeout(interarrival)

			job_no += 1
			job_id = f"JOB-{job_no:03d}"

			pickup, dropoff = random.sample(valid_nodes, 2)
			created_at = env.now

			priority_options = get_args(Job.__annotations__['priority'])
			priority = random.choice(priority_options)

			print(f"[t={created_at:.1f}] {job_id} 생성")

			job = Job(
				id=job_id,
				pickup_node=pickup,
				dropoff_node=dropoff,
				created_at=created_at,
				priority=priority,
			)
			self.job_queue[job_id] = job
