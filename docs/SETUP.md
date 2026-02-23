# facil.guide -- Setup & Credentials

## Local Development

```bash
cd /Users/kiddok/Desktop/labs/facil-guide

# Install
npm install

# Dev server (hot reload)
npm run dev        # http://localhost:4321

# Build (static)
npm run build      # output: dist/

# Preview build
npm run preview    # http://localhost:4322
```

## Git

```
Repo:   https://github.com/DropTheOrg/facil-guide (public)
User:   DropThe
Email:  mike@dropthe.org
Auth:   HTTPS (arnaudleroy-studio GitHub account, DropTheOrg member)
```

Note: `arnaudleroy-studio` has push access but NOT org-level create-repo permission. Push via HTTPS works fine.

## Cloudflare Pages (Hosting)

```
Account ID:  166e52169c00e38f7054c88ba803c9f7
Zone ID:     5025a05560927a229da0eb63b768b66d
Project:     facil-guide
Live URL:    https://facil.guide
Backup URL:  https://facil-guide.pages.dev
Custom domains: facil.guide, www.facil.guide
```

### Deploy Command

```bash
cd /Users/kiddok/Desktop/labs/facil-guide
npm run build
CLOUDFLARE_ACCOUNT_ID="166e52169c00e38f7054c88ba803c9f7" \
  npx wrangler pages deploy dist \
  --project-name facil-guide \
  --branch main \
  --commit-dirty=true
```

### Why Not GitHub Auto-Deploy?

Cloudflare Pages GitHub integration returns error `8000011` ("internal issue with Git installation"). Known CF bug. Must use `wrangler pages deploy` direct upload instead.

### Cloudflare API Auth

```
Email:   $CLOUDFLARE_EMAIL (in /Users/kiddok/.openclaw/workspace/.env)
API Key: $CLOUDFLARE_API_KEY (in /Users/kiddok/.openclaw/workspace/.env)
```

### CF Cache Purge (if needed)

```bash
source /Users/kiddok/.openclaw/workspace/.env
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/5025a05560927a229da0eb63b768b66d/purge_cache" \
  -H "X-Auth-Email: $CLOUDFLARE_EMAIL" \
  -H "X-Auth-Key: $CLOUDFLARE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"files":["https://facil.guide/en/","https://facil.guide/fr/"]}'
```

## DNS

Domain `facil.guide` DNS managed in Cloudflare. Custom domains added to CF Pages project. SSL auto-provisioned.

## robots.txt Issue

Cloudflare prepends their managed "Content-Signal" directives to robots.txt. Google flags `Content-Signal: search=yes,ai-train=no` as unknown directive. 

**Fix:** Cloudflare Dashboard > facil.guide zone > Security > Bots > disable "AI Scrapers and Crawlers" or "Content credentials" toggle. Our own `public/robots.txt` already blocks AI scrapers with standard Disallow.

## No Supabase Yet

No `facil_` tables exist in Supabase. The DB schema is planned (see internal docs at `dropthe-org-internal/facil/DATABASE_SCHEMA.md`) but not built. Currently everything is static markdown files.

## No npm Publish

`dropthe-charts` npm publish requires `npm adduser` with a 90-day token. Not related to facil.guide but noted since it was in the same work session.

## Environment Variables

facil.guide itself needs NO env vars. It's fully static. The only env vars are for deployment:

| Variable | Location | Purpose |
|----------|----------|---------|
| `CLOUDFLARE_EMAIL` | `~/.openclaw/workspace/.env` | CF API auth |
| `CLOUDFLARE_API_KEY` | `~/.openclaw/workspace/.env` | CF API auth |
| `CLOUDFLARE_ACCOUNT_ID` | Passed inline to wrangler | CF Pages deploy |
