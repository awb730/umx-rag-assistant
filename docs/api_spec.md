# UMExchange API Reference

Base URL: https://underground-music-stock-exchange.onrender.com

## Public Endpoints

### GET /
Health check. Returns a message confirming the API is running.

### GET /artists
Returns a list of all tracked artists with their IDs and names.

### GET /leaderboard
Returns all tracked artists ranked by signal priority then 7-day listener growth.
Each artist includes: artist_id, name, signal, listeners_now, listener_growth_7d,
listener_growth_30d, acceleration, z_score.

### GET /artist/{artist_id}/metrics
Returns computed momentum features for a specific artist by ID.
Includes: listeners_now, listener_growth_7d, listener_growth_30d,
playcount_growth_7d, acceleration, z_score.

### GET /artist/{artist_id}/signal
Returns the current signal classification for a specific artist.
Includes all metrics plus the signal label.

### GET /artist/{artist_id}/history
Returns the 30-day listener history time series for charting.
Each entry includes: date (formatted string), listeners (integer).

### GET /search?name={artist_name}
Searches Last.fm for an artist by name. If found, adds them to the database,
seeds 30 days of historical data, computes features, and returns their signal.

## Auth Endpoints

### POST /register
Creates a new user account. Requires: username, email, password.
Returns: JWT token, username, credits (starting balance: 1000).

### POST /login
Authenticates a user. Requires: username, password.
Returns: JWT token, username, credits, avatar_url.

### GET /me
Returns the current authenticated user's profile.
Requires: Bearer token in Authorization header.
Returns: id, username, email, credits, avatar_url.

## Position Endpoints (Auth Required)

### POST /positions/open
Opens a LONG or SHORT position on an artist.
Requires: artist_id (int), direction ("LONG" or "SHORT"), credits_wagered (int).
Deducts credits from user balance immediately.
Records listener count at time of opening for P&L calculation.

### POST /positions/close/{position_id}
Closes an open position and settles P&L.
P&L is calculated as: credits_wagered * listener_growth_since_open.
LONG profits from growth. SHORT profits from decline.
Returns wagered credits plus or minus P&L to user balance.

### GET /portfolio
Returns the authenticated user's full portfolio.
Includes: credits balance, all open and closed positions with live P&L.

## Payment Endpoints (Auth Required)

### POST /payments/create-checkout-session
Creates a Stripe Checkout session for purchasing credits.
Requires: bundle_key ("small", "medium", "large", or "xlarge").
Returns: checkout_url to redirect user to Stripe's hosted payment page.

### POST /payments/webhook
Stripe webhook endpoint. Receives payment confirmation events.
On successful payment, credits are added to the user's balance.
Protected by Stripe signature verification.

## Settings Endpoints (Auth Required)

### POST /settings/check-username
Checks if a username is available. Requires: username.
Returns: available (boolean).

### POST /settings/update-username
Updates the authenticated user's username if available.
Returns: new username and a fresh JWT token.

### POST /settings/update-password
Updates the authenticated user's password.
Requires: current_password, new_password (min 6 characters).

### POST /settings/upload-avatar
Uploads a profile picture to Supabase Storage.
Accepts: multipart/form-data with image file (JPEG, PNG, or WEBP, max 5MB).
Returns: public avatar_url stored in the database.

## Credit Bundles

| Bundle Key | Label    | Credits | Price  | Bonus      |
|------------|----------|---------|--------|------------|
| small      | Starter  | 250     | $2.99  |            |
| medium     | Standard | 500     | $4.99  |            |
| large      | Pro      | 1200    | $9.99  | 20% bonus  |
| xlarge     | Elite    | 3500    | $24.99 | 40% bonus  |