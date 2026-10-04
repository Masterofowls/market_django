# Activity Log

## 2026-10-04

- Initialized `market-django` with uv, ruff, pytest-django.
- Scaffolded Django project `config` and domain apps under `apps/`.
- Configured Postgres/Supabase via `DATABASE_URL`, django-allauth + passkeys, DRF, Ninja, CMS, health-check, imagekit, import-export.
- Implemented catalog/cart/orders/favourites/reviews/marketing/notifications/recommendations.
- Added admin CSV import for products, users, orders; section management for storefront cards.
- Added Fly.io Dockerfile/entrypoint/`fly.toml`, docs, storefront templates (no seed products).
- Applied migrations; pytest 3 passed; fixed empty `DATABASE_URL` / health-check 4.x wiring.
- Seeded 9 real smartphones (Samsung / Nothing / Apple) with Wikimedia images + specs.
- Redesigned storefront (full-bleed hero, brand rail, product cards, detail specs table).
- Noted Supabase API keys are present but Django still needs Postgres `DATABASE_URL`.
- Product detail: fixed CSS loading (fonts via link + cache-bust), removed image float animation.
- Added public share link UI + `/products/<slug>/share/`, search by public ID, similar items.
- Styled allauth login/signup via shared store chrome; mobile hamburger nav; single Share control.
- Wired SUPABASE_URL `https://eadxantpovgupzwemomv.supabase.co`; email optional on signup (passkey signup off).
- Fly restart loop: fixed CRLF entrypoint; wired Supabase session pooler `DATABASE_URL`; secrets staged.
- Fly `/ht/` 500: disabled health_check DNS (machine id hostname); Database+Cache only; ALLOWED_HOSTS=* on Fly.
- Confirmed Fly `DATABASE_URL` → Supabase pooler; seeded 4 categories / 9 products / 9 images / 13 tags into Supabase.
- Fixed product images 404: serve `/media/` in production + bake `media/` into Fly image.
- Storefront cart + favourites actions; cart/checkout pages; account hub (profile, security/passkeys, orders, favourites, viewed history).
- Deployed cart/account hub to Fly (`electromarket.fly.dev`).
- Forced Django superuser `admin` / `admin@gmail.com` on Supabase (shared with Fly).
- Admin-managed header categories via `Category.show_in_header` + `header_order`.
- Fixed mobile layout: header overflow, sticky cart chip, brand chips, 2-col product grid.
