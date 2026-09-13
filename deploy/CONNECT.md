# Connect the USAspending tool

Works in **Claude Desktop** and **ChatGPT**. Pick your section below.

One-time setup, ~30 seconds. You need a Claude **Pro**, **Max**, **Team**, or
**Enterprise** plan (Free supports one custom connector).

## Claude Desktop

1. Open **Claude Desktop**.
2. Go to **Settings → Connectors** (also reachable via **Customize → Connectors**).
3. Click **Add custom connector**.
4. **Name:** `USAspending`
5. **URL:** paste the endpoint your admin gave you — it ends in `/mcp`, e.g.
   `https://usaspending-mcp.xxxxx.us-east-1.cs.amazonlightsail.com/mcp`
6. Click **Add**, then enable the connector.

That's it — no login, no token. The USAspending tools now appear in your chats
and in Cowork.

## ChatGPT

Requires **Developer mode**, which OpenAI enables per account/workspace policy.
If you don't see the option, ask your workspace admin.

1. In ChatGPT, open **Settings → Security and login** and turn on
   **Developer mode**.
2. Go to <https://chatgpt.com/plugins> and click the **+** (add) button.
3. **Name:** `USAspending`. Add a short description if prompted.
4. **Connection:** choose the public-endpoint option and paste the same
   `/mcp` URL as above.
5. If asked about authentication, choose the no-auth / none option — the
   server needs no login.
6. Create the connection, then enable it in a chat via the tools/plugins menu.

Note: this connector works in normal chats. It does **not** work with ChatGPT's
**deep research** or **company knowledge** features, which require the server
to expose special `search` and `fetch` tools it doesn't have.

## Try it

Ask something like:

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
