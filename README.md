# Route Atlas · 航线图志

> An editorial atlas of international nonstop routes, organized by **where you depart from**:
> China, the United States, or Europe. Every page is one flow diagram plus a line-by-line
> table with source grades, policy and traffic-rights background, and an explicit list of
> what could **not** be verified. **Pure static HTML, no server, no build step, zero running cost.**

[![pages](https://img.shields.io/badge/pages-17%20route%20pages%20%C2%B7%203%20families-2b5f8f)](#what-it-is)
[![routes](https://img.shields.io/badge/routes-1%2C159%20rows%20%C2%B7%20per--direction%20weekly-4a5d3a)](#conventions)
[![fares](https://img.shields.io/badge/fares-deliberately%20unverified-b8893e)](#conventions)
[![License](https://img.shields.io/badge/license-PolyForm--Noncommercial--1.0.0-4a5d3a)](LICENSE)
[![Live](https://img.shields.io/badge/live-atlas.klay--wang.com%20(soon)-a0392f)](https://atlas.klay-wang.com/)
[![中文](https://img.shields.io/badge/%E4%B8%AD%E6%96%87-README-2b5f8f)](README.zh.md)

**Live (deploying): <https://atlas.klay-wang.com/>** · Sister site: [Market Chronicle](https://chronicle.klay-wang.com/)

## What it is

Three **departure families**, seventeen pages, one home page with a world-flow diagram.
Content is in Chinese; the data modules and tooling are language-neutral.

| Family | Pages |
|---|---|
| **China departures** 中国出发 | US · Europe (13 countries + Hong Kong as the quota-free transit port) · Asia (9 destinations) · Australia/NZ · Canada · Africa |
| **US departures** 美国出发 | China (mirror) · Europe (14 cities × 10 gateways) · Asia (Hong Kong vs Taipei as the transit port home) · Mexico & Caribbean · South America (incl. "how to connect from China") · Australia/NZ & South Pacific |
| **Europe departures** 欧洲出发 | China (mirror) · US (mirror) · Asia ("the Gulf year") · Africa & Indian Ocean |

Every page follows the same structure:

1. **The picture** — market structure, joint ventures, traffic-rights caps (or their absence), what changed this year.
2. **Flow diagram** — origin cities → destination cities, line width = weekly frequency, colour = home carrier / foreign carrier / discontinued. Filters by direction and destination country. Rendered from the page's own table DOM, so the table is the single source of truth.
3. **Country-by-country tables** — city pair · carrier + flight number · weekly frequency (per direction) · block time · notes · source grade.
4. **Policy background** — Russian airspace asymmetry, the 50/50 US–China cap, EU–US Open Skies, the 2026 Gulf airspace closures, etc.
5. **Conventions and unverified items** — everything the research could not confirm is listed, never silently filled in.

**Mirror pages share data, not research.** `regions/us_cn.py` declares `MIRROR_OF = "usa"`,
borrows the source module's routes, and only writes its own narrative, default flow direction,
and an auto-generated "where you are → where you can fly nonstop" table (`regions/_mirror.py`).

## Conventions

- Frequencies are **per direction, per week**; a daily service is 7. Both directions are assumed symmetric.
- **Source grades**: **[A]** airline schedule filings / official timetables · **[S]** airport or airline press releases, Cirium/OAG/AeroRoutes/FlightConnections · **[D]** aggregated schedule databases or trade press (do not distinguish operating vs. codeshare) · **[C]** aggregators / common knowledge.
- **Fares are never quoted, on purpose.** Aggregator prices include connections, swing wildly by date, and ignore direction; a per-route fare would be false precision. Use Google Flights' price graph for a given day.
- Rows the research could not confirm carry `未核` (unverified) and a frequency of 0 — they draw as thin lines, not as invented numbers.
- Schedules change at the IATA season boundaries (late March, late October). **Everything must be re-verified after a season change.**
- One hard-coded self-check per constraint: the US–China page asserts that both sides sum to exactly 50 weekly frequencies under the bilateral cap; every page asserts that the number of rendered rows equals the number of data rows.

## Architecture

```
regions/*.py         one data module per page: ROUTES tuples + META + sections()
      │
      ▼
tools/build_region_page.py   →  <family>/<page>.html   (tables + flow-diagram adapter)
tools/build_index.py         →  index.html + 3 family indexes (world-flow diagram)
tools/inject_flowviz.py      →  embeds the FlowViz runtime (version-pinned, --check on commit)
tools/build_theme.py         →  injects the shared palette from theme.css (--check on commit)
      │
      ▼
Static HTML: vanilla JS, no framework, day/night theme, floating TOC
```

The design system is shared with [Market Chronicle](https://chronicle.klay-wang.com/):
parchment / night palettes, capsule table of contents, starfield header.
Flow diagrams use the embedded `FlowViz` runtime — red = home carriers, green = foreign carriers,
grey dashed = discontinued or no nonstop.

## Build locally

```bash
git clone https://github.com/klaywang24/route-atlas.git
cd route-atlas
python3 tools/build_region_page.py            # all pages (or: ... europe)
python3 tools/build_index.py
python3 tools/inject_flowviz.py inject 中国出发/*航线.html 美国出发/*航线.html 欧洲出发/*航线.html index.html
python3 tools/build_theme.py
python3 -m http.server 8765                   # open http://localhost:8765
```

The order is fixed: region pages → indexes → FlowViz runtime → theme. Both `--check` gates run in
`.githooks/pre-commit` (`git config core.hooksPath .githooks`). **Do not hand-edit the HTML** — it is
a build artifact; edit `regions/*.py` and rebuild.

## Research provenance

Each page was built from a dedicated research pass (September 2026) against airline filings,
AeroRoutes, Cirium/OAG figures as reported by the trade press, airport press releases and
FlightConnections snapshots. The raw research reports, including every conflict between sources
and every item left unverified, are kept in [`research/`](research/). Working notes and the
current state of the project are in [`HANDOFF.md`](HANDOFF.md) (Chinese).

## License

[PolyForm Noncommercial 1.0.0](LICENSE) — free to read, cite, adapt and use for any
noncommercial purpose; commercial use requires a separate license.
