# GovAssist Original Architecture Audit

## Original Frontend Pages
- `Landing`: Main marketing page with "Find My Schemes" CTA.
- `Assistant`: The core scheme discovery interface (currently single-turn form with textarea).
- `Details`: Deep-dive view for a single scheme.
- `Dashboard`: User portal linking to Assistant and Profile.
- `Profile`: Form to manage user demographics (`age`, `gender`, `state`, `education`, `occupation`, `income`, `caste_category`).
- `Auth`: Handles Login and Registration flows.
- `Directory`: Basic scheme search directory.
- `HowItWorks` & `About`: Informational pages.

## Original Navigation
- Managed via `react-router-dom` in `App.jsx`.
- Standard Navbar/Sidebar (implemented in `Layout.jsx`).
- Routing is preserved; `Auth`, `Dashboard`, and `Profile` use `ProtectedRoute`.

## Original Login/Signup Flow
- Handled by `Auth` component in `Pages.jsx`.
- Frontend calls `login()` or `register()` from `api/client.js`.
- Token is stored in `localStorage('govassist-access-token')`.
- On successful login/signup, redirects to `/dashboard`.

## Original API Endpoints (Backend)
- `POST /api/auth/register`: Creates new user.
- `POST /api/auth/login`: Returns bearer token.
- `POST /api/auth/logout`: Invalidates token.
- `GET /api/auth/me`: Validates session.
- `GET /api/user/profile`: Fetches demographic info.
- `PUT /api/user/profile`: Updates demographic info.
- `POST /api/recommend`: Accepts `{ "query": "..." }`, returns RAG recommendations.
- `GET /api/schemes/{scheme_id}`: Scheme details.

## Current Chat Flow
- **Not a chat flow yet.** It is a single-turn form:
  1. User types in `<textarea>`.
  2. Submits.
  3. `recommend()` API is called.
  4. Response replaces previous `data`.
  5. UI displays `data.grounded_answer` and maps over `data.recommendations`.

## Current Memory Flow
- **None exists.** The `/api/recommend` endpoint is completely stateless regarding conversation turns.
- Only long-term memory exists in the form of the `UserProfile` stored in SQLite database.

## What Changed Previously (From User Feedback)
- A previous attempt completely redesigned the UI to look like ChatGPT.
- It broke the Auth routing and styling.
- It destroyed the visual identity of the GovAssist app.

## What Must NOT Be Changed
- The styling (`shell`, `bg-govlight`, `text-govnavy`).
- The routing and layout structure.
- The `Auth` flow and database schema.
- The `Profile` and `Dashboard` flows.
- The existing FAISS index and underlying RAG model.
