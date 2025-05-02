"""
User Session Management Demo with Consistent Hashing

This script generates random session data for 50 users, mimicking what might be stored in a real web application's session store.

DESIGN:
To start with a User Session Management (Fullstack) demo using consistent hashing, here’s a step-by-step plan:

1. Define the Scenario

Imagine a web application with multiple backend servers.
Each user’s session data needs to be stored on one of these servers.
We want to use consistent hashing to assign each user to a server, so that if servers are added or removed, only a small number of users are affected (i.e., need to log in again).
2. Identify the Key Components

Users: Each with a unique user ID (e.g., email, username, or UUID).
Servers: A list of backend servers (e.g., ServerA, ServerB, ServerC).
Consistent Hash Ring: The mechanism to map user IDs to servers.
3. Plan the Demo Steps

Create a list of sample users (user IDs).
Create a list of backend servers.
Use a consistent hashing implementation to assign each user to a server.
Simulate adding or removing a server, and show which users are affected (i.e., whose sessions would move).
4. Decide on Output

Print a table showing user-to-server assignments before and after server changes.
Highlight or count how many users are affected by the change.
5. (Optional) Visualize or Extend

Optionally, visualize the hash ring or show a percentage of users affected.
You could also simulate session data being moved.

"""

import uuid
import random
from datetime import datetime, timedelta, timezone
import hashlib
import bisect
from typing import List, Dict

# Step 1: Create a list of 50 users (user1, user2, ..., user50)
users = [f"user{i+1}" for i in range(50)]

# Step 1b: Create a list of backend servers named after Greek alphabet (up to Zeta)
servers = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta"]

# Step 2: Define possible values for session fields
themes = ["light", "dark"]
languages = ["en", "es", "fr", "de", "zh"]
roles_list = [
    ["user"],
    ["user", "premium"],
    ["user", "admin"],
    ["user", "moderator"],
    ["user", "premium", "admin"]
]
item_ids = [f"item{n}" for n in range(1, 101)]

def random_session(user_id):
    """
    Generate a random session dictionary for a given user_id.

    The session includes:
    - session_id: Unique session identifier (UUID4)
    - user_id: The user's ID
    - is_authenticated: Randomly True or False
    - created_at: Random creation time within the last 2 hours
    - last_accessed: Random time after creation
    - expires_at: Random expiry 1-4 hours after last access
    - preferences: Random theme and language
    - cart: 0-3 random item IDs
    - csrf_token: Random UUID4 for CSRF protection
    - roles: Random selection of user roles
    """
    now = datetime.now(timezone.utc)
    created_at = now - timedelta(minutes=random.randint(0, 120))
    last_accessed = created_at + timedelta(minutes=random.randint(0, 120))
    expires_at = last_accessed + timedelta(hours=random.randint(1, 4))
    return {
        "session_id": str(uuid.uuid4()),
        "user_id": user_id,
        "is_authenticated": random.choice([True, False]),
        "created_at": created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "last_accessed": last_accessed.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "expires_at": expires_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "preferences": {
            "theme": random.choice(themes),
            "language": random.choice(languages)
        },
        "cart": random.sample(item_ids, random.randint(0, 3)),
        "csrf_token": str(uuid.uuid4()),
        "roles": random.choice(roles_list)
    }

# Step 3: Generate session data for all users
sessions = [random_session(user) for user in users]

# Consistent Hashing Implementation
class ConsistentHashRing:
    """
    Consistent Hash Ring for mapping keys (user IDs) to nodes (servers).
    """
    def __init__(self, nodes: List[str] = None, replicas: int = 3):
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

if __name__ == "__main__":
    # Print all generated session data
    print("Sample session data for 50 users:\n")
    for session in sessions:
        print(session)

    # Assign users to servers using consistent hashing (no virtual nodes, replicas=1)
    ring = ConsistentHashRing(nodes=servers, replicas=1)
    assignments = ring.get_assignments(users)
    print("\nUser-to-server assignments (initial, no virtual nodes):")
    for user, server in assignments.items():
        print(f"{user} -> {server}")

    # Simulate adding a server ("Eta")
    ring.add_node("Eta")
    assignments_after_add = ring.get_assignments(users)
    moved_add = [user for user in users if assignments[user] != assignments_after_add[user]]
    print("\nAfter adding server 'Eta':")
    print(f"Users whose assigned server changed: {len(moved_add)}/{len(users)}")
    for user in moved_add:
        print(f"{user}: {assignments[user]} -> {assignments_after_add[user]}")

    # Simulate removing a server ("Beta")
    ring.remove_node("Beta")
    assignments_after_remove = ring.get_assignments(users)
    moved_remove = [user for user in users if assignments_after_add[user] != assignments_after_remove[user]]
    print("\nAfter removing server 'Beta':")
    print(f"Users whose assigned server changed: {len(moved_remove)}/{len(users)}")
    for user in moved_remove:
        print(f"{user}: {assignments_after_add[user]} -> {assignments_after_remove[user]}")
