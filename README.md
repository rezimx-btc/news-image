# The World — 13 November 2026

A one-page newspaper summing up 13 November 2026's world news in a
single image, built for make.fun's news-image-01 bounty.

## The design

A classic 3-column broadsheet in deep navy on cream. The masthead reads
THE WORLD over the date line, then the lead story — four tankers hit in
the Strait of Hormuz, radar destroyed in Bahrain — with a small tanker
silhouette. Below it, three ruled columns carry the day's other stories:
Ukraine peace talks and the Microsoft 365 outage; the Nvidia CEO
resigning (shares down 16%) and the Binance $1.2 billion seizure; the
Gaza hospital strike and the Van Hollen v Schumer Senate showdown. An
"Also in the news" strip covers Pope Leo, Gemini 4 and England v
Croatia, and the footer credits AP, Reuters, AFP and wire reports.

## Files

- `news.png` — the newspaper, 1024x1024, 14 KB
- `render.py` — draws news.png from scratch (stdlib only: a hand-written
  PNG encoder and a 5x7 bitmap font, no Pillow)
- `main.py` — the entrypoint: copies news.png to /output/entry.png and
  verifies sha256, the 1 MiB size cap and the 1024x1024 dimension cap
- `README.md`, `LICENSE`, `.makefun/owner.json`

## Run

```
python3 render.py   # rebuilds news.png
python3 main.py     # writes /output/entry.png
```

Both scripts use the standard library only, so they run in a bare
python:3.13 image.
