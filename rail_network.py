import heapq
import random

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
		a에서 b까지 최단 경로를 노드 ID 리스트로 반환 (다익스트라)
		distance가 동일한 경우, heapq가 튜플의 다음 항목(node_id)으로 비교하므로
		알파벳/문자열 순서상 먼저 오는 쪽이 선택됨 -> "임의 선택"에 대한 결정론적 근사
		경로가 없으면 빈 리스트 반환
		"""
		if a == b:
			return [a]
		if a not in self.nodes or b not in self.nodes:
			raise ValueError(f"Unknown node: {a if a not in self.nodes else b}")

		# dist[node] = a로부터의 최단 거리, prev[node] = 경로 역추적용 이전 노드
		dist = {a: 0}
		prev: dict[str, str] = {}
		visited = set()
		heap = [(0, a)]

		while heap:
			d, node = heapq.heappop(heap)
			if node in visited:
				continue
			visited.add(node)

			if node == b:
				break

			for edge in self.adjacency[node]:
				neighbor = edge.to_id
				new_dist = d + edge.distance
				if neighbor not in dist or new_dist < dist[neighbor]:
					dist[neighbor] = new_dist
					prev[neighbor] = node
					heapq.heappush(heap, (new_dist, neighbor))

		if b not in dist:
			return []  # 도달 불가

		# 역추적으로 경로 복원
		path = [b]
		while path[-1] != a:
			path.append(prev[path[-1]])
		path.reverse()
		return path

	def path_distance(self, path: List[str]) -> int:
		"""
		shortest_path()가 반환한 노드 리스트를 실제 거리(합산 distance)로 환산.
		dispatcher가 '가까운 차량'을 판단할 때 홉 수(len(path))가 아니라
		이 값을 써야 함 - 엣지 가중치가 균일하지 않기 때문.
		"""
		total = 0
		for i in range(len(path) - 1):
			edge = self.get_edge(path[i], path[i + 1])
			if edge is None:
				raise ValueError(f"No edge between {path[i]} and {path[i+1]}")
			total += edge.distance
		return total

	def neighbors(self, node_id: str) -> list[str]:
		"""
		node_id에 인접한 노드 ID 리스트를 반환
		"""
		return [e.to_id for e in self.adjacency[node_id]]

	def generate_random_network(self, max_stockers: int = 3, max_ports: int = 5, max_junctions: int = 2):
		"""
		랜덤한 환경(노드, 엣지 정보)을 생성하는 제너레이터.
		주의: 매 실행마다 레이아웃이 달라져서 디버깅 재현이 어려움.
		개발 중에는 아래 build_reference_layout()을 우선 사용 권장.
		"""

		num_stockers = random.randint(1, max_stockers)
		num_tools = random.randint(1, max_ports)
		num_junctions = random.randint(0, max_junctions)

		# add nodes
		coords = set()
		node_types = ["STOCKER", "PORT", "JUNCTION"]
		for type_idx, count_range in enumerate([range(num_stockers), range(num_tools), range(num_junctions)]):
			for i in count_range:
				node_id = f"{node_types[type_idx]}_{i+1}"
				while True:
					coord = (random.randint(0, 30), random.randint(0, 30))
					if coord not in coords:
						coords.add(coord)
						break
				self.add_node(Node(id=node_id, type=node_types[type_idx], x=coord[0], y=coord[1]))

		# add edges - every node gets at least one edge to keep the graph connected
		for from_node in self.nodes.values():
			for _ in range(random.randint(1, max(1, len(self.nodes) // 2))):
				candidates = [n for n in self.nodes.values() if n.id != from_node.id]
				if not candidates:
					break
				to_node = random.choice(candidates)
				if to_node.id not in self.neighbors(from_node.id):
					distance = random.randint(1, 10)
					self.add_edge(Edge(from_id=from_node.id, to_id=to_node.id, distance=distance))

	def build_reference_layout(self):
		"""
		Architecture.md 설계 앵커: 4개 JUNCTION이 메인 링을 이루고,
		2개 베이(bay)에 각각 STOCKER 1개 + TOOL PORT 2개가 분기로 연결됨.
		총 12노드 (JUNCTION 4 + STOCKER 2 + PORT 6).
		랜덤 생성과 달리 매번 동일해서 디버깅/시연에 적합.
		"""
		self.nodes.clear()
		self.adjacency.clear()

		# 메인 링을 이루는 4개 분기점 (정사각형 배치)
		junctions = [
			Node(id="J1", type="JUNCTION", x=0, y=0),
			Node(id="J2", type="JUNCTION", x=20, y=0),
			Node(id="J3", type="JUNCTION", x=20, y=20),
			Node(id="J4", type="JUNCTION", x=0, y=20),
		]
		for n in junctions:
			self.add_node(n)

		# 링 엣지 (J1-J2-J3-J4-J1)
		ring_edges = [("J1", "J2", 5), ("J2", "J3", 5), ("J3", "J4", 5), ("J4", "J1", 5)]
		for from_id, to_id, dist in ring_edges:
			self.add_edge(Edge(from_id=from_id, to_id=to_id, distance=dist))

		# 베이 A: J1 쪽 지선 - 스토커 1개 + 툴포트 2개
		self.add_node(Node(id="STOCKER_A", type="STOCKER", x=-5, y=-5))
		self.add_node(Node(id="TOOL_A1", type="PORT", x=-8, y=-8))
		self.add_node(Node(id="TOOL_A2", type="PORT", x=-8, y=-2))
		self.add_edge(Edge(from_id="J1", to_id="STOCKER_A", distance=3))
		self.add_edge(Edge(from_id="STOCKER_A", to_id="TOOL_A1", distance=2))
		self.add_edge(Edge(from_id="STOCKER_A", to_id="TOOL_A2", distance=2))

		# 베이 B: J3 쪽 지선 - 스토커 1개 + 툴포트 2개
		self.add_node(Node(id="STOCKER_B", type="STOCKER", x=25, y=25))
		self.add_node(Node(id="TOOL_B1", type="PORT", x=28, y=28))
		self.add_node(Node(id="TOOL_B2", type="PORT", x=28, y=22))
		self.add_edge(Edge(from_id="J3", to_id="STOCKER_B", distance=3))
		self.add_edge(Edge(from_id="STOCKER_B", to_id="TOOL_B1", distance=2))
		self.add_edge(Edge(from_id="STOCKER_B", to_id="TOOL_B2", distance=2))

		# 추가 툴포트 2개를 J2, J4 쪽에도 하나씩 배치해 12노드 채움
		self.add_node(Node(id="TOOL_C1", type="PORT", x=20, y=-5))
		self.add_edge(Edge(from_id="J2", to_id="TOOL_C1", distance=3))

		self.add_node(Node(id="TOOL_C2", type="PORT", x=0, y=25))
		self.add_edge(Edge(from_id="J4", to_id="TOOL_C2", distance=3))

	def print_network(self):
		print("Nodes:")
		for node in self.nodes.values():
			print(f"  {node.id} ({node.type}) at ({node.x}, {node.y})")
		print("Edges:")
		for from_id, edges in self.adjacency.items():
			for edge in edges:
				print(f"  {from_id} -> {edge.to_id} (distance: {edge.distance})")
