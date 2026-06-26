# How UMExchange Works

## Core Concept

UMExchange applies quantitative finance concepts to music artists streaming data.
Artists are treated like financial assets. Listener counts are price. Engagement
velocity is volume. The platform tracks how these numbers move over time and
classifies each artist into a market signal.

## Data Pipeline

Every 24 hours, an automated ingestion job pulls fresh listener and playcount data
from the Last.fm API for every tracked artist. This data is stored as a time-series
in PostgreSQL — one row per artist per day — building up a historical record that
the feature engine uses to compute momentum.

When a new artist is searched and added to the platform, 30 days of historical data
is seeded using a randomized growth model based on their current metrics. This
bootstraps enough history for the signal engine to function immediately.

## Feature Engineering

For each artist, the system computes five momentum indicators:

**7-day listener growth** — percentage change in listener count over the past 7 days.
Captures short-term momentum.

**30-day listener growth** — percentage change over the full 30-day window.
Captures sustained trend direction.

**Playcount 7-day growth** — percentage change in total plays over 7 days.
Plays often lead listeners as a leading indicator of breakout activity.

**Acceleration** — compares growth in the second half of the 30-day window
against the first half. Positive acceleration means momentum is building.
Negative means it is slowing down. This captures whether an artist is speeding
up or cooling off, which a simple growth rate misses.

**Z-score** — measures how far the current listener count deviates from the
30-day mean in standard deviations. A high z-score means the current count is
abnormally high relative to recent history, which is a strong signal of unusual
activity.

## Signal Classification

The five features feed into a rule-based classifier that assigns one of five signals:

**BREAKOUT** — 7-day growth above 5%, positive acceleration, and z-score above 1.5.
Artist is growing fast and the momentum is accelerating.

**RISING** — 7-day growth above 2% and 30-day growth above 5%.
Artist is growing steadily across both timeframes.

**STABLE** — Does not meet BREAKOUT or RISING thresholds, and not declining.
Artist has consistent but unremarkable listener activity.

**COOLING** — 7-day growth below -2% and negative acceleration.
Artist is losing listeners and the decline is getting worse.

**DORMANT** — Z-score below -1 and 30-day growth below 1%.
Artist has low activity relative to their historical baseline.

## Leaderboard Ranking

Artists are ranked first by signal priority:
BREAKOUT → RISING → STABLE → COOLING → DORMANT

Within each signal tier, artists are ranked by 7-day listener growth descending,
so the fastest growing artist in each tier appears at the top.

## The Investing Mechanic

Users start with 1,000 free credits on registration. Credits can be used to open
positions on artists — essentially betting on whether their listener count will
rise or fall.

**LONG position** — you believe the artist will grow. You profit if listeners
increase after you open the position.

**SHORT position** — you believe the artist will decline. You profit if listeners
decrease after you open the position.

P&L is calculated as:
- Growth = (current_listeners - listeners_at_open) / listeners_at_open
- LONG P&L = credits_wagered * growth
- SHORT P&L = credits_wagered * -growth

When you close a position, your original wagered credits plus or minus the P&L
are returned to your balance. Credits can be purchased in bundles via Stripe.

## Authentication

UMExchange uses JWT (JSON Web Token) authentication. When you register or log in,
the server returns a signed token containing your user ID and username. This token
is stored in localStorage and sent as a Bearer token in the Authorization header
on every protected request. Tokens expire after 7 days.

## Tech Stack

**Backend:** FastAPI (Python), PostgreSQL (Supabase), Pandas for feature engineering,
JWT auth via python-jose, bcrypt password hashing via passlib, Stripe for payments,
Supabase Storage for avatar uploads.

**Frontend:** React (Vite), Tailwind CSS, Recharts for charts, Axios for API calls.

**Infrastructure:** Render (API hosting), Netlify (frontend hosting),
Supabase (managed PostgreSQL + storage), Windows Task Scheduler (daily ingestion).

**External APIs:** Last.fm (artist data), Stripe (payments).