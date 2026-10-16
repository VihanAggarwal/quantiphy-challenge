# Lab audit: family 0037 (captured_0037, 0037s, 0037x). One event, so one label per question

Inputs: `../inputs/0037.json` (18 scored rows: 4 static sizes and 2 ping-pong speeds, x 3 renders). Clip: 24 fps,
49 frames, 1280x720. The camera set-up is the same as captured_0040: the table outline matches to within 1 px, and
the cup, poker tower and credit card are in the same places, while the jar and the tape have moved. I used 0040 as a
second, independent view of the same props. No labels were used. I used test inputs only: frames, `prior` and
`depth_info`.

Scripts (all in this folder): `table.py` (table edges -> vanishing points -> plane normal), `cards.py` /
`rectcards.py` (credit card rectified on the plane), `static.py` (heights from the plane), `cyl.py` (exact fit of a
vertical cylinder's silhouette: centre, R, H), `track.py` / `track3d.py` / `speed.py` / `bounce.py` (ball track,
speeds, and a check of the plane height against the bounces). Frames are in `frames/` (all 3 renders) and `f40/` (0040).

## Camera and plane (f = 711, pp = (640, 360))
- The table edges give a normal that is nearly level (the camera sits about 2.3 deg off the table normal). The camera
  is h above the table top:
  - front side = 76.0 cm -> h = 0.169; side = 60.3 cm -> h = 0.1765;
  - **credit card corners rectified -> 8.55 x 5.43 cm at h = 0.172** (true 8.56 x 5.40);
  - ping-pong ball (4 cm, own size scale): the hop parabolas give a centre height of 1.3-2.2 cm at the bounces for
    h = 0.172, and 2.0 cm is expected;
  - the tape diameter of the current pipeline (10.3-10.6) implies h of about 0.176.
  - Taken together: **h = 0.172-0.176**.
- Stated ToF ranges compared with the plane at h = 0.172: credit card 0.679 vs 0.669 (+1.5%), cup 0.845 vs 0.872
  (-3%), tape 1.038 vs 1.005 (+3%), poker tower 0.905 vs 0.86-0.88 (+3..5%). The **glass jar reads 1.008 vs a jar
  centre range of 0.95 (+6%) and a front-glass range of 0.926 (+9%)**: the ToF reading passes through the
  transparent glass.
- The ball's size agrees with the stated depth: the minor axis is 27.1 px at frame 24, which gives Z = 1.065 from
  4 cm, against the stated 1.055.

## Static rows
| qid (o/s/x) | question | current | plane / cylinder fit (h 0.172-0.176) | verdict |
|---|---|---|---|---|
| 2681/2687/2693 | white cup height | 14.82 / 14.75 / 14.75 | 15.0-15.3 (top rim almost edge-on, 127 px) | OK |
| 2682/2688/2694 | poker tower height | 10.42 / 10.41 / 10.41 | 9.3-10.1 (apex 416.5, feet 496-499.5; depends on the apex depth) | OK (within 3-11%) |
| 2683/2689/2695 | glass jar height | 10.65 / 10.21 / 10.21 | **9.0-9.2** | high by 12-17%, below the threshold (see below) |
| 2684/2690/2696 | tape width | 10.64 / 10.29 / 10.50 | diameter 10.25-10.49 (axial band 4.8-4.9) | OK as the diameter reading |

### Glass jar (examined, not proposed)
- Cylinder fits:
  - 0037 view: D 6.71, H 8.99 at h = 0.172 (D 6.87, H 9.20 at h = 0.176).
  - **0040 view of the same jar** at another position and depth: D 6.76, H 9.02 (9.23).
  - The two views agree within 0.5%. The tape also measures 10.25 x 4.80 in both events, which validates n and f.
- Ratios that do not depend on h:
  - jar/tape = 0.88. Scaled by the current tape answers (10.3-10.6), the jar is 9.0-9.3.
  - jar/cup = 0.59. Scaled by the current cup answer (14.8), the jar is 8.7.
- Readings are ±2 px, which gives ±0.25 cm.
- **The cause of the high current value:** the current value is the pixel extent times the stated jar depth, divided
  by f. Two things inflate it:
  - the stated jar depth (1.008) is read through the glass;
  - the extent runs from the top-back of the lid ellipse to the bottom-front (76 px), and that ellipse is about 4-7 px
    open because the camera looks down onto the lid from about 8 cm above it.
- **Best estimate: 9.1 cm.**
- Against the current answers this is -14.6% for o (10.65) and -11% for s/x (10.21, the event median). Criterion (b),
  a change of at least 15%, is not met, so I propose no fix. The paper measures static sizes by ruler, so if the
  orchestrator accepts sub-15% changes, this would be the first one to take: 9.1 for all three renders.

### Poker tower
The physical ceiling for an A-frame of standard 8.89 cm cards is 8.9 cm. The plane gives 9.3-10.1 cm. The flat card
in front rectifies to about 10 x 6.4 cm, but that outline is two stacked, offset cards, so it does not settle the card
size. The current 10.4 is 3-11% above the plane value. That is not a clear error, so I leave it.

### Tape "width"
- Same tape roll as 0040, where the question says "diameter" (current answer 10.47).
- "Width" may mean the axial band of the tape: about 4.8 cm, which is standard 48 mm packing tape. That would be a
  factor of 2.2.
- Against that, lab questions use "width" loosely for horizontal extent: desk, book, box, table, whiteboard.
- There is no evidence either way, so I keep the current answer, which reads "width" as the diameter (10.3-10.6, and
  the geometry agrees). This is the largest open risk in this family.

## Motion rows: ping-pong ball, thrown from behind the cup toward the camera and to the left
- Bounces at frames 19.4, 28.2, 36.1 and 43.4. Depth falls from 1.45 m (frame 12) to 0.70 m (frame 48).
- t = 1.0 s (frame 24) is an apex, so the velocity is horizontal only:
  - my tracks: forward 24->25 is 60-73 cm/s, central 53-66;
  - current: o 59.0, x 58.1, s 48.5.
- t = 1.4 s (frame 33.6) is just after the apex at about 32.1-32.5:
  - my tracks: forward 33->34 is 64-69, forward 34->35 is 72-106, central 54-85;
  - physics (horizontal 0.55-0.65 m/s plus vertical 0.4-0.6) gives 70-85;
  - current: o 76.6, x 75.9, s 55.1.
- **The s render is low against o/x by 1.2x and 1.38x.** The labmot pool candidate (`pool_changes.csv`: s -> 58.1 /
  75.9) would fix this, but the gap is below the 1.5x gross-error bar, so I leave it. No motion fix.

## Result
No fixes. All 18 rows were checked. The jar height (9.1 vs 10.2-10.65) is the only well-measured discrepancy, and it
is below the 15% bar.
