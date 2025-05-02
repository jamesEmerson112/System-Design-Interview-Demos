"""
User Session Management Demo with Consistent Hashing (No Virtual Nodes, Interactive)

This script generates random session data for 50 users and assigns them to backend servers using consistent hashing
with no virtual nodes (replicas=1). You can interactively add or remove servers and see which users are affected.
"""

# ==================================================================
#  SECTION: Imports and Data Setup
# ==================================================================

import uuid
import random
from datetime import datetime, timedelta, timezone
import hashlib
import bisect
from typing import List, Dict

# Step 1: Create a list of 50 users (user1, user2, ..., user50)
users = [f"user{i+1}" for i in range(50)]

# Step 1b: Initial backend servers (Greek alphabet up to Zeta)
initial_servers = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta"]

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

# ==================================================================
#  SECTION: Consistent Hash Ring Implementation
# ==================================================================

# Step 3: Generate session data for all users
sessions = [random_session(user) for user in users]

class ConsistentHashRing:
    """
    Minimal Consistent Hash Ring for mapping keys (user IDs) to servers.
    No virtual nodes: each server has only one position on the ring.
    """
    def __init__(self, servers: List[str]):
        self.ring = dict()
        self.sorted_keys = []
        for server in servers:
            key = self._hash(server)
            self.ring[key] = server
            self.sorted_keys.append(key)
        self.sorted_keys.sort()

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def get_server(self, key_str: str) -> str:
        # --------------------------------------------------------------
        # Assign a key (e.g., user ID) to a server on the hash ring.
        # Steps:
        # 1. Hash the key to get its position on the ring.
        # 2. Find the first server clockwise from that position.
        # 3. If past the last server, wrap around to the first.
        # --------------------------------------------------------------
        if not self.ring:
            return None

        # Hash the key to get its position on the ring
        key_hash = self._hash(key_str)

        # Find the index of the first server whose position is >= key_hash
        insert_index = bisect.bisect(self.sorted_keys, key_hash)

        # If key_hash is greater than all server positions, wrap around to the first server
        server_index = insert_index % len(self.sorted_keys)

        # Get the server at the found position
        server_hash = self.sorted_keys[server_index]
        assigned_server = self.ring[server_hash]

        return assigned_server

    def get_assignments(self, keys: List[str]) -> Dict[str, str]:
        return {k: self.get_server(k) for k in keys}

# ==================================================================
#  SECTION: CLI Utilities and Main Loop
# ==================================================================

def print_assignments(assignments: Dict[str, str]):
    # Print the mapping of users to servers.
    print("\nUser-to-server assignments:")
    for user, server in assignments.items():
        print(f"{user} -> {server}")

def print_moved_users(old_assignments, new_assignments):
    # Print users whose assigned server changed after a ring update.
    moved = [user for user in old_assignments if old_assignments[user] != new_assignments[user]]
    print(f"\nUsers whose assigned server changed: {len(moved)}/{len(old_assignments)}")
    for user in moved:
        print(f"{user}: {old_assignments[user]} -> {new_assignments[user]}")

def main():
    # Main interactive CLI loop for adding/removing servers and showing assignments.
    servers = initial_servers.copy()
    prev_assignments = None

    while True:
        print("\nCurrent servers:", servers)
        print("Choose an action:")
        print("1. Add server")
        print("2. Remove server")
        print("3. Show assignments")
        print("4. Exit")
        choice = input("> ").strip()

        if choice == "1":
            name = input("Enter server name to add: ").strip()
            if name in servers:
                print(f"Server '{name}' already exists.")
                continue
            servers.append(name)
            ring = ConsistentHashRing(servers)
            new_assignments = ring.get_assignments(users)
            if prev_assignments:
                print_moved_users(prev_assignments, new_assignments)
            else:
                print_assignments(new_assignments)
            prev_assignments = new_assignments

        elif choice == "2":
            name = input("Enter server name to remove: ").strip()
            if name not in servers:
                print(f"Server '{name}' does not exist.")
                continue
            servers = [s for s in servers if s != name]
            if not servers:
                print("No servers left!")
                prev_assignments = None
                continue
            ring = ConsistentHashRing(servers)
            new_assignments = ring.get_assignments(users)
            if prev_assignments:
                print_moved_users(prev_assignments, new_assignments)
            else:
                print_assignments(new_assignments)
            prev_assignments = new_assignments

        elif choice == "3":
            ring = ConsistentHashRing(servers)
            assignments = ring.get_assignments(users)
            print_assignments(assignments)
            prev_assignments = assignments

        elif choice == "4":
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()
