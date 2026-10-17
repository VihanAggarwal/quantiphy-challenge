# 0029 independent remeasure (second measurer)

I worked from scratch and did not read the other measurer's notes, scripts or JSON in this folder.
My scripts and crops are in `remeasure2/`: track.py, table2.py, plane.py, geo.py, size2.py, line.py, line2.py and anchors.py.

## Setup
- The event is a tennis ball (stated D = 6.7 cm). It is thrown from a hand at the front-right of the table, rolls about straight to the whiteboard at the back edge, bounces off, and rolls back toward the camera and to the left. The renders c, s and x share pixel geometry: centroids agree within 1 px.
- **Clock:** the 49 video frames map to capture frame k = floor(i*25/24 + 0.5), with dropped capture frames 12 and 37. The track confirms this: there is a double-length step between v35 and v36 (21.6 px against about 10.5 px). The mapping gives:
  - t = 1.00 s (c25) is v24, and its next frame is v25.
  - The hit at t = 1.24 s (c31) is v30. The ball is visibly at the board there: its image y is at a minimum and the step shortens. The next frame is v31.
  - t = 1.6 s (c40) is v38.
- **Camera:** f = 711, principal point (640, 360).
- **Table plane check:** the vanishing points of the top-edge lines give f = 699, which is consistent. The camera sits about 17 cm above the table top, so the view is grazing.
- **Plane scale:** from the 76.0 cm side the scale is h = 17.0, and from the 60.3 cm side it is 17.8. The ToF anchors at v24 and v30 both imply a scale of 1.025 times the h = 17.0 plane, so h is about 17.4.

## Routes
- **A. Anchor line.** C = (depth + 3.35 cm)·u at v24 (0.901) and at v30 (1.144). The image rays at the frames in between meet the straight line C24 to C30 within 0.35 cm. Positions come from closest points, and label-style points are P = (|C| − 3.35)·u.
- **B. Table plane.** Ball centre plane at 3.35 cm above the table top, scale calibrated to the anchors.
- **C. Ball size.** Circle fits on the x render. These are inflated by the SAM mask, so they are used for relative range only: v30 to v31 shows no range change within 1%. Motion blur makes this route unusable before the hit.

## Results
| qid | quantity | best | routes | confidence |
|---|---|---|---|---|
| 2494 / 2500 / 2505 | v at 1.0 s | **133 cm/s** | A raw forward difference v24→v25 (surface, label-style) 131.4; A smoothed centre 134.8; B smoothed 136.5; B linear 134.5; anchor radial rate plus pixel lateral 134 | medium (a ToF noise of σ 1–2 cm at c26 alone moves the label ±25–50 cm/s) |
| 2495 | v when it hits the whiteboard (forward difference c31→c32) | **50 cm/s** | A' post-bounce line through the anchors at v30 and v38: 50.0 (surface), 49–52; B post-bounce steps v31–v34 about 47–55; C range change from v30 to v31 is about 0, so with a 1.6 cm lateral step the floor is about 40 | low–medium. The physical incoming speed just before impact is about 125 cm/s; the rebound is about 50 cm/s. B is not usable at v30 because the ball is lifted about 0.7 cm at the board (a 4 px y jump). |
| 2502 / 2507 | distance travelled when it hits the whiteboard | **28.9 cm** | \|1.144·u(v30) − 0.901·u(v24)\| = 28.9 (from 28.7 to 29.2 for f between 690 and 730; click jitter sd 0.25); B gives 29.2 | medium (this assumes the start is at t = 1.00 s, the first depth anchor). Alternatives: from release (v19, about 0.80 s) about 58–60 cm; from t = 0 with the ball in the hand about 70 cm. |

## Extra check (not my qid)
Route A' gives a forward difference at t = 1.6 s (v38→v39) of 47.4 cm/s label-style (48.4 for the centre).

## Note
The plane route puts the post-bounce ranges about 3 cm closer than the ToF anchor at v38 (1.027). The size route agrees with the anchor to within 1.3%.
