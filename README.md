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

On a school computer, **Install for all users** asks for an administrator password.
Plain **Install** puts the fonts on your own account only, and usually needs no password.
If both are blocked, ask whoever looks after the school's computers to install them.

## What you can type

- Letters **A–Z** and **a–z**, and numbers **0–9**
- Marks: `. , ? ! : ; ' ’ ‘ " “ ” - – — ( ) + = % & # / …`

Word's curly quotes and apostrophes, and the long dash Word makes from " - ", are included.
Other characters (for example é, @ or $) are not in the fonts, so Word shows them in a different font.

## Tips for Word

- Lined fonts: use a big size (36–72) so the kids have room to write.
- Lined fonts: set line spacing to **Single** so the lines don't get cut.
- Spaces also have the lines, so a whole line of text stays lined.
- Sending a worksheet to someone else, or printing it from another computer: in Word go to
  **File → Options → Save** and tick **Embed fonts in the file**. Otherwise a computer
  without the fonts shows the worksheet in a different font.

## The rules every letter follows

- Small letters go from the bottom line up to the dotted line, in the solid and the dotted fonts alike.
- Capitals, tall letters and numbers go from the bottom line up to the top line.
- Bars of A E F H G, middles of B P R, and where K and Y meet sit on the dotted line.
- Tails of g j p q y go below the bottom line.
- The small t starts about halfway up the top space and ends with a small curve.
- The i and j dot is a round dot, about halfway up the top space.
- The q ends with a little kick to the right, so it never looks like a g.
- The capital J has a roof: a bar across the top line.

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

3. On each computer that has the old fonts: close Word, open **Settings → Personalization → Fonts**,
   search for **YYS Print**, uninstall each one, then install the new files.

## Other files

| File | What it is |
| --- | --- |
| `yys_print.html` | the YYS Print page: type any words and see them in our letters |
| `yys_print.py` | the letter shapes (used to make the practice sheets and the fonts) |
| `build_fonts.py` | rebuilds the four fonts into the `fonts` folder |
| `requirements.txt` | the Python packages `build_fonts.py` needs |
