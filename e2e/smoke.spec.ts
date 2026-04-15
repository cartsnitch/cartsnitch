import { test, expect, mockAuthRoutes } from './fixtures';

test('app loads', async ({ page }) => {
  mockAuthRoutes(page, false);
  await page.goto('/');
  // Unauthenticated users are redirected to /login
  await expect(page).toHaveURL(/\/login/);
  await expect(page.getByRole('heading', { name: /CartSnitch/i })).toBeVisible();
});
