#!/usr/bin/env python3
"""Widen Allo horizontally at the source level.

Allo is drawn for a text size; on ynckz.tech the layout it has to match was set
in Benzin, which is a good deal wider. Scaling the outlines, advances, anchors
and kerning on the X axis makes the words the same width without touching sizes
or line heights.

The same transform is applied to every master and to the separately drawn static
sources, so the variable font and the statics stay identical in width.

What it does not do, and what you should know before using it:

* Vertical stems get sx times thicker while the horizontal ones stay; the font
  becomes wider *and* slightly heavier. Corners (ROND) become elliptical: the
  fillet is wider than it is tall. At text sizes neither is visible, at display
  sizes the second one is.
* Obliques are left out of the copy: a plain X scale changes the slant angle
  (atan(sx * tan a)). The wide family is upright only.
* Dashes, arrows and other glyphs whose width is part of their drawing are
  scaled uniformly with everything else, so no shape is redrawn.

Usage:
    python3 tools/wide/widen.py --src sources --dst build/wide-sources --sx 1.25

Then build the wide release from the widened sources:

    ALLO_SOURCES=build/wide-sources ALLO_RELEASE=build/wide-sources/release.json \\
    ALLO_UPRIGHT_ONLY=1 ALLO_ZIP_README=tools/wide/README.txt python3 build.py

License: the derivative is covered by SIL OFL 1.1 (see OFL.txt). Allo has no
Reserved Font Name, so the family is renamed to "Allo Wide" to keep it apart
from the original in font menus.
"""
import argparse
import json
import shutil
from pathlib import Path

import ufoLib2
from fontTools.designspaceLib import DesignSpaceDocument
from fontTools.misc.roundTools import otRound

FAMILY = 'Allo Wide'
VARIABLE_FAMILY = 'Allo Wide Variable'
FILE_PREFIX = 'AlloWide'


def rebrand(text, family):
    """Swap the family name at the start of a name-table string, longest first.

    Allo's masters are named "Allo Variable ..." and "AlloVariable-...", so the
    spaced and the PostScript spelling both have to be handled before "Allo".
    """
    for old, new in (('Allo Variable', family),
                     ('AlloVariable', family.replace(' ', '')),
                     ('Allo', family)):
        if text.startswith(old):
            return new + text[len(old):]
    return text


def scale_x(value, sx):
    return otRound(value * sx) if value is not None else None


def scale_glyph(glyph, sx, foreground):
    for contour in glyph.contours:
        for point in contour.points:
            point.x = scale_x(point.x, sx)
    for component in glyph.components:
        xx, xy, yx, yy, dx, dy = component.transformation
        # the component is placed, then the whole glyph is scaled on X
        component.transformation = (xx * sx, xy, yx * sx, yy, dx * sx, dy)
    for anchor in glyph.anchors:
        anchor.x = scale_x(anchor.x, sx)
    for guideline in glyph.guidelines:
        guideline.x = scale_x(guideline.x, sx)
    if foreground:
        glyph.width = scale_x(glyph.width, sx)


def scale_font(font, sx, family, style=None):
    """Scale one UFO in place: every layer, metrics, kerning, anchors, names."""
    default = font.layers.defaultLayer
    for layer in font.layers:
        for glyph in layer:
            scale_glyph(glyph, sx, foreground=layer is default)
    font.kerning = {(a, b): scale_x(v, sx) for (a, b), v in font.kerning.items()}
    for guideline in font.guidelines:
        guideline.x = scale_x(guideline.x, sx)

    info = font.info
    if info.postscriptStemSnapV:
        info.postscriptStemSnapV = [scale_x(v, sx) for v in info.postscriptStemSnapV]
    # width defaults written into the CFF Private dict, if the sources carry them
    for attr in ('postscriptNominalWidthX', 'postscriptDefaultWidthX'):
        value = getattr(info, attr, None)
        if value is not None:
            setattr(info, attr, scale_x(value, sx))

    # ufo2ft builds the name table from these, not from familyName alone. Only
    # the family part changes; the per-master style strings stay as upstream.
    info.familyName = family
    if style is not None:
        info.styleName = style
    info.openTypeNamePreferredFamilyName = family
    if info.postscriptFontName:
        # the PostScript name has no spaces: AlloWide-Medium, not Allo Wide-Medium
        info.postscriptFontName = rebrand(info.postscriptFontName, family.replace(' ', ''))
    for attr in ('openTypeNameUniqueID', 'styleMapFamilyName',
                 'openTypeNameCompatibleFullName', 'openTypeNameDescription'):
        value = getattr(info, attr, None)
        if value:
            setattr(info, attr, rebrand(value, family))


def widen(src: Path, dst: Path, sx: float):
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)

    # ---- masters -----------------------------------------------------------
    masters_dst = dst / 'masters'
    shutil.copytree(src / 'masters', masters_dst)
    masters = sorted(masters_dst.glob('*.ufo'))
    for index, path in enumerate(masters, 1):
        font = ufoLib2.Font.open(path)
        scale_font(font, sx, VARIABLE_FAMILY)
        font.save(path, overwrite=True)
        print(f'  master {index}/{len(masters)} {path.name}', flush=True)

    # ---- statics (upright only) -------------------------------------------
    static_dst = dst / 'static'
    static_dst.mkdir()
    statics = [p for p in sorted((src / 'static').glob('*.ufo')) if 'Oblique' not in p.name]
    for index, path in enumerate(statics, 1):
        target = static_dst / path.name
        shutil.copytree(path, target)
        font = ufoLib2.Font.open(target)
        scale_font(font, sx, FAMILY)
        font.save(target, overwrite=True)
        print(f'  static {index}/{len(statics)} {path.name}', flush=True)

    # ---- designspace -------------------------------------------------------
    ds = DesignSpaceDocument.fromfile(src / 'Allo.designspace')
    for source in ds.sources:
        if source.familyName:
            source.familyName = rebrand(source.familyName, VARIABLE_FAMILY)
        # point each source at the widened copy: designspaceLib resolves paths
        # relative to the document, and writing to another folder otherwise
        # rewrites them to the original masters
        source.path = str(masters_dst / Path(source.filename).name)
    for instance in ds.instances:
        instance.familyName = VARIABLE_FAMILY
        if getattr(instance, 'postScriptFontName', None):
            instance.postScriptFontName = rebrand(instance.postScriptFontName, VARIABLE_FAMILY)
    ds.write(dst / 'Allo.designspace')

    # ---- release config ----------------------------------------------------
    config = json.loads((src.parent / 'release.json').read_text())
    if 'smallShift' in config:
        # opsz 9 is the text design moved apart on both sides; keep that move
        # proportional, otherwise the small size loses its relative tracking
        config['smallShift'] = otRound(config['smallShift'] * sx)
    config['family'] = FAMILY
    config['filePrefix'] = FILE_PREFIX
    config['widen'] = {'scaleX': sx, 'family': FAMILY}
    (dst / 'release.json').write_text(json.dumps(config, indent=2) + '\n')
    return masters, statics, config


def report(masters, statics):
    widest = ('', 0)
    upm = None
    for path in masters[:1]:
        upm = ufoLib2.Font.open(path).info.unitsPerEm
    for path in masters + statics:
        font = ufoLib2.Font.open(path)
        for glyph in font:
            if glyph.width > widest[1]:
                widest = (glyph.name, glyph.width)
    print(f'masters {len(masters)}, statics {len(statics)}, upm {upm}')
    print(f'widest glyph {widest[0]} = {widest[1]} units' + (' (> upm)' if upm and widest[1] > upm else ''))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', type=Path, default=Path('sources'))
    ap.add_argument('--dst', type=Path, default=Path('build/wide-sources'))
    ap.add_argument('--sx', type=float, default=1.25)
    args = ap.parse_args()
    masters, statics, config = widen(args.src.resolve(), args.dst.resolve(), args.sx)
    report(masters, statics)
    print(f'smallShift {config["smallShift"]}')


if __name__ == '__main__':
    main()
