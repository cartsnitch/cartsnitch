import { test, expect } from '@playwright/test';
import { mockAuthRoutes } from '../fixtures';

test.describe('J8: Unauthenticated Access', () => {
  test('redirects /dashboard (/) to /login when not authenticated', async ({ page }) => {
    mockAuthRoutes(page, false);
    await page.context().clearCookies();
    await page.goto('/');

    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByRole('heading', { name: /cartsnitch/i })).toBeVisible();
  });

  test('redirects /purchases to /login when not authenticated', async ({ page }) => {
    mockAuthRoutes(page, false);
    await page.context().clearCookies();
    await page.goto('/purchases');

    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByRole('heading', { name: /cartsnitch/i })).toBeVisible();
  });

  test('redirects /products to /login when not authenticated', async ({ page }) => {
    mockAuthRoutes(page, false);
    await page.context().clearCookies();
    await page.goto('/products');

    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByRole('heading', { name: /cartsnitch/i })).toBeVisible();
  });

  test('redirects /coupons to /login when not authenticated', async ({ page }) => {
    mockAuthRoutes(page, false);
    await page.context().clearCookies();
    await page.goto('/coupons');

    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByRole('heading', { name: /cartsnitch/i })).toBeVisible();
  });

  test('shows loading spinner while auth session is pending', async ({ page }) => {
    mockAuthRoutes(page, false);
    await page.context().clearCookies();
    await page.goto('/purchases');
    await expect(page).toHaveURL(/\/login/, { timeout: 10_000 });
  });
});
