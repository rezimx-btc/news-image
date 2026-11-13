# THE WORLD — 13 November 2026 (v3)

A bold red tabloid front page summing up 13 November 2026's world news in
one image, built for the make.fun news-image-01 bounty.

## The design

v3 is a tabloid, not a broadsheet: a solid red masthead band with THE WORLD
in big white letters, the giant headline **HORMUZ ON FIRE**, and a drawn
lead scene of the Strait of Hormuz at dusk — four tankers on a navy sea,
two of them burning under starburst explosions, dotted missile arcs
overhead, and the radar station on the Bahrain coast crossed out in red.
Six more stories fill a two-column grid below, an ALSO strip carries the
three short items, and the footer cites the wire sources.

## The stories

1. **Lead:** Iran strikes in the Strait of Hormuz — four tankers hit, the
   radar station in Bahrain destroyed.
2. Ukraine peace talks resume; ceasefire hopes rise.
3. Nvidia's chief executive resigns; shares fall 16%.
4. Microsoft 365 outage hits millions of users.
5. Authorities seize $1.2 billion from Binance.
6. Gaza hospital hit as fighting rages on.
7. Van Hollen v Schumer clash over the shutdown.
8. Also: Pope Leo • Gemini 4 • England–Croatia.

## Files

- `news.png` — the rendered front page (1024x1024, under 1 MiB).
- `render.py` — draws `news.png` from scratch: a tiny 5x7 bitmap font,
  rectangles, lines, discs and starbursts, packed into a PNG by hand.
  Standard library only.
- `main.py` — the entrypoint: copies `news.png` to `/output/entry.png`
  and verifies it (PNG magic, IHDR size, 8-bit truecolour, 1 MiB and
  1024x1024 limits, sha256 match). Standard library only.

## Run

```sh
python3 render.py   # rebuild news.png
python3 main.py     # write /output/entry.png
```
