# Florin Management — parent-company site

Static holding page for **Florin Management**, the parent company of
Summit Strategic, Wine Dark Pictures, and AutoBoss.

Live: **https://florinmanagement.com**

---

## Architecture (no server, no cost)

| Piece      | Choice                                                             |
|------------|-------------------------------------------------------------------|
| Content    | A single `index.html` — no framework, no build step, no runtime.  |
| Hosting    | **GitHub Pages** (free static CDN). Repo `occidencel/florin-management`, branch `main`, root `/`. |
| Domain     | `florinmanagement.com`, registered at **GoDaddy**.                |
| DNS        | Managed via the **GoDaddy API** (see `scripts/gd.sh`).            |
| HTTPS      | Let's Encrypt via GitHub Pages, auto-renews. "Enforce HTTPS" is ON. |

There is **no VPS and nothing running.** The whole site is files on a CDN.

---

## How to change the site content

1. Edit `index.html`.
2. `git commit -am "…" && git push`.
3. Live in ~1 minute (GitHub Pages rebuild). No other step.

Brand rows, copy, and contact email all live in `index.html`.

---

## How the domain is wired (DNS)

Credentials for the GoDaddy API live in **`~/.florin-godaddy.env`** on the
owner's machine (gitignored, `chmod 600`, never committed). They are a
Production API key from developer.godaddy.com.

Helper script — `scripts/gd.sh`:

```bash
bash scripts/gd.sh check                    # read-only: domain status + all DNS records
bash scripts/gd.sh github-pages occidencel  # (re)point apex + www at GitHub Pages
```

Records that make it work:

- Apex `@` → four GitHub Pages A records: `185.199.108.153`, `.109.153`, `.110.153`, `.111.153`
- `www` → CNAME `occidencel.github.io`
- `CNAME` file in this repo contains `florinmanagement.com` (tells GitHub which custom domain to serve + certify)

---

## ⚠️ The gotcha that cost us an hour (read before debugging DNS)

GoDaddy **Website Builder was connected to this domain** and *overrode* the
apex A records at the authoritative nameservers — even though the DNS API
zone correctly showed our GitHub records.

**Symptom:** `dig +short @ns53.domaincontrol.com florinmanagement.com A`
returns GoDaddy/Website-Builder IPs (`76.223.105.230` / `13.248.243.5`),
NOT the records you set via the API. The `www` CNAME updates fine; only the
apex is hijacked. The original apex record's `data` was the literal string
`"WebsiteBuilder Site"` (a synthetic value, not an IP) — that's the tell.

**Fix:** unpublish / disconnect the Website Builder site. There is **no
public API** for this. It was done by unpublishing in the GoDaddy dashboard
(or PATCHing GoDaddy's internal Websites API:
`PATCH https://websites.api.godaddy.com/v2/websites/<id>` with
`{"properties":{"publishStatus":"unpublished"}}`). Once unpublished, the
apex A records take effect and GitHub auto-provisions the cert within ~an hour.

If you ever re-point this domain and the apex won't budge, this is why.

---

## Reusable pattern for the other brands

The exact recipe works for **winedarkpictures.com**, **autobossapp.com**, or
any future brand:

1. Copy this repo, swap `index.html` content and the `CNAME` file.
2. `gh repo create … --public --source=. --push`, then enable Pages.
3. Point the domain's DNS at GitHub (adapt `scripts/gd.sh` for the new domain).
4. If the domain is on GoDaddy Website Builder, unpublish it first (see gotcha).

Total production footprint per brand: **one repo + a few DNS records. $0.**

---

## Open items (content, not plumbing)

- [ ] Real one-line descriptions for **Wine Dark Pictures** and **AutoBoss**
- [ ] Final Florin lede copy (currently a placeholder)
- [ ] Confirm contact email (currently `hello@florinmanagement.com`)
- [ ] Confirm "AutoBoss" is the correct display name for autobossapp.com
