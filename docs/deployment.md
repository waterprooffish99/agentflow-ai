# Deployment Architecture

## Targets
- Frontend: Vercel
- Backend: Render or Railway (container deploy)
- Database: Neon PostgreSQL
- Redis: Upstash Redis

## Backend
- Build from `backend/Dockerfile`.
- Set runtime env from `.env.example` with secure secrets.
- Ensure `DATABASE_URL` and `REDIS_URL` point to managed services.
- Expose `/health` and `/health/ready` for platform health checks.

## Frontend
- Deploy `frontend` on Vercel.
- Set `NEXT_PUBLIC_API_URL` to backend `/api/v1` endpoint.
- Use Vercel environment separation for preview/production.

## Security
- Enable strict CORS allowlist.
- Set `PUBLIC_API_KEY` for widget/chat endpoints.
- Rotate JWT keys with `JWT_KID_CURRENT` and `JWT_PREVIOUS_SECRET`.

## Demo Mode
- Run demo seeding script post-migration:
  - `python backend/scripts/seed_demo_data.py`

## Post-Deploy Validation
1. `/health` returns `status=ok`.
2. `/health/ready` returns `status=ready` with database+redis checks true.
3. Login and token refresh flow works.
4. Analytics dashboard loads KPI and chart endpoints.
5. Tenant isolation smoke test prevents cross-tenant data read.
