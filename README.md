# CartSnitch

**Grocery price intelligence — know what you're paying, every time.**

CartSnitch is a self-hosted grocery price intelligence platform that connects to your store loyalty accounts, tracks prices across retailers, monitors shrinkflation, and helps you find the best deals.

---

## Project Overview

CartSnitch solves the problem of **grocery price opacity**. Most shoppers don't know if they're getting a good deal, whether prices have spiked since their last visit, or if the "sale" is actually a worse price than a competitor. CartSnitch makes prices transparent.

**Core features:**
- Connect Meijer, Kroger, Target loyalty accounts
- View purchase history across all stores in one timeline
- Track per-item price charts across stores over time
- Receive shrinkflation and price increase alerts
- Browse active coupons and deals
- Generate optimized shopping lists with store-split plans
- Public price transparency dashboards

---

## Architecture

CartSnitch is a polyglot microservices platform. The monorepo contains the frontend PWA and core services.

```
┌─────────────────────────────────────────────────────────────────┐
│                         CartSnitch PWA                          │
│                    (React, mobile-first PWA)                     │
└──────────┬────────────────────┬────────────────────┬───────────┘
           │                    │                    │
           ▼                    ▼                    ▼
┌──────────────────┐  ┌─────────────────┐  ┌─────────────────────┐
│   Auth Service   │  │   API Gateway   │  │  ReceiptWitness     │
│  (Better-Auth)   │  │ (Python/FastAPI)│  │   (Python/Scrapers) │
│  Session mgmt   │  │  REST + proxy   │  │  Purchase ingestion  │
└────────┬─────────┘  └────────┬────────┘  └──────────┬──────────┘
         │                      │                        │
         └──────────────────────┼────────────────────────┘
                                ▼
                   ┌────────────────────────┐
                   │   CloudNativePG (PGSQL) │
                   │   Shared database      │
                   └────────────────────────┘
```

### Services in This Repo

| Directory | Service | Description |
|-----------|---------|-------------|
| `/` (root) | Frontend | React PWA, mobile-first |
| `auth/` | Auth | Better-Auth service — session management, email/password, OAuth |
| `api/` | API Gateway | Frontend-facing REST API, Python/FastAPI |
| `common/` | Common | Shared Python models, Pydantic schemas, Alembic migrations |
| `receiptwitness/` | ReceiptWitness | Purchase data ingestion via retailer scrapers |

### Other CartSnitch Repos

| Repo | Service |
|------|---------|
| `cartsnitch/stickershock` | Price increase detection & CPI comparison |
| `cartsnitch/shrinkray` | Shrinkflation monitoring |
| `cartsnitch/clipartist` | Coupon/deal watching |
| `cartsnitch/infra` | Kubernetes manifests, Flux kustomizations |

---

## Tech Stack

### Frontend
- **React 18+** with TypeScript
- **Vite** — build tool
- **Tailwind CSS v4** — mobile-first responsive design
- **Workbox** — service worker, offline caching, PWA manifest
- **Recharts** — price trend visualizations
- **TanStack Query** — data fetching and caching
- **React Router v7** — client-side routing
- **Zustand** — lightweight state management

### Backend Services
- **Better-Auth** — authentication (session management, email/password, OAuth)
- **Node.js** (API Gateway)
- **Python/FastAPI** (API Gateway, ReceiptWitness)
- **PostgreSQL** via CloudNativePG
- **DragonflyDB** for caching

### Infrastructure
- **Kubernetes** (k3s-compatible)
- **Flux CD** — GitOps deployment
- **GitHub Actions** — CI/CD
- **CalVer** (`YYYY.MM.DD[.N]`) — image tagging
- **Bitnami Sealed Secrets** — secret management
- **Authentik** — OIDC/OAuth2 provider

---

## Getting Started

### Prerequisites

- Node.js 20+
- npm or pnpm
- PostgreSQL (local or containerized)
- Docker (for running services locally)

### Local Development

1. **Clone the repo**
   ```bash
   git clone https://github.com/cartsnitch/cartsnitch.git
   cd cartsnitch
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your local settings
   ```

4. **Start the frontend dev server**
   ```bash
   npm run dev
   ```
   The PWA will be available at `http://localhost:5173`.

5. **Run tests**
   ```bash
   npm test
   ```

6. **Build for production**
   ```bash
   npm run build
   ```

### Running Backend Services Locally

The frontend PWA communicates with three backend services. For full local development, you'll need to run each service:

```bash
# Auth service (Better-Auth)
cd auth
npm install
npm run dev

# API Gateway (separate repo: cartsnitch/api)
# See api/README.md

# ReceiptWitness (separate repo: cartsnitch/receiptwitness)
# See receiptwitness/README.md
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | API Gateway base URL | `http://localhost:3000` |
| `VITE_AUTH_URL` | Auth service base URL | `http://localhost:3001` |

---

## Contributing

We welcome contributions. Please follow the workflow below.

### Branching Strategy

- Branch from `dev`
- Use prefix: `feature/`, `fix/`, `docs/`, `chore/`
- Examples: `feature/shopping-list-optimization`, `fix/price-chart-zoom`

### Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add shopping list export
fix: correct price chart date formatting
docs: update API documentation
chore: update dependencies
```

### Pull Request Workflow

1. Open a PR against `dev`
2. CI must pass (lint, type check, tests, e2e)
3. QA reviews and approves
4. CTO merges to `dev`
5. Dev deploys automatically
6. CTO promotes `dev → uat`
7. UAT and security review
8. CEO merges `uat → main`
9. Production deploys automatically

**Never push directly to `main`, `dev`, or `uat`.**

### Code Standards

- ESLint for linting
- TypeScript strict mode
- Mobile-first responsive design
- Accessibility (WCAG 2.1 AA)

---

## Testing

### Unit Tests

```bash
npm test
```

### E2E Tests (Playwright)

```bash
npm run test:e2e
```

Tests run headless by default. For headed mode:

```bash
npm run test:e2e:headed
```

### Lighthouse CI

Performance audits run automatically in CI. To run locally:

```bash
npm run build
npm run preview
# In another terminal:
npx lighthouse http://localhost:4173 --output=html --output-path=./report/lighthouse.html
```

---

## CI/CD Pipeline

All branches (`main`, `dev`, `uat`) run through GitHub Actions on every push.

### Pipeline Stages

| Job | Trigger | Purpose |
|-----|---------|---------|
| `lint` | Every push | ESLint + TypeScript type check |
| `test` | Every push | Unit tests via Vitest |
| `audit` | Every push | Security vulnerability scan |
| `e2e` | Every push | Playwright end-to-end tests |
| `lighthouse` | After test | Performance budget check |
| `build-and-push` | On push to main/dev/uat | Build and push Docker images to GHCR |
| `deploy-dev` | On push to dev or main | Update `cartsnitch/infra` → auto-deploy to dev |
| `deploy-uat` | On push to uat or main | Update `cartsnitch/infra` → auto-deploy to uat |

### Image Tagging

- **Production (`main`):** CalVer tag (`YYYY.MM.DD[.N]`) + `latest`
- **Development (`dev`):** SHA tag (`sha-<short-sha>`)

### Deployment Environments

| Environment | Namespace | URL | Trigger |
|-------------|-----------|-----|---------|
| Dev | `cartsnitch-dev` | `cartsnitch.dev.farh.net` | Push to `dev` branch |
| UAT | `cartsnitch-uat` | `cartsnitch.uat.farh.net` | Push to `uat` branch |
| Production | `cartsnitch` | `cartsnitch.farh.net` | Push to `main` branch |

---

## Deployment

### Infrastructure

The infrastructure repository ([cartsnitch/infra](https://github.com/cartsnitch/infra)) contains Kubernetes manifests and Flux Kustomize overlays.

### Flux GitOps Flow

1. CI builds and pushes a new Docker image
2. CI opens a PR to `cartsnitch/infra` updating the image tag
3. On merge, Flux reconciles the manifests and rolls out the new image

### Forcing a Rollout

To force pods to pick up a new `:latest` image:

```bash
kubectl rollout restart deployment/<name> -n <namespace>
```

### Secrets

Secrets are managed via **Bitnami Sealed Secrets**. No plain Kubernetes secrets are used.

---

## Related Projects

- [StickerShock](https://github.com/cartsnitch/stickershock) — Price increase detection
- [ShrinkRay](https://github.com/cartsnitch/shrinkray) — Shrinkflation monitoring
- [ClipArtist](https://github.com/cartsnitch/clipartist) — Coupon/deal optimization
- [Infra](https://github.com/cartsnitch/infra) — Kubernetes infrastructure

---

## License

MIT &copy; 2025 CartSnitch
