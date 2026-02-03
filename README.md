# TapusAI

Initial scaffold for the waitlist/messaging platform. Structure:

- `apps/admin` – admin/host tablet app (Expo)
- `apps/kiosk` – guest-facing kiosk tablet (Expo)
- `apps/guest-web` – guest web/PWA
- `backend` – FastAPI backend
- `packages/core` – shared types and API clients
- `packages/ui` – shared UI components/design tokens
- `packages/config` – shared configs

Next steps:
1. Add Turborepo/Nx workspace config.
2. Scaffold Expo apps and guest web app.
3. Install backend dependencies and run FastAPI health check.
