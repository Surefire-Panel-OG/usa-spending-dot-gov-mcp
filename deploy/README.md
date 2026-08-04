# Deploying the USAspending MCP server (AWS Lightsail Containers)

This deploys the server as a single always-on container behind a managed HTTPS
URL, at a **flat ~$7/month** (Lightsail `micro` power). No per-query cost: the
USAspending API is free and Claude usage is covered by your existing plan.

## What you get

- A public HTTPS URL like `https://usaspending-mcp.<random>.us-east-1.cs.amazonlightsail.com/`
- The MCP endpoint your team pastes into Claude Desktop: that URL + `mcp`
- A `/healthz` endpoint for the load-balancer health check

## Access model

There is **no application-level auth** — the underlying data is 100% public, so
the only thing worth protecting is the container's compute. That is handled by:

- **Per-client rate limiting** (`MCP_SERVER_RATE_LIMIT_PER_MINUTE`, default 120/min)
- `MCP_SERVER_DEBUG=false` (no stack traces leaked)

If you later need real access control (restrict to specific people), the right
move is to add OAuth in front — see "Hardening beyond this" below. A static
bearer token is intentionally *not* used because the Claude Desktop connector UI
has no field for one.

## Prerequisites (install once on the machine you deploy from)

- [Docker](https://docs.docker.com/get-docker/) (running)
- AWS CLI v2, configured: `aws configure`
- [lightsailctl plugin](https://lightsail.aws.amazon.com/ls/docs/en_us/articles/amazon-lightsail-install-software)
  (macOS: `brew install aws/tap/lightsailctl`)
- `jq`

## Deploy

```bash
# from the repo root
AWS_REGION=us-east-1 ./deploy/lightsail/deploy.sh
```

The script creates the Lightsail container service (first run only), builds the
image for `linux/amd64`, pushes it, deploys it, and prints the public URL. First
deployment takes a few minutes to go **ACTIVE**.

Re-run the same command any time to ship an update (e.g. after adding endpoints).

## Verify

```bash
curl https://<your-service-url>/healthz     # -> {"status":"ok"}
```

Then follow [CONNECT.md](./CONNECT.md) to add it in Claude Desktop.

## Tuning

Environment variables (set in `deploy/lightsail/containers.json`):

| Variable | Default | Purpose |
|---|---|---|
| `MCP_SERVER_HOST` | `0.0.0.0` | Bind address (must be `0.0.0.0` in a container) |
| `MCP_SERVER_PORT` | `8000` | Listen port |
| `MCP_SERVER_DEBUG` | `false` | Starlette debug (keep `false` in prod) |
| `MCP_SERVER_CORS_ALLOW_ORIGINS` | `*` | Comma-separated CORS origins |
| `MCP_SERVER_RATE_LIMIT_PER_MINUTE` | `120` | Per-client request cap; `0` disables |

## Costs

- **Lightsail micro container**: ~$7/mo flat, regardless of query volume.
- **Data egress**: negligible (small JSON responses).
- **USAspending API / Claude**: $0 incremental.

To stop paying, delete the service:

```bash
aws lightsail delete-container-service --service-name usaspending-mcp --region us-east-1
```

## Hardening beyond this (optional, later)

If access must be limited to specific individuals:

1. Put the service behind an OAuth-aware proxy, or
2. Front it with Cloudflare Access / an ALB + OIDC (Cognito/Google) and have
   teammates sign in.

Both are more work than the flat public+rate-limited setup and are only worth it
if you need to gate *who* can query (not *what* they can see — it's all public).
