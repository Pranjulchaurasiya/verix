---
name: Authenticity Verification Utility
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#45464d'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#76777d'
  outline-variant: '#c6c6cd'
  surface-tint: '#565e74'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#131b2e'
  on-primary-container: '#7c839b'
  inverse-primary: '#bec6e0'
  secondary: '#4b41e1'
  on-secondary: '#ffffff'
  secondary-container: '#645efb'
  on-secondary-container: '#fffbff'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#002113'
  on-tertiary-container: '#009668'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae2fd'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465c'
  secondary-fixed: '#e2dfff'
  secondary-fixed-dim: '#c3c0ff'
  on-secondary-fixed: '#0f0069'
  on-secondary-fixed-variant: '#3323cc'
  tertiary-fixed: '#6ffbbe'
  tertiary-fixed-dim: '#4edea3'
  on-tertiary-fixed: '#002113'
  on-tertiary-fixed-variant: '#005236'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  display:
    fontFamily: Plus Jakarta Sans
    fontSize: 40px
    fontWeight: '800'
    lineHeight: 48px
    letterSpacing: -0.03em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 26px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  label-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 14px
    letterSpacing: 0.04em
  data-mono:
    fontFamily: Plus Jakarta Sans
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: -0.01em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-sm: 1rem
  margin: 2rem
  margin-sm: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

The design system is engineered for an accessible, consumer-first fraud detection and product authentication engine. It balances institutional authority with consumer friendliness, moving consciously away from dystopian cybersecurity aesthetics (dark matrix grids, harsh terminal green, aggressive hazard badges) toward the empowering, calm clarity of modern fintech and intelligent visual search utilities (such as Stripe, Wise, and Google Lens).

### Visual Tone
- **Authoritative yet Approachable:** Employs precise typography, structured data hierarchies, and generous whitespace paired with soft, inviting corner radii.
- **Transparent & Objective:** Avoids alarmism. Visual signals provide instant, friction-free clarity so users instantly comprehend risk levels without panicking.
- **Empowering Consumer Utility:** Designed for speed during active commerce journeys—drag-and-drop imagery, immediate confidence scoring, and side-by-side merchant evidence breakdown.

### Style Archetype
- **Modern Clean Utility with Tonal Depth:** Crisp, high-contrast surfaces over off-white and pale slate canvases, reinforced by delicate hairline borders (`#E2E8F0`), micro-radii on interactive tags, and soft, ambient indigo-tinted drop shadows.

## Colors

The palette establishes an immediate foundation of trust and precision through deep navy and vibrant cobalt, while status colors strictly communicate verification states through high-contrast pairings of tinted container fills and saturated indicators.

### Core Roles
- **Primary (`#0F172A` / `#1E293B`):** Anchors high-emphasis headers, active navigational elements, key action buttons, and critical framing borders.
- **Secondary / Electric Accent (`#4F46E5` / `#6366F1`):** Represents algorithmic intelligence, search execution, file processing, and interactive links.
- **Surfaces & Backgrounds:** Base canvas uses Crisp Slate `#F8FAFC`, card elevated containers use pure `#FFFFFF`, and structural section dividers use `#E2E8F0`.

### Status & Verification Roles
- **Verified / Authentic (Emerald):** Accent `#10B981`, Background Surface `#ECFDF5`, Border `#A7F3D0`. Applied when seller verification, metadata lineage, and image hashes match known legitimate goods.
- **Caution / Flagged (Amber):** Accent `#F59E0B`, Background Surface `#FFFBEB`, Border `#FDE68A`. Used for price discrepancies, recycled stock imagery, or unverified seller domains.
- **High Risk / Counterfeit (Rose):** Accent `#EF4444`, Background Surface `#FEF2F2`, Border `#FECACA`. Dictates known clone listings, manipulated product packaging, and reported malicious links.
- **Indeterminate / Neutral (Slate):** Accent `#64748B`, Background Surface `#F1F5F9`, Border `#CBD5E1`. Used during processing, pending reverse-lookup checks, or low-confidence samples.

## Typography

The design system uses **Plus Jakarta Sans** across all roles to achieve a balance between geometric approachability and technical rigor. 

### Typographic Hierarchy
- **Display & Large Headlines:** Set with tight tracking (`-0.02em` to `-0.03em`) and heavy weights (`700`–`800`) to present unambiguous authenticity verdicts and bold section anchors.
- **Body Text:** Uses standard tracking with open line-height ratios (`1.5` to `1.6`) to ensure high readability when reviewing dense evidence lists, SerpApi merchant match descriptions, and safety warnings.
- **Labels & Status Badges:** Set in `600` and `700` weights with positive tracking (`+0.01em` to `+0.04em`) to maintain sharp legibility at micro sizes on compact status pills and metric cards.
- **Tabular Figures:** Always use OpenType `tnum` (tabular numbers) for risk percentages, match counts, pricing deltas, and timestamp audits to prevent layout jittering during real-time analysis updates.

## Layout & Spacing

The layout is structured around an 8pt metric system operating within a responsive 12-column grid for desktop/tablet and a 4-column grid for mobile viewports.

### Breakpoints & Reflow Rules
- **Desktop (1024px and above):** 12-column layout, max content container `1200px`, `gutter: 1.5rem`, `margin: 2rem`. Used for side-by-side inspection screens (query image on the left, SerpApi search cluster and visual comparison matches on the right).
- **Tablet (768px – 1023px):** 8-column layout, `gutter: 1.25rem`, `margin: 1.5rem`. Side-by-side evidence stacks sequentially into unified inspection blocks.
- **Mobile (below 768px):** 4-column layout, `gutter: 1rem`, `margin: 1rem`. All panels stack vertically. The primary score summary fixes to the bottom or top of the viewport for persistent awareness.

### Spacing Discipline
- `space-xs` (4px) and `space-sm` (8px): Used strictly for badge internal padding, icon-to-label gaps, and metadata pairings.
- `space-md` (16px): Standard inner card padding and input field internal spacing.
- `space-lg` (24px): Gap between distinct evaluation cards, form blocks, and visual comparison thumbnails.
- `space-xl` (40px): Section-level vertical offsets between dashboard modules.

## Elevation & Depth

Visual hierarchy uses a refined combination of hairline borders and soft, diffused, navy-tinted ambient drop shadows. This prevents the harsh visual noise common in threat intelligence tools, projecting lightweight, software-as-a-service calm.

### Elevation Tiers
- **Flat / Surface Level (Canvas):** `#F8FAFC`. Houses background utility areas, filter strips, and contextual side rails with zero shadow.
- **Level 1 (Resting Cards & Modules):** Pure white background (`#FFFFFF`) with a 1px border (`#E2E8F0`) and an ambient shadow: `0px 1px 3px rgba(15, 23, 42, 0.04), 0px 4px 8px -2px rgba(15, 23, 42, 0.03)`.
- **Level 2 (Hovered Cards & Interactive Verification Drops):** `0px 4px 6px -1px rgba(15, 23, 42, 0.06), 0px 10px 15px -3px rgba(15, 23, 42, 0.05)`, with a border shift to `#CBD5E1`.
- **Level 3 (Modals, Overlays, Image Inspect Drawers):** `0px 20px 25px -5px rgba(15, 23, 42, 0.08), 0px 8px 10px -6px rgba(15, 23, 42, 0.04)`, bordered by `#CBD5E1`.

## Shapes

The design system implements a modern, friendly `roundedness: 2` philosophy. Rounded edges soften high-density tabular and cryptographic data, creating a tactile, consumer-safe look.

### Geometry Standards
- **Cards & Data Panels:** `1rem` (16px) base radius for modular scan reports and visual analysis containers.
- **Large Hero Uploaders & Scan Modules:** `1.5rem` (24px) for the central drag-and-drop zone and top-level summary banners.
- **Interactive Controls (Inputs, Primary Buttons):** `0.5rem` (8px) for buttons and text fields to maintain an accurate, clickable perimeter.
- **Pills, Confidence Badges, & Chips:** Full circular curvature (`9999px`) to immediately differentiate categorical tags from actionable square cards.

## Components

### Buttons
- **Primary:** Background `#0F172A`, text `#FFFFFF`, radius `0.5rem`, height `44px` (touch-target compliant). Hover shifts to `#1E293B` with a subtle elevation shift. Focus ring: `2px solid #4F46E5` with `2px` offset.
- **Accent (Scan Action):** Background `#4F46E5`, text `#FFFFFF`. Hover `#4338CA`. Dedicated exclusively to triggering verification, analyzing URLs, or rescanning.
- **Secondary / Outline:** Background `#FFFFFF`, border `1px solid #E2E8F0`, text `#1E293B`. Hover: `#F8FAFC` and border `#CBD5E1`.

### Verification Status Chips & Badges
- Pill-shaped (`rounded-full`), `height: 24px` or `28px`, uppercase tracking (`+0.04em`), font size `11px` or `12px` bold.
- **Verified:** `#ECFDF5` background, `#065F46` label, paired with a solid `#10B981` leading icon indicator.
- **Flagged:** `#FFFBEB` background, `#92400E` label, paired with an amber warning icon.
- **High Risk:** `#FEF2F2` background, `#991B1B` label, paired with a red shield or alert icon.

### Cards & Evidence Panels
- Constructed on `#FFFFFF` with `1px solid #E2E8F0` borders and `1rem` border radius.
- Must feature a header row containing title, timestamp/match count, and risk pill.
- Body sections containing metadata tables must use alternating subtle striping or border separators in `#F1F5F9`.

### Input Fields & Search Bars
- Background `#FFFFFF`, border `1.5px solid #E2E8F0`, border-radius `0.5rem`, height `48px`.
- Prefix icon (search, link, or image upload) tinted `#64748B`.
- Focus state: border `#4F46E5`, box-shadow `0px 0px 0px 3px rgba(79, 70, 229, 0.15)`.

### Specialized Authenticity Components
- **Image Drop Zone:** Dashed border `2px solid #CBD5E1`, background `#F8FAFC`, radius `1.5rem`. Drag-over activates an indigo glow: border `#4F46E5`, background `rgba(79, 70, 229, 0.04)`.
- **Confidence Meter:** A horizontal segmented gauge or radial progress ring indicating risk levels (0–100%) dynamically shifting color from Emerald through Amber to Rose based on heuristic thresholds.
- **Source Match Row:** Compact card containing thumbnail of visual match, domain favicon, source trust tier, and a price delta chip indicating whether the item is suspiciously underpriced relative to the market baseline.