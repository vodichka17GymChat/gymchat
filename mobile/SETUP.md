# GymChat Mobile — Setup Guide

## Prerequisites

- Node.js 18+
- Expo Go app on your phone (iOS or Android) — install from the App Store / Play Store
- A free Supabase account — [supabase.com](https://supabase.com)

---

## Step 1 — Create your Supabase project

1. Go to [supabase.com](https://supabase.com) and sign in
2. Click **New project**
3. Name it `gymchat`, pick a region close to you, set a database password
4. Wait ~2 minutes for provisioning

---

## Step 2 — Run the database migration

1. In the Supabase dashboard, go to **SQL Editor**
2. Click **New query**
3. Paste the entire contents of `supabase/migrations/001_initial.sql`
4. Click **Run**

This creates all tables, Row Level Security policies, indexes, and seeds the 56-exercise library.

---

## Step 3 — Get your API keys

1. In Supabase, go to **Project Settings → API**
2. Copy:
   - **Project URL** (e.g. `https://abcdefgh.supabase.co`)
   - **anon / public** key (starts with `eyJ...`)

---

## Step 4 — Configure the app

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```
EXPO_PUBLIC_SUPABASE_URL=https://your-project-ref.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

---

## Step 5 — Install dependencies and run

```bash
npm install
npm start
```

Expo will print a QR code. Scan it with the **Expo Go** app on your phone.

The app will open with the login screen. Create an account — Supabase handles auth automatically.

---

## Development workflow

| Command | What it does |
|---|---|
| `npm start` | Start Expo dev server (scan QR with Expo Go) |
| `npm run web` | Run in browser (limited native features) |
| `npm run android` | Open Android emulator (requires Android Studio) |
| `npm run ios` | Open iOS simulator (requires Xcode on macOS) |

---

## Project structure

```
mobile/
  app/
    _layout.tsx          # Root layout — auth guard, safe area
    (auth)/
      login.tsx          # Login screen
      register.tsx       # Register screen
    (tabs)/
      _layout.tsx        # Tab bar
      index.tsx          # Dashboard (home)
      workout.tsx        # Active workout logging
      history.tsx        # Past session history
      profile.tsx        # User profile and settings
  components/
    ui/                  # Text, Button, Input, Card
  constants/
    theme.ts             # Colors, spacing, typography
    config.ts            # App constants (workout types, goals, etc.)
  hooks/
    useAuth.ts           # Supabase auth state hook
  lib/
    supabase.ts          # Supabase client
    types.ts             # TypeScript types for all DB tables
  supabase/
    migrations/
      001_initial.sql    # Full schema — run this in Supabase SQL Editor
```

---

## Troubleshooting

**"Cannot connect to Supabase"** — Check that your `.env` values are correct and the file is saved. Restart the Expo server after changing `.env`.

**"Table does not exist"** — The migration hasn't been run yet. Complete Step 2.

**"Row Level Security error"** — You're trying to access another user's data. This is expected behavior — each user can only see their own workouts.

**QR code not working** — Make sure your phone and computer are on the same Wi-Fi network.
