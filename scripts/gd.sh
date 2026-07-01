#!/usr/bin/env bash
# GoDaddy DNS helper for florinmanagement.com
# Usage:
#   gd.sh check                         -> auth test + show domain status & records (read-only)
#   gd.sh set-a   <name> <ip>           -> upsert an A record
#   gd.sh set-cname <name> <target>     -> upsert a CNAME record
set -euo pipefail

ENV_FILE="$HOME/.florin-godaddy.env"
DOMAIN="florinmanagement.com"
API="https://api.godaddy.com/v1"

# shellcheck disable=SC1090
set -a; . "$ENV_FILE"; set +a
AUTH="Authorization: sso-key ${GODADDY_API_KEY}:${GODADDY_API_SECRET}"

cmd="${1:-check}"

case "$cmd" in
  check)
    echo "== auth + domain status =="
    curl -s -w "\nHTTP %{http_code}\n" -H "$AUTH" "$API/domains/$DOMAIN"
    echo "== current records =="
    curl -s -w "\nHTTP %{http_code}\n" -H "$AUTH" "$API/domains/$DOMAIN/records"
    ;;
  set-a)
    name="$2"; ip="$3"
    curl -s -w "\nHTTP %{http_code}\n" -X PUT \
      -H "$AUTH" -H "Content-Type: application/json" \
      "$API/domains/$DOMAIN/records/A/$name" \
      -d "[{\"data\":\"$ip\",\"ttl\":600}]"
    ;;
  set-cname)
    name="$2"; target="$3"
    curl -s -w "\nHTTP %{http_code}\n" -X PUT \
      -H "$AUTH" -H "Content-Type: application/json" \
      "$API/domains/$DOMAIN/records/CNAME/$name" \
      -d "[{\"data\":\"$target\",\"ttl\":600}]"
    ;;
  github-pages)
    # apex -> GitHub Pages' 4 anycast IPs; www -> user.github.io
    ghuser="${2:-occidencel}"
    echo "== set apex A records =="
    curl -s -w "\nHTTP %{http_code}\n" -X PUT \
      -H "$AUTH" -H "Content-Type: application/json" \
      "$API/domains/$DOMAIN/records/A/@" \
      -d '[{"data":"185.199.108.153","ttl":600},{"data":"185.199.109.153","ttl":600},{"data":"185.199.110.153","ttl":600},{"data":"185.199.111.153","ttl":600}]'
    echo "== set www CNAME =="
    curl -s -w "\nHTTP %{http_code}\n" -X PUT \
      -H "$AUTH" -H "Content-Type: application/json" \
      "$API/domains/$DOMAIN/records/CNAME/www" \
      -d "[{\"data\":\"${ghuser}.github.io\",\"ttl\":600}]"
    ;;
  *)
    echo "unknown command: $cmd" >&2; exit 1 ;;
esac
