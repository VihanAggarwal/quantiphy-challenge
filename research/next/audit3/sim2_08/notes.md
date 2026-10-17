# Audit sim2_08: family simulation_0257 / 0258 / 0259 / 0260 (D2)

All four clips have the same fixed camera and the same table scene. One object free-falls from rest at t=0
(0257 plant, 0258 pen, 0259 red cup, 0260 mug) and lands on the back part of the table (contact y about 868-871).
Prior: g = 9.8 m/s^2. The containers for 0257/0258 say 24 fps, but the stated fps is 30, and the pixel acceleration
per frame^2 is the same in all four clips (6.83-6.99 px/fr^2). All clips therefore share one frame rate (30) and one scale.

## Scale (my own template track, quadratic fit; scripts fit.py, util.py)
| clip | object | a px/fr^2 | n0 (frames) | s (m/px at object depth) | v(0.2) | v(0.4) |
|---|---|---|---|---|---|---|
| 0257 | plant | 6.938 | -0.02 | 1.5695e-3 | 1.804 | 3.764 |
| 0258 | pen | 6.83-6.95 (template/edges) | -0.15..0.05 | 1.566-1.594e-3 | 1.78-1.84 | 3.74-3.80 |
| 0259 | red cup | 6.988 | -0.06 | 1.5582e-3 | 1.815 | 3.775 |
| 0260 | mug | 6.961 | -0.06 | 1.5643e-3 | 1.817 | 3.777 |

## Perspective: the scene is NOT telephoto
Camera with lens shift. The depth vanishing point (VP) is about (1462, 724.5). It comes from three separate sets of cues:
- The window-sill bottom edge on the right wall (y = 0.386x + 159.9) meets the table top's slanted left edge
  (518,895)->(679,866) at about (1462, 724.5).
- The AC's right-side grille louvers, fitted alone, give a VP of about (1433, 738). Louver slopes measured vs. predicted
  from VP (1462,724.5): y~825 -0.105/-0.115; y~955 -0.255/-0.27; y~995 -0.305/-0.31; y~1037 -0.36/-0.36.
- The table top's left end slants. The front-left corner is at (518, 895). The back-left corner is at (679, 866): the top
  surface boundary follows that line (z_tl2.png), and the back-left leg sits at x 677-707.
  So the table's back edge is about 1.205x as deep as its front edge.
Falling objects rest at contact y about 868-869.5. The table front edge is at y=895 and the back edge at y=865.75.
So the front edge is about 15% closer than the objects whose fall sets the scale: Z_front/Z_obj = 0.846 (VP A) or 0.833 (VP B).

## Rows checked (quick-check value vs current)
| qid | clip | quantity | current | quick check | verdict |
|---|---|---|---|---|---|
| 883 | 0257 | plant height | 0.101 | 0.096-0.099 (61-63 px) | ok |
| 884 | 0257 | plant diameter | 0.0757 | 0.074-0.075 (47-48 px) | ok |
| 885 | 0257 | table width | 1.578 | 1.34-1.36 | **FIX -> 1.35** |
| 886 | 0257 | AC width | 0.797 | 0.64-0.72 if AC is near table depth (front face 436.5 px) | unresolved, no fix (see AC) |
| 887 | 0257 | phone width | 0.079 | 0.069-0.079 (45 px near edge / 50 px x-extent) | ok |
| 888 | 0257 | plant v(0.2) | 1.817 | 1.804 | ok |
| 889 | 0257 | plant v(0.4) | 3.776 | 3.764 | ok |
| 890 | 0258 | plant height | 0.097 | 0.095-0.097 | ok |
| 891 | 0258 | plant diameter | 0.075 | 0.074 | ok |
| 892 | 0258 | table width | 1.62 | 1.34-1.36 | **FIX -> 1.35** |
| 893 | 0258 | AC width | 0.82 | see AC | unresolved, no fix |
| 894 | 0258 | phone width | 0.081 | 0.069-0.079 | ok (<15%) |
| 895 | 0258 | pen v(0.2) | 1.85 | 1.78-1.84 | ok |
| 896 | 0258 | pen v(0.4) | 3.81 | 3.74-3.80 | ok |
| 897 | 0259 | red cup height | 0.1006 | 0.096-0.098 (62.5 px raw) | ok |
| 898 | 0259 | plant height | 0.0958 | 0.095-0.097 | ok |
| 899 | 0259 | plant diameter | 0.0756 | 0.074 | ok |
| 900 | 0259 | table width | 1.367 | 1.34-1.36 | ok |
| 901 | 0259 | AC width | 0.77 | see AC | unresolved, no fix |
| 902 | 0259 | iPhone width | 0.078 | 0.069-0.079 | ok |
| 903 | 0259 | cup v(0.2) | 1.83 | 1.815 | ok |
| 904 | 0259 | cup v(0.4) | 3.79 | 3.775 | ok |
| 905 | 0259 | mug height | 0.0836 | 0.084 (53.5 px) | ok |
| 906 | 0259 | bag long side | 0.35 | 0.348 (222 px) | ok |
| 907 | 0260 | red cup height | 0.097 | 0.096-0.098 | ok |
| 908 | 0260 | plant height | 0.094 | 0.095-0.097 | ok |
| 909 | 0260 | plant diameter | 0.073 | 0.074 | ok |
| 910 | 0260 | table width | 1.34 | 1.34-1.36 | ok |
| 911 | 0260 | AC width | 0.634 | see AC | ok/unresolved |
| 912 | 0260 | iPhone width | 0.08 | 0.069-0.079 | ok |
| 913 | 0260 | mug v(0.2) | 1.81 | 1.817 | ok |
| 914 | 0260 | mug v(0.4) | 3.77 | 3.777 | ok |
| 915 | 0260 | mug height | 0.085 | 0.084 | ok |
| 916 | 0260 | bag long side | 0.342 | 0.348 | ok |

## Fix: table width, 0257 (qid 885) and 0258 (qid 892) -> 1.35
The table top's front edge runs from x=518.0 to x=1538.8 (1020.8 px) at front-edge depth.
- Route A: horizon 724.5 from the sill line and the table's left edge, with the y-ratio of object contact to front edge.
  Gives 1020.8 x s x 0.846: 0257 1.358, 0258 1.360, 0259 1.353, 0260 1.341.
- Route B: horizon 738 from the AC louvers alone. Gives 1.333-1.338.
- Route C: x-convergence of the left-end corners (k = 1.206-1.214), plus 1/Z interpolation of the object y between the
  front and back edges, with no horizon needed. Gives 1.344-1.352.
- The independent per-clip agents for 0259 and 0260 got 1.367 and 1.34.
Why the current values are wrong: the 0257 and 0258 agents scaled the 1020-px front edge with the object-depth scale.
0257 called the view "telephoto, perspective ~3%". 0258 made no correction. The front edge is about 15% closer than
the objects, so their answers are 16-20% too high.

## AC width: no fix proposed (criterion not met), but the family is inconsistent
- The full 132-637 extent (505 px) used by 0257, 0258 and 0259 includes the AC's RIGHT SIDE FACE (x 568-637.5).
  Its louver slopes change with height exactly as lines receding to the VP should (table above).
  The front face is only 131.5-568, which is 436.5 px.
- The front-face width is 436.5 px x 1.568e-3 x (Z_ac/Z_obj). The AC's depth cannot be measured: the floor is not
  visible, and its distance to the wall and the table is unknown.
  - Z_ac/Z_obj = 0.94 (AC back against a wall at the table's back edge) gives 0.644.
  - Z_ac/Z_obj = 1.0 gives 0.684.
  - If the AC is a real-scale LG unit (W/H <= 1.36 forces about 870x650 or larger), the width would be 0.87-0.95,
    which needs the AC well behind the table.
- So the plausible range is 0.64-0.95. The current 0.77/0.80/0.82 rest on the wrong reading (side face included),
  but there are no two independent routes that pin the value. Left unchanged. 0260's 0.634 is the layout-prior reading.

## Phone (low confidence, no fix)
The phone lies with its long side in depth. The near edge is x 1141-1187 (about 45 px). The whole x-extent, including
the slanted far corner, is about 51 px. That gives a width of 0.069-0.079. The current 0.078-0.081 is less than 15% off.
