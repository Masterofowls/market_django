# Architecture Decision Records

## ADR-001 — Dual API surfaces (DRF + Ninja)

**Decision:** Expose full marketplace resources on DRF and a slim typed surface on Django Ninja.

**Why:** DRF covers filters/pagination/admin-friendly browsable API; Ninja gives a fast typed OpenAPI for product search/health.

## ADR-002 — Supabase Postgres via DATABASE_URL

**Decision:** Use `dj-database-url` with Supabase connection strings; SQLite default for local.

**Why:** Keeps secrets out of code and matches Fly.io secret injection.

## ADR-003 — Empty catalog until content phase

**Decision:** Ship schema, admin import, and APIs without seed products/images.

**Why:** Product copy and media will be added after the platform is complete.

## ADR-004 — django CMS for content pages

**Decision:** CMS owns marketing pages; store app owns catalog/cart UX under `/store/`.

**Why:** Separates merchandising content from transactional catalog logic.
