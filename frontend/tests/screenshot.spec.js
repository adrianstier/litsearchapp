import { test } from '@playwright/test';

test('capture current design', async ({ page }) => {
  await page.goto('http://localhost:5173/');
  await page.waitForLoadState('networkidle');
  await page.screenshot({ path: 'current-design.png', fullPage: true });
});
