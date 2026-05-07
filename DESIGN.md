---
name: Celestial Serenity
colors:
  surface: '#101415'
  surface-dim: '#101415'
  surface-bright: '#363a3b'
  surface-container-lowest: '#0b0f10'
  surface-container-low: '#191c1e'
  surface-container: '#1d2022'
  surface-container-high: '#272a2c'
  surface-container-highest: '#323537'
  on-surface: '#e0e3e5'
  on-surface-variant: '#cfc2d2'
  inverse-surface: '#e0e3e5'
  inverse-on-surface: '#2d3133'
  outline: '#988d9c'
  outline-variant: '#4c4451'
  surface-tint: '#e0b6ff'
  primary: '#e0b6ff'
  on-primary: '#4a067a'
  primary-container: '#581c87'
  on-primary-container: '#ca8efc'
  inverse-primary: '#7c43ab'
  secondary: '#44e2cd'
  on-secondary: '#003731'
  secondary-container: '#03c6b2'
  on-secondary-container: '#004d44'
  tertiary: '#bec6e0'
  on-tertiary: '#283044'
  tertiary-container: '#353d52'
  on-tertiary-container: '#a0a8c1'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#f2daff'
  primary-fixed-dim: '#e0b6ff'
  on-primary-fixed: '#2d004f'
  on-primary-fixed-variant: '#632892'
  secondary-fixed: '#62fae3'
  secondary-fixed-dim: '#3cddc7'
  on-secondary-fixed: '#00201c'
  on-secondary-fixed-variant: '#005047'
  tertiary-fixed: '#dae2fd'
  tertiary-fixed-dim: '#bec6e0'
  on-tertiary-fixed: '#131b2e'
  on-tertiary-fixed-variant: '#3f465c'
  background: '#101415'
  on-background: '#e0e3e5'
  surface-variant: '#323537'
typography:
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 40px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.3'
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  container-padding: 2rem
  gutter: 1.5rem
  section-gap: 4rem
---

## Brand & Style
The brand personality of this design system is a sophisticated blend of "Lullaby Modernism"—where the whimsical nature of children's storytelling meets the precision of generative AI. It aims to evoke an emotional response of calm curiosity, reassuring parents of the technology's safety while enchanting children with its possibilities.

The visual style utilizes a **Modern Glassmorphism** approach. By layering translucent surfaces over deep, atmospheric gradients, the UI mimics a night sky. This creates a sense of depth and "magic" without sacrificing the clean, professional structure required for a premium SaaS product. High-quality whitespace and intentional focal points ensure the experience remains serene and never overwhelming.

## Colors
The palette is anchored in a dark-mode-first philosophy to align with the bedtime context. 

- **Primary (Moonlight Purple):** Used for key actions and brand moments, symbolizing imagination and the ethereal.
- **Secondary (Mint):** A high-vibrancy accent used sparingly for success states, interactive highlights, and call-to-action "sparks" that pop against the dark background.
- **Neutral (Deep Navy & Soft Cream):** The Deep Navy serves as the foundational canvas, while the Soft Cream is reserved for high-readability text and primary surfaces, ensuring a gentle contrast that is easy on the eyes in low-light environments.

## Typography
This design system pairs **Plus Jakarta Sans** for headlines with **Inter** for body copy. 

Plus Jakarta Sans provides a friendly, geometric, and modern feel that resonates with the playful nature of storytelling. Its slightly rounded terminals offer a welcoming aesthetic. Inter is utilized for body text and functional UI labels to ensure maximum legibility and a professional, systematic grounding. Headlines should use tighter tracking to feel "contained," while body text maintains a generous line height to promote a relaxed reading pace.

## Layout & Spacing
The layout follows a **Fixed-Width Grid** model for desktop to ensure the story-creation experience feels focused and intimate, while transitioning to a fluid model for tablet and mobile. 

A strict 8px rhythmic scale is used to manage spatial relationships. Generous section gaps and internal container padding are essential to maintain the "calm and serene" atmosphere, preventing the UI from feeling cluttered. Content is often centered to create a theatrical, "stage-like" focus for the AI-generated stories.

## Elevation & Depth
Depth is conveyed through **Glassmorphism and Ambient Glows**. Rather than traditional grey shadows, this design system uses:

- **Backdrop Blurs:** Surfaces use a 12px to 20px blur with a low-opacity Deep Navy tint.
- **Inner Borders:** A 1px translucent border (Soft Cream at 10% opacity) on cards mimics the edge of a glass pane.
- **Purple Luminescence:** Elevated elements, like the primary "Create" card, emit a soft Moonlight Purple outer glow (32px blur, 15% opacity) to suggest they are "floating" on a bed of light.
- **Tonal Tiering:** The background is the darkest (#0F172A), while interactive cards are one shade lighter, creating a clear stack without needing heavy drop shadows.

## Shapes
The shape language is defined by significant roundedness to evoke safety and friendliness. While the base unit is `rounded-md` (8px), the signature element of this design system is the **2xl card (24px)**. 

Buttons should utilize a "Pill" shape for secondary actions and a `rounded-xl` shape for primary buttons to maintain a soft touch. Icons should always feature rounded caps and corners to match the surrounding UI elements. Hard 90-degree angles are strictly avoided to ensure the evaluator-ready, serene atmosphere.

## Components

- **Dream Cards:** The primary container for story previews. These feature `2xl` rounded corners, a subtle Moonlight Purple glow on hover, and a glassmorphic footer for story metadata.
- **Magic Buttons:** Primary buttons use a gradient fill from Moonlight Purple to a slightly lighter violet, with a Mint accent "sparkle" icon. On hover, the gradient should subtly shift to suggest movement.
- **Story Inputs:** Text areas and prompt fields should be Soft Cream with low opacity (approx. 5%), turning to a solid, slightly brighter border when focused to indicate "trustworthy" interaction.
- **Progress Steppers:** Use soft, glowing Mint dots to indicate completion. The active state should have a pulse animation to mimic a "breath," reinforcing the calm atmosphere.
- **Chips & Tags:** Small, Pill-shaped elements used for story themes (e.g., "Space," "Fairies"). These use a Mint outline with no fill to keep the UI light and airy.
- **Audio Visualizers:** For narrated stories, use smooth, rounded bars in Mint that animate with a low-frequency ease, avoiding jagged or rapid movements.