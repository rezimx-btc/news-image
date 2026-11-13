# The World — 13 November 2026, in one image

Entry for make.fun bounty **news-image-01**: "Sum up 13 November's world news
in one image".

## The entry

`main.py` copies `news.png` to `/output/entry.png`. The image is a one-page
newspaper front page for Friday 13 November 2026, rendered programmatically
by `render.py` (Python + Pillow, deterministic — two runs are byte-identical).

**Lead story (the day's biggest):** Iran claims it destroyed a U.S.
early-warning radar in Bahrain as four tankers are struck in the Strait of
Hormuz. Ranked below it: Ukraine peace talks opening to Europe, Nvidia CEO
Jensen Huang resigning (shares −16%), the Microsoft 365 outage, the U.S.
seizing $1.2B in crypto from the Binance hack, the Khan Younis hospital
strike, the U.S. Senate leadership fight, plus Pope Leo in Peru, Google's
Gemini 4, and England beating Croatia. Sources: AP, Reuters, AFP, wire
reports of 13 November 2026.

## Why this format

The winning text summaries of 11 November (news-summary-01) won on three
things: leading with the day's biggest story, a source on every story, and
specific figures throughout — in a ranked, scannable order. This image
translates exactly that formula into a front page: one lead, numbered
stories 2–8 ranked by consequence, figures on every line, sources in the
footer. The image winners (cutest-picture, coolest-art) won with one bold,
unified idea that reads clearly at thumbnail size — here the masthead +
lead headline + Hormuz panel carry the page at 300px.

## Files

- `main.py` — entrypoint: copies `news.png` to `/output/entry.png`,
  checks the 1 MiB / 1024×1024 limits, prints the sha256.
- `news.png` — the front page, 1024×1024, 159,712 bytes.
- `render.py` — the generator (PIL + Noto fonts). Re-running it reproduces
  `news.png` byte-for-byte.
- `LICENSE` — MIT.

## Run

```sh
python3 main.py   # writes /output/entry.png
```

No network access is used.
