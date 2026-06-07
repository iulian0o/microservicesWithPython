# Module 4 — Reflection

**Team name**: _______________
**Branch**: `module-04/<team-name>`
**Submitted**: before Module 5 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

In Module 3, services called each other directly over HTTP. Now activity-service drops a message into a broker and moves on — it never waits for a reply.

**What does the activity-service gain by not waiting? And what does the notification-service gain by consuming at its own pace?**

Think about what happens under load, or when notification-service is temporarily down.

> *Your answer:* The activity is still saved and the HTTP request returns 201. The publisher wraps
the RabbitMQ call in a *try except*, if the broker is unreachable it logs the error
and moves on. The message is lost in that case, but the core operation (saving the
activity) is not affected.

---

## 2. Your choice

In Module 3 you already knew how to call another service directly over HTTP — you did it for user validation and game enrichment.

**Why not use the same approach for notifications? What does introducing a broker give you that a direct HTTP call doesn't?**

Think about what happens if notification-service is slow, or crashes mid-message.

> *Your answer:* A direct HTTP call would make activity creation wait for notification-service to
respond. If notification-service is slow or down, the activity request fails too.
With RabbitMQ, activity-service drops the message and continues — the two services
are decoupled. Notification-service can even be down and catch up when it restarts.

---

## 3. The tradeoff

With synchronous REST, you get an immediate answer: success or failure. With async messaging, the activity is saved and the message is sent — but you have no idea if the notification was ever delivered.

**How would a user know if their notification was never sent? How would you know as a developer?**

What visibility do you lose when you go async?

> *Your answer:* With a synchronous call you get an immediate success or failure response. With async
messaging you have no confirmation the notification was delivered or processed. If
notification-service crashes after receiving the message but before storing it, you
won't know. You need the RabbitMQ management UI or logging to observe what happened.

---

*Keep this file. You will refer back to it during the oral presentation.*
