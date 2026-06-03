# Negative Test Catalog — concrete examples

Reusable negative cases for any REST API. Each shows the *attack*, the *expected*
result, and why. Adapt field names to the endpoint under test. Examples assume a
`POST /users` taking `{ "email": string(required), "age": int 0..120, "role": enum }`.

## 1. Missing required field

```http
POST /users
Content-Type: application/json

{ "age": 30 }
```
Expect: **400/422**, error names the missing `email`. NOT 500, NOT a created row.

## 2. Null in a non-nullable field

```json
{ "email": null, "age": 30 }
```
Expect: **400/422**. Null must be rejected distinctly from "missing".

## 3. Empty / whitespace-only string

```json
{ "email": "   ", "age": 30 }
```
Expect: **400/422** (after trim it is empty). Server should trim before storing.

## 4. Wrong type (type confusion)

```json
{ "email": 12345, "age": "thirty" }
```
Expect: **400/422**. No silent coercion of `"thirty"` → 0 or `12345` → "12345".

## 5. Out-of-range / boundary numbers

```json
{ "email": "a@b.com", "age": -1 }     // below min
{ "email": "a@b.com", "age": 121 }    // above max
{ "email": "a@b.com", "age": 99999999999999999999 }  // overflow
```
Expect: **400/422** for each. Test min-1, min, max, max+1 explicitly.

## 6. Invalid format / enum

```json
{ "email": "not-an-email", "age": 30 }
{ "email": "a@b.com", "age": 30, "role": "superadmin" }  // not in enum
```
Expect: **400/422** with the offending field named.

## 7. Over-length string / oversized payload

```json
{ "email": "<100 KB string>", "age": 30 }
```
Expect: **400** (length) or **413 Payload Too Large**. Must not hang or OOM.

## 8. Malformed / truncated JSON

```http
POST /users
Content-Type: application/json

{ "email": "a@b.com", "age":
```
Expect: **400** "invalid JSON". A 500 here is a bug.

## 9. Unknown / extra fields (and mass assignment)

```json
{ "email": "a@b.com", "age": 30, "is_admin": true, "id": "00000000-...", "user_id": "<other user>" }
```
Expect: extra fields ignored OR rejected — and privileged fields (`is_admin`,
`id`, `user_id`, `role`) MUST NOT be writable from the body. This is a mass
assignment vulnerability if accepted.

## 10. Wrong / missing Content-Type

```http
POST /users
Content-Type: text/plain

{ "email": "a@b.com", "age": 30 }
```
Expect: **415 Unsupported Media Type** (or 400). Missing Content-Type on a body
request → also 400/415.

## 11. Wrong HTTP method

```http
DELETE /users        # collection doesn't support DELETE
```
Expect: **405 Method Not Allowed**, with an `Allow` header.

## 12. Auth — missing / malformed / expired

```http
GET /users/me                              # no Authorization header  → 401
Authorization: Bearer garbage              # malformed                 → 401
Authorization: Bearer <expired jwt>        # expired                   → 401
Authorization: Bearer <valid, wrong sig>   # tampered signature        → 401
```
Expect **401** for all. The body must not reveal whether the user exists.

## 13. Authorization — forbidden role

```http
GET /admin/reports
Authorization: Bearer <valid token, role=user>
```
Expect: **403 Forbidden** (authenticated but not allowed). Not 401, not 200.

## 14. BOLA / IDOR (object-level authorization) — the #1 API risk

```http
GET /orders/{id_belonging_to_another_user}
Authorization: Bearer <user A token>
```
Expect: **403 or 404** — never user B's data. Repeat for read, update, delete.
Try sequential/guessable IDs.

## 15. Unknown resource

```http
GET /users/00000000-0000-0000-0000-000000000000
```
Expect: **404**, consistent error shape, no internal detail.

## 16. Injection probes

```json
{ "email": "a@b.com' OR '1'='1", "age": 30 }
{ "email": "<script>alert(1)</script>@b.com", "age": 30 }
{ "email": "../../etc/passwd", "age": 30 }
```
Expect: treated as plain data (validation 400, or stored/escaped safely). NO SQL
error, NO reflected script, NO path traversal.

## 17. Pagination / list abuse

```http
GET /users?limit=-1
GET /users?limit=99999999
GET /users?offset=-5
GET /users?sort=__proto__
```
Expect: bounds enforced (400 or clamped), no full-table dump, no DoS.

## 18. State integrity on failure

Trigger a mutating call that fails partway (e.g. an invalid nested item).
Expect: **the database is unchanged** — no partial write. Then **retry the same
failed call** and confirm it does NOT create a duplicate (idempotency).

## 19. Error-leak check (run on every 4xx/5xx above)

For each error response, assert the body contains **none** of: stack frames,
`Traceback`, SQL text, table/column names, file paths, framework/version
strings, raw exception class names. Error = `{ type, title, status, detail }`
(RFC 9457) or the project's documented shape — and nothing more.

## 20. Contract conformance

Every response (success and error) must validate against the declared OpenAPI/
JSON Schema. A response field missing, renamed, or wrongly typed vs the spec is
**contract drift** and a bug even if the status code is 200.
