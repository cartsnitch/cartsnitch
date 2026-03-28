# CartSnitch Monorepo

CartSnitch is a self-hosted grocery price intelligence platform. This repo consolidates the core services and the flagship frontend PWA.

## Services

| Directory | Service | Purpose |
|-----------|---------|---------|
| `/` (root) | **Frontend** | React 18 PWA — mobile-first price intelligence UI |
| `api/` | **API Gateway** | FastAPI — frontend-facing REST API |
| `common/` | **Common** | Shared Python models, schemas, Alembic migrations |
| `receiptwitness/` | **ReceiptWitness** | Purchase ingestion via retailer scrapers |

## Quick Start

### Frontend (root)

```bash
npm install
npm run dev        # http://localhost:5173
npm run build      # production build
npm run test       # unit tests (Vitest)
```

### Python Services

Each Python service uses [uv](https://github.com/astral-sh/uv) and has its own `pyproject.toml`:

```bash
cd api             # or common / receiptwitness
uv sync
uv run pytest
```

## Development Workflow

- **Never push directly to main.** Always open a PR from a feature branch.
- Branch naming: `feature/<description>` or `fix/<description>`
- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`

## Architecture

For full details see [CLAUDE.md](./CLAUDE.md) or the per-service `CLAUDE.md` in each subdirectory.

CartSnitch is a polyrepo-style monorepo: each service can be built and deployed independently, but sharing code between `common/` and the other Python services is done via local path dependencies in `pyproject.toml`.
