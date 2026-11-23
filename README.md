# Scandinavian Nomads

Source for [scandinaviannomads.com](https://scandinaviannomads.com) – budget-luxury travel guides, tips and weekly travel news.

## How it works

- `content/` – all text. One Markdown file per destination, tip and weekly news post, with settings at the top (between `---` lines).
- `content/site.yaml` – site name, contact email and the Travel Toolkit (affiliate tools).
- `assets/` – CSS, JavaScript, icons, share image.
- `php/` – contact and newsletter form handlers plus `.htaccess`.
- `build.py` – builds the finished site into `dist/` (`python3 build.py`, needs `pip install markdown pyyaml`).
- `publish.sh` – builds and pushes `dist/` to the `site` branch. Hostinger serves the `site` branch.

Branches: `main` = source, `site` = finished website (generated, do not edit by hand).

## Weekly content

- **Monday – news:** add `content/news/2026-w49.md` with `week`, `year`, `summary` and an `items` list (`headline`, `summary`, `impact`, `source`, `url`).
- **Wednesday – destination:** add `content/destinations/<slug>.md` (copy an existing one). Set `featured: true` on it and `false` on the previous one.
- **Friday – tip:** add `content/tips/<slug>.md`.

Set `draft: true` to keep a file off the site.

## Affiliate links

Fill in `links:` in a destination (hotel, activities, transfer, flights, insurance), `products:` in a tip, or `tools:` in `site.yaml`. Boxes only appear when a link is filled in, always with the disclosure line and `rel="sponsored nofollow"`.
Mark paid content with `sponsored: true` – it then gets a visible "Sponsored" label.
