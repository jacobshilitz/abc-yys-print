# YYS Print – our school letters

*Credit: YYS*

## Fonts (for typing in Word)

The fonts are in the [`fonts`](fonts) folder.

| File | What it is |
| --- | --- |
| `ABCYYSPrint.ttf` | solid letters |
| `ABCYYSPrintDots.ttf` | dotted letters, for tracing |
| `ABCYYSPrintLined.ttf` | solid letters with the three handwriting lines built in |
| `ABCYYSPrintDotsLined.ttf` | dotted letters with the three lines built in |

## How to install (Windows)

1. Open the `fonts` folder.
2. Right-click each `.ttf` file and choose **Install** (or **Install for all users**).
3. Close Word and open it again.
4. In Word, pick the font by name: **ABC YYS Print**, **ABC YYS Print Dots**,
   **ABC YYS Print Lined** or **ABC YYS Print Dots Lined**.

## How to reinstall (after the fonts are rebuilt)

Windows keeps using the old copy until it is removed, so take the old fonts out first:

1. Close Word, and any other program that uses the fonts.
2. Open **Settings → Personalization → Fonts**.
3. Search for **YYS Print**. Click each font it finds and choose **Uninstall**.
   This also removes the old fonts from before the rename (called just "YYS Print").
4. Install the new files from the `fonts` folder, as described above.
5. Open Word again.

If Windows says a font is in use, restart the computer and uninstall it again
before opening Word.

Word documents made with the old names ("YYS Print", "YYS Print Dots", and so on)
need the text selected and the font changed to the new "ABC" name.

## Tips for Word

- Lined fonts: use a big size (36–72) so the boys have room to write.
- Lined fonts: set line spacing to **Single** so the lines don't get cut.
- Spaces also have the lines, so a whole line of text stays lined.

## The rules every letter follows

- Small letters go from the bottom line up to the dotted line
  (in the dotted fonts they stop just below it, so the dots stay easy to see).
- Capitals, tall letters and numbers go from the bottom line up to the top line.
- Bars of A E F H G, middles of B P R, and where K and Y meet sit on the dotted line.
- Tails of g j p q y go below the bottom line.
- The small t starts about halfway up the top space and ends with a small curve.
- The i and j dot is a short dash (two dots in the dotted fonts).

## Rebuilding the fonts

After a letter is changed in `yys_print.py`, rebuild the four fonts:

1. Install what the build needs (only the first time):

   ```bash
   python -m pip install -r requirements.txt
   ```

2. Build the fonts:

   ```bash
   python build_fonts.py
   ```

   The new fonts are saved into the `fonts` folder, replacing the old ones.

3. Reinstall them in Windows (see [How to reinstall](#how-to-reinstall-after-the-fonts-are-rebuilt)).

## Other files

| File | What it is |
| --- | --- |
| `yys_print.html` | the YYS Print page: type any words and see them in our letters |
| `yys_print.py` | the letter shapes (used to make the practice sheets and the fonts) |
| `build_fonts.py` | rebuilds the four fonts into the `fonts` folder |
| `requirements.txt` | the Python packages `build_fonts.py` needs |
