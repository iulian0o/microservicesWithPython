# Module 1 — Service Decomposition

**Duration**: 2h in class
**Branch to submit**: `module-01/<team-name>`

---

## Objective

Before writing a single line of code, you need to design the system on paper. Every decision you make here: where to draw service boundaries, who owns what data, how services talk to each other, is hard to reverse once you start coding.

This module is about slowing down and thinking like an architect, not a developer.

Read these two documents before doing anything else:

- `docs/domain.md` — what GameHub is and who uses it
- `docs/specs.md` — the tech stack and key architectural decisions

> The CTO has already laid out the `services/` folder structure. Use it as a starting point, but your job is to **justify** why each folder deserves to be its own service — not just accept it.

---

## Task 1 — Identify bounded contexts _(~40 min)_

A bounded context is a part of the system that has a clear responsibility and owns its data exclusively. No other service should reach into its database.

For each bounded context you identify, fill in the table:

## Iulian ##

| Bounded Context | Responsibilities                                         | Owned Entities  | Team        |
| --------------- | -------------------------------------------------------- | ----------------| ----------- |
| Identity | Manages who users are, handles registration and profiles | User, Session   | Platform    |
| Game Library | Manages the game catalog, genres, search and game metadata | Game, Genre, Tag | Catalog  |
| Activity | Records what users play, follow and rate, serves the social feed | ActivityEvent, Follow, Rating | Social |
| Logging | Stores GDPR consent status, records activity only for opted-in users | ConsentRecord, ActivityLog | Compliance |
| Notification | Delivers alerts via push and email, manages notification preferences | Notification, NotificationPreference | Platform |   


There is no single correct answer: what matters is that you can justify each row.

---

## Task 2 — Define service contracts _(~30 min)_

For each pair of services that need to communicate, define:

- **Direction**: A → B
- **Trigger**: what causes the call
- **Protocol**: REST or event (async)
- **Payload**: key fields exchanged

## Iulian ##

**Flow 1**

- **Direction**: client -> gateway -> auth-service
- **Trigger**: User submits login form
- **Protocol**: REST (synchronous or how it is written) - Client is waiting for the token
- **Payload**: {email, password} -> returns {jwt_token}

**Flow 2**

- **Direction**: activity-service -> logging-service
- **Trigger**: An activity event is recorded
- **Protocol**: RabbitMQ message - activity-service shouldn't wait or fail if logging is slow
- **Payload**: {activity_id, user_id, action, game_id, timestamp}

**Flow 3**

- **Direction**: activity-service -> notification-service
- **Trigger**: A followed froend starts playing
- **Protocol**: Still a RabbitMQ message - Notification dlelivery can be slow so like this the activity write is not blocked
- **Payload**: {email, password} -> returns {jwt_token}

Example:

```
activity-service → logging-service
Trigger: an activity is logged
Protocol: RabbitMQ message (async — why not REST here?)
Payload: { activity_id, user_id, action, game_id, timestamp }
```

Focus on the flows that feel non-obvious. You do not need to document every possible pair.

---

## Task 3 — Draw the service map _(~20 min)_

Draw the full GameHub service map:

- One box per service
- Arrows between services (solid line = synchronous REST, dashed line = async event)
- Label each arrow with its protocol
- One box at the top labelled **gateway** — all client requests enter here, no client ever calls a service directly

This can be a sketch on paper, a whiteboard photo, or ASCII art committed to your branch.

## It is made in DrawIO ##

---

## Discussion _(~15 min)_

Three questions to discuss as a team before you leave:

'''
1. Why does `notification-service` use Node.js instead of Python like the rest? What does that tell you about microservices and technology choices?

- Because microservices have the best tools fot your job. Notification delivery involves holding many open connections and Node.js has the event loop (we did this in Server-side JS) which was built for this. Python would work, but Node.js is more natural here. The key insight is that services are isolated enough that a different language in one place doesn't contaminate the others.


2. What is the risk of `activity-service` calling `logging-service` synchronously — why might you prefer an async event instead?

- If logging-service is slow, or down, activity-service would be blocked waiting or it would fail. Every user action would feel not-user-friendly, and a logging outage would break the entire activity feature. Using an async event instead, activity-service fires the event and moves on immediately. Logging-service processes it when it can. The two services fail independently (unfortunetley).

3. Why does `logging-service` need a GDPR consent check before recording any activity?

- EU law requires that you have the user's explicit consent before tracking their behavior (GDPR class). If you record first and check later, you've already violated the regulation. Logging-service is the gatekeeper: it receives the activity event, checks its own consent table for that user, and only writes the record if consent exists. The consent data lives in logging-service's database and nobody else owns it.

'''
You do not need to write these answers down — they are warm-up for your REFLECTION.md.

---

## Minimum to submit this branch

- [x] Bounded context table filled in (at least 4 services justified)
- [x] At least 3 service contracts defined
- [x] Service map committed (sketch, photo, or ASCII)
- [ ] `REFLECTION.md` completed and committed

The map does not need to be perfect. It needs to be yours.


