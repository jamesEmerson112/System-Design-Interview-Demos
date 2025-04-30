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

if __name__ == "__main__":
    # Print all generated session data
    print("Sample session data for 50 users:\n")
    for session in sessions:
        print(session)
