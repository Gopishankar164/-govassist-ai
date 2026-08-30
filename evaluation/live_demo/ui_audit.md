# UI/UX Audit for GovAssist

## Unnecessary Pages
- `Dashboard`: Currently just an intermediate page linking to Assistant and Profile. Redundant.
- `Directory`: A manual browsing page that detracts from the Assistant-first experience.

## Unnecessary Navigation
- Top Navigation: `Directory`, `How It Works`, `About`
- Mobile Navigation: Cluttered with too many links.

## Duplicate Information
- "Official Government Scheme Assistant Tool" and "Secure & Private" banner.
- RAG architecture explanations in `How It Works` and `About` (should be relegated to footer or removed).
- Overly verbose disclaimers duplicated in `Landing` and `About`.

## Distracting Text & Unnecessary Marketing Content
- The `Landing` page has 4 full-width sections explaining how the platform works and who it's for.
- "GovAssist AI Platform" in the header is too corporate.

## Useful Existing Components
- `RecommendationCard.jsx`: Essential for displaying retrieved schemes cleanly.
- `Assistant` Chat interface: The core functionality.
- `Profile` and `Auth` flows.

## Final Recommended Navigation Structure
**Unauthenticated:**
- Home (`/`)
- Assistant (`/assistant`)
- Login
- Create Account

**Authenticated:**
- Assistant (`/assistant`)
- Profile (`/profile`)
- Logout

*(Footer will contain links to How It Works / About for those who still need it without cluttering the main UI).*
