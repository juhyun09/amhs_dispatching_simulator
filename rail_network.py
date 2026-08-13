from typing import List

class RailNetwork:
  """
  팹 레이아웃을 그래프로 표현. 노드=스토커/툴 포트/분기점, 엣지=레일 구간
  """
  '''
  v1은 단일 트랙 링 + 지선 구조, 방향성 없는 그래프로 단순화. 트랙 점유 충돌(교착) 처리는 v1에서 제외하고 스트레치 목표로 분리
  '''

  DISTANCES = {
    ("STOCKER", "TOOL_A"): 3,
    ("TOOL_A", "STOCKER"): 3,
    ("STOCKER", "TOOL_B"): 5,
    ("TOOL_B", "STOCKER"): 5,
    ("TOOL_A", "TOOL_B"): 4,
    ("TOOL_B", "TOOL_A"): 4,
  }

  

  def shortest_path(a: int, b: int) -> List[int]:
    """
    a에서 b까지 최단 경로를 노드 ID 리스트로 반환
    """
    pass

  def neighbors(node_id: int) -> List[int]:
    """
    node_id에 인접한 노드 ID 리스트를 반환
    """
    pass