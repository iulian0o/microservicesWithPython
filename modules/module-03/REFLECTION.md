# Module 3 — Reflection

**Team name**: Just me
**Branch**: `module-03/iulian`
**Submitted**: After Module 4 lesson unfortunetley 👉👈

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

All client requests now go through the gateway. No client ever calls a service directly.

**Why does that single entry point exist? What would the client's life look like without it?**

Think about what the client would need to know and manage if it talked to each service on its own port.

> *Your answer:* The gateway gives the client a single address to talk to instead of having to know the port and location of every service. Without it the client would need to track which service lives where, handle each service's errors separately, and update its own config every time a service moves or a new one is added.


---

## 2. Your choice

The activity-service makes two outbound calls: one to validate the user (with retry logic), one to fetch game data (with a null fallback if it fails).

**Why are these two calls treated differently? Why does one retry and the other just give up gracefully?**

What is the consequence for the user in each case if the downstream service is unavailable?

> *Your answer:* User validation is a hard requirement and if the user does not exist the activity must not be saved, so it is worth retrying on a transient failure before rejecting the request. Game enrichment is optional, the activity is still valid without it, so a failure just returns null and the user loses the game details but keeps their activity. Retrying enrichment would only slow the response for data that is not critical.


---

## 3. The tradeoff

Every time a client creates an activity, three services are involved synchronously. They all have to be running, healthy, and fast.

**What is the systemic risk of chaining synchronous calls like this?**

What happens to the user experience if the slowest service in the chain takes 3 seconds to respond?

> *Your answer:* If any service in the chain is slow or down the entire request stalls waiting for it. If user-service takes 3 seconds every activity creation takes at least 3 seconds, which the user feels directly as a slow response. One unhealthy service can degrade the whole system even if everything else is working fine.

---

*Keep this file. You will refer back to it during the oral presentation.*
