import simpy
import random

from rail_network import RailNetwork
from schema import Node, Edge, Job, Vehicle

DISTANCES = {
    ("STOCKER", "TOOL_A"): 3,
    ("TOOL_A", "STOCKER"): 3,
    ("STOCKER", "TOOL_B"): 5,
    ("TOOL_B", "STOCKER"): 5,
    ("TOOL_A", "TOOL_B"): 4,
    ("TOOL_B", "TOOL_A"): 4,
}

def generate_random_network(max_stockers:int=3, max_ports:int=5, max_junctions:int=2) -> RailNetwork:
    """
    랜덤한 환경(노드, 엣지 정보)을 생성하는 제너레이터
    """
    network = RailNetwork()

    num_stockers = random.randint(1, max_stockers)
    num_tools = random.randint(1, max_ports)
    num_junctions = random.randint(0, max_junctions)

    # add nodes
    coords = set()
    node_types = ["STOCKER", "PORT", "JUNCTION"]
    for type, nodes in enumerate([range(num_stockers), range(num_tools), range(num_junctions)]):
        for i in nodes:
            node_id = f"{node_types[type]}_{i+1}"
            while True:
                coord = (random.randint(0, 30), random.randint(0, 30))
                if coord not in coords:
                    coords.add(coord)
                    break
            network.add_node(Node(id=node_id, type=node_types[type], x=coord[0], y=coord[1]))

    # add edges
    # every nodes should have at least one edge to ensure connectivity
    for from_node in network.nodes.values():
        for _ in range(random.randint(1, len(network.nodes)//2)):
            while True:
                to_node = random.choice(list(set(network.nodes.values())-{from_node}))
                if from_node.id != to_node.id and to_node.id not in network.neighbors(from_node.id):
                    distance = random.randint(1, 10)
                    network.add_edge(Edge(from_id=from_node.id, to_id=to_node.id, distance=distance))
                    break
    return network

'''
# ---- 4. 시뮬레이션 실행 ----
if __name__ == "__main__":
    env = simpy.Environment()
    env.process(vehicle_process(env, "OHT-1", "STOCKER", job))
    env.run()
    print("\n시뮬레이션 종료.")'''

network = generate_random_network()
network.print_network()
