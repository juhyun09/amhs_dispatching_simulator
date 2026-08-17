class MetricsCollector:
	"""
	처리량(moves/hour), 평균 반송 시간, 차량 가동률(idle 대비 이동 시간 비율), 정시 배송률

	Architecture.md 설계대로 Observer 패턴: 이벤트 발생 시 원시 로그만 쌓아두고,
	집계는 시뮬레이션 종료 후 별도 단계에서 계산한다. 이번 주 범위에서는
	job_completed 기반 지표(평균 반송시간, 처리량)까지만 구현하고,
	가동률/정시배송률은 vehicle_state_changed 이벤트가 필요해 향후 계획으로 남긴다.
	"""

	def __init__(self):
		self.job_events: list[dict] = []  # {job_id, created_at, completed_at, duration}

	def record_job_completed(self, job, vehicle, completed_at: float):
		self.job_events.append({
			"job_id": job.id,
			"vehicle_id": vehicle.id,
			"created_at": job.created_at,
			"completed_at": completed_at,
			"duration": completed_at - job.created_at,
		})

	def average_turnaround_time(self) -> float:
		"""평균 반송 시간 (job 생성 ~ 완료까지, 시뮬레이션 시간 단위)"""
		if not self.job_events:
			return 0.0
		return sum(e["duration"] for e in self.job_events) / len(self.job_events)

	def throughput_per_hour(self, sim_duration_minutes: float) -> float:
		"""처리량 (완료된 job 수 / 시뮬레이션 총 시간(시간 단위))"""
		if sim_duration_minutes <= 0:
			return 0.0
		hours = sim_duration_minutes / 60
		return len(self.job_events) / hours

	def summary(self, sim_duration_minutes: float) -> dict:
		return {
			"completed_jobs": len(self.job_events),
			"average_turnaround_time_min": round(self.average_turnaround_time(), 2),
			"throughput_per_hour": round(self.throughput_per_hour(sim_duration_minutes), 2),
		}

	def print_summary(self, sim_duration_minutes: float):
		s = self.summary(sim_duration_minutes)
		print("\n=== Metrics Summary ===")
		print(f"  완료된 job 수:      {s['completed_jobs']}")
		print(f"  평균 반송 시간:      {s['average_turnaround_time_min']} 분")
		print(f"  처리량:             {s['throughput_per_hour']} moves/hour")
