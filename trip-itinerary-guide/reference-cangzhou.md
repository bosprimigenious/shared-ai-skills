# Worked pattern: 沧州两日行

Example output root: `~/Desktop/沧州两日行攻略/`

## Skeleton that drove the pages

- Day 1: 沧州西 → 博物馆 → 狮城公园铁狮 → 0317火锅鸡 → afternoon 非遗馆 / 南川老街+清风楼 → evening bars flexible → hotel in **蓝圈**（南川老街/清风楼/运河区）
- Day 2: 大化工业遗址 → 驴肉火烧 → 沧州西返程（约 17:00）
- Bars: recommended only（贰楼酒吧 / 地心引力 optional）—not locked
- Hotels in blue circle: 全季·市政府南川老街店（首选）, 亚汀清风楼店, 桔子南川老街店, 亚汀市政府店, 如家精选清风楼店; 汉庭火车站店 = budget, not true center

## Asset pipeline that worked

1. Browser → specific Ctrip / BTH hotel page
2. CDP / network → `dimg04.c-ctrip.com` or `images.bthhotels.com` exterior URLs
3. Download → `ref-photos/hotels_real/`
4. `GenerateImage` with that ref → `guofeng/gf-hotel-*.png`
5. Compose page with **one hotel ↔ one image** rows
6. Final guide width **3600px**

Food: same idea—real dish ref → `gf-food-*-hd.png` → timeline rows.

## What failed (do not repeat)

- Bing/Unsplash “hotel lobby” generics
- Baidu image search lazy-load guessing wrong dishes
- Top collage of mixed landmarks on the hotel page
- Low-res finals that crush the upper half

## Transit spine pattern

Pick **one** bus line as the day axis + taxi for short hops; put both on page 02 with 约 minutes / 约 cost.
