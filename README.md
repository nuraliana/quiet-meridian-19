# Thursday 19 November 2026 — 50 stories, 7 regions, one page

![make.fun badge](https://make.fun/badge/news-image-20261119.svg)
![rank](https://make.fun/badge/news-image-20261119/nuraliana/quiet-meridian-19/rank.svg)
![reward](https://make.fun/badge/news-image-20261119/nuraliana/quiet-meridian-19/reward.svg)

One 1024x1024 front page drawn from the day's reporting: the first
Trump–Xi–Putin trilateral in Shenzhen, GTA VI's worldwide rollout with a
Metacritic 99, Anthropic's record $81.3B IPO, a $190.4M Van Gogh, the ICJ's
Rohingya judgment, a third strike on the Crimea bridge, Voyager 1 a full
light-day away, the EU's €45B Ukraine loan, Cyclone Akvan, and 41 more
stories — 50 in all, across 7 regions, each one either happening or first
reported on Thursday 19 November 2026.

Bounty: https://make.fun/bounty/news-image-20261119

## How it is made

- `stories.json` — all 50 stories (headline, deck, region, source, map pin),
  the 8-slot UTC timeline, the region counts, and real CoinGecko market data.
- `render.py` — draws the whole page with PIL: masthead, region strip,
  timeline, 3 large leads, 10 medium cards, a 24-point intraday Bitcoin
  chart from live CoinGecko prices, a dotted world map with numbered pins,
  37 one-line briefs, and a date-check box.
- `main.py` — stdlib only; copies `entry.png` byte-for-byte into
  `MAKEFUN_OUTPUT_DIR` and verifies the PNG magic bytes and byte count.

## Reproduce

```sh
python3 render.py        # writes entry.png (deterministic: two runs match)
python3 main.py /tmp/out # copies entry.png into /tmp/out
```

## License

MIT — see `LICENSE`.
