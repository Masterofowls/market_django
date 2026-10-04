# Architecture — ElectroMarket

## Overview

Django marketplace for electronics with:

- HTML storefront (`/`) + django CMS pages (`/pages/`)
- DRF API (`/api/v1/`) and Django Ninja (`/api/ninja/`)
- django-allauth (email/username + passkeys/WebAuthn via MFA)
- Postgres via Supabase (`DATABASE_URL`)
- Fly.io deployment (`fly.toml` + `infra/fly/Dockerfile`)

## Layout

```
apps/
  accounts/          Custom user + allauth adapter + CSV user import
  catalog/           Categories, tags, products, images, sections, share
  cart/              Session/user cart
  orders/            Checkout + order history + CSV import
  favourites/        Wishlist
  reviews/           Ratings, reviews, commentaries
  recommendations/   Suggestions + personalized recommendations
  marketing/         Banners + sliders
  notifications/     In-app notifications
  core/              Storefront views + branding
config/              Settings, URLs, Ninja API, DRF router
packages/utils/      Shared helpers (reserved)
infra/fly/           Container entrypoint + Dockerfile
docs/                Architecture, ADRs, activity log
tests/               Pytest suite
```

## Data flow

1. Admin creates categories/tags/sections and imports products/users/orders via CSV.
2. Storefront/API list and filter catalog (name, category, id, tag, price, discount).
3. Cart → checkout creates `Order` + `OrderItem`, clears cart, emits notification.
4. Reviews update `Product.average_rating` / `rating_count` via signals.
5. Recommendations use category/tag overlap, favourites, and order history.

## Auth

- Session auth for storefront + browsable API
- Token auth available for DRF clients
- Passkeys: `/accounts/` allauth MFA/WebAuthn endpoints (`MFA_PASSKEY_LOGIN_ENABLED`)

## Health

- `django-health-check` at `/ht/`
- Ninja health at `/api/ninja/health`
