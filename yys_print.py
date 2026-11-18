"""YYS Print: a single-line school print alphabet drawn on the three handwriting lines.

Units: baseline y=0, dotted middle line y=1, top line y=2, tails go down to y=-0.9.
Every glyph is a list of strokes (polylines). Rules:
  - small letters fill 0..1, tall letters / capitals / digits fill 0..2
  - bars of A E F H, middles of B P R K Y, bar of G, 4 and the meeting point of K sit on y=1
  - dot of i / j: a short upright stroke between the dotted line and the top line (1.38..1.72)
  - q has a straight tail, Q a short straight slanted tail
"""
import math

TAIL = -0.9          # how far tails (g j p q y) go below the baseline
GAP = 0.45           # space between letters
SPACE = 1.0         # word space


XH = 1.0             # solid letters touch the dotted line; use XH_DOTTED for dotted tracing letters
XH_DOTTED = 0.97     # dotted: small letters and middle bars stop just below the dotted line


def ymap(y, xh=XH):
    """Drawing height -> line height: 0..1 squeezes to 0..xh, 1..2 stretches to xh..2."""
    return y * xh if y <= 1 else xh + (y - 1) * (2 - xh)


def arc(cx, cy, rx, a0, a1, ry=None, n=None):
    """Arc from angle a0 to a1 (degrees, counter-clockwise if a1 > a0)."""
    ry = rx if ry is None else ry
    n = n or max(8, int(abs(a1 - a0) / 6))
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * t / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * t / n))) for t in range(n + 1)]


def circle(cx, cy, r, ry=None, start=90):
    # starts at the top and goes counter-clockwise, the way kids draw "o"
    return arc(cx, cy, r, start, start + 360, ry)


def line(*pts):
    return list(pts)


def spline(pts, n=8):
    """Smooth Catmull-Rom curve through the given points."""
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = [pts[0]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(1, n + 1):
            t = k / n; t2 = t * t; t3 = t2 * t
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    return out


DOT = lambda x: line((x, 1.32), (x, 1.5))   # short upright dash, a small gap above the stem


# small s: one pen line from the top tip to the bottom tip, traced from the writing letters
# in the students' reading books. The capital S is the same shape, twice the size.
S_PTS = [
    (0.826, 0.785), (0.806, 0.83), (0.78, 0.872), (0.746, 0.907), (0.706, 0.936), (0.662, 0.958),
    (0.615, 0.974), (0.567, 0.986), (0.519, 0.993), (0.469, 0.998), (0.42, 1), (0.371, 0.998),
    (0.322, 0.994), (0.273, 0.986), (0.226, 0.973), (0.18, 0.955), (0.137, 0.932), (0.097, 0.902),
    (0.063, 0.867), (0.036, 0.825), (0.02, 0.779), (0.012, 0.73), (0.016, 0.681), (0.031, 0.635),
    (0.061, 0.596), (0.102, 0.568), (0.146, 0.547), (0.194, 0.533), (0.242, 0.523), (0.29, 0.514),
    (0.339, 0.507), (0.388, 0.501), (0.437, 0.495), (0.486, 0.488), (0.535, 0.481), (0.583, 0.472),
    (0.632, 0.463), (0.679, 0.45), (0.724, 0.43), (0.765, 0.402), (0.796, 0.364), (0.811, 0.318),
    (0.815, 0.269), (0.807, 0.22), (0.79, 0.174), (0.764, 0.133), (0.729, 0.097), (0.69, 0.068),
    (0.646, 0.045), (0.6, 0.027), (0.553, 0.014), (0.504, 0.006), (0.455, 0.001), (0.406, 0), (0.357, 0.002),
    (0.307, 0.007), (0.259, 0.014), (0.211, 0.026), (0.164, 0.042), (0.12, 0.064), (0.08, 0.092),
    (0.046, 0.128), (0.02, 0.17), (0, 0.215),
]
S_W = 0.826

G = {}   # char -> (strokes, width)

# ---------------- lowercase (x-height 1) ----------------
G['a'] = ([circle(0.5, 0.5, 0.5), line((1, 1), (1, 0))], 1.0)
G['b'] = ([line((0, 2), (0, 0)), circle(0.5, 0.5, 0.5)], 1.0)
G['c'] = ([arc(0.5, 0.5, 0.5, 45, 315)], 0.9)
G['d'] = ([circle(0.5, 0.5, 0.5), line((1, 2), (1, 0))], 1.0)
G['e'] = ([line((0, 0.5), (1, 0.5)) + arc(0.5, 0.5, 0.5, 0, 315)[1:]], 1.0)
G['f'] = ([arc(0.75, 1.65, 0.35, 30, 180) + [(0.4, 0)], line((0, 1), (0.85, 1))], 0.85)
G['g'] = ([circle(0.5, 0.5, 0.5), line((1, 1), (1, TAIL + 0.5)) + arc(0.5, TAIL + 0.5, 0.5, 0, -165)[1:]], 1.0)   # long hook, as wide as the bowl
G['h'] = ([line((0, 2), (0, 0)), line((0, 0.5)) + arc(0.5, 0.5, 0.5, 180, 0)[1:] + [(1, 0)]], 1.0)
G['i'] = ([line((0, 1), (0, 0)), DOT(0)], 0.0)
G['j'] = ([line((0.45, 1), (0.45, TAIL + 0.5)) + arc(-0.05, TAIL + 0.5, 0.5, 0, -165)[1:], DOT(0.45)], 0.45)   # same long hook as g
G['k'] = ([line((0, 2), (0, 0)), line((0.85, 1), (0, 0.45), (0.85, 0))], 0.85)
G['l'] = ([line((0, 2), (0, 0))], 0.0)
G['m'] = ([line((0, 1), (0, 0)),
           line((0, 0.5)) + arc(0.4, 0.5, 0.4, 180, 0, ry=0.5)[1:] + [(0.8, 0)],
           line((0.8, 0.5)) + arc(1.2, 0.5, 0.4, 180, 0, ry=0.5)[1:] + [(1.6, 0)]], 1.6)   # wide, round humps so it reads clearly as m
G['n'] = ([line((0, 1), (0, 0)), line((0, 0.5)) + arc(0.5, 0.5, 0.5, 180, 0)[1:] + [(1, 0)]], 1.0)
G['o'] = ([circle(0.5, 0.5, 0.5)], 1.0)
G['p'] = ([line((0, 1), (0, TAIL)), circle(0.5, 0.5, 0.5)], 1.0)
G['q'] = ([circle(0.5, 0.5, 0.5), line((1, 1), (1, TAIL))], 1.0)
G['r'] = ([line((0, 1), (0, 0)), line((0, 0.5)) + arc(0.5, 0.5, 0.5, 180, 50)[1:]], 0.82)
G['s'] = ([S_PTS], S_W)
G['t'] = ([line((0.35, 1.55), (0.35, 0.3)) + arc(0.65, 0.3, 0.3, 180, 270)[1:] + [(0.78, 0)], line((0, 1), (0.75, 1))], 0.8)   # curved foot; low top, about halfway up the top space
G['u'] = ([line((0, 1), (0, 0.5)) + arc(0.5, 0.5, 0.5, 180, 360)[1:], line((1, 1), (1, 0))], 1.0)
G['v'] = ([line((0, 1), (0.5, 0), (1, 1))], 1.0)
G['w'] = ([line((0, 1), (0.33, 0), (0.66, 1), (0.99, 0), (1.32, 1))], 1.32)
G['x'] = ([line((0.45, 0.5), (0, 1)), line((0.45, 0.5), (0.9, 1)), line((0.45, 0.5), (0, 0)), line((0.45, 0.5), (0.9, 0))], 0.9)   # drawn from the shared middle
G['y'] = ([line((0, 1), (0.5, 0)), line((1, 1), (0.05, TAIL))], 1.0)
G['z'] = ([line((0, 1), (0.9, 1), (0, 0), (0.9, 0))], 0.9)

# ---------------- capitals (height 2, middle on the dotted line) ----------------
G['A'] = ([line((0, 0), (0.75, 2), (1.5, 0)), line((0.375, 1), (1.125, 1))], 1.5)
G['B'] = ([line((0, 2), (0, 0)),
           line((0, 2), (0.65, 2)) + arc(0.65, 1.5, 0.5, 90, -90)[1:] + [(0, 1)],
           line((0, 1), (0.75, 1)) + arc(0.75, 0.5, 0.5, 90, -90)[1:] + [(0, 0)]], 1.25)
G['C'] = ([arc(1, 1, 1, 45, 315)], 1.75)
G['D'] = ([line((0, 2), (0, 0)), line((0, 2), (0.5, 2)) + arc(0.5, 1, 1, 90, -90)[1:] + [(0, 0)]], 1.5)
G['E'] = ([line((1.15, 2), (0, 2), (0, 0), (1.15, 0)), line((0, 1), (0.95, 1))], 1.15)
G['F'] = ([line((1.15, 2), (0, 2), (0, 0)), line((0, 1), (0.95, 1))], 1.15)
G['G'] = ([arc(1, 1, 1, 45, 360), line((2, 1), (1.15, 1))], 2.0)
G['H'] = ([line((0, 2), (0, 0)), line((1.35, 2), (1.35, 0)), line((0, 1), (1.35, 1))], 1.35)
G['I'] = ([line((0.45, 2), (0.45, 0)), line((0, 2), (0.9, 2)), line((0, 0), (0.9, 0))], 0.9)
G['J'] = ([line((1.1, 2), (1.1, 0.55)) + arc(0.55, 0.55, 0.55, 0, -180)[1:]], 1.1)
G['K'] = ([line((0, 2), (0, 0)), line((1.25, 2), (0, 1), (1.25, 0))], 1.25)
G['L'] = ([line((0, 2), (0, 0), (1.1, 0))], 1.1)
G['M'] = ([line((0, 0), (0, 2), (0.95, 0), (1.9, 2), (1.9, 0))], 1.9)
G['N'] = ([line((0, 0), (0, 2), (1.4, 0), (1.4, 2))], 1.4)
G['O'] = ([circle(1, 1, 1)], 2.0)
G['P'] = ([line((0, 0), (0, 2), (0.7, 2)) + arc(0.7, 1.5, 0.5, 90, -90)[1:] + [(0, 1)]], 1.2)
G['Q'] = ([circle(1, 1, 1), line((1.25, 0.45), (1.9, -0.1))], 2.0)
G['R'] = ([line((0, 0), (0, 2), (0.7, 2)) + arc(0.7, 1.5, 0.5, 90, -90)[1:] + [(0, 1)], line((0.5, 1), (1.25, 0))], 1.25)
G['S'] = ([[(2 * x, 2 * y) for x, y in S_PTS]], 2 * S_W)   # same shape as s
G['T'] = ([line((0, 2), (1.4, 2)), line((0.7, 2), (0.7, 0))], 1.4)
G['U'] = ([line((0, 2), (0, 0.65)) + arc(0.65, 0.65, 0.65, 180, 360)[1:] + [(1.3, 2)]], 1.3)
G['V'] = ([line((0, 2), (0.75, 0), (1.5, 2))], 1.5)
G['W'] = ([line((0, 2), (0.5, 0), (1, 2), (1.5, 0), (2, 2))], 2.0)
G['X'] = ([line((0.7, 1), (0, 2)), line((0.7, 1), (1.4, 2)), line((0.7, 1), (0, 0)), line((0.7, 1), (1.4, 0))], 1.4)
G['Y'] = ([line((0, 2), (0.7, 1), (1.4, 2)), line((0.7, 1), (0.7, 0))], 1.4)
G['Z'] = ([line((0, 2), (1.3, 2), (0, 0), (1.3, 0))], 1.3)

# ---------------- digits (height 2) ----------------
G['0'] = ([arc(0.6, 1, 0.6, 90, 450, ry=1)], 1.2)
G['1'] = ([line((0.15, 2), (0.15, 0))], 0.3)   # plain straight line, like school books
G['2'] = ([arc(0.55, 1.45, 0.55, 160, -35) + [(0, 0), (1.15, 0)]], 1.15)
G['3'] = ([arc(0.5, 1.5, 0.5, 155, -90) + arc(0.5, 0.5, 0.5, 90, -155)[1:]], 1.05)
G['4'] = ([line((0.85, 0), (0.85, 2)), line((0, 2), (0, 1), (1.2, 1))], 1.2)
G['5'] = ([line((1.05, 2), (0.15, 2)) + [(0.09, 1.006)] + arc(0.55, 0.62, 0.6, 140, -150)[1:]], 1.15)
G['6'] = ([arc(1.6, 0.6, 1.6, 120, 180)[:-1] + arc(0.55, 0.55, 0.55, 180, 540)], 1.1)
G['7'] = ([line((0, 2), (1.15, 2), (0.35, 0))], 1.15)
G['8'] = ([arc(0.55, 1.55, 0.45, -90, 270), arc(0.55, 0.55, 0.55, 90, 450)], 1.1)
G['9'] = ([arc(0.55, 1.45, 0.55, 0, 360), line((1.1, 1.45), (1.1, 0))], 1.1)

# ---------------- marks ----------------
G['.'] = ([line((0, 0), (0, 0.001))], 0.0)
G[','] = ([line((0.12, 0.05), (0, -0.3))], 0.12)
G['-'] = ([line((0, 0.55), (0.6, 0.55))], 0.6)
G['/'] = ([line((0, -0.1), (0.9, 2))], 0.9)
G[':'] = ([line((0, 0), (0, 0.001)), line((0, 0.9), (0, 0.901))], 0.0)
G["'"] = ([line((0, 2), (0, 1.55))], 0.0)
G['#'] = ([line((0.35, 1.8), (0.25, 0.2)), line((0.85, 1.8), (0.75, 0.2)), line((0, 1.35), (1.05, 1.35)), line((0, 0.65), (1.05, 0.65))], 1.05)


def layout(text, gap=GAP, space=SPACE, dotted=False):
    """Strokes for a whole string (in line units) and its total width."""
    out, x = [], 0.0
    for i, ch in enumerate(text):
        if ch == ' ':
            x += space; continue
        if ch not in G:
            ch = '-'
        strokes, w = G[ch]
        out.append((i, [[(x + px, ymap(py, XH_DOTTED if dotted else XH)) for px, py in s] for s in strokes]))
        x += w + gap
    return out, max(0.0, x - gap)
