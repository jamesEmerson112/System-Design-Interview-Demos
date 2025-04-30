# Consistent Hashing: Practical Examples

Consistent hashing is a powerful technique for distributing data or workload across multiple servers, especially when the number of servers can change over time. It minimizes disruption and keeps systems efficient and stable.

## 1. User Session Management (Fullstack)
Assign user sessions to backend servers using consistent hashing. When servers are added or removed, only a small fraction of sessions move, so most users stay logged in.

## 2. Database Sharding (Data)
Distribute customer records across multiple database servers. Consistent hashing ensures that scaling up or down only requires moving a small portion of the data.

## 3. Distributed Caching (Fullstack/Data)
Assign cache keys to cache servers. When a cache server fails or is added, only a few keys are reassigned, minimizing cache misses and keeping the app fast.

---

| Scenario                  | How Consistent Hashing Helps                        |
|---------------------------|----------------------------------------------------|
| User session management   | Keeps most users logged in during server changes    |
| Database sharding         | Minimizes data movement when scaling up/down        |
| Distributed caching       | Reduces cache misses and rebalancing effort        |
