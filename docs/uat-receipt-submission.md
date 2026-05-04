# UAT Receipt Submission Path

**Issue:** [CAR-812](/CAR/issues/CAR-812)
**Author:** Barcode Betty
**Date:** 2026-05-04

---

## Overview

The UAT environment supports receipt submission via **inbound email**. This is the only supported submission method in UAT — there is no public REST API surface for receipt ingestion.

---

## How It Works

### Architecture

```
User composes email
    ↓
Email sent to <user_token>@cartsnitch.<env>.farh.net
    ↓
Mailgun webhook receives the email
    ↓
Email job enqueued to DragonflyDB stream: email:receipts
    ↓
email-worker (ReceiptWitness) consumes the job
    ↓
Worker resolves user via email_inbound_token lookup in DB
    ↓
Retailer detected from email content (meijer / kroger / target)
    ↓
Email parsed into Purchase + PurchaseItem records
    ↓
receipt.ingested event published to Redis
    ↓
MatchResult created with method=upc, confidence=1.0 for known UPCs
```

### Key Components

| Component | Location | Role |
|-----------|----------|------|
| `users.email_inbound_token` | DB (migration `001_add_email_inbound_token`) | 22-char unique token per user; used as email routing identifier |
| `email:receipts` stream | DragonflyDB | Queue holding pending email jobs |
| `email-worker` | `receiptwitness/src/receiptwitness/worker/email_worker.py` | Async worker consuming the stream |
| `BaseEmailParser` | `receiptwitness/src/receiptwitness/parsers/email/base.py` | Abstract parser; subclasses for meijer/kroger/target |
| Retailer detectors | `receiptwitness/src/receiptwitness/parsers/email/detector.py` | Sifts sender/subject to pick the right parser |

### Email Address Format

Each user is assigned a unique inbound token. The email address format depends on the environment:

| Environment | Domain |
|-------------|--------|
| Dev | `cartsnitch.dev.farh.net` |
| UAT | `cartsnitch.uat.farh.net` |

**Address:** `<email_inbound_token>@cartsnitch.<env>.farh.net`

To find a user's token in the UAT database (requires `kubectl` access to `cartsnitch-uat`):

```bash
kubectl exec -n cartsnitch-uat deployment/cartsnitch-api -- \\
  python -c "from cartsnitch_common.database import get_sync_session; \\
  from cartsnitch_common.models.user import User; \\
  from sqlalchemy import select; \\
  s = get_sync_session('postgresql://cartsnitch:cartsnitch@cartsnitch-pg-rw:5432/cartsnitch'); \\
  u = s.execute(select(User).where(User.email=='dottie@example.com')).scalar_one(); \\
  print(u.email_inbound_token)"
```

---

## Submitting a Test Receipt (Step-by-Step)

### Prerequisites

- A test user account in UAT with a known `email_inbound_token`
- A sample receipt email with a **known UPC** from the seeded `normalized_products` table

### Steps

1. **Obtain the test user's inbound token.**
   Use the UAT Settings → Account page in the UI, or query the DB directly (see above).

2. **Compose the email.**
   Send to: `<token>@cartsnitch.uat.farh.net`
   Subject: anything
   Body: plain-text or HTML receipt content

3. **Expected behavior after email is processed:**
   - A `Receipt` row is created in `purchases`
   - `PurchaseItem` rows are created with `upc` matching the seeded product UPC
   - A `MatchResult` is created with `method='upc'` and `confidence=1.0`

---

## Sample Receipt for Dottie's Regression

> **TODO — to be filled in after running the seed against UAT (Step 3 of CAR-812):**
> - `id`: <product-id-from-uat-db>
> - `name`: <product-name-from-uat-db>
> - `sample UPC`: <upc-from-upc_variants-jsonb>
>
> Paste these after running `bash scripts/seed-env.sh uat` and querying the DB.

### Meijer Sample Receipt (plain text)

```
Meijer
===================================
Purchase Date: 03/15/2026
Store: Meijer #127 - Ann Arbor, MI
-----------------------------------
 1 x Organic Whole Milk 1gal      $4.99
 1 x Whole Wheat Bread            $3.29
 1 x Bananas (2 lb)               $0.67
 1 x Chicken Breast (3 lb)       $12.47
 1 x Cheddar Cheese Block 8oz     $5.99
-----------------------------------
Subtotal:                       $27.41
Tax:                             $1.93
Total:                          $29.34
===================================
THANK YOU FOR SHOPPING MEIJER
===================================
```

> **Note:** The `email-worker` parses the email body and extracts line items by retailer. The exact format and field mapping depends on the retailer parser. For Meijer, the parser looks for item lines matching `(\d+) x (.+?)\s+\$([\d.]+)`. UPCs in the `upc_variants` JSONB of seeded products will be matched during the normalization step.

### Kroger Sample Receipt (plain text)

```
KROGER
===================================
Purchase Date: 03/15/2026
Store: KROGER #412 - Ann Arbor MI
-----------------------------------
 1 Organic Whole Milk 1gal        $5.29
 1 Whole Wheat Bread              $3.49
 1 Bananas (2 lb)                 $0.69
 1 Chicken Breast (3 lb)         $11.99
 1 Sharp Cheddar Cheese 8oz       $4.99
-----------------------------------
Subtotal:                       $26.45
Tax:                             $1.85
Total:                          $28.30
===================================
```

### Target Sample Receipt (plain text)

```
TARGET
===================================
03/15/2026  14:32
Store: 0874 Ann Arbor, MI
===================================
 1  Organic Whole Milk 1G         $5.49
 1  Whole Wheat Bread             $3.29
 1  Bananas LB 2                  $0.68
 1  Chicken Breast 3#             $12.99
 1  Cheddar Cheese 8OZ           $5.79
-----------------------------------
Subtotal:                       $28.24
Tax (6%):                        $1.69
Total:                          $29.93
===================================
```

---

## Troubleshooting

### Email not processed

1. Check the `email:receipts` stream has messages:
   ```bash
   kubectl exec -n cartsnitch-uat deploy/email-worker -- python -c \\
     "import asyncio; from receiptwitness.queue.email import get_redis; \\
     async def chk(): c = await get_redis(); info = await c.xinfo_stream('email:receipts'); print(info); \\
     asyncio.run(chk())"
   ```

2. Check `email-worker` logs for retailer detection failures:
   ```bash
   kubectl logs -n cartsnitch-uat deploy/email-worker -f
   ```

3. Verify the token resolves to a user in the DB:
   ```bash
   kubectl exec -n cartsnitch-uat deploy/cartsnitch-api -- \\
     python -c "from cartsnitch_common.database import get_sync_session; \\
     from cartsnitch_common.models.user import User; \\
     from sqlalchemy import select; \\
     s = get_sync_session('postgresql://...'); \\
     r = s.execute(select(User.email_inbound_token).limit(5)).all(); \\
     print(r)"
   ```

### No MatchResult created

The normalization pipeline requires a `normalized_product` row with the submitted UPC in `upc_variants`. If the seed was run, the product should be found. Check the `match_results` table after submission:

```sql
SELECT mr.*, np.canonical_name
FROM match_results mr
JOIN normalized_products np ON np.id = mr.normalized_product_id
WHERE mr.match_method = 'upc'
ORDER BY mr.created_at DESC
LIMIT 10;
```

---

## Related Files

| File | Role |
|------|------|
| `common/alembic/versions/001_add_email_inbound_token.py` | Adds `email_inbound_token` column |
| `receiptwitness/src/receiptwitness/worker/email_worker.py` | Consumes email jobs from stream |
| `receiptwitness/src/receiptwitness/queue/email.py` | DragonflyDB stream consumer group |
| `receiptwitness/src/receiptwitness/parsers/email/detector.py` | Retailer detection |
| `receiptwitness/src/receiptwitness/parsers/email/meijer.py` | Meijer email parser |
| `receiptwitness/src/receiptwitness/parsers/email/kroger.py` | Kroger email parser |
| `receiptwitness/src/receiptwitness/parsers/email/target.py` | Target email parser |
| `docs/uat-runbook.md` | UAT runbook (defect classification, entry/exit criteria) |