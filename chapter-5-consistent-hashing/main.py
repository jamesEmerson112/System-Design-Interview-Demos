import hashlib
import bisect
from typing import List, Dict

class ConsistentHashRing:
    def __init__(self, nodes: List[str] = None, replicas: int = 1):
        self.replicas = replicas
        self.ring = dict()
        self.sorted_keys = []
        self.nodes = set()
        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node: str):
        self.nodes.add(node)
        for i in range(self.replicas):
            virtual_node = f"{node}#{i}"
            key = self._hash(virtual_node)
            self.ring[key] = node
            bisect.insort(self.sorted_keys, key)

    def remove_node(self, node: str):
        self.nodes.discard(node)
        for i in range(self.replicas):
            virtual_node = f"{node}#{i}"
            key = self._hash(virtual_node)
            if key in self.ring:
                del self.ring[key]
                idx = bisect.bisect_left(self.sorted_keys, key)
                if idx < len(self.sorted_keys) and self.sorted_keys[idx] == key:
                    self.sorted_keys.pop(idx)

    def get_node(self, key_str: str) -> str:
        if not self.ring:
            return None
        key = self._hash(key_str)
        idx = bisect.bisect(self.sorted_keys, key) % len(self.sorted_keys)
        return self.ring[self.sorted_keys[idx]]

    def get_assignments(self, keys: List[str]) -> Dict[str, str]:
        return {k: self.get_node(k) for k in keys}

def print_assignments(title: str, assignments: Dict[str, str]):
    print(f"\n{title}")
    print("-" * len(title))
    for k, v in assignments.items():
        print(f"Key '{k}' -> Node '{v}'")
    print()

if __name__ == "__main__":
    # Demo parameters
    nodes = ["NodeA", "NodeB", "NodeC"]
    keys = ["apple", "banana", "cherry", "date", "fig", "grape"]
    ring = ConsistentHashRing(nodes=nodes, replicas=3)

    # Initial assignments
    assignments = ring.get_assignments(keys)
    print_assignments("Initial assignments", assignments)

    # Add a node
    ring.add_node("NodeD")
    assignments_after_add = ring.get_assignments(keys)
    print_assignments("After adding NodeD", assignments_after_add)

    # Show how many keys moved
    moved = sum(assignments[k] != assignments_after_add[k] for k in keys)
    print(f"Keys moved after adding NodeD: {moved}/{len(keys)}\n")

    # Remove a node
    ring.remove_node("NodeB")
    assignments_after_remove = ring.get_assignments(keys)
    print_assignments("After removing NodeB", assignments_after_remove)

    moved_remove = sum(assignments_after_add[k] != assignments_after_remove[k] for k in keys)
    print(f"Keys moved after removing NodeB: {moved_remove}/{len(keys)}")
