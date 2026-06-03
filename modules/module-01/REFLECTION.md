## YOU NEED TO COMMIT THIS FILE BEFORE MOVING ON TO THE NEXT MODULE ! 🚨

**feel free to delete this comment**

# Module 1 — Reflection

**Team name**: **Iulian - just me**
**Branch**: `module-01/iulian`
**Submitted**: Unfortuneltey a bit late 👉👈

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

You started from a painful monolith. Now you're splitting it into separate services.

**What concrete problem does that split solve: and for whom?**

Think about it from three angles: the developer who has to change code, the team that has to deploy it, and the user who has to live with its failures. You don't need to cover all three, pick the one that felt most real to you today.

```
It solves a problem for the developer who has to change code.

In a monolith, changing the logging logic means opening the same codebase
that handles login, games, and notifications. You risk breaking something
unrelated every time you deploy.

With separate services, you change one thing, deploy one thing, and nothing
else is at risk.

```
---

## 2. Your choice

Look at your service map. Every arrow between two services is a decision someone made.

**Pick one boundary, one place where you decided service A should not be part of service B. Explain why that line exists.**

What would break, slow down, or become harder to manage if you merged those two services back together?

``` 
The line between activity-service and logging-service.

They both deal with what users do, but for completely different reasons.
activity-service powers the social feed. logging-service exists because of
GDPR — it has to check consent before writing anything down.

If I merged them, a bug in the feed logic could accidentally bypass the
consent check. Two very different responsibilities tangled in one place.
```

---

## 3. The tradeoff

Microservices solve the monolith's problems. But they create new ones.

**Name one thing that was simpler in the monolith and is now harder in your distributed design.**

No need to solve it: just name it honestly. This is exactly the tension the rest of the course is about.

```
In the monolith, "did this user consent AND what did they play today" is
one SQL query joining two tables.

In the distributed design, that data lives in two separate services that
cannot touch each other's database. A simple question became a distributed
systems problem.

I don't have a solution yet — I think that's what the rest of the course
is for.
```

---

_Keep this file. You will refer back to it during the oral presentation._
