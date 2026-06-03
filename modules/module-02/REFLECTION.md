# Module 2 — Reflection

**Team name**: Just me
**Branch**: `module-02/iulian`
**Submitted**: After Module 3 lesson unfortlunetley 👉👈

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

You built a service with distinct layers: models, schemas, repository, service, and routes — each with a single responsibility.

**Why not just put everything in one file and call it done?**

Think about what happens six months later when someone new joins the team, or when you need to swap SQLite for PostgreSQL. What does the layered structure protect you from?

> If everything is in one file, swapping SQLite for PostgreSQL means
digging through HTTP handlers, business logic, and SQL all mixed together.
With layers, I only touch `database.py` and `repository.py` — the rest
doesn't know the database even exists.

---

## 2. Your choice

Each service owns its data exclusively — no other service is allowed to touch its database directly.

**Pick one entity your service owns (e.g. `User`, `Game`). What would go wrong if another service could write to that table directly?**

Give a concrete scenario, not a general principle.

> If another service wrote directly to the `games` table, it could insert
a game with a missing `genre` or a malformed `cover_url` that bypasses
the Pydantic validation in `game-service`. The data would land in the DB
in a broken state and my service would start returning garbage without
any error ever being raised.
---

## 3. The tradeoff

You now have models, schemas, a repository, a service, and routes — five layers for what is essentially a CRUD service.

**For a system this small, what is the cost of all this structure?**

And at what point does the complexity start to pay off? Where is the tipping point?

> For two endpoints it feels like overkill — I wrote five files where one
would have worked. The cost is time and mental overhead just to add a
single field.

It starts paying off the moment a second person touches the code, or when
a test needs to mock just the repository without touching the HTTP layer.
At that point having clear boundaries is worth more than the extra files.

---

*Keep this file. You will refer back to it during the oral presentation.*
