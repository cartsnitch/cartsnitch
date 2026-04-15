import { test, expect } from '@playwright/test';

const uniqueEmail = () => `betty+e2e-${Date.now()}@cartsnitch.test`;

test.describe('J1: Registration and Login', () => {
  test('shows check your email page after registration', async ({ page }) => {
    await page.goto('/register');
    await page.fill('[placeholder="Full Name"]', 'Betty Tester');
    await page.fill('[placeholder="Email"]', uniqueEmail());
    await page.fill('[placeholder="Password (min. 8 characters)"]', 'TestPass123!');
    await page.click('button[type="submit"]');

    await expect(page.getByRole('heading', { name: /check your email/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /resend email/i })).toBeVisible();
  });

  test('shows validation error when registration fields are empty', async ({ page }) => {
    await page.goto('/register');
    await page.click('button[type="submit"]');

    await expect(page.locator('.bg-red-50')).toContainText('Please fill in all fields');
  });

  test('can navigate from register to login', async ({ page }) => {
    await page.goto('/register');
    await page.getByRole('link', { name: /sign in/i }).click();

    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByRole('heading', { name: /cartsnitch/i })).toBeVisible();
  });

});
