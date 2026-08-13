from typing import List, Tuple

from schema import Vehicle, Job


class Dispatcher:
  """
  Job Queue와 idle Vehicle을 매칭하는 정책 컴포넌트
  """
  def assign(jobs: List[Job], idle_vehicles: List[Vehicle]) -> List[Tuple[Job, Vehicle]]:
    pass