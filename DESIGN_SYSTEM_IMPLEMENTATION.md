# LitSearch Design System Implementation

## Overview

This document outlines the comprehensive design system implemented for LitSearch, transforming it from a functional prototype into a modern, professional academic research platform that rivals commercial tools like ResearchRabbit.

## Design Philosophy

**Core Principles:**
1. **Academic Professionalism** - Trust, credibility, intelligence
2. **Modern Aesthetics** - Clean, minimal, breathable
3. **Content First** - Information hierarchy that prioritizes research content
4. **Delightful Interactions** - Smooth animations and microinteractions
5. **Accessibility** - WCAG compliant, keyboard navigation, reduced motion support

---

## Color Palette

### Primary Colors
```css
--color-primary: #2563EB        /* Deep Blue - Trust, academia, intelligence */
--color-primary-dark: #1E40AF   /* Hover/active states */
--color-primary-light: #3B82F6  /* Light accents */
```

**Usage:** Primary actions, links, active navigation, focus states

### Secondary Colors
```css
--color-secondary: #10B981      /* Emerald - Growth, discovery, connections */
--color-secondary-dark: #059669
--color-secondary-light: #34D399
```

**Usage:** Download buttons, success states, growth metrics

### Accent Colors
```css
--color-accent: #F59E0B         /* Amber - Highlights, citations, warmth */
--color-accent-dark: #D97706
--color-accent-light: #FBBF24
```

**Usage:** Citation highlights, important metadata, special badges

### Semantic Colors
```css
--color-success: #22C55E        /* Green - Success states */
--color-warning: #F97316        /* Orange - Warnings */
--color-error: #EF4444          /* Red - Errors */
--color-info: #06B6D4           /* Cyan - Information */
```

**Usage:** Status messages, notifications, alerts

### Neutral Colors

**Light Mode:**
```css
--color-bg-primary: #F8FAFC     /* Main background */
--color-bg-secondary: #FFFFFF   /* Cards, surfaces */
--color-bg-tertiary: #F1F5F9    /* Input backgrounds, subtle areas */
--color-text-primary: #0F172A   /* Main text */
--color-text-secondary: #475569 /* Secondary text */
--color-text-tertiary: #94A3B8  /* Muted text */
--color-border: #E2E8F0         /* Default borders */
```

**Dark Mode:**
```css
--color-bg-primary: #0F172A     /* Deep slate - Main background */
--color-bg-secondary: #1E293B   /* Lighter slate - Cards */
--color-bg-tertiary: #334155    /* Even lighter - Inputs */
--color-text-primary: #F1F5F9   /* Almost white */
--color-text-secondary: #CBD5E1 /* Slate gray */
--color-text-tertiary: #94A3B8  /* Muted slate */
--color-border: #334155         /* Subtle borders */
```

---

## Typography

### Font Families
```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif
--font-mono: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace
```

**Inter:** Clean, modern, excellent screen readability. Used for all UI text.
**JetBrains Mono:** For DOIs, code snippets, technical identifiers.

### Font Scale
```css
--text-xs: 0.75rem    /* 12px - Labels, badges */
--text-sm: 0.875rem   /* 14px - Secondary text */
--text-base: 1rem     /* 16px - Body text */
--text-lg: 1.125rem   /* 18px - Paper titles (cards) */
--text-xl: 1.25rem    /* 20px - Section headings */
--text-2xl: 1.5rem    /* 24px - Page headings, logo */
--text-3xl: 1.875rem  /* 30px - Major headings */
--text-4xl: 2.25rem   /* 36px - Hero headings */
```

### Font Weights
```css
--font-normal: 400    /* Body text */
--font-medium: 500    /* Emphasized text, labels */
--font-semibold: 600  /* Active states, important text */
--font-bold: 700      /* Headings, titles */
--font-extrabold: 800 /* Logo, major emphasis */
```

### Line Heights
```css
--leading-tight: 1.25    /* Headings */
--leading-normal: 1.5    /* Body text */
--leading-relaxed: 1.75  /* Long-form content */
```

---

## Spacing System

**8px Base Grid:**
```css
--space-1: 0.25rem   /* 4px */
--space-2: 0.5rem    /* 8px */
--space-3: 0.75rem   /* 12px */
--space-4: 1rem      /* 16px */
--space-5: 1.25rem   /* 20px */
--space-6: 1.5rem    /* 24px */
--space-8: 2rem      /* 32px */
--space-10: 2.5rem   /* 40px */
--space-12: 3rem     /* 48px */
--space-16: 4rem     /* 64px */
```

**Usage:**
- Inner padding: space-3 to space-6
- Component spacing: space-4 to space-8
- Section spacing: space-8 to space-16

---

## Border Radius

```css
--radius-sm: 6px      /* Small buttons, pills */
--radius-md: 8px      /* Default buttons, inputs */
--radius-lg: 12px     /* Cards, containers */
--radius-xl: 16px     /* Large containers */
--radius-full: 9999px /* Circular badges, pills */
```

---

## Shadows

**Layered Elevation System:**
```css
--shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.05)       /* Subtle borders */
--shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1)        /* Default cards */
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07)       /* Hover states */
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1)      /* Dropdowns, modals */
--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15)     /* Major elevations */
--shadow-card: 0 1px 3px rgba(0, 0, 0, 0.1)      /* Paper cards */
--shadow-card-hover: 0 4px 12px rgba(0, 0, 0, 0.15) /* Card hover */
```

**Dark Mode:** Shadows are deeper with higher opacity for better visibility.

---

## Components

### Paper Cards

**Design Features:**
- 12px border radius for modern feel
- Subtle shadow with hover elevation
- 4px gradient left border on hover (blue → green)
- Organized sections: header, abstract, metadata, actions
- Microinteraction: translateY(-2px) on hover

**Color-Coded Source Badges:**
- PubMed: Green (#22C55E)
- arXiv: Red (#EF4444)
- Crossref: Cyan (#06B6D4)
- Semantic Scholar: Blue (#2563EB)
- OpenAlex: Amber (#F59E0B)

**Action Buttons:**
- Primary (View Details): Solid blue, prominent
- Secondary (Download): Emerald green, gradient for UCSB access
- Tertiary (External links): Outlined, hover blue

### Navigation

**Sidebar Design:**
- 240px width (280px expanded)
- Sticky positioning for persistent access
- Custom scrollbar with primary color
- Logo with gradient icon (36x36px)
- Badge counters for library/collections

**Nav Link States:**
- Default: Muted text, no background
- Hover: Light background, translateX(4px), icon scale(1.1)
- Active: Primary color, 4px left border, bold weight

**UCSB Status Badge:**
- Authenticated: Green background, success border
- Not Authenticated: Red background, error border
- Hover: Lift effect (translateY(-2px))

### Buttons

**Primary Buttons:**
```css
Background: var(--color-primary)
Color: white
Padding: 12px 20px
Border Radius: 8px
Font Weight: 600
Hover: Darker shade + translateY(-1px) + shadow
```

**Secondary Buttons:**
```css
Background: var(--color-secondary)
(Same other properties as primary)
```

**Outlined Buttons:**
```css
Background: Transparent
Border: 1px solid var(--color-border)
Color: var(--color-text-primary)
Hover: Primary color background + border
```

**Icon Buttons:**
```css
Size: 32x32px
Border Radius: 8px
Hover: Scale(1.05) + color change
```

### Forms & Inputs

**Text Inputs:**
```css
Height: 40px
Border Radius: 8px
Border: 1px solid var(--color-border)
Focus: Primary color ring (2px), primary border
Background: Surface color
```

**Search Bar:**
```css
Height: 48px
Border Radius: 24px (full rounded)
Prominent placement
Icon prefix
```

### Tabs

**Tab Navigation:**
```css
Horizontal layout
Active: Bottom border (4px primary), bold weight
Hover: Background color change
Badge counts in top-right
```

### Badges & Pills

**Design:**
```css
Padding: 4px 12px (vertical, horizontal)
Border Radius: 9999px (full)
Font Size: 12px
Font Weight: 600
Border: 1px solid (30% opacity of color)
Background: Translucent color (10% opacity)
```

---

## Animations & Transitions

### Transition Speeds
```css
--transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1)   /* Quick responses */
--transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1)   /* Default */
--transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1)   /* Deliberate */
```

### Keyframe Animations

**Shimmer (Loading):**
```css
@keyframes shimmer {
  0% { background-position: -1000px 0; }
  100% { background-position: 1000px 0; }
}
```

**Pulse:**
```css
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
```

**Slide Up (Page Entry):**
```css
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

**Slide Down (Dropdowns):**
```css
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

**Spin (Loading Icons):**
```css
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

### Microinteractions

1. **Button Hover:** Color change + slight lift (translateY(-1px)) + shadow increase
2. **Card Hover:** Lift (translateY(-2px)) + shadow increase + left border gradient reveal
3. **Icon Hover:** Scale(1.05-1.1) + color change
4. **Nav Link Hover:** Background color + slide right (translateX(4px)) + icon scale
5. **Badge Hover:** Scale(1.05)
6. **Download Success:** Checkmark animation + green status banner slide in
7. **Menu Open:** Slide down + fade in
8. **Page Load:** Slide up + fade in

---

## Layout Structure

### Desktop (> 768px)
```
┌─────────────────────────────────────────┐
│  Sidebar (240px)  │  Main Content       │
│  - Logo           │  - Padding: 48px    │
│  - Nav Links      │  - Max Width: 1400px│
│  - Footer Status  │  - Centered         │
└─────────────────────────────────────────┘
```

### Tablet (768px - 1024px)
```
┌─────────────────────────────────────────┐
│  Sidebar (260px)  │  Main Content       │
│                   │  - Padding: 40px 24px│
└─────────────────────────────────────────┘
```

### Mobile (< 768px)
```
┌─────────────────────────────────────────┐
│  ☰ Toggle Button (Fixed top-left)      │
│                                         │
│  Main Content (Full Width)              │
│  - Padding: 24px 16px                   │
│  - Top padding: 5rem (for toggle)       │
│                                         │
│  [Sidebar slides in from left]          │
└─────────────────────────────────────────┘
```

**Mobile Sidebar:**
- Fixed position
- Slides in from -100% to 0
- 280px width (or 100% on small mobile)
- Dark overlay backdrop with blur
- Closes on outside click or navigation

---

## Dark Mode Implementation

**Theme Toggle:**
- Located in sidebar header (top-right of logo)
- Moon icon (dark mode) / Sun icon (light mode)
- Smooth color transitions (200ms)
- Persisted to localStorage

**Dark Mode Adjustments:**
1. Background uses slate scale (#0F172A to #334155)
2. Reduce pure white to off-white (#F1F5F9)
3. Increase elevation through lighter grays, not shadows
4. Maintain color accent intensity
5. Soften graphs (less saturation)
6. Deeper shadows with higher opacity

**Color Inversion Strategy:**
- Light BG → Dark BG
- Dark text → Light text
- Keep semantic colors vibrant
- Adjust opacity for readability

---

## Responsive Breakpoints

```css
/* Small Mobile */
@media (max-width: 480px) {
  Font size: 14px base
  Sidebar: 100% width
  Padding reduced
}

/* Mobile */
@media (max-width: 768px) {
  Sidebar: Hidden (slide-in)
  Mobile toggle: Visible
  Bottom nav: Optional
  Single column layouts
}

/* Tablet */
@media (max-width: 1024px) {
  Sidebar: 260px
  Content padding: Reduced
  Some 2-column → 1-column
}

/* Desktop */
@media (min-width: 1025px) {
  Sidebar: 240px (sticky)
  Full multi-column layouts
  Max content width: 1400px
}
```

---

## Accessibility Features

1. **Keyboard Navigation:**
   - All interactive elements focusable
   - Visible focus states (2px primary outline)
   - Logical tab order
   - Keyboard shortcuts supported

2. **Screen Readers:**
   - Semantic HTML (nav, main, article, etc.)
   - ARIA labels on icon-only buttons
   - Alt text on images
   - Role attributes where needed

3. **Reduced Motion:**
   ```css
   @media (prefers-reduced-motion: reduce) {
     * {
       animation-duration: 0.01ms !important;
       transition-duration: 0.01ms !important;
     }
   }
   ```

4. **Color Contrast:**
   - WCAG AA compliant (4.5:1 minimum)
   - Never rely on color alone
   - Icons + text labels
   - Pattern fills for charts

5. **Touch Targets:**
   - Minimum 44x44px for mobile
   - Adequate spacing between buttons
   - Larger hit areas than visible elements

---

## Z-Index Scale

```css
--z-dropdown: 1000      /* Dropdown menus */
--z-sticky: 1020        /* Sticky headers */
--z-fixed: 1030         /* Fixed elements */
--z-modal-backdrop: 1040 /* Modal backgrounds */
--z-modal: 1050         /* Modals */
--z-popover: 1060       /* Popovers */
--z-tooltip: 1070       /* Tooltips (highest) */
```

---

## Performance Optimizations

1. **CSS:**
   - Single design system file
   - CSS custom properties for theming
   - Minimal specificity
   - No !important (except accessibility overrides)

2. **Animations:**
   - CSS transforms (GPU-accelerated)
   - Will-change hints where needed
   - Reduced motion support
   - Frame-rate conscious (60fps target)

3. **Images:**
   - Lazy loading
   - Responsive images
   - WebP with fallbacks
   - Proper sizing

4. **Fonts:**
   - System font stack fallbacks
   - Font-display: swap
   - Subset fonts where possible

---

## Component Patterns

### Card Pattern
```jsx
<div className="paper-card">
  <div className="paper-header">
    <div className="paper-title-row">
      <h3 className="paper-title">{title}</h3>
      <QuickActions />
    </div>
    <div className="paper-sources">
      <Badge>{source}</Badge>
    </div>
  </div>

  <Authors />
  <Abstract />
  <Metadata />
  <DOI />
  <Actions />
</div>
```

### Button Pattern
```jsx
<button className="btn-primary">
  <Icon /> Label
</button>
```

### Badge Pattern
```jsx
<span className="source-badge pubmed">
  PubMed
</span>
```

---

## Future Enhancements

1. **Command Palette (⌘K):**
   - Quick access to all functions
   - Keyboard-driven navigation
   - Fuzzy search

2. **Reading Mode:**
   - Distraction-free paper reading
   - Focus on content
   - Hide UI chrome

3. **Collaborative Features:**
   - Shared collections
   - Comments/annotations
   - Team workspaces

4. **Advanced Animations:**
   - Page transitions
   - Skeleton loading states
   - Progress indicators
   - Success celebrations

5. **Data Visualization:**
   - Publication trends (area charts)
   - Citation networks (force-directed graphs)
   - Research topics (treemaps)
   - Author networks

---

## Files Modified

1. **frontend/src/styles/design-system.css** (NEW)
   - Complete design token system
   - Color palette
   - Typography scale
   - Spacing, radius, shadows
   - Animation keyframes
   - Utility classes

2. **frontend/src/App.css** (UPDATED)
   - Imports design system
   - App layout structure
   - Sidebar styling
   - Navigation components
   - Responsive design
   - Dark mode support

3. **frontend/src/components/PaperCard.css** (UPDATED)
   - Modern card design
   - Hover effects with gradient border
   - Source badge colors
   - Action button styles
   - Quick actions menu
   - Responsive adjustments

---

## Implementation Status

✅ **Completed:**
- Design system foundation
- Color palette and theming
- Typography system
- Spacing and layout
- App navigation structure
- Paper card redesign
- Dark mode support
- Responsive breakpoints
- Animation system
- Accessibility features

🚧 **In Progress:**
- Paper detail page redesign
- Citation network enhancements
- Loading states and skeletons
- Mobile bottom navigation

📋 **Planned:**
- Command palette
- Reading mode
- Advanced microinteractions
- Data visualization improvements
- Collaborative features

---

## Design Resources

**Color Palette Tool:** https://uicolors.app
**Typography Tester:** https://type-scale.com
**Shadow Generator:** https://shadows.brumm.af
**Accessibility Checker:** https://webaim.org/resources/contrastchecker

**Inspiration:**
- ResearchRabbit: https://researchrabbit.ai
- Linear: https://linear.app
- Notion: https://notion.so
- GitHub: https://github.com

---

**Last Updated:** 2025-11-08
**Version:** 1.0.0
**Author:** LitSearch Design Team
