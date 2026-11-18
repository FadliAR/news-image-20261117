# news-image-20261117 — World News in One Image

[![make.fun](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/FadliAR/news-image-20261117/rank.svg)](https://make.fun/bounty/news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/FadliAR/news-image-20261117/reward.svg)](https://make.fun/bounty/news-image-20261117)

Entry for the [make.fun bounty "Sum up 17 November's world news in one image"](https://make.fun/bounty/news-image-20261117)
(news-image-20261117, $250 escrowed, fee $0).

## What it does

`main.py` (Python 3.13, standard library only, no network) renders a
1024x1024 PNG that sums up the world news of **Tuesday 17 November 2026**:

- Masthead: **17 NOVEMBER 2026** / **TUESDAY**
- Six verified stories from that day, across regions and fields:
  1. **Kerch Bridge hit** — Ukraine strike collapses a road span; Russia hits two Kyiv bridges (Europe)
  2. **Tankers hit at Hormuz** — mines strike tankers; a third US carrier arrives (Middle East)
  3. **Trump in Asia** — Manila ASEAN visit; Xi–Trump–Putin talks set for Thursday in Shenzhen (Asia)
  4. **JPMorgan outage** — software bug disrupts online banking and Zelle payments (Business)
  5. **EU migrant hub** — five states plan a Rwanda return hub for rejected asylum seekers (Europe)
  6. **Vulcan rocket fails** — ULA rocket fails in flight; 40 Amazon satellites lost (Space)

Every story was verified against real reporting of 17 November 2026
(BBC, AP, Reuters, Al Jazeera and others) before it was drawn.

## How it draws

Everything is built from scratch in `main.py`: a hand-written PNG encoder
(zlib), a small raster canvas (rects, lines, circles, ellipses), six simple
pictograms, and a hand-built 5x7 bitmap font. Fully deterministic — two runs
produce byte-identical output.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png (1024x1024, <= 1 MiB)
```

## License

MIT — see [LICENSE](LICENSE).
