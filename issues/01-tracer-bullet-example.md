# Issue 1: [Tracer Bullet — Feature Name, Visible on Dashboard]

**Type:** AFK  
**Blocked by:** none  
**Estimated size:** Medium

---

## Goal

A user can [do the core action] and see [the result] on the dashboard — end-to-end, all layers wired together.

## Layers touched

- [x] Database / schema
- [x] Service / business logic
- [x] API / route
- [x] Frontend / UI

## Acceptance criteria

- [ ] Schema migration runs cleanly
- [ ] Service function exists and is tested
- [ ] Route returns correct data
- [ ] Dashboard shows [visible element] after [user action]

## Implementation notes

- New deep module: `src/services/[feature].ts` — owns all [feature] logic
- Expose interface: `get[Feature]()`, `create[Feature]()`
- Use existing DB client pattern from `src/lib/db.ts`
- Minimal UI — just enough to confirm the flow works end-to-end

## Tests required

- [ ] `[feature].test.ts` — integration test from service interface, using in-memory test DB
- [ ] At minimum: creates a record, retrieves it, verifies shape
