  ALLO WIDE  1.0 ........................................ type specimen

  A wider cut of Allo, built for interfaces laid out in a wider face.


  WHAT THIS IS
    Allo by Josh Puckett, with Cyrillic by Degroshi (upstream PR #8),
    stretched 25% horizontally. Outlines, advances, anchors and kerning
    are scaled on the X axis; nothing was redrawn.

    The result is the same size, the same line height and the same
    spacing rhythm, but every word is a quarter wider. Vertical stems
    are a quarter thicker, and the ROND corners are slightly wider than
    they are tall. At 12-24 px neither is noticeable.

    There are no obliques in this family: a plain X scale would change
    the slant angle.


  STYLES
    100 Thin        400 Regular     700 Bold
    200 ExtraLight  500 Medium      800 ExtraBold
    300 Light       600 SemiBold    900 Black

    Upright only. The variable font covers weight and optical size,
    and roundness (0 sharp, 50 friendly, 100 round).


  FILES
    fonts/otf/        9 static fonts. Install these on your computer.
    fonts/variable/   AlloWideVariable.ttf, for apps with variable
                      fonts. Its family is "Allo Wide Variable", so it
                      installs beside the static fonts.
    fonts/webfonts/   The same fonts as WOFF2, for websites, plus
                      AlloWideVariableFriendly.woff2: the variable font
                      with roundness fixed at Friendly (50). About half
                      the size; it has no ROND axis.
    OFL.txt           The license.

    Mac       double-click a font, then Install
    Windows   select the files, right-click, Install


  WEB
    @font-face {
      font-family: "Allo Wide";
      src: url("AlloWideVariable.woff2") format("woff2");
      font-weight: 100 900;
    }
    body { font-family: "Allo Wide", sans-serif; }
    /* Optical size follows the font size on its own.
       To keep Text everywhere: font-optical-sizing: none; */

    Not changing roundness? Use AlloWideVariableFriendly.woff2:
    about half the size, optical size and weight still work, and
    roundness stays at 50 ("ROND" does nothing).


  ....................................................................
  Allo (c) Josh Puckett  .  joshpuckett.me
  Cyrillic (c) Degroshi  .  github.com/degroshi
  Wide cut: github.com/ynckz/allo
  SIL Open Font License 1.1
