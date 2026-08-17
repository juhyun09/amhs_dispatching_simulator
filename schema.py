from dataclasses import dataclass
from typing import List, Literal

@dataclass(frozen=True)
class Node:
	id: str
	type: Literal["STOCKER", "PORT", "JUNCTION"]
	x: int
	y: int

@dataclass(frozen=True)
class Edge:
	from_id: str
	to_id: str
	distance: int
	#travel_time: int

@dataclass
class Vehicle:
	id: str
	current_node: str  # Node.id 문자열. Node 객체 자체를 들고 있으면 neighbors()/shortest_path() 등에 id를 넘길 때마다 변환이 필요해져서 문자열로 통일
	status: Literal["IDLE", "MOVING_TO_PICKUP", "LOADING", "MOVING_TO_DROPOFF", "UNLOADING"] = "IDLE"
	assigned_job: str = None
	speed: float = 1.0  # 이동 속도 (m/s)

@dataclass
class Job:
	id: str
	pickup_node: str
	dropoff_node: str
	created_at: float
	priority: Literal["HIGH", "NORMAL", "LOW"] = 'NORMAL'