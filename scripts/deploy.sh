#!/bin/bash
# facil.guide -- Build, Deploy, Submit to Google
#
# Usage:
#   ./scripts/deploy.sh              # Build + deploy + submit new URLs
#   ./scripts/deploy.sh --skip-gsc   # Build + deploy only (no Google submission)
#
# Called by cron or manually after adding/updating content.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CLOUDFLARE_ACCOUNT_ID="166e52169c00e38f7054c88ba803c9f7"

cd "$PROJECT_DIR"

echo "=== Building ==="
npm run build

echo ""
echo "=== Deploying to Cloudflare Pages ==="
CLOUDFLARE_ACCOUNT_ID="$CLOUDFLARE_ACCOUNT_ID" \
  npx wrangler pages deploy dist \
  --project-name facil-guide \
  --branch main \
  --commit-dirty=true

echo ""
echo "=== Git commit & push ==="
git add -A
if git diff --cached --quiet; then
  echo "No changes to commit."
else
  git commit -m "Content update $(date +%Y-%m-%d)"
  git push
fi

# Google submission
if [[ "$1" != "--skip-gsc" ]]; then
  echo ""
  echo "=== Submitting new URLs to Google ==="
  python3 "$SCRIPT_DIR/gsc_submit.py" --new-only 2>&1 || echo "GSC submission failed (is facil.guide added to Search Console?)"
fi

echo ""
echo "=== Done ==="

# IndexNow submission (Bing, DuckDuckGo, Yandex -- no auth needed)
echo ""
echo "=== Submitting to IndexNow (Bing/DDG/Yandex) ==="
python3 "$SCRIPT_DIR/indexnow_submit.py" --new-only 2>&1 || echo "IndexNow submission failed"
