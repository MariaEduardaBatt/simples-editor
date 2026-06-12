# Supabase auth integration — design

## Context
Issue #7 asks for the backend-side Supabase auth foundation. The PRD states that Supabase is the auth provider, the backend must validate JWTs locally, and all protected requests use `Authorization: Bearer <jwt>` except `/api/health`.

This first slice is backend-only. Frontend login wiring and devops changes stay out of scope for this step.

## Goals
- Load Supabase auth environment variables on backend startup.
- Validate Supabase JWTs locally with the project secret.
- Expose a reusable auth guard for protected Flask routes.
- Provide `POST /api/auth/verify` for the frontend to confirm an access token after login.

## Non-goals
- Building the login UI.
- Adding database tables.
- Implementing OAuth providers or magic-link flows.
- Replacing Supabase auth with custom auth.

## Proposed approach
Use a small Flask auth layer with three parts:

1. **Config loading**  
   Read `SUPABASE_URL` and `SUPABASE_JWT_SECRET` from env vars and fail fast if they are missing.

2. **JWT verifier**  
   Parse the `Authorization` header, validate the token signature and expiration with PyJWT, and extract canonical identity claims (`sub` as `user_id`, plus `email` when present).

3. **Decorator + verify endpoint**  
   Expose `@verify_jwt` for protected routes and `POST /api/auth/verify` for the frontend to test a token and receive a normalized response.

## Alternatives considered
- **Global middleware**: simpler for coverage, but too invasive for a repo that is still being bootstrapped.
- **Remote token introspection**: adds network dependency and conflicts with the PRD, which prefers local validation.
- **Helper-only module**: too weak for the issue because it does not give the frontend a concrete verification endpoint.

## Request flow
1. Frontend receives `access_token` from Supabase.
2. Frontend sends `Authorization: Bearer <token>` to the backend.
3. Backend validates the JWT locally.
4. If valid, the backend attaches the decoded identity to request context and returns `200`.
5. If invalid or missing, the backend returns `401` with a small JSON error payload.

## Error handling
- Missing env vars: startup error, no silent fallback.
- Missing/empty bearer token: `401 unauthorized`.
- Invalid signature, expired token, or malformed JWT: `401 unauthorized`.
- Unexpected verifier failure: surface a clear `500` response.

## Tests
- Valid token returns `200` from `POST /api/auth/verify`.
- Missing bearer token returns `401`.
- Expired token returns `401`.
- Invalid signature returns `401`.
- Missing env vars fail backend startup.

## Success criteria
- The backend can validate a Supabase JWT without consulting a database.
- The frontend has a stable verification endpoint to call after login.
- The implementation matches the PRD auth model and keeps the first slice narrow.
