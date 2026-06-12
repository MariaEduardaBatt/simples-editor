# Issue 8 — Login screen frontend design

## Context

Issue 8 asks for a real login screen so the user can enter the IDE. The PRD defines Supabase as the auth provider, requires email/password login, and says a successful login must persist the session and unlock access to the application.

This work is frontend-only. The login screen must not depend on any additional backend changes to work.

## Goals

- Create a `frontend/` app using React + Tailwind CSS.
- Provide a real email/password login form backed by Supabase Auth.
- Persist the authenticated session across reloads.
- Gate the main app behind authentication.
- Provide a logout action from the protected area.

## Non-goals

- Monaco editor integration.
- xterm.js terminal integration.
- Compile/run flows.
- Saving user code or session history.
- Reworking backend auth.

## Proposed approach

Use a small Vite-based React app with three auth-focused layers:

1. **Supabase client setup**  
   Initialize the browser client from `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`. Let Supabase handle session persistence.

2. **Auth state provider**  
   Build a lightweight auth context/hook that reads the current session on startup, subscribes to auth changes, and exposes `session`, `user`, `loading`, `signIn`, and `signOut`.

3. **Route protection**  
   Add a `/login` route and a protected app route. Unauthenticated users are redirected to `/login`; authenticated users land on the app shell.

## User flow

1. User opens the app.
2. If no session exists, the app redirects to `/login`.
3. The login screen accepts email and password.
4. On success, Supabase stores the session and the app navigates to the protected shell.
5. If the user refreshes the page, the stored session is restored and access remains unlocked.
6. The protected shell shows a logout action that clears the session and returns the user to `/login`.

## UI behavior

- The login form has email and password fields, a submit button, and inline error feedback.
- The submit button is disabled while the request is in flight.
- Empty or invalid input is blocked before submission.
- Authentication failures show a clear message without losing the typed email.
- The protected shell is intentionally minimal for this issue; it only confirms successful access and leaves editor/terminal surfaces for later issues.

## Error handling

- Missing Supabase env vars fail fast during app bootstrap.
- Invalid credentials show an inline login error.
- Network or unexpected auth errors show a generic failure message.
- While the session is loading, the app keeps a neutral loading state instead of flashing the wrong route.

## Testing

- Render the login screen and verify both fields and the submit action exist.
- Reject empty form submission.
- Verify a successful login transitions to the protected shell.
- Verify an existing session bypasses `/login`.
- Verify logout clears the session and returns to `/login`.

## Success criteria

- A user can log in with email and password.
- The session survives reloads.
- Unauthenticated users cannot access the protected app shell.
- The implementation stays narrow and does not pull editor or terminal behavior into issue 8.
