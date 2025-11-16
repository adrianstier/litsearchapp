# LitSearch Design System Documentation

## Table of Contents

1. [Overview](#overview)
2. [UX Strategy](#ux-strategy)
3. [Information Architecture](#information-architecture)
4. [Design System Specification](#design-system-specification)
5. [Component Library](#component-library)
6. [Implementation Guidelines](#implementation-guidelines)
7. [Accessibility Standards](#accessibility-standards)

---

## Overview

This document defines the complete design system for the LitSearch application, a literature search and management platform for academic researchers at UCSB.

### Design Philosophy

- **Clarity over cleverness**: Simple, direct interactions
- **Consistency over creativity**: Predictable patterns throughout
- **Function over form**: Purpose-driven design decisions
- **Restraint over decoration**: Minimal, elegant aesthetics

### Technology Stack

- **Framework**: React 19 + Vite
- **Styling**: Tailwind CSS v3
- **Icons**: React Icons
- **Charts**: Recharts
- **Routing**: React Router DOM v7

---

## UX Strategy

### Target Users

#### Primary Persona: Academic Researcher
- **Demographics**: Graduate students, postdocs, faculty (22-65 years)
- **Technical proficiency**: High
- **Context**: UCSB institutional access, research-intensive workflows
- **Pain points**:
  - Scattered research across multiple databases
  - PDF access barriers
  - Inefficient organization of literature
  - Time-consuming citation management

#### Secondary Persona: Undergraduate Researcher
- **Demographics**: Upper-division students (20-22 years)
- **Technical proficiency**: Medium
- **Context**: First research experiences
- **Pain points**:
  - Overwhelming search results
  - Unclear source authority
  - Need guidance on search strategies

### Core User Goals

1. **Discovery**: Find relevant papers quickly across multiple sources
2. **Access**: Download PDFs with minimal friction
3. **Organization**: Save and categorize papers for ongoing research
4. **Analysis**: Understand research landscape through visualizations
5. **Efficiency**: Reduce time spent on literature management

### Mental Models

- **Search**: Google-like simplicity with academic precision
- **Results**: Card-based browsing (familiar from ArXiv, Google Scholar)
- **Collections**: Folder metaphor (like file systems)
- **Library**: Personal repository (like Zotero, Mendeley)
- **Download**: One-click access (institutional auth should be invisible)

### Key User Flows

#### 1. Quick Search & Download (Most Critical)
```
Enter query → View results → Download PDF → Save to library
Success criteria: < 30 seconds, < 3 clicks to PDF
```

#### 2. Comprehensive Research
```
Enter query → Filter sources/dates → Browse results → Save multiple papers → Organize into collection
Success criteria: Efficient bulk operations, clear visual feedback
```

#### 3. Library Management
```
Browse library → Search within saved papers → Create collection → Add papers → Export/download batch
Success criteria: Fast search, intuitive categorization
```

#### 4. Research Analysis
```
View collection → Analyze visualizations → Identify trends → Discover gaps → Return to search
Success criteria: Actionable insights, interactive exploration
```

---

## Information Architecture

### Site Map

```
Literature Search App (/)
│
├── 🔍 Search (/) [PRIMARY]
│   ├── Search Form
│   ├── Source Selection (PubMed, arXiv, Crossref, Scholar, WoS)
│   ├── Filters (Year range, Max results)
│   ├── Search History (Last 5 queries)
│   └── Results Grid
│
├── 📚 Library (/library)
│   ├── All Saved Papers
│   ├── Library Search
│   ├── Pagination Controls
│   └── Paper Actions
│
├── 📁 Collections (/collections)
│   ├── Collection Grid
│   ├── Create New Collection
│   ├── Collection Detail View
│   └── Collection Management
│
├── 📊 Visualizations (/visualizations)
│   ├── Timeline View
│   ├── Network View
│   └── Topics View
│
└── ⚙️ Settings (/settings)
    ├── UCSB Authentication
    ├── Cookie Import/Export
    └── Theme Toggle
```

### Navigation Structure

**Primary Navigation** (Sidebar - always visible on desktop):
- Search (Home)
- Library (with paper count badge)
- Collections (with collection count badge)
- Visualizations
- Settings

**Mobile Navigation**: Hamburger menu with slide-in sidebar

---

## Design System Specification

### Typography

#### Font Families
```css
Primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif
Monospace: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace
```

#### Type Scale (Responsive)
```
Display:   text-5xl (48px) → text-6xl (60px)   [Desktop]
H1:        text-3xl (30px) → text-4xl (36px)   [Desktop]
H2:        text-2xl (24px) → text-3xl (30px)   [Desktop]
H3:        text-xl (20px)  → text-2xl (24px)   [Desktop]
H4:        text-lg (18px)  → text-xl (20px)    [Desktop]
Body-L:    text-base (16px) → text-lg (18px)   [Desktop]
Body:      text-sm (14px)  → text-base (16px)  [Desktop]
Caption:   text-xs (12px)  → text-sm (14px)    [Desktop]
```

#### Line Heights
```
Tight:     leading-tight (1.25)    [Headings]
Normal:    leading-normal (1.5)    [Body text]
Relaxed:   leading-relaxed (1.75)  [Long-form]
```

#### Font Weights
```
Regular:   font-normal (400)
Medium:    font-medium (500)
Semibold:  font-semibold (600)   [UI elements]
Bold:      font-bold (700)        [Section headers]
Extrabold: font-extrabold (800)   [Page titles]
```

### Color System

#### Primary Palette (Indigo - Academic Authority)
```
primary-50:  #eef2ff  (Backgrounds)
primary-100: #e0e7ff  (Hover backgrounds)
primary-200: #c7d2fe  (Borders)
primary-300: #a5b4fc  (Disabled states)
primary-400: #818cf8  (Interactive elements)
primary-500: #6366f1  (Primary brand) ← DEFAULT
primary-600: #4f46e5  (Hover states)
primary-700: #4338ca  (Active states)
primary-800: #3730a3  (Dark backgrounds)
primary-900: #312e81  (Text on light)
primary-950: #1e1b4b  (Deep contrast)
```

#### Secondary Palette (Pink - Energy, Accents)
```
secondary-500: #ec4899  (DEFAULT)
secondary-600: #db2777  (Hover)
```

#### Semantic Colors

**Success (Green)**:
```
success-500: #22c55e  (DEFAULT)
success-600: #16a34a  (Hover)
```

**Warning (Amber)**:
```
warning-500: #f59e0b  (DEFAULT)
warning-600: #d97706  (Hover)
```

**Error (Red)**:
```
error-500: #ef4444  (DEFAULT)
error-600: #dc2626  (Hover)
```

**Info (Blue)**:
```
info-500: #3b82f6  (DEFAULT)
info-600: #2563eb  (Hover)
```

#### Theme Colors

**Light Mode**:
- Background: `bg-slate-50`
- Card: `bg-white`
- Text Primary: `text-slate-900`
- Text Secondary: `text-slate-600`
- Border: `border-slate-200`

**Dark Mode**:
- Background: `bg-slate-950`
- Card: `bg-slate-800`
- Text Primary: `text-slate-50`
- Text Secondary: `text-slate-300`
- Border: `border-slate-700`

### Spacing System

#### Universal Scale
```
0:    0px
1:    4px    (Tight padding)
2:    8px    (Button padding Y)
3:    12px   (Small gaps)
4:    16px   (Base unit) ← STANDARD
6:    24px   (Card padding)
8:    32px   (Section spacing)
12:   48px   (Hero spacing)
16:   64px   (XL spacing)
24:   96px   (Section dividers)
```

#### Layout Rules
- **Grid gaps**: `gap-4` to `gap-6` (16-24px)
- **Card padding**: `p-6` (24px) on desktop, `p-4` (16px) on mobile
- **Page margins**: `p-8` (32px) on desktop, `p-4` (16px) on mobile
- **Section spacing**: `space-y-12` to `space-y-16` (48-64px)

#### Responsive Breakpoints
```
sm:  640px   (Large phones, landscape)
md:  768px   (Tablets)
lg:  1024px  (Small laptops)
xl:  1280px  (Desktops)
2xl: 1536px  (Large desktops)
```

### Shadow System
```
shadow-sm:  Small shadow for subtle elevation
shadow-md:  Medium shadow for cards
shadow-lg:  Large shadow for hover states
shadow-xl:  Extra large for modals/overlays
```

### Border Radius
```
rounded-lg:  0.5rem (8px)   [Buttons, inputs]
rounded-xl:  0.75rem (12px) [Cards]
rounded-full: 9999px        [Badges, pills]
```

---

## Component Library

### Buttons

#### Primary Button
```jsx
<button className="btn-primary">
  Search Papers
</button>
```

**Classes**: `btn-primary` (defined in index.css)
- Default: `bg-primary-600` with white text
- Hover: `bg-primary-700` with shadow-md
- Focus: 4px ring primary-200
- Active: scale-95
- Disabled: opacity-50, cursor-not-allowed

#### Secondary Button
```jsx
<button className="btn-secondary">
  Cancel
</button>
```

**Classes**: `btn-secondary`
- Default: White bg, slate border
- Hover: primary-500 border
- Focus: ring-2 slate-200

#### Ghost Button
```jsx
<button className="btn-ghost">
  Clear
</button>
```

**Classes**: `btn-ghost`
- Hover: bg-slate-100 dark:bg-slate-700

### Cards

#### Standard Card
```jsx
<div className="card">
  {/* Content */}
</div>
```

#### Hoverable Card
```jsx
<div className="card-hover">
  {/* Content */}
</div>
```

Adds hover effects: `hover:shadow-lg hover:-translate-y-1`

### Inputs

#### Text Input
```jsx
<input type="text" className="input" placeholder="Enter search query..." />
```

**States**:
- Default: border-slate-300
- Focus: border-primary-500 with ring-4
- Error: use `input-error` class

#### Checkbox
```jsx
<input type="checkbox" className="w-5 h-5 rounded border-2 border-slate-300 checked:bg-primary-600" />
```

### Badges

#### Source Badges
```jsx
<span className="badge-pubmed">PubMed</span>
<span className="badge-arxiv">arXiv</span>
<span className="badge-crossref">Crossref</span>
<span className="badge-scholar">Scholar</span>
<span className="badge-wos">WoS</span>
```

#### Status Badges
```jsx
<span className="badge-success">Success</span>
<span className="badge-warning">Warning</span>
<span className="badge-error">Error</span>
```

### Navigation

#### Sidebar Nav Link
```jsx
<NavLink to="/library" icon={FaBook} badge={247}>
  Library
</NavLink>
```

**Active state**: Primary background, bold text, right border accent
**Inactive state**: Slate text, hover background

### Loading States

#### Skeleton Loader
```jsx
<div className="animate-pulse space-y-4">
  <div className="h-6 w-3/4 bg-slate-200 dark:bg-slate-700 rounded" />
  <div className="h-4 w-full bg-slate-200 dark:bg-slate-700 rounded" />
  <div className="h-4 w-5/6 bg-slate-200 dark:bg-slate-700 rounded" />
</div>
```

---

## Implementation Guidelines

### Tailwind Configuration

The Tailwind config is located at `frontend/tailwind.config.js` and includes:
- Custom color palette (primary, secondary, semantic colors)
- Custom animations (fade-in, slide-in-right, scale-in)
- Extended shadow system
- Font family configuration

### Dark Mode Implementation

Dark mode uses Tailwind's `class` strategy:
1. ThemeContext toggles `dark` class on `<html>` element
2. All components use `dark:` variant for dark mode styles
3. Preferences saved to localStorage
4. Respects system preference on first load

### Component Patterns

#### Conditional Styling
```jsx
className={`
  base-classes
  ${condition ? 'true-classes' : 'false-classes'}
`}
```

#### Responsive Design
```jsx
className="text-sm md:text-base lg:text-lg"
```

#### State-Based Styling
```jsx
className="hover:bg-slate-100 focus:ring-4 active:scale-95 disabled:opacity-50"
```

### File Organization

```
src/
├── components/          # Reusable UI components
│   ├── PaperCard.jsx
│   ├── Toast.jsx
│   └── LoadingSkeleton.jsx
├── pages/              # Page-level components
│   ├── SearchPage.jsx
│   ├── LibraryPage.jsx
│   ├── CollectionsPage.jsx
│   ├── VisualizationsPage.jsx
│   └── SettingsPage.jsx
├── context/            # React contexts
│   ├── ThemeContext.jsx
│   └── ToastContext.jsx
├── services/           # API services
│   └── api.js
├── index.css           # Tailwind directives + custom utilities
└── App.jsx             # Main app layout
```

---

## Accessibility Standards

### WCAG Compliance

Target: **WCAG 2.1 Level AA**

#### Color Contrast
- Body text: Minimum 4.5:1
- Large text: Minimum 3:1
- Interactive elements: Minimum 3:1 against background

#### Keyboard Navigation
- All interactive elements accessible via Tab
- Visible focus indicators (4px ring)
- Logical tab order
- Keyboard shortcuts:
  - `/` or `Ctrl+K`: Focus search
  - `Esc`: Close modals/clear search
  - `?`: Help menu

#### ARIA Patterns
```jsx
// Buttons
<button aria-label="Toggle sidebar" />

// Links
<a href="#" aria-current="page">Home</a>

// Live regions
<div role="status" aria-live="polite">Loading...</div>

// Modals
<div role="dialog" aria-modal="true" aria-labelledby="dialog-title">
```

#### Screen Reader Support
- Semantic HTML (`<nav>`, `<main>`, `<aside>`)
- Logical heading hierarchy (H1 → H2 → H3)
- Alt text for all images
- Skip links for main content
- Descriptive link text (no "click here")

### Focus Management

```jsx
// Focus visible for keyboard users
*:focus-visible {
  @apply outline-none ring-4 ring-primary-200 dark:ring-primary-800 ring-offset-2;
}
```

### Motion Preferences

Respect `prefers-reduced-motion`:
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Design Principles Checklist

Before shipping any new feature, verify:

- [ ] **Visual Hierarchy**: Clear distinction between primary and secondary elements
- [ ] **Spacing Consistency**: Uses spacing scale (4, 8, 12, 16, 24, 32, 48, 64)
- [ ] **Color Usage**: Follows semantic color system, maintains contrast ratios
- [ ] **Typography**: Uses type scale, appropriate weights for hierarchy
- [ ] **Responsive Design**: Works on mobile (375px), tablet (768px), desktop (1280px+)
- [ ] **Dark Mode**: All states work in both light and dark themes
- [ ] **Accessibility**: Keyboard navigable, proper ARIA, sufficient contrast
- [ ] **Performance**: No layout shift, smooth animations, optimized images
- [ ] **Error States**: Clear feedback for all error conditions
- [ ] **Loading States**: Skeleton screens or spinners for async operations
- [ ] **Empty States**: Helpful guidance when no content exists
- [ ] **Interactive States**: Hover, focus, active, disabled for all interactive elements

---

## Version History

- **v1.0.0** (2025-11-16): Initial design system with Tailwind CSS implementation
  - Established UX strategy and information architecture
  - Defined comprehensive color, typography, and spacing systems
  - Implemented Tailwind-based component library
  - Documented accessibility standards and implementation guidelines

---

## References

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [React Accessibility](https://react.dev/learn/accessibility)
- [Nielsen Norman Group - UX Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/)
