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
	current_node: str
	status: str
	assigned_job: str = None
	speed: float = 1.0  # 이동 속도 (m/s)

@dataclass
class Job:
	id: str
	pickup_node: str
	dropoff_node: str
	created_at: float
	priority: str = 'NORMAL'