---
name: Precision Ledger & Verification Console
colors:
  surface: '#faf9ff'
  surface-dim: '#d7d9e7'
  surface-bright: '#faf9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f1f3ff'
  surface-container: '#ebedfb'
  surface-container-high: '#e5e8f5'
  surface-container-highest: '#dfe2ef'
  on-surface: '#181b25'
  on-surface-variant: '#3f4850'
  inverse-surface: '#2c303a'
  inverse-on-surface: '#eef0fe'
  outline: '#707881'
  outline-variant: '#bfc7d2'
  surface-tint: '#006398'
  primary: '#006194'
  on-primary: '#ffffff'
  primary-container: '#007bb9'
  on-primary-container: '#fdfcff'
  inverse-primary: '#93ccff'
  secondary: '#0051d5'
  on-secondary: '#ffffff'
  secondary-container: '#316bf3'
  on-secondary-container: '#fefcff'
  tertiary: '#006b2c'
  on-tertiary: '#ffffff'
  tertiary-container: '#00873a'
  on-tertiary-container: '#f7fff2'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#cce5ff'
  primary-fixed-dim: '#93ccff'
  on-primary-fixed: '#001d31'
  on-primary-fixed-variant: '#004b73'
  secondary-fixed: '#dbe1ff'
  secondary-fixed-dim: '#b4c5ff'
  on-secondary-fixed: '#00174b'
  on-secondary-fixed-variant: '#003ea8'
  tertiary-fixed: '#7ffc97'
  tertiary-fixed-dim: '#62df7d'
  on-tertiary-fixed: '#002109'
  on-tertiary-fixed-variant: '#005320'
  background: '#faf9ff'
  on-background: '#181b25'
  surface-variant: '#dfe2ef'
  surface-canvas: '#F8FAFC'
  surface-subtle: '#F1F5F9'
  surface-card: '#FFFFFF'
  border-subtle: '#E2E8F0'
  border-strong: '#CBD5E1'
  text-muted: '#64748B'
  code-bg: '#090D16'
  code-fg: '#F8FAFC'
  alert-amber: '#D97706'
  alert-rose: '#E11D48'
typography:
  headline-xl:
    fontFamily: Geist
    fontSize: 2.25rem
    fontWeight: '600'
    lineHeight: 2.75rem
    letterSpacing: -0.03em
  headline-lg:
    fontFamily: Geist
    fontSize: 1.75rem
    fontWeight: '600'
    lineHeight: 2.25rem
    letterSpacing: -0.025em
  headline-md:
    fontFamily: Geist
    fontSize: 1.25rem
    fontWeight: '600'
    lineHeight: 1.75rem
    letterSpacing: -0.02em
  body-lg:
    fontFamily: Geist
    fontSize: 1rem
    fontWeight: '400'
    lineHeight: 1.5rem
    letterSpacing: -0.01em
  body-md:
    fontFamily: Geist
    fontSize: 0.875rem
    fontWeight: '400'
    lineHeight: 1.375rem
    letterSpacing: -0.005em
  body-sm:
    fontFamily: Geist
    fontSize: 0.75rem
    fontWeight: '400'
    lineHeight: 1.125rem
    letterSpacing: '0'
  mono-data:
    fontFamily: JetBrains Mono
    fontSize: 0.8125rem
    fontWeight: '500'
    lineHeight: 1.25rem
    letterSpacing: -0.01em
  mono-badge:
    fontFamily: JetBrains Mono
    fontSize: 0.6875rem
    fontWeight: '600'
    lineHeight: 1rem
    letterSpacing: 0.02em
  label-caps:
    fontFamily: Geist
    fontSize: 0.6875rem
    fontWeight: '600'
    lineHeight: 1rem
    letterSpacing: 0.06em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-lg: 1.5rem
  margin: 1rem
  margin-md: 1.5rem
  margin-lg: 2.5rem
  space-2xs: 0.125rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1rem
  space-xl: 1.5rem
  space-2xl: 2rem
  space-3xl: 3rem
---

## Brand & Style

This design system targets high-stakes verification engines, cryptographic consensus tools, and institutional fintech dashboards. The aesthetic is rigorous, technical, and surgical—rooted in modern utilitarian minimalism with structural micro-grid details. It rejects superficial consumer flourishes in favor of architectural framing, high data density, micro-typography, and unmistakable state telegraphing.

Key aesthetic pillars:
- **Architectural Rigor:** Interface components sit within structural grid lines, crisp 1px borders, and disciplined surface tiers.
- **Verification-First Legibility:** Primary narrative elements utilize tight-tracked modern grotesk typography, paired with monospaced accents for hashes, latency metrics, public keys, and ledger payloads.
- **Instrument Precision:** Accents of pure electric cerulean provide tactical guidance across a field of slate and zinc neutrals without visual fatigue.

## Colors

The palette employs an analytical, high-contrast light foundation. Canvas layers transition subtly from cool ambient slate (`#F8FAFC`) to pure white card elevations (`#FFFFFF`), bounded by razor-sharp border strokes (`#E2E8F0` and `#CBD5E1`). 

### Chromatic Strategy
- **Primary Accent (`#0284C7` / `#2563EB`):** Reserved strictly for active focal states, key metric highlights, primary action triggers, and active data conduits.
- **Success & Integrity (`#16A34A`):** Used for cryptographic validity, ledger confirmation pulses, and positive compliance status markers.
- **Monochrome Foundation (`#090D16`):** High-density text output ensuring AA/AAA contrast ratios against light gray background fields.
- **Data Visualization & Terminals:** Terminal panels invert into true obsidian (`#090D16`) with high-legibility crisp off-white (`#F8FAFC`) code text and muted structural borders.

## Typography

The type system creates an immediate binary dialogue between structural prose (`Geist`) and cryptographic metadata (`JetBrains Mono`). 

### Rules & Application
- **Prose Hierarchy:** Geist headlines must always leverage tight negative tracking (`-0.02em` to `-0.03em`) to mimic swiss international technical publications. Avoid heavy black weights; cap emphasis at weight 600.
- **Monospace Metadata:** JetBrains Mono is strictly applied to raw numerical balances, cryptographic signatures, UUIDs, IP addresses, JSON inspector trees, and protocol status tags.
- **Micro-Labels:** Header tags, table column categorizations, and metric keys utilize `label-caps` in uppercase, styled with `text-muted` (`#64748B`).

## Layout & Spacing

The system runs on a base-4 micro grid and base-8 layout grid to enforce mathematical precision across dense information surfaces.

### Layout Model
- **Grid Structure:** 12-column responsive layout with fixed maximum content constraints (standard at 1440px). 
- **Architectural Separation:** Prefer structural border dividers (`border-subtle` at 1px) over empty whitespace alone. Columns, panels, and side-trays lock directly against one another using shared 1px stroke borders.
- **Viewport Density:** Compact paddings (`space-md` for row items, `space-lg` to `space-xl` for card interiors) maintain continuous viewport visibility without excessive scrolling.

## Elevation & Depth

Visual hierarchy is maintained via low-contrast outlines and micro-offset ambient shadows. Heavy blurs and exaggerated floating layers are avoided.

### Stacking Model
- **Background Texture:** A subtle dot-grid background mask (`radial-gradient(#CBD5E1 1px, transparent 1px)` with 16px × 16px dimensions) renders behind the primary canvas layout.
- **Level 0 (Canvas):** Solid `#F8FAFC`.
- **Level 1 (Panels / Containers):** Solid `#FFFFFF` enclosed by a 1px border of `#E2E8F0`. Shadow: `0 1px 2px 0 rgba(9, 13, 22, 0.04)`.
- **Level 2 (Dropdowns / Flyouts / Command Palettes):** `#FFFFFF` bordered with `#CBD5E1`. Shadow: `0 4px 12px -2px rgba(9, 13, 22, 0.08), 0 2px 6px -1px rgba(9, 13, 22, 0.04)`.
- **Level 3 (Terminal Modules & Inspect Drawers):** Dark surface `#090D16` anchored with sharp 1px semi-transparent borders (`rgba(255, 255, 255, 0.1)`).

## Shapes

The design system adheres to a disciplined, low-radius geometric language (`roundedness: 1`). Elements favor technical squareness with softened corners that preserve data density while preventing visual harshness.

- **Standard Elements (Buttons, Inputs, Badges, Table Rows):** 0.25rem (4px to 6px maximum).
- **Cards & Data Modules:** 0.5rem (8px).
- **Status Pills & Live Indicators:** Fully circular / capsule geometries (`rounded-full`) to contrast against the sharp structural boxes.

## Components

### Buttons
- **Primary:** Filled `#0284C7` with white text, 1px border of `#0369A1`. Hover: `#0369A1`. Focus: 2px electric-blue ring with 2px white offset. Text set in `Geist` 500.
- **Secondary / Outline:** Background `#FFFFFF`, border 1px `#E2E8F0`, text `#090D16`. Hover: background `#F1F5F9`, border `#CBD5E1`.
- **Terminal / Monospace Utility:** Monospace font label, transparent background, dashed border `#CBD5E1`, compact horizontal padding.

### Status Indicators & Pills
- Small horizontal capsules (`height: 20px` to `24px`) with a pill border.
- Features a live glowing beacon: a 6px central solid dot accompanied by an animated or static ping ring with 20% opacity.
- Success state: `#ECFDF5` background, `#16A34A` text, `#16A34A` dot.
- Verified/Active state: `#F0F9FF` background, `#0284C7` text, `#0284C7` dot.

### Inputs & Verification Fields
- Bordered in 1px `#E2E8F0`, background `#FFFFFF`. Focus transitions border to `#0284C7` with zero blur spread.
- Text uses `mono-data` for token inputs, contract addresses, and verification parameters.
- Affixes (protocol prefixes like `https://`, `0x`, or currency codes) sit in an inset grey container `#F8FAFC` separated by a 1px border.

### Diagrammatic Data Cards
- Pure white container surfaces bounded by 1px `#E2E8F0`.
- Card headers feature an upper metadata bar: split into section title (`label-caps`) on the left and monospaced timestamp/status on the right, divided from card content by an edge-to-edge 1px stroke.

### Metadata Tables & Key-Value Grids
- Alternating subtle borders (`#F1F5F9`) with no row drop-shadows.
- Header cells styled with `label-caps` in `#64748B`.
- Content columns displaying addresses, hashes, and balances strictly enforce `JetBrains Mono` with text selection highlights in pale blue (`#E0F2FE`).