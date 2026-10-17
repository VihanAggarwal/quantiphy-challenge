# sim3audit: simulation_0057 family (street scene + museum clip 0019)

48 scored rows across 0019(+seg), 0021(+seg), 0033, 0052, 0055, 0056. **Result: no fixes proposed.** All rows stay as they are.

## 1. Cross-clip table (street scene: 0021, 0033, 0052, 0055, 0056)

| quantity | 0021 | 0033 | 0052 | 0055 | 0056 | spread |
|---|---|---|---|---|---|---|
| hydrant height | 1.01 | 1.03 | 1.04 | 1.026 | 1.045 | 3.5% |
| streetlight height | 4.38 | 4.44 | 4.43 | 4.366 | 4.55 | 4% (0056 +3%) |
| orange car length | - | 4.97 | 5.10 | 4.99 | - | 2.6% |
| orange car height | - | 1.48 | 1.50 | 1.433 | - | 4.6% |
| curb height | - | 0.22 | 0.211 | 0.191 | - | 14% (mean 0.207, each within 8%) |
| green car speed | - | 11.9 (t=1) | 11.92 (t=1) | - | 12.08 (avg 0-1) | 1.5% |
| streetlight spacing | - | - | 7.89 | - | 7.98 | 1.1% |
| person speed | 0.40 (t=1) | 0.50 (t=1) | - | 0.535 (avg 1-2) | - | see section 2 |

- The static sizes all agree. No clip is scaled off and no object was measured as a different object.
- Single-clip car rows (green height 1.55, length 4.95, width 2.03; orange width 2.28): proportions are close to a Mercedes 300SL and a Kia Stinger at about 1.04-1.1x real size.
  - In 0052 the green roof crest sits above the horizon while the orange roof sits on it. So the green car is taller than the orange car (about 1.47), and a correction of 15% or more (green height 1.32 or less) is ruled out.
  - Rechecking the orange mirror span in 0056 at frame 30: 327 px at a mirror depth of about 11.0 m, with f=1610, gives 2.23 m (agent: 2.28).
  - The family hydrant and lamp values point to f of about 1640-1660 in 0056. Every 0056 size would then drop by about 2-3%, which is too small to act on.

## 2. Walking person: 0033 is 0021 shifted by exactly 27 frames
- Head-edge tracks (`edgetrack.py`; `e21_head.txt`, `e33_head.txt`) show 0033 frame j = 0021 frame j+27. The mean L-edge difference is 0.55 px over 50 frames. The depths agree too: 0021 at 0.9 s interpolates to 13.779, and 0033 gives d(0)=13.780.
- So 1131 (0033 at t=1.0) is 0021 at t=1.9 s, and 1096 is 0021 at t=1.0 s. They are different phases of the same motion.
- The stride-averaged speed (`speedprofile.py`, k=1.87/215.4 m/px) is flat at about 0.43-0.44 m/s from 0 to 1.5 s, then rises: 0.475 at 1.67 s, 0.53 at 1.9 s, 0.55 at 2.13 s, and about 0.68 at the end.
  - 1096 = 0.40: the smooth value is 0.426-0.44, and the depth pair over 0-1 s gives 0.427. Both are about 7-9% above the current answer, which is under the 15% bar. The agent's 0.40 is the local trunk speed at mid-stance. Keep.
  - 1131 = 0.50: the smooth value is 0.50-0.53. The local value at mid-stance is about 0.41. The depth pair implies 0.55 average over 0-1 s, which is not consistent with the pixel motion of 0.44 there, unexplained. Keep.
  - 1665 (0021_seg, average over the clip) = 0.5: whole-clip displacement gives 0.497. Keep.
- 0055 (the same walk animation, whose ramp starts earlier): the head R edge moves 105.6 px over frames 30-60. Person height is 374 px (sole 947, head top 573), so k=0.0050, giving 0.528. Current 0.535. Keep.

## 3. simulation_0019 (museum, singleton)
- Speed: the head track over frames 0-48 moves 5.65 px/frame, which with s=0.00711 at 33 fps gives 1.33 m/s. 1090 and 1659 = 1.3. Keep.
- Which object is the pedestal: the dark plinth (1.47 x 0.60) or the light stone slab (1.30 x 0.31)?
  - Pedestal and sculpture have identical ranges (5.085). The agent's geometry puts that shared origin at about 0.6-0.67 m, the top of the plinth.
  - A separate plinth object would have its origin at 0-0.3 m, which gives a range of 5.17-5.27. That favours the stone slab, which is the agent's choice.
  - This is a question of interpretation, not a measurement error I can show, so I am not flagging it.

## Files
extract.py, ptrack.py, headtrack.py, edgetrack.py, edge55.py, speedprofile.py (+ .txt outputs), frames/ (a few PNG crops, 15 MB).
