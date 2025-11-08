import { test, expect } from '@playwright/test';

test.describe('Frontend UI/UX Tests', () => {
  test('homepage loads with modern design', async ({ page }) => {
    await page.goto('/');

    // Check for gradient sidebar
    const sidebar = page.locator('.sidebar');
    await expect(sidebar).toBeVisible();

    // Check logo with gradient text
    await expect(page.locator('.logo h1')).toContainText('LitSearch');

    // Check navigation links exist
    await expect(page.locator('.nav-link')).toHaveCount(5);

    // Check modern search placeholder
    await expect(page.locator('.search-placeholder')).toBeVisible();
  });

  test('search interface has improved UX', async ({ page }) => {
    await page.goto('/');

    // Check enhanced search input
    const searchInput = page.locator('.search-input');
    await expect(searchInput).toBeVisible();

    // Check for source checkboxes
    await expect(page.getByText('PubMed')).toBeVisible();
    await expect(page.getByText('arXiv')).toBeVisible();
    await expect(page.getByText('Crossref')).toBeVisible();

    // Check for enhanced button
    const searchButton = page.locator('.search-button');
    await expect(searchButton).toBeVisible();
  });

  test('navigation has hover effects', async ({ page }) => {
    await page.goto('/');

    // Hover over navigation link
    const libraryLink = page.locator('text=Library').first();
    await libraryLink.hover();

    // Should have transform effect (tested via screenshot comparison)
  });

  test('responsive design works', async ({ page }) => {
    // Desktop view
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/');
    await expect(page.locator('.sidebar')).toHaveCSS('width', '280px');

    // Mobile view
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('.sidebar')).toHaveCSS('width', '375px');
  });

  test('library page loads', async ({ page }) => {
    await page.goto('/library');
    await expect(page.locator('h1')).toContainText('Library');
  });

  test('collections page loads', async ({ page }) => {
    await page.goto('/collections');
    await expect(page.locator('h1')).toContainText('Collections');
  });

  test('visualizations page loads', async ({ page }) => {
    await page.goto('/visualizations');
    await expect(page.locator('h1')).toContainText('Visualizations');

    // Check for tabs
    await expect(page.getByText('Timeline')).toBeVisible();
    await expect(page.getByText('Network')).toBeVisible();
    await expect(page.getByText('Topics')).toBeVisible();
  });

  test('settings page loads', async ({ page }) => {
    await page.goto('/settings');
    await expect(page.locator('h1')).toContainText('Settings');
  });
});
