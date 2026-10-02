---
name: trip-itinerary-guide
description: >-
  Plan short city trips and produce illustrated Chinese travel guides (玩什么 /
  地图换乘 / 吃什么 / 酒店). Use when the user asks for 行程规划, 旅游攻略,
  两日游, 周末游, 打卡路线, 地图换乘, 酒店推荐, or 国风手绘攻略; or provides a
  marked map / day-by-day itinerary to turn into visual deliverables.
when-to-use: 行程规划, 旅游攻略, 两日游, 周末游, 打卡路线, 地图换乘, 酒店推荐, 国风手绘攻略
---

# Trip Itinerary Illustrated Guide

Turn a short-trip request (map pins, day plan, constraints) into a **folder of illustrated guide pages**—not a wall of chat text.

## When to use

- User wants 1–3 day city itinerary with places / transit / food / hotels
- User uploads or annotates a map and wants a usable playbook
- User asks for 国风手绘 / 攻略图 / 可打印海报-style outputs

## Default deliverables (4 pages)

Output under `~/Desktop/<城市><天数>行攻略/` (and optional `HD高清/`):

| # | File | Purpose |
|---|------|---------|
| 01 | `01-两日行·玩什么.png` | Landmarks + what to do (atmosphere illustration OK) |
| 02 | `02-地图换乘·打车公交.png` | Annotated map + taxi/bus backbone + times/costs |
| 03 | `03-吃什么·时间地点.png` | Food timeline; **one dish ↔ one image** |
| 04 | `04-酒店专页.png` | Zone hotels; **one hotel ↔ one image** |

Adjust page count if user asks fewer/more; keep the same pairing rules.

## Workflow

### 1. Lock the itinerary skeleton

Extract and confirm before drawing:

- Arrival / departure stations and train windows
- Day blocks (morning / afternoon / evening)
- Must-see landmarks vs optional
- Hotel **zone** (e.g. blue circle on map)—prefer stays inside the zone
- Food must-haves vs flexible evening (bars can stay “recommended, not fixed”)
- Constraints: budget, walking tolerance, no-car, return-by time

If ambiguous, ask 1–3 sharp questions; do not invent fixed bar bookings or hotel bookings unless asked.

### 2. Research facts (verify, don’t invent)

For each stop collect:

- Open hours / ticket notes (if public)
- Relative distances and **primary transit spine** (one bus line + taxi fallback)
- Typical taxi minutes/cost ranges (label as estimates)
- Hotel candidates **inside the agreed zone** + 1 cheaper fallback outside if useful

Prefer official / booking-site / map sources over memory.

### 3. Real photos first (critical)

**Never** fill hotels or named dishes with random Unsplash/Bing stock or a mixed collage.

For **each named hotel**:

1. Open that hotel’s Ctrip / booking / brand page in the browser
2. Extract real exterior (or lobby) CDN URLs (e.g. `dimg*.c-ctrip.com`, brand CDNs)
3. Download into `ref-photos/hotels_real/<slug>.jpg`
4. Only then stylize

For **each named dish / restaurant**:

1. Find a real reference of that dish or that shop’s signature look
2. Save under `ref-photos/food_real/`
3. Stylize from that reference

If a real photo cannot be obtained, say so and use text-only for that slot—do **not** substitute an unrelated image.

### 4. Stylize (国风手绘)

- `GenerateImage` with the **specific** real photo as reference
- One subject per generation (one hotel façade, one dish)
- Keep recognizable building massing / dish identity; no swapping names
- Save under `guofeng/` with clear slugs (`gf-hotel-quanji.png`, `gf-food-huoguoji.png`)

### 5. Compose guide pages

Hard layout rules (learned from failure modes):

- **Name ↔ image pairing**: the label next to an image must be that place/dish. No top strip of scrambled unrelated photos.
- **No mixed collage header** of random attractions on hotel/food pages.
- Prefer **HD width ~3600px** for final PNGs; keep individual assets ~1800px+.
- Map page: keep user annotations (circles/arrows) legible; overlay taxi + bus times/costs.
- Play page: landmarks as one coherent illustration or clearly labeled spots—not a junk collage.
- Food page: timeline (when / where / what) with one image per row.
- Hotel page: zone explanation + ranked list; one image per hotel row.

Also include practical text: ticket prices, open windows, “估计” for taxi, bus line number as spine.

### 6. Package for the user

```
~/Desktop/<城市><天数>行攻略/
  01-….png
  02-….png
  03-….png
  04-….png
  HD高清/          # optional upscaled finals
  guofeng/         # stylized assets
  ref-photos/      # real sources (hotels_real/, food_real/)
  vignettes/       # optional detail crops
```

Tell the user the folder path and what each page is for. Offer edits (swap hotel, change evening, add HD) rather than regenerating everything blindly.

## Quality checklist

Before delivering:

- [ ] Itinerary matches user’s day plan and return constraint
- [ ] Transit spine is concrete (e.g. one bus + taxi), not “自己查地图”
- [ ] Every hotel/dish image is from a **named** real reference, then stylized
- [ ] No stock-photo placeholders pretending to be that hotel/dish
- [ ] No top collage mixing wrong images
- [ ] Finals are high-res enough to read on phone and desktop
- [ ] Bars/evening marked flexible unless user locked them
- [ ] Hotel zone preference honored; out-of-zone stays labeled as such

## Anti-patterns

- Random web images “close enough” for a named hotel
- One moodboard strip reused across all pages
- Tiny / heavily compressed top half with huge empty bottom
- Inventing exact bar reservations or live prices without a source
- Starting project file edits from home when a dedicated project folder already exists—create/use the Desktop (or project) folder for assets

## Optional extras

Only if user asks:

- Separate bar page, printable PDF, English version
- Proof sheet: real photo vs 国风 side-by-side for one hero hotel
- Calendar/ICS of the day blocks

## Style defaults (Chinese short trips)

- Tone: practical + light; avoid tourist-brochure fluff
- Visual: 国风手绘 unless user specifies otherwise
- Language on graphics: Simplified Chinese
- Money/time: use 约 / 估计 when not quoted from a live source
