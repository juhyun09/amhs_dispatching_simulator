from typing import List
from collections import defaultdict

from schema import Node, Edge

class RailNetwork:
	"""
	팹 레이아웃을 그래프로 표현. 노드=스토커/툴 포트/분기점, 엣지=레일 구간
	"""
	'''
	v1은 단일 트랙 링 + 지선 구조, 방향성 없는 그래프로 단순화. 트랙 점유 충돌(교착) 처리는 v1에서 제외하고 스트레치 목표로 분리
	'''

	def __init__(self):
		self.nodes: dict[str, Node] = {}
		# 인접 리스트: node_id -> list[Edge]
		self.adjacency: dict[str, list[Edge]] = defaultdict(list)

	def add_node(self, node: Node):
		self.nodes[node.id] = node

	def add_edge(self, edge: Edge):
		self.adjacency[edge.from_id].append(edge)
		# 무방향 그래프라고 하셨으니 역방향도 추가
		self.adjacency[edge.to_id].append(
			Edge(edge.to_id, edge.from_id, edge.distance)
		)

	def get_edge(self, from_id: str, to_id: str) -> Edge | None:
		for edge in self.adjacency[from_id]:
			if edge.to_id == to_id:
				return edge
		return None

	def shortest_path(self, a: str, b: str) -> List[str]:
		"""
		a에서 b까지 최단 경로를 노드 ID 리스트로 반환
		"""
		pass

	def neighbors(self, node_id: str) -> list[str]:
		"""
		node_id에 인접한 노드 ID 리스트를 반환
		"""
		return [e.to_id for e in self.adjacency[node_id]]

	def print_network(self):
		print("Nodes:")
		for node in self.nodes.values():
			print(f"  {node.id} ({node.type}) at ({node.x}, {node.y})")
		print("Edges:")
		for from_id, edges in self.adjacency.items():
			for edge in edges:
				print(f"  {from_id} -> {edge.to_id} (distance: {edge.distance})")