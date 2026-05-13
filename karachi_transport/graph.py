import math

from .nodes import NODES
from .edges import EDGES


class KarachiGraph:

    def __init__(self):

        self.nodes = NODES
        self.adjacency_list = self.build_adjacency_list()

    def build_adjacency_list(self):

        adjacency_list = {node_id: [] for node_id in self.nodes}

        for node_a, node_b, weight in EDGES:

            adjacency_list[node_a].append((node_b, weight))
            adjacency_list[node_b].append((node_a, weight))

        return adjacency_list

    def get_neighbors(self, node_id):

        return self.adjacency_list[node_id]

    def get_node_name(self, node_id):

        return self.nodes[node_id]["name"]

    def get_node_id(self, location_name):

        for node_id, data in self.nodes.items():

            if data["name"].lower() == location_name.lower():
                return node_id

        return None

    def get_coordinates(self, node_id):

        lat = self.nodes[node_id]["lat"]
        lon = self.nodes[node_id]["lon"]

        return (lat, lon)

    def get_edge_weight(self, node_a, node_b):

        for neighbor, weight in self.adjacency_list[node_a]:

            if neighbor == node_b:
                return weight

        return None

    def calculate_path_cost(self, path):

        total_cost = 0

        for i in range(len(path) - 1):

            total_cost += self.get_edge_weight(path[i], path[i + 1])

        return total_cost

    def straight_line_distance(self, node_a, node_b):

        lat1, lon1 = self.get_coordinates(node_a)
        lat2, lon2 = self.get_coordinates(node_b)

        lat1, lon1, lat2, lon2 = map(
            math.radians,
            [lat1, lon1, lat2, lon2]
        )

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1)
            * math.cos(lat2)
            * math.sin(dlon / 2) ** 2
        )

        c = 2 * math.asin(math.sqrt(a))

        radius = 6371

        distance_km = radius * c

        minutes = (distance_km / 25) * 60

        return minutes

    def print_graph_summary(self):

        total_edges = (
            sum(len(neighbors)
            for neighbors in self.adjacency_list.values()) // 2
        )

        print(f"Graph loaded: {len(self.nodes)} nodes")
        print(f"Graph loaded: {total_edges} edges")

        print()

        for node_id, neighbors in self.adjacency_list.items():

            node_name = self.get_node_name(node_id)

            neighbor_names = [
                self.get_node_name(neighbor)
                for neighbor, weight in neighbors
            ]

            print(f"{node_name} -> {neighbor_names}")


if __name__ == "__main__":

    graph = KarachiGraph()

    graph.print_graph_summary()