# ElectroMarket

Electronic store marketplace built with Django, DRF, Django Ninja, django CMS, and django-allauth (passkeys).

## Stack

- **Runtime:** Django 5.2, uv, ruff
- **Auth:** django-allauth + MFA/WebAuthn passkeys
- **API:** Django REST Framework + Django Ninja
- **CMS / media:** django CMS, django-filer, django-imagekit
- **Ops:** django-health-check, django-import-export
- **DB:** PostgreSQL (Supabase) via `DATABASE_URL`
- **Deploy:** Fly.io (`fly.toml`)

## Features

Authentication, passkeys, shopping cart, orders, catalog search/filters (name, category, id, tag), favourites, recommendations/suggestions, product cards, descriptions, tags, discounts, share, banners/sliders/previews, commentaries, ratings, notifications, admin sections/cards, CSV import for products/users/orders.

