# OmniCare UI — design direction

**Direction: editorial "claim file".** The interface should feel like a well-kept insurance
case file on a desk — letterhead, typed correspondence, highlighted policy passages and rubber
stamps — not a generic chat app.

## Locked tokens (see `src/index.css`)

| Token | Value | Use |
|---|---|---|
| `--color-paper` | `#F5F1E8` | page background (warm, not white) |
| `--color-paper-2` | `#ECE6D8` | panels, hover fills |
| `--color-ink` | `#1A1714` | text, rules, filled buttons |
| `--color-ink-2` | `#6B645A` | secondary text, labels |
| `--color-rule` | `rgb(26 23 20 / 0.18)` | hairlines |
| `--color-stamp` | `#B8322A` | the single accent: stamps, active states, errors |
| `--color-mark` | `#F3E28B` | highlighter behind cited passages |
| Display | Fraunces (optical serif) | headings, stamps, the wordmark |
| Body | IBM Plex Sans | correspondence |
| Data | IBM Plex Mono | ids, amounts, timestamps, the ledger |
| Radius | `2px` | everything |
| Elevation | none | hairlines separate; nothing floats |
| Motion | one moment | a stamp is "pressed" once when it appears; nothing else moves |

## Rules

- One accent colour. No gradients, no glows, no glass.
- No chat bubbles: entries are typed correspondence separated by dotted rules.
- Sources are shown as *highlighted passages of the policy*, numbered, in the case file.
- Numbers are tabular (`font-variant-numeric: tabular-nums`) and set in mono.
- Asymmetric layout: correspondence 7/12, case file 5/12, sticky.
- Light only. The paper is the brand.
