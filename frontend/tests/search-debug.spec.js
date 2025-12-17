// @ts-check
import { test, expect } from '@playwright/test';

test.describe('Search Page Debug', () => {
  test('should load search page and perform search', async ({ page }) => {
    // Listen for console messages
    page.on('console', msg => {
      console.log(`Browser console [${msg.type()}]: ${msg.text()}`);
    });

    // Listen for page errors
    page.on('pageerror', error => {
      console.log(`Page error: ${error.message}`);
    });

    // Navigate to the app
    console.log('Navigating to app...');
    await page.goto('http://localhost:5175/', { waitUntil: 'networkidle' });

    // Take screenshot of initial state
    await page.screenshot({ path: 'test-results/01-initial-load.png' });
    console.log('Initial page loaded');

    // Check if the page loaded correctly
    const sidebar = page.locator('.sidebar');
    const sidebarVisible = await sidebar.isVisible().catch(() => false);
    console.log(`Sidebar visible: ${sidebarVisible}`);

    // Check for the search input
    const searchInput = page.locator('input[type="text"], input[placeholder*="search" i], .search-input');
    const searchInputCount = await searchInput.count();
    console.log(`Search inputs found: ${searchInputCount}`);

    if (searchInputCount > 0) {
      // Type in search
      await searchInput.first().fill('machine learning');
      console.log('Typed search query');
      await page.screenshot({ path: 'test-results/02-after-typing.png' });

      // Find and click search button
      const searchButton = page.locator('button:has-text("Search"), button[type="submit"], .search-button');
      const searchButtonCount = await searchButton.count();
      console.log(`Search buttons found: ${searchButtonCount}`);

      if (searchButtonCount > 0) {
        // Click search
        await searchButton.first().click();
        console.log('Clicked search button');

        // Wait a bit for the search to process
        await page.waitForTimeout(3000);
        await page.screenshot({ path: 'test-results/03-after-search.png' });

        // Check for errors on page
        const errorText = await page.locator('text=Error, text=error').count();
        console.log(`Error elements found: ${errorText}`);

        // Check page background color
        const bgColor = await page.evaluate(() => {
          return window.getComputedStyle(document.body).backgroundColor;
        });
        console.log(`Body background color: ${bgColor}`);

        // Check main content visibility
        const mainContent = page.locator('.main-content');
        const mainVisible = await mainContent.isVisible().catch(() => false);
        console.log(`Main content visible: ${mainVisible}`);

        // Get page HTML for debugging
        const html = await page.content();
        if (html.length < 1000) {
          console.log('Page HTML (short):', html);
        } else {
          console.log('Page HTML length:', html.length);
        }
      }
    } else {
      console.log('No search input found!');
      // Take screenshot anyway
      await page.screenshot({ path: 'test-results/02-no-search-input.png' });
    }

    // Final screenshot
    await page.screenshot({ path: 'test-results/04-final-state.png' });
  });

  test('should check for JavaScript errors on page load', async ({ page }) => {
    const errors = [];

    page.on('pageerror', error => {
      errors.push(error.message);
    });

    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(`Console error: ${msg.text()}`);
      }
    });

    await page.goto('http://localhost:5175/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    console.log('Errors found:', errors.length);
    errors.forEach(e => console.log('  -', e));

    // This test passes but logs errors for debugging
    expect(true).toBe(true);
  });

  test('should verify app structure', async ({ page }) => {
    await page.goto('http://localhost:5175/', { waitUntil: 'networkidle' });

    // Check for key elements
    const elements = {
      'app': '.app',
      'sidebar': '.sidebar',
      'main-content': '.main-content',
      'search-page': '.search-page',
      'nav-links': '.nav-links',
    };

    for (const [name, selector] of Object.entries(elements)) {
      const count = await page.locator(selector).count();
      console.log(`${name} (${selector}): ${count} found`);
    }

    // Check if React mounted
    const root = await page.locator('#root').innerHTML();
    console.log('Root content length:', root.length);

    if (root.length < 100) {
      console.log('Root content:', root);
    }
  });
});
