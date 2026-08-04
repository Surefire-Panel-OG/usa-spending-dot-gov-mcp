# Connect the USAspending tool in Claude Desktop

One-time setup, ~30 seconds. You need a Claude **Pro**, **Max**, **Team**, or
**Enterprise** plan (Free supports one custom connector).

## Steps

1. Open **Claude Desktop**.
2. Go to **Settings → Connectors** (also reachable via **Customize → Connectors**).
3. Click **Add custom connector**.
4. **Name:** `USAspending`
5. **URL:** paste the endpoint your admin gave you — it ends in `/mcp`, e.g.
   `https://usaspending-mcp.xxxxx.us-east-1.cs.amazonlightsail.com/mcp`
6. Click **Add**, then enable the connector.

That's it — no login, no token. The USAspending tools now appear in your chats
and in Cowork.

## Try it

Ask Claude something like:

- "Which companies won the most Navy contracts in FY2024?"
- "Show Department of Veterans Affairs spending over the last 5 fiscal years."
- "Find active IT contracts at DHS expiring in the next 12 months."

## Troubleshooting

- **Connector won't add / errors:** confirm the URL ends in `/mcp` and that
  `https://<same-host>/healthz` returns `{"status":"ok"}` in a browser.
- **"Rate limit exceeded" (HTTP 429):** the server caps requests per user per
  minute; wait a minute and retry. Ask your admin to raise the limit if it's
  too low for normal use.
- **Tools don't show up:** fully quit and reopen Claude Desktop after adding the
  connector.
