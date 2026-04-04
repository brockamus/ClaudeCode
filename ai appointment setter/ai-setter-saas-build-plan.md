# AI Appointment Setter SaaS — Claude Code Build Plan

## Project Overview

Build a multi-tenant SaaS ("Konversly AI Setter") that completely replaces the GoHighLevel automation stack for AI SMS/IG appointment setting. Instead of building GHL workflows per client, an agency operator provisions a client account in this SaaS, pastes in their GHL API key, and the platform handles all conversation logic, memory, follow-up sequencing, and message sending via the GHL API directly.

**The only thing left in GHL:** A single inbound webhook trigger per channel (SMS, Instagram, etc.) pointing to this SaaS. No multi-step automations. No blueprints to import.

---

## Core Logic This SaaS Replaces

| Old GHL Automation | SaaS Equivalent |
|---|---|
| AI Setter Multi-Text Aggregator | Message aggregation queue (60s window per contact) |
| User response counter | Supabase contact_state table |
| Follow-up counter (max 4) | Supabase follow_up_counter field |
| Make.com router + datastore | Supabase conversation_memory table |
| AI Assistant module | Claude API call with full conversation history |
| AI Response field update | GHL API direct message send |
| NULL detection → stop automations | SaaS opt-out handler |
| 23-hour follow-up wait | SaaS scheduled follow-up job (pg_cron or BullMQ) |
| Tag-based exclusion (call booked) | Supabase exclusion_tags list per account |

---

## Tech Stack

- **Runtime:** Node.js 20+ with TypeScript
- **Framework:** Express.js (lean, Claude Code friendly)
- **Database:** Supabase (Postgres + pg_cron for scheduled follow-ups)
- **Queue/Aggregation:** BullMQ + Redis (message aggregation window)
- **AI:** Anthropic Claude API (`claude-sonnet-4-20250514`)
- **GHL Integration:** GHL REST API v2 (send messages, read/write contact fields)
- **Auth/Multi-tenant:** Supabase Auth + Row Level Security
- **Dashboard UI:** React + Vite (operator dashboard for provisioning clients)
- **Hosting Target:** Railway or Render (one-click deploy)

---

## Database Schema (Supabase)

```sql
-- Tenant accounts (agency operator or sub-account)
CREATE TABLE accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  ghl_location_id TEXT NOT NULL UNIQUE,
  ghl_api_key TEXT NOT NULL,         -- GHL private integration key
  ai_system_prompt TEXT NOT NULL,    -- The AI persona/instructions
  follow_up_max INT DEFAULT 4,       -- Max follow-ups before stopping
  follow_up_delay_hours INT DEFAULT 23,
  aggregation_window_seconds INT DEFAULT 60,
  exclusion_tags TEXT[] DEFAULT '{}', -- e.g. ['call_booked', 'dnc']
  active BOOL DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Per-channel webhook configurations
CREATE TABLE channels (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
  channel_type TEXT NOT NULL,        -- 'sms', 'instagram', 'facebook', 'email'
  webhook_secret TEXT NOT NULL,      -- used to verify GHL webhook
  active BOOL DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Contact state per account
CREATE TABLE contact_state (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
  contact_id TEXT NOT NULL,          -- GHL contact ID
  channel_type TEXT NOT NULL,
  follow_up_counter INT DEFAULT 0,
  opted_out BOOL DEFAULT false,
  excluded BOOL DEFAULT false,       -- tag-based exclusion
  last_user_message_at TIMESTAMPTZ,
  last_ai_message_at TIMESTAMPTZ,
  follow_up_scheduled_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(account_id, contact_id, channel_type)
);

-- Conversation memory (full history per contact)
CREATE TABLE conversation_memory (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
  contact_id TEXT NOT NULL,
  channel_type TEXT NOT NULL,
  role TEXT NOT NULL,                -- 'user' | 'assistant'
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Inbound message aggregation buffer
CREATE TABLE message_buffer (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
  contact_id TEXT NOT NULL,
  channel_type TEXT NOT NULL,
  message_part TEXT NOT NULL,
  received_at TIMESTAMPTZ DEFAULT now()
);

-- Audit log for all AI send events
CREATE TABLE ai_send_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
  contact_id TEXT NOT NULL,
  channel_type TEXT NOT NULL,
  direction TEXT NOT NULL,           -- 'inbound' | 'outbound'
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

---

## Project File Structure

```
ai-setter-saas/
├── src/
│   ├── index.ts                     # Express app entry
│   ├── config.ts                    # Env vars, constants
│   │
│   ├── routes/
│   │   ├── webhook.ts               # POST /webhook/:locationId/:channel
│   │   ├── accounts.ts              # CRUD for tenant accounts (dashboard API)
│   │   └── health.ts               # GET /health
│   │
│   ├── services/
│   │   ├── aggregator.ts            # BullMQ: 60s message aggregation window
│   │   ├── ai.ts                    # Claude API call + conversation builder
│   │   ├── ghl.ts                   # GHL API wrapper (send message, get contact, get tags)
│   │   ├── followup.ts              # Schedule / cancel / fire follow-up jobs
│   │   └── exclusion.ts             # Check contact tags against account exclusion list
│   │
│   ├── db/
│   │   ├── supabase.ts              # Supabase client init
│   │   ├── contactState.ts          # get/set contact_state helpers
│   │   ├── memory.ts                # append/fetch conversation_memory helpers
│   │   └── buffer.ts                # message_buffer flush helpers
│   │
│   ├── workers/
│   │   ├── aggregationWorker.ts     # Processes aggregation queue jobs
│   │   └── followupWorker.ts        # Processes scheduled follow-up jobs
│   │
│   └── utils/
│       ├── logger.ts
│       └── sanitize.ts              # Strip/escape unsafe chars from AI output
│
├── dashboard/                       # React + Vite operator UI
│   ├── src/
│   │   ├── App.tsx
│   │   ├── pages/
│   │   │   ├── Accounts.tsx         # List + provision client accounts
│   │   │   ├── AccountDetail.tsx    # Edit prompt, keys, follow-up settings
│   │   │   ├── Conversations.tsx    # Browse conversation logs per account
│   │   │   └── Login.tsx
│   │   └── components/
│   │       ├── AccountCard.tsx
│   │       ├── ChannelList.tsx
│   │       └── ConversationViewer.tsx
│   └── vite.config.ts
│
├── supabase/
│   └── migrations/
│       └── 001_initial_schema.sql
│
├── .env.example
├── package.json
├── tsconfig.json
├── Dockerfile
└── README.md
```

---

## Core Flow (Step by Step)

### Inbound Message Flow

```
GHL sends webhook → POST /webhook/:locationId/:channelType
  │
  ├─ 1. Verify webhook (location ID + secret)
  ├─ 2. Load account config from Supabase
  ├─ 3. Check contact exclusion (opted_out, excluded, GHL tags)
  │       → if excluded: return 200, do nothing
  │
  ├─ 4. Write message to message_buffer table
  ├─ 5. Enqueue aggregation job in BullMQ with delay (aggregation_window_seconds)
  │       → If job for this contact already exists: DO NOTHING (it will flush all buffered msgs)
  │
  └─ Return 200 immediately to GHL
```

### Aggregation Worker (fires after window)

```
aggregationWorker processes job for {accountId, contactId, channelType}
  │
  ├─ 1. Fetch all rows from message_buffer for this contact
  ├─ 2. Concatenate into single string (joined by ". ")
  ├─ 3. Delete those rows from message_buffer
  ├─ 4. Cancel any pending follow-up job for this contact
  ├─ 5. Reset follow_up_counter to 0 in contact_state
  ├─ 6. Append aggregated user message to conversation_memory
  ├─ 7. → Call AI Service
```

### AI Service

```
ai.ts receives {account, contactId, channelType, userMessage}
  │
  ├─ 1. Fetch full conversation_memory for contact (ordered ASC)
  ├─ 2. Build messages array: [{role, content}, ...] + new user message
  ├─ 3. Call Claude API with account.ai_system_prompt as system prompt
  ├─ 4. Parse response text
  │
  ├─ 5. Check for NULL keyword in response
  │       → if NULL: set contact opted_out = true, log, STOP
  │
  ├─ 6. Append assistant response to conversation_memory
  ├─ 7. → Call GHL Service to send message
  ├─ 8. → Schedule follow-up job (account.follow_up_delay_hours from now)
```

### GHL Service

```
ghl.ts sendMessage({account, contactId, channelType, message})
  │
  ├─ POST https://services.leadconnectorhq.com/conversations/messages
  │   Headers: Authorization: Bearer {account.ghl_api_key}
  │   Body: { type: "SMS", contactId, message }
  │
  └─ Log to ai_send_log
```

### Follow-up Worker

```
followupWorker fires when scheduled job delay elapses
  │
  ├─ 1. Load contact_state
  ├─ 2. Check if opted_out or excluded → STOP if true
  ├─ 3. Check follow_up_counter >= account.follow_up_max → STOP if true
  ├─ 4. Increment follow_up_counter
  ├─ 5. Append empty user message to conversation_memory
  │       (with system note: "[No response from user — send follow-up]")
  ├─ 6. → Call AI Service (AI knows from system prompt how to handle empty/follow-up)
  └─ 7. → Schedule next follow-up job (recursive until max reached)
```

---

## Environment Variables (.env.example)

```env
# Supabase
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=

# Anthropic
ANTHROPIC_API_KEY=

# Redis (BullMQ)
REDIS_URL=redis://localhost:6379

# App
PORT=3000
NODE_ENV=production

# Dashboard Auth (Supabase Auth)
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
```

---

## GHL Setup Per Client (What Agency Does)

1. In GHL, go to **Settings → Integrations → Private Integrations** → create a new key with scopes: `conversations.write`, `contacts.readonly`, `conversations/messages.write`
2. In **Workflows**, create ONE trigger: **Customer Replied** (or Inbound Message) → **Send Webhook** → `https://yoursaas.com/webhook/{locationId}/sms`
3. That's it. No other automations needed.
4. In the SaaS dashboard, add the client account with their Location ID and API key.

---

## Build Order for Claude Code

### Phase 1 — Backend Core
1. Scaffold Express + TypeScript project with `ts-node-dev`
2. Set up Supabase client and run migration SQL
3. Build `POST /webhook/:locationId/:channelType` route
4. Build `contactState.ts` and `memory.ts` DB helpers
5. Build `aggregator.ts` with BullMQ + Redis (60s delayed job, deduplicated per contact)
6. Build `aggregationWorker.ts` that flushes buffer and calls AI service
7. Build `ai.ts` — Claude API call, history builder, NULL detection
8. Build `ghl.ts` — send message via GHL API
9. Build `followup.ts` + `followupWorker.ts` — delayed follow-up with counter logic
10. Build `exclusion.ts` — fetch GHL contact tags, compare to account exclusion list

### Phase 2 — Account Management API
11. Build `GET/POST/PUT /accounts` routes (CRUD for tenant provisioning)
12. Build `GET/POST /accounts/:id/channels` routes
13. Add webhook secret verification middleware

### Phase 3 — Dashboard UI
14. Scaffold React + Vite dashboard in `/dashboard`
15. Build Login page (Supabase Auth)
16. Build Accounts list + provisioning form
17. Build AccountDetail page (edit prompt, settings, copy webhook URL)
18. Build ConversationViewer (browse memory log per contact)

### Phase 4 — Deploy
19. Add Dockerfile (multi-stage: build dashboard, serve from Express static)
20. Add `railway.json` or `render.yaml`
21. Write README with deploy steps + GHL setup guide

---

## AI System Prompt Template (Starter)

Include this in the `accounts.ai_system_prompt` field for each client:

```
You are [CLIENT_NAME]'s AI appointment setter. Your job is to qualify leads and book them onto a call with our team.

RULES:
- Be conversational, warm, and human. Never say you are an AI.
- Your goal is to get them booked on a call at [BOOKING_LINK].
- If the lead is unqualified or asks to stop receiving messages, respond with exactly: NULL
- If you receive an empty or blank user message, it means you are following up because they have not responded. Send a natural follow-up. Do not acknowledge the gap explicitly.
- Keep responses under 160 characters when possible (SMS-friendly).
- Never send more than one question per message.

CONTEXT:
Current date/time: {CURRENT_DATETIME}
```

> Claude Code: inject `{CURRENT_DATETIME}` dynamically in `ai.ts` before sending to the API.

---

## Key Technical Notes for Claude Code

- **BullMQ deduplication:** Use `jobId: \`agg-${accountId}-${contactId}-${channelType}\`` when enqueuing. BullMQ will ignore duplicate job IDs if the job is still delayed/waiting. This is the aggregation window mechanism.
- **Follow-up job IDs:** Use `jobId: \`followup-${accountId}-${contactId}-${channelType}\`` so you can call `queue.remove(jobId)` when the user responds (cancels the pending follow-up).
- **GHL API base URL:** `https://services.leadconnectorhq.com` — use v2 endpoints.
- **Message type mapping:** GHL channel type in webhook payload is usually `TYPE_SMS`, `TYPE_IG`, `TYPE_FB`. Map these to your internal `sms | instagram | facebook`.
- **Supabase RLS:** Enable RLS on all tables. Dashboard queries use anon key + Supabase Auth JWT. Backend workers use service role key directly.
- **NULL response:** Do a case-insensitive `.includes('null')` check on AI response content. If matched, do NOT send the message to GHL — just set `opted_out = true` and stop.
- **Conversation history limit:** Cap history fetch at last 40 messages to stay within token limits. Use `ORDER BY created_at ASC LIMIT 40` offset from end.
