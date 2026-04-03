"""Integration tests for purchase endpoints."""

import secrets
import uuid
from datetime import UTC, datetime, date, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import text

from cartsnitch_api.models import Purchase, PurchaseItem, Store


@pytest.fixture
async def purchase_data(db_engine):
    """Seed a user, store, purchase, and items using session-cookie auth."""
    factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        user_id = str(uuid.uuid4())
        session_token = secrets.token_urlsafe(32)
        now = datetime.now(UTC).isoformat()
        expires = (datetime.now(UTC) + timedelta(days=7)).isoformat()

        # Create the user
        await session.execute(
            text(
                "INSERT INTO users (id, email, hashed_password, display_name, email_inbound_token, created_at, updated_at) "
                "VALUES (:id, :email, :hashed_password, :display_name, :email_inbound_token, :created_at, :updated_at)"
            ),
            {
                "id": user_id,
                "email": "buyer@example.com",
                "hashed_password": "not-used-with-better-auth",
                "display_name": "Buyer",
                "email_inbound_token": secrets.token_urlsafe(16),
                "created_at": now,
                "updated_at": now,
            },
        )

        # Create the session
        await session.execute(
            text(
                "INSERT INTO sessions (id, token, user_id, expires_at, created_at, updated_at) "
                "VALUES (:id, :token, :user_id, :expires_at, :created_at, :updated_at)"
            ),
            {
                "id": str(uuid.uuid4()),
                "token": session_token,
                "user_id": user_id,
                "expires_at": expires,
                "created_at": now,
                "updated_at": now,
            },
        )

        # Create the store
        store = Store(name="Kroger", slug="kroger", id=uuid.uuid4())
        session.add(store)
        await session.flush()
        await session.refresh(store)

        # Create the purchase
        purchase = Purchase(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id),
            store_id=store.id,
            receipt_id="receipt-001",
            purchase_date=date(2026, 3, 10),
            total=Decimal("42.50"),
        )
        session.add(purchase)
        await session.flush()
        await session.refresh(purchase)

        # Create the purchase item
        item = PurchaseItem(
            id=uuid.uuid4(),
            purchase_id=purchase.id,
            product_name_raw="Organic Milk 1gal",
            quantity=Decimal("1"),
            unit_price=Decimal("5.99"),
            extended_price=Decimal("5.99"),
        )
        session.add(item)
        await session.commit()

        return {
            "user_id": user_id,
            "store": store,
            "purchase": purchase,
            "headers": {"Cookie": f"better-auth.session_token={session_token}"},
        }


@pytest.mark.asyncio
async def test_list_purchases(client, purchase_data):
    resp = await client.get("/purchases", headers=purchase_data["headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["store_name"] == "Kroger"
    assert data[0]["total"] == 42.50


@pytest.mark.asyncio
async def test_get_purchase_detail(client, purchase_data):
    pid = str(purchase_data["purchase"].id)
    resp = await client.get(f"/purchases/{pid}", headers=purchase_data["headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["line_items"]) == 1
    assert data["line_items"][0]["name"] == "Organic Milk 1gal"


@pytest.mark.asyncio
async def test_get_purchase_not_found(client, auth_headers):
    resp = await client.get(f"/purchases/{uuid.uuid4()}", headers=auth_headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_purchase_stats(client, purchase_data):
    resp = await client.get("/purchases/stats", headers=purchase_data["headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_spent"] == 42.50
    assert data["purchase_count"] == 1
    assert "Kroger" in data["by_store"]
