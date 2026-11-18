# Allo Wide

Downstream variant of [Allo](https://github.com/joshpuckett/allo) built from the
Cyrillic branch ([PR #8](https://github.com/joshpuckett/allo/pull/8), authored by
[Degroshi](https://github.com/degroshi)). Everything in the drawing stays
upstream's; the only change is that every glyph is **25% wider**.

Why: the interface this fork was made for (ynckz.tech) was designed in Benzin,
which is wider than Allo. At the same size and line height, Allo's words came out
~20% narrower than the layout, so the text was stretched on the X axis until the
widths matched. Nothing was redrawn: outlines, advances, anchors and kerning are
scaled uniformly, which keeps the interpolation compatible and the spacing
rhythm intact.

## What is different

| | upstream Allo | this branch |
|---|---|---|
| glyph width | 100% | **125%** |
| vertical stems | 100% | **125%** (an X scale thickens them; horizontal stems stay) |
| ROND corners | round | slightly elliptical (wider than tall) |
| sizes, line heights, UPM | — | unchanged |
| obliques | 9 | **none** (an X scale would change the slant angle) |
| family name | Allo | **Allo Wide** |

The heavier vertical stems and the elliptical corners are the honest cost of a
plain horizontal scale. At text sizes (12–24 px) neither is visible; at display
sizes the corners are. If you need a corrected display cut, the sources are here
and `tools/wide/widen.py` is the place to start.

## Build

Requires Python 3.9+ and the pinned dependencies:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt

# 1. widen every master and the upright statics into build/wide-sources
.venv/bin/python tools/wide/widen.py --src sources --dst build/wide-sources --sx 1.25

# 2. compile that into fonts/ (9 statics + variable + woff2 + zip)
ALLO_SOURCES=build/wide-sources \
ALLO_RELEASE=build/wide-sources/release.json \
ALLO_UPRIGHT_ONLY=1 \
ALLO_ZIP_README=tools/wide/README.txt \
.venv/bin/python build.py
```

PowerShell, one line each:

```powershell
python tools\wide\widen.py --src sources --dst build\wide-sources --sx 1.25
$env:ALLO_SOURCES='build\wide-sources'; $env:ALLO_RELEASE='build\wide-sources\release.json'
$env:ALLO_UPRIGHT_ONLY='1'; $env:ALLO_ZIP_README='tools\wide\README.txt'
python build.py
```

`build.py` grew four environment hooks for this (`ALLO_SOURCES`,
`ALLO_RELEASE`, `ALLO_FONTS`, `ALLO_UPRIGHT_ONLY`, plus `ALLO_ZIP_README`); with
none of them set it builds exactly what it built before.

## Branches

| branch | what |
|---|---|
| `main` | mirror of `joshpuckett/allo` |
| `cyrillic` | mirror of `degroshi/allo:cyrillic` (PR #8) |
| `wide` | this: `cyrillic` + the widening tool + the built release |

`wide` is based on `9623d58` (`cyrillic`), which is 4 commits behind upstream
`main` (1.0.1–1.0.3: redrawn X, stem caps, kerning fixes). Merging upstream into
the Cyrillic branch currently conflicts in ~180 UFO files, so it is left to the
Cyrillic authors; when PR #8 is rebased, rebase this branch on top.

## License

SIL Open Font License 1.1, same as Allo (`OFL.txt`). Allo has no Reserved Font
Name, so the rename to "Allo Wide" is a courtesy, not a requirement. The
derivative stays under the OFL. Original credits: Allo © Josh Puckett, Cyrillic
© Degroshi, parts from Inter © The Inter Project Authors.
