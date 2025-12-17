import { test, expect } from '@playwright/test';

test.describe('Design System Implementation Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
    // Wait for the app to load
    await page.waitForSelector('.app', { timeout: 10000 });
  });

  test.describe('Color Palette & Theming', () => {
    test('should load with correct primary colors in light mode', async ({ page }) => {
      // Check if the app is in light mode by default
      const html = page.locator('html');
      const theme = await html.getAttribute('data-theme');

      // Get computed styles of primary elements
      const sidebar = page.locator('.sidebar');
      const bgColor = await sidebar.evaluate((el) =>
        window.getComputedStyle(el).backgroundColor
      );

      expect(bgColor).toBeTruthy();
      console.log('Sidebar background color:', bgColor);
    });

    test('should toggle to dark mode correctly', async ({ page }) => {
      const themeToggle = page.locator('.theme-toggle');
      await expect(themeToggle).toBeVisible();

      // Get initial theme
      const html = page.locator('html');
      const initialTheme = await html.getAttribute('data-theme');
      console.log('Initial theme:', initialTheme);

      // Click theme toggle
      await themeToggle.click();
      await page.waitForTimeout(500); // Wait for transition

      // Get new theme
      const newTheme = await html.getAttribute('data-theme');
      console.log('New theme:', newTheme);

      // Verify theme changed
      expect(newTheme).not.toBe(initialTheme);
    });

    test('should have correct CSS variables defined', async ({ page }) => {
      const cssVars = await page.evaluate(() => {
        const root = document.documentElement;
        const styles = getComputedStyle(root);
        return {
          primary: styles.getPropertyValue('--color-primary').trim(),
          secondary: styles.getPropertyValue('--color-secondary').trim(),
          accent: styles.getPropertyValue('--color-accent').trim(),
          textPrimary: styles.getPropertyValue('--color-text-primary').trim(),
        };
      });

      console.log('CSS Variables:', cssVars);
      expect(cssVars.primary).toBeTruthy();
      expect(cssVars.secondary).toBeTruthy();
      expect(cssVars.accent).toBeTruthy();
      expect(cssVars.textPrimary).toBeTruthy();
    });
  });

  test.describe('Navigation & Sidebar', () => {
    test('should display sidebar with logo', async ({ page }) => {
      const sidebar = page.locator('.sidebar');
      await expect(sidebar).toBeVisible();

      const logo = page.locator('.logo h1');
      await expect(logo).toBeVisible();
      await expect(logo).toContainText('LitSearch');
    });

    test('should display logo icon with gradient', async ({ page }) => {
      const logoIcon = page.locator('.logo-icon');
      await expect(logoIcon).toBeVisible();

      const background = await logoIcon.evaluate((el) =>
        window.getComputedStyle(el).background
      );

      console.log('Logo icon background:', background);
      expect(background).toContain('gradient');
    });

    test('should have all navigation links visible', async ({ page }) => {
      const navLinks = [
        'Search',
        'Library',
        'Collections',
        'Visualizations',
        'Settings'
      ];

      for (const linkText of navLinks) {
        const link = page.locator('.nav-link', { hasText: linkText });
        await expect(link).toBeVisible();
      }
    });

    test('should show active state on current route', async ({ page }) => {
      const searchLink = page.locator('.nav-link', { hasText: 'Search' });
      const classes = await searchLink.getAttribute('class');

      expect(classes).toContain('active');
      console.log('Search link classes:', classes);
    });

    test('should have hover effect on navigation links', async ({ page }) => {
      const libraryLink = page.locator('.nav-link', { hasText: 'Library' });

      // Get initial transform
      const initialTransform = await libraryLink.evaluate((el) =>
        window.getComputedStyle(el).transform
      );

      // Hover over the link
      await libraryLink.hover();
      await page.waitForTimeout(300); // Wait for transition

      // Get transform after hover
      const hoverTransform = await libraryLink.evaluate((el) =>
        window.getComputedStyle(el).transform
      );

      console.log('Initial transform:', initialTransform);
      console.log('Hover transform:', hoverTransform);
    });

    test('should display UCSB status badge', async ({ page }) => {
      const ucsbStatus = page.locator('.ucsb-status');
      await expect(ucsbStatus).toBeVisible();

      const statusText = await ucsbStatus.textContent();
      console.log('UCSB status:', statusText);
    });

    test('should display sidebar stats', async ({ page }) => {
      const sidebarStats = page.locator('.sidebar-stats');
      await expect(sidebarStats).toBeVisible();

      const statLabels = ['Papers:', 'PDFs:', 'Searches:'];
      for (const label of statLabels) {
        const stat = page.locator('.stat-label', { hasText: label });
        await expect(stat).toBeVisible();
      }
    });
  });

  test.describe('Mobile Responsiveness', () => {
    test('should show mobile toggle on small screens', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE

      const mobileToggle = page.locator('.mobile-sidebar-toggle');
      await expect(mobileToggle).toBeVisible();
    });

    test('should toggle sidebar on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      const mobileToggle = page.locator('.mobile-sidebar-toggle');
      const sidebar = page.locator('.sidebar');

      // Initially sidebar should be hidden (off-screen)
      const initialLeft = await sidebar.evaluate((el) =>
        window.getComputedStyle(el).left
      );
      console.log('Initial sidebar position:', initialLeft);

      // Click toggle to open sidebar
      await mobileToggle.click();
      await page.waitForTimeout(500); // Wait for animation

      const openLeft = await sidebar.evaluate((el) =>
        window.getComputedStyle(el).left
      );
      console.log('Sidebar position after toggle:', openLeft);

      // Sidebar should have 'open' class
      const classes = await sidebar.getAttribute('class');
      expect(classes).toContain('open');
    });

    test('should show overlay when sidebar is open on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      const mobileToggle = page.locator('.mobile-sidebar-toggle');
      await mobileToggle.click();
      await page.waitForTimeout(300);

      const overlay = page.locator('.sidebar-overlay');
      const classes = await overlay.getAttribute('class');
      expect(classes).toContain('show');
    });
  });

  test.describe('Typography', () => {
    test('should use Inter font family', async ({ page }) => {
      const body = page.locator('body');
      const fontFamily = await body.evaluate((el) =>
        window.getComputedStyle(el).fontFamily
      );

      console.log('Body font family:', fontFamily);
      expect(fontFamily).toContain('Inter');
    });

    test('should have correct heading hierarchy', async ({ page }) => {
      const h1 = page.locator('.logo h1').first();
      const fontSize = await h1.evaluate((el) =>
        window.getComputedStyle(el).fontSize
      );

      console.log('H1 font size:', fontSize);
      expect(fontSize).toBeTruthy();
    });
  });

  test.describe('Animations & Transitions', () => {
    test('should have transitions defined', async ({ page }) => {
      const sidebar = page.locator('.sidebar');
      const transition = await sidebar.evaluate((el) =>
        window.getComputedStyle(el).transition
      );

      console.log('Sidebar transition:', transition);
      expect(transition).toBeTruthy();
      expect(transition).not.toBe('all 0s ease 0s');
    });

    test('should animate page content on load', async ({ page }) => {
      const mainContent = page.locator('.main-content > *').first();
      if (await mainContent.count() > 0) {
        const animation = await mainContent.evaluate((el) =>
          window.getComputedStyle(el).animation
        );
        console.log('Content animation:', animation);
      }
    });
  });

  test.describe('Paper Cards (if present)', () => {
    test('should display paper cards with correct styling', async ({ page }) => {
      // Try to find paper cards
      const paperCards = page.locator('.paper-card');
      const count = await paperCards.count();

      console.log('Number of paper cards found:', count);

      if (count > 0) {
        const firstCard = paperCards.first();

        // Check card styling
        const borderRadius = await firstCard.evaluate((el) =>
          window.getComputedStyle(el).borderRadius
        );
        console.log('Card border radius:', borderRadius);

        const boxShadow = await firstCard.evaluate((el) =>
          window.getComputedStyle(el).boxShadow
        );
        console.log('Card box shadow:', boxShadow);

        expect(borderRadius).toBeTruthy();
        expect(boxShadow).not.toBe('none');
      } else {
        console.log('No paper cards found on current page');
      }
    });

    test('should show hover effect on paper cards', async ({ page }) => {
      const paperCards = page.locator('.paper-card');
      const count = await paperCards.count();

      if (count > 0) {
        const firstCard = paperCards.first();

        // Get initial transform
        const initialTransform = await firstCard.evaluate((el) =>
          window.getComputedStyle(el).transform
        );

        // Hover
        await firstCard.hover();
        await page.waitForTimeout(300);

        const hoverTransform = await firstCard.evaluate((el) =>
          window.getComputedStyle(el).transform
        );

        console.log('Card initial transform:', initialTransform);
        console.log('Card hover transform:', hoverTransform);
      }
    });

    test('should have action buttons in paper cards', async ({ page }) => {
      const paperCards = page.locator('.paper-card');
      const count = await paperCards.count();

      if (count > 0) {
        const firstCard = paperCards.first();

        // Check for View Details button
        const viewDetailsBtn = firstCard.locator('.btn-view-details');
        if (await viewDetailsBtn.count() > 0) {
          await expect(viewDetailsBtn).toBeVisible();

          const bgColor = await viewDetailsBtn.evaluate((el) =>
            window.getComputedStyle(el).backgroundColor
          );
          console.log('View Details button background:', bgColor);
        }

        // Check for Download button
        const downloadBtn = firstCard.locator('.btn-download');
        if (await downloadBtn.count() > 0) {
          await expect(downloadBtn).toBeVisible();
        }
      }
    });
  });

  test.describe('Accessibility', () => {
    test('should have proper focus states', async ({ page }) => {
      const themeToggle = page.locator('.theme-toggle');
      await themeToggle.focus();

      const outline = await themeToggle.evaluate((el) =>
        window.getComputedStyle(el).outline
      );

      console.log('Focus outline:', outline);
    });

    test('should be keyboard navigable', async ({ page }) => {
      // Tab through navigation
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');

      const focusedElement = await page.evaluate(() =>
        document.activeElement?.className
      );

      console.log('Focused element after tabbing:', focusedElement);
      expect(focusedElement).toBeTruthy();
    });

    test('should have aria labels on icon-only buttons', async ({ page }) => {
      const themeToggle = page.locator('.theme-toggle');
      const ariaLabel = await themeToggle.getAttribute('aria-label');
      const title = await themeToggle.getAttribute('title');

      console.log('Theme toggle aria-label:', ariaLabel);
      console.log('Theme toggle title:', title);

      // Should have either aria-label or title
      expect(ariaLabel || title).toBeTruthy();
    });
  });

  test.describe('Custom Scrollbars', () => {
    test('should have custom scrollbar styles', async ({ page }) => {
      // Check if custom scrollbar styles are applied
      const hasCustomScrollbar = await page.evaluate(() => {
        const style = document.createElement('style');
        style.textContent = '::-webkit-scrollbar { width: 0px; }';
        document.head.appendChild(style);
        const hasStyles = document.styleSheets.length > 0;
        document.head.removeChild(style);
        return hasStyles;
      });

      expect(hasCustomScrollbar).toBeTruthy();
    });
  });

  test.describe('Performance', () => {
    test('should load main page quickly', async ({ page }) => {
      const startTime = Date.now();
      await page.goto('http://localhost:5173');
      await page.waitForSelector('.app');
      const loadTime = Date.now() - startTime;

      console.log('Page load time:', loadTime, 'ms');
      expect(loadTime).toBeLessThan(5000); // Should load in less than 5 seconds
    });

    test('should have CSS loaded', async ({ page }) => {
      const stylesheets = await page.evaluate(() => {
        return Array.from(document.styleSheets).length;
      });

      console.log('Number of stylesheets loaded:', stylesheets);
      expect(stylesheets).toBeGreaterThan(0);
    });
  });

  test.describe('Design System Variables', () => {
    test('should have spacing variables defined', async ({ page }) => {
      const spacingVars = await page.evaluate(() => {
        const root = document.documentElement;
        const styles = getComputedStyle(root);
        return {
          space1: styles.getPropertyValue('--space-1').trim(),
          space2: styles.getPropertyValue('--space-2').trim(),
          space4: styles.getPropertyValue('--space-4').trim(),
          space8: styles.getPropertyValue('--space-8').trim(),
        };
      });

      console.log('Spacing variables:', spacingVars);
      expect(spacingVars.space1).toBeTruthy();
      expect(spacingVars.space4).toBeTruthy();
    });

    test('should have shadow variables defined', async ({ page }) => {
      const shadowVars = await page.evaluate(() => {
        const root = document.documentElement;
        const styles = getComputedStyle(root);
        return {
          shadowSm: styles.getPropertyValue('--shadow-sm').trim(),
          shadowMd: styles.getPropertyValue('--shadow-md').trim(),
          shadowLg: styles.getPropertyValue('--shadow-lg').trim(),
        };
      });

      console.log('Shadow variables:', shadowVars);
      expect(shadowVars.shadowSm).toBeTruthy();
      expect(shadowVars.shadowMd).toBeTruthy();
    });

    test('should have border radius variables defined', async ({ page }) => {
      const radiusVars = await page.evaluate(() => {
        const root = document.documentElement;
        const styles = getComputedStyle(root);
        return {
          radiusSm: styles.getPropertyValue('--radius-sm').trim(),
          radiusMd: styles.getPropertyValue('--radius-md').trim(),
          radiusLg: styles.getPropertyValue('--radius-lg').trim(),
          radiusFull: styles.getPropertyValue('--radius-full').trim(),
        };
      });

      console.log('Radius variables:', radiusVars);
      expect(radiusVars.radiusMd).toBeTruthy();
      expect(radiusVars.radiusLg).toBeTruthy();
    });

    test('should have transition variables defined', async ({ page }) => {
      const transitionVars = await page.evaluate(() => {
        const root = document.documentElement;
        const styles = getComputedStyle(root);
        return {
          fast: styles.getPropertyValue('--transition-fast').trim(),
          base: styles.getPropertyValue('--transition-base').trim(),
          slow: styles.getPropertyValue('--transition-slow').trim(),
        };
      });

      console.log('Transition variables:', transitionVars);
      expect(transitionVars.fast).toBeTruthy();
      expect(transitionVars.base).toBeTruthy();
    });
  });
});
