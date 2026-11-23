"""Build installable YYS Print fonts (.ttf) from yys_print.py.

Four fonts:
  ABC YYS Print            solid letters (small letters touch the dotted line)
  ABC YYS Print Dots       dotted letters for tracing (same heights as the solid letters)
  ABC YYS Print Lined      solid letters with the three handwriting lines built in
  ABC YYS Print Dots Lined dotted letters with the three lines built in
The dot rules are the same as on the YYS Print page.
"""
import math
from shapely.geometry import LineString, Point, Polygon, MultiPolygon, box
from shapely.ops import unary_union
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
import yys_print as Y

VERSION = '1.200'            # raise this whenever the letters change, so Windows and Word see a new version
U = 350                      # one line space (bottom line -> dotted line) in font units
UPM = 1000
STROKE = 0.12 * U            # solid pen width (same ratio as the page)
SW = 0.11 * U                # dot diameter: big enough to see and to survive a photocopier
STEP = U / 6                 # dot spacing: close enough that small letters (s, t, ?) still read as letters
LINE_W = 10                  # guide line thickness
SIDE = Y.GAP / 2             # side bearing on each side, in line units
DESC = int(1.25 * U)         # room below the baseline (tails + bottom of lined fonts)
ASC = int(2 * U + 90)


# ---------------- dot placement: same rules as the page ----------------
def seg_int(p, q, r, s):
    d = (q[0]-p[0])*(s[1]-r[1]) - (q[1]-p[1])*(s[0]-r[0])
    if abs(d) < 1e-9: return None
    t = ((r[0]-p[0])*(s[1]-r[1]) - (r[1]-p[1])*(s[0]-r[0])) / d
    u = ((r[0]-p[0])*(q[1]-p[1]) - (r[1]-p[1])*(q[0]-p[0])) / d
    return t if (1e-6 < t < 1-1e-6 and -1e-6 <= u <= 1+1e-6) else None


def proj(pt, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]; L2 = dx*dx + dy*dy
    if not L2: return 0, math.dist(pt, a)
    t = max(0, min(1, ((pt[0]-a[0])*dx + (pt[1]-a[1])*dy) / L2))
    return t, math.hypot(pt[0]-a[0]-t*dx, pt[1]-a[1]-t*dy)


def place_dots(S, half, step):
    tol = 0.06 * half
    splits = [dict() for _ in S]
    for i, A in enumerate(S):
        for j, B in enumerate(S):
            if i == j: continue
            for a in range(len(A)-1):
                for b in range(len(B)-1):
                    t = seg_int(A[a], A[a+1], B[b], B[b+1])
                    if t is not None: splits[i].setdefault(a, []).append(t)
                for e in (B[0], B[-1]):
                    t, d = proj(e, A[a], A[a+1])
                    if d < tol and 1e-3 < t < 1-1e-3: splits[i].setdefault(a, []).append(t)
    pieces = []
    for i, A in enumerate(S):
        pts, anc = [A[0]], [True]
        for a in range(len(A)-1):
            for t in sorted(splits[i].get(a, [])):
                pts.append((A[a][0]+(A[a+1][0]-A[a][0])*t, A[a][1]+(A[a+1][1]-A[a][1])*t)); anc.append(True)
            pts.append(A[a+1]); anc.append(a+1 == len(A)-1)
        for k in range(1, len(pts)-1):
            a1 = math.atan2(pts[k][1]-pts[k-1][1], pts[k][0]-pts[k-1][0]); a2 = math.atan2(pts[k+1][1]-pts[k][1], pts[k+1][0]-pts[k][0])
            t = abs(math.degrees(a2-a1)); t = 360-t if t > 180 else t
            if t > 35: anc[k] = True
        cur = [pts[0]]
        for k in range(1, len(pts)):
            cur.append(pts[k])
            if anc[k]: pieces.append((len(A) == 2, cur, i)); cur = [pts[k]]
    out = []
    def add(p):
        if not any(math.dist(p, q) < 0.38*step for q in out): out.append(p)
    sticks = [(A[k-1], A[k], si) for si, A in enumerate(S) for k in range(1, len(A)) if math.dist(A[k-1], A[k]) > 1.5*step]
    def beside_stick(p, si): return any(sj != si and proj(p, u, v)[1] < 0.6*step for u, v, sj in sticks)
    for straight, P, si in pieces:
        seg = [math.dist(P[k-1], P[k]) for k in range(1, len(P))]; L = sum(seg)
        n = max(1, round(L/step))
        for k in range(n+1):
            t = L*k/n; i = 0
            while i < len(seg)-1 and t > seg[i]: t -= seg[i]; i += 1
            f = min(1, t/seg[i]) if seg[i] else 0
            q = (P[i][0]+(P[i+1][0]-P[i][0])*f, P[i][1]+(P[i+1][1]-P[i][1])*f)
            if not straight and seg[i] <= 1.5*step and 0 < k < n and beside_stick(q, si): continue
            add(q)
    return out


# ---------------- glyph shapes ----------------
def glyph_shape(ch, dotted):
    """Shapely geometry of one character, in font units, starting at x=SIDE*U."""
    strokes, w = Y.G[ch]
    xh = Y.XH_DOTTED if dotted else Y.XH
    r = (SW / 2) if dotted else (STROKE / 2)          # half the pen: keep the outside edge on the line, not past it
    def fy(yl):
        return (r + yl * (U - 2 * r)) if yl <= 1 else (U - r) + (yl - 1) * U
    S = [[((SIDE + px) * U, fy(Y.ymap(py, xh))) for px, py in s] for s in strokes]
    parts = []
    if not dotted:
        for s in S:
            if len(s) == 2 and math.dist(s[0], s[1]) < 1:      # a dot (i, j, period, colon): a bit bigger than the pen
                parts.append(Point(s[0]).buffer(STROKE * 0.65, 16))
            else:
                parts.append(LineString(s).buffer(STROKE / 2, 16, cap_style=1, join_style=1))
    else:
        keep = []
        for s in S:
            L = math.dist(s[0], s[-1]) if len(s) == 2 else 99 * U
            if L < STEP * 1.2:                       # short marks: i/j dot, period, comma, colon: one round dot
                x, y = (s[0][0]+s[-1][0])/2, (s[0][1]+s[-1][1])/2
                parts.append(Point(x, y).buffer(SW*0.6, 12))
                continue
            keep.append(s)
        parts += [Point(p).buffer(SW/2, 12) for p in place_dots(keep, U, STEP)]
    return unary_union(parts) if parts else None, (w + 2*SIDE) * U


def lines_shape(adv, lw=LINE_W):
    """The three handwriting lines across one character's width."""
    LINE_W = lw
    parts = [box(0, 2*U - LINE_W/2, adv, 2*U + LINE_W/2), box(0, -LINE_W/2, adv, LINE_W/2)]
    # dashed middle line: every character starts and ends halfway through a gap, so neighbours join seamlessly
    period = U * 0.32
    n = max(1, round(adv / period)); period = adv / n; dash = period / 2
    for k in range(n):
        x0 = k * period + (period - dash) / 2
        parts.append(box(x0, U - LINE_W/2, x0 + dash, U + LINE_W/2))
    return unary_union(parts)


def to_glyph(geom):
    pen = TTGlyphPen(None)
    if geom is None or geom.is_empty:
        return pen.glyph()
    polys = [geom] if isinstance(geom, Polygon) else list(getattr(geom, 'geoms', []))
    for poly in polys:
        if not isinstance(poly, Polygon): continue
        rings = [(poly.exterior, False)] + [(r, True) for r in poly.interiors]
        for ring, hole in rings:
            pts = [(round(x), round(y)) for x, y in ring.coords[:-1]]
            clean = [p for i, p in enumerate(pts) if p != pts[i-1]]
            if len(clean) < 3: continue
            # TrueType: outer contours clockwise, holes counter-clockwise
            area = sum(clean[i][0]*clean[(i+1) % len(clean)][1] - clean[(i+1) % len(clean)][0]*clean[i][1] for i in range(len(clean)))
            if (area > 0) != hole: clean = clean[::-1]
            pen.moveTo(clean[0])
            for p in clean[1:]: pen.lineTo(p)
            pen.closePath()
    return pen.glyph()


# ---------------- kerning: measured from the letter shapes, so it stays right when a letter changes ----------------
KERN_BAND = 20          # measure the edges every 20 units of height
KERN_TOL = 70           # look this far up and down for the nearest ink, so letters never get closer than normal
KERN_MAX = 300          # never tighten a pair by more than this
KERN_MIN = 30           # skip tiny changes (round letters measure a few units off)
KERN_MARK_MAX = 100     # after a small letter, a period or comma moves in at most this much (so "r." never reads "r:")


def edge_profiles(geom):
    """Left and right ink edge of a letter in each height band (None where the band is empty)."""
    lo, hi = -DESC, ASC
    bands = list(range(lo, hi, KERN_BAND))
    left, right = [], []
    for y in bands:
        part = geom.intersection(box(-10 * U, y, 20 * U, y + KERN_BAND)) if geom is not None else None
        if part is None or part.is_empty:
            left.append(None); right.append(None)
        else:
            x0, _, x1, _ = part.bounds
            left.append(x0); right.append(x1)
    return left, right


def make_kerning():
    """{(first, second): units} for every pair that sits further apart than two n's.

    For each height, the gap is (space right of the first letter) + (space left of the second);
    the first letter's edge is taken as the furthest ink within KERN_TOL above or below.
    A pair is pulled together until its smallest gap equals the n-n gap. Pairs are never pushed apart."""
    chars = list(Y.G)
    shape = {c: glyph_shape(c, False) for c in chars}
    prof = {c: edge_profiles(shape[c][0]) for c in chars}
    reach = KERN_TOL // KERN_BAND
    def right_tol(c):
        r = prof[c][1]; out = []
        for j in range(len(r)):
            near = [v for v in r[max(0, j - reach): j + reach + 1] if v is not None]
            out.append(max(near) if near else None)
        return out
    rt = {c: right_tol(c) for c in chars}
    def min_gap(a, b):
        adv = shape[a][1]; gaps = [adv - r + l for r, l in zip(rt[a], prof[b][0]) if r is not None and l is not None]
        return min(gaps) if gaps else None
    target = min_gap('n', 'n')
    letters = [c for c in chars if c.isalpha()]
    firsts = letters + [c for c in chars if c.isdigit()]
    seconds = letters + ['.', ',']          # quotes, dashes and other marks keep their normal space
    kern = {}
    for a in firsts:
        for b in seconds:
            if a.isdigit() and b.isalpha(): continue
            g = min_gap(a, b)
            if g is None: continue
            k = max(-KERN_MAX, round(target - g))
            if a.islower() and b in '.,': k = max(-KERN_MARK_MAX, k)
            if k <= -KERN_MIN: kern[(a, b)] = int(k)
    return kern


def add_kerning(font, kern, names):
    """Write the kerning both ways: the modern 'kern' feature (GPOS) and the old kern table older Word reads."""
    from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
    from fontTools.ttLib import newTable
    from fontTools.ttLib.tables._k_e_r_n import KernTable_format_0
    pairs = {(names[a], names[b]): v for (a, b), v in kern.items()}
    fea = 'languagesystem DFLT dflt;\nlanguagesystem latn dflt;\nfeature kern {\n' + \
          ''.join(f'  pos {l} {r} {v};\n' for (l, r), v in sorted(pairs.items())) + '} kern;\n'
    addOpenTypeFeaturesFromString(font, fea)
    t = newTable('kern'); t.version = 0
    sub = KernTable_format_0(); sub.version = 0; sub.coverage = 1; sub.kernTable = dict(pairs)
    t.kernTables = [sub]; font['kern'] = t


def update_page(kern, page='yys_print.html'):
    """Copy the letters (G) and the kerning (K, in line units) into the YYS Print page, so it matches the fonts."""
    import json, os, re
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), page)
    html = open(path, encoding='utf-8', newline='').read()
    G = {c: {'w': w, 's': [[[round(x, 3), round(y, 3)] for x, y in s] for s in st]} for c, (st, w) in Y.G.items()}
    K = {a + b: round(v / U, 3) for (a, b), v in sorted(kern.items())}
    m = re.search(r'const G=\{.*?\};(\r?\n)', html)
    nl = m.group(1)
    new = 'const G=' + json.dumps(G, separators=(',', ':')) + ';' + nl + 'const K=' + json.dumps(K, separators=(',', ':')) + ';   // kerning, made by build_fonts.py' + nl
    html = html[:m.start()] + new + html[m.end():]
    html = re.sub(r'const K=\{.*?\};[^\r\n]*\r?\n(?=const K=)', '', html)   # drop an older K line if there was one
    html = re.sub(r'(const K=\{.*?\};[^\r\n]*\r?\n)const K=\{.*?\};[^\r\n]*\r?\n', r'\1', html)
    open(path, 'w', encoding='utf-8', newline='').write(html)


def build(family, dotted, lined, path, kern=None):
    chars = [c for c in Y.G] + [' ']
    names = {c: ('space' if c == ' ' else f'uni{ord(c):04X}') for c in chars}
    order = ['.notdef'] + [names[c] for c in chars]
    glyphs, metrics = {'.notdef': TTGlyphPen(None).glyph()}, {'.notdef': (int(U), 0)}
    for c in chars:
        if c == ' ':
            geom, adv = None, Y.SPACE * U
        else:
            geom, adv = glyph_shape(c, dotted)
        adv = int(round(adv))
        if lined:
            lw = 9 if dotted else 10
            geom = lines_shape(adv, lw) if geom is None else unary_union([geom, lines_shape(adv, lw)])
        g = to_glyph(geom)
        glyphs[names[c]] = g
        g.recalcBounds(None) if hasattr(g, 'recalcBounds') else None
        metrics[names[c]] = (adv, 0)
    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap({**{ord(c): names[c] for c in chars}, 0xA0: 'space'})   # Word's no-break space looks like a space
    fb.setupGlyf(glyphs)
    gl = fb.font['glyf']
    hm = {}
    for n in order:
        g = gl[n]; g.recalcBounds(gl)
        hm[n] = (metrics[n][0], getattr(g, 'xMin', 0) if g.numberOfContours else 0)
    fb.setupHorizontalMetrics(hm)
    fb.setupHorizontalHeader(ascent=ASC, descent=-DESC)
    style = 'Regular'
    fb.setupNameTable({'familyName': family, 'styleName': style, 'uniqueFontIdentifier': f'{family.replace(" ", "")}-{style};{VERSION};YYS',
                       'fullName': family, 'psName': family.replace(' ', '') + '-' + style, 'version': f'Version {VERSION}',
                       'copyright': 'YYS Print. Credit: YYS', 'designer': 'YYS'})
    fb.setupOS2(sTypoAscender=ASC, sTypoDescender=-DESC, sTypoLineGap=0, usWinAscent=ASC, usWinDescent=DESC,
                sxHeight=int(U), sCapHeight=int(2*U), achVendID='YYS ', fsType=0)
    fb.setupPost()
    # tell Windows/Word to smooth only, never snap each letter to the pixel grid (keeps the built-in lines straight)
    from fontTools.ttLib import newTable
    gasp = newTable('gasp'); gasp.gaspRange = {0xFFFF: 0x000A}   # symmetric smoothing + smoothing, no grid-fitting
    fb.font['gasp'] = gasp
    fb.setupHead(unitsPerEm=UPM, fontRevision=float(VERSION))
    if kern:
        add_kerning(fb.font, kern, names)
    fb.save(path)


if __name__ == '__main__':
    import os
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
    os.makedirs(out_dir, exist_ok=True)
    kern = make_kerning()   # one table, measured on the solid letters, used in all four fonts
    print('kerning pairs:', len(kern))
    update_page(kern)
    print('updated yys_print.html (letters and kerning)')
    for fam, dotted, lined in [('ABC YYS Print', False, False), ('ABC YYS Print Dots', True, False),
                               ('ABC YYS Print Lined', False, True), ('ABC YYS Print Dots Lined', True, True)]:
        p = os.path.join(out_dir, f"{fam.replace(' ', '')}.ttf")
        build(fam, dotted, lined, p, kern)
        print('built', p, os.path.getsize(p) // 1024, 'KB')
