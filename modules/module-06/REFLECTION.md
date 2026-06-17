# Module 6 — Reflection

**Team name**: _______________
**Branch**: `module-06/iulian`
**Submitted**: before Module 7 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

The gateway now validates every JWT before forwarding a request. Individual services no longer need to check identity themselves.

**What does centralising authentication at the gateway buy you?** What would the alternative look like — if every service validated tokens on its own?

Think about what happens when you need to rotate the secret key, or add a new service to the system.

> *Your answer:*

Centralising authentication means every service does not need to import jose, read a SECRET_KEY, or write its own decode logic. The check happens once, at the edge, before a request ever reaches user-service, game-service, or activity-service. If every service validated tokens independently, that logic (and its bugs) would be duplicated N times, and adding a new service would mean re-implementing the same JWT decode block again.
Rotating the secret key shows this clearly. With centralised validation, only the gateway and auth-service need the new key. Without it, every single service would need to be updated and restarted at the same time, or tokens signed with the new key would be rejected by services still holding the old one.
One thing this module made me notice directly: even with centralised gateway validation, game-service still needed its own auth_secret_key to implement require_admin for the DELETE endpoint. So "centralised" here is not absolute — the gateway centralises identity verification (is this token valid), but role enforcement (is this identity allowed to do this specific action) still has to live in the service that owns the resource, because only that service knows what the action means.
---

## 2. Your choice

When activity-service calls user-service internally, it uses a Machine-to-Machine (M2M) token — not a user's token.

**Why can't it just reuse the user's token that arrived in the original request?**

What would break, or what door would you accidentally leave open, if services passed user tokens between themselves?

> *Your answer:*

Reusing the user's token would mean activity-service is acting "as" that user when it talks to user-service, which is not actually true — activity-service is the one making the call, not the gamer. A user's token also carries a user's role (gamer, admin), so passing it along blurs the distinction between "this request originated from a human" and "this request originated from a backend service doing internal work."
The door this leaves open is mostly about scope and lifetime. A user's token expires in 30 minutes and is tied to whatever that specific user is allowed to do. If a service started forwarding user tokens to other services, every downstream service would need to handle arbitrary user roles correctly, and any bug in that chain could let a low-privilege user's token be replayed in a context it was never meant for. An M2M token, by contrast, has a fixed, known role (service) and is something the calling service controls itself, separate from whatever the end user is doing.
While testing this part, I noticed that validate_user and fetch_game in activity-service currently call user-service and game-service directly on their own ports (8001, 8002), not through the gateway. So in the current implementation neither call is actually protected by a token at all — the M2M client in auth_client.py is built and would work if called, but main.py never calls get_auth_headers() before making those requests. The gateway lock only protects the path a client takes through port 8000; calls between services on their own ports bypass it entirely. This was useful to actually see rather than just be told, because it shows the M2M token is not automatically enforced just because it exists in the codebase — it has to be deliberately wired into the outbound call.
---

## 3. The tradeoff

The gateway and the auth-service share the same `SECRET_KEY` to verify tokens without making a network call on every request.

**What is the security risk of sharing this key?** What happens if it leaks?

And what would the alternative look like — verifying tokens by calling auth-service on every request instead? What does that cost you?

> *Your answer:*

The risk is that the secret key is the single point of trust for the entire system. If it leaks, anyone can forge a token with jwt.encode using that same key and any claims they want, including {"role": "admin"}, and every service that trusts that key (gateway, game-service via auth_secret_key) would accept it as genuine. There is no way for the gateway to tell a forged token from a real one — the signature is all it checks.
The alternative is calling auth-service to validate every token, on every request, instead of decoding it locally. That removes the "everyone needs the same secret" problem, since only auth-service would hold the key, but it adds a network round trip to every single request in the system and makes auth-service a hard dependency for every other service to even respond — if auth-service is slow or down, everything else effectively goes down too, even requests that have nothing to do with login.
This is the actual tradeoff: shared-secret/local-verification gets you speed and no extra point of failure per request, at the cost of needing very careful secret management (env vars, not hardcoding, rotating it if it leaks). I ran into a version of this risk by accident during this module — my .env file for game-service ended up with stale or duplicated content from copying between services, and a mismatched or missing setting was enough to break authentication. That made it concrete that this whole system's security is only as good as how carefully the shared secret is kept identical and kept private across every service that needs it.
---

*Keep this file. You will refer back to it during the oral presentation.*
