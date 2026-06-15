# Module 5 — Reflection

**Team name**: _______________
**Branch**: `module-05/<team-name>`
**Submitted**: before Module 6 lesson

---

## 1. The "why"

The game-service now has two models for the same data: SQLite for writes, Redis for
reads. They store the same games in two different shapes.

**Why go through the trouble of maintaining two representations of the same data?**

> *Your answer:*
SQLite is optimised for reliable, consistent writes — it handles transactions,
constraints, and relationships well. But under high read traffic, every request
hits the same database file with a full query. Redis, by contrast, stores a
pre-computed projection in memory and returns it in microseconds with no query
planning overhead.
If we used the write model for reads at scale, SQLite would become a bottleneck —
thousands of concurrent reads competing with writes on the same file. By maintaining
two representations, we let each model do what it is best at: SQLite owns the truth,
Redis owns the speed. The cost is the extra complexity of keeping them in sync,
which is a deliberate tradeoff we accept in exchange for scalability.

---

## 2. Your choice

The logging-service checks GDPR consent before recording any activity. If a user
has not opted in, the log is silently dropped.

**What does this consent check force you to accept about your data?**

> *Your answer:*
It forces us to accept that our dataset is intentionally incomplete. We will never
have a full picture of user activity — only the activity of users who have opted in.
Any analytics or reporting built on top of this data has a built-in blind spot.
The right place to enforce this rule is inside the logging-service, not at the
gateway or in the activity-service. The gateway does not know what a log entry
is and it just routes requests. The activity-service should not need to know whether
logging is enabled; its job is to record game activity, not to manage consent.
Placing the check in the logging-service keeps the rule close to the data it
protects, and ensures it is enforced regardless of how the service is reached —
whether through the gateway or called directly.

---

## 3. The tradeoff

With CQRS, your write model and read model can drift out of sync — a game is
updated in SQLite but the Redis projection still shows the old data.

**In what scenario does this inconsistency matter? In what scenario is it acceptable?**

> *Your answer:*
> It matters when the user just performed an action and immediately expects to see
> the result. For example: an admin updates a game's title, refreshes the catalogue
> page, and still sees the old title because Redis has not been updated yet. That
> broken feedback loop erodes trust in the system.
>
> It is completely acceptable when the data changes rarely and the user has no
> reason to expect an immediate update — for example, displaying a game's genre or
> platform on a browsing page. A few seconds or even minutes of staleness has no
> real consequence there.
>
> Eventual consistency is never acceptable in systems where correctness is
> safety-critical or legally binding: banking and payment systems (a balance must
> reflect every transaction immediately), medical records (a stale drug dosage
> could cause harm), and inventory systems where overselling has direct financial
> consequences. In these domains, the cost of inconsistency is too high to accept
> any window of drift.

---

*Keep this file. You will refer back to it during the oral presentation.*