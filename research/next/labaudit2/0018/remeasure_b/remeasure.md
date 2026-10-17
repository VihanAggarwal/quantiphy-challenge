# captured_0018 / 0018s / 0018x - independent remeasure (measurer B)

Written by an independent second measurer; did NOT read research/next/labaudit/0018 or labaudit2/0018 notes
(the pre-existing labaudit2/0018/remeasure.md was left untouched and unread; these notes live in remeasure_b/).
Scripts: remeasure_b/scripts/{track_x.py, assoc.py, bounce.py, final.py, zoom.py}. Images: remeasure_b/img/.

## The time problem
All three renders are 49 frames @24 fps = 2.04 s, identical timing. Questions ask at 3.0 s and 3.4 s (only lab
family with times past the clip end). Primary hypothesis H2: the clip is the original capture window [2.00, 4.00] s
(51 capture frames incl. both ends), question times were not re-zeroed. Evidence:
- 0015 was exported 3.04 s long to contain its t=2.6 s question -> creators trim windows to contain question times;
  0018 (2.04 s) can contain 3.0/3.4 only if t0 in [1.44, 3.0].
- with t0=2.0: t=3.0 -> clip capture 25 = video 24 = all four objects still held, last frame before release
  (natural "distance" moment); t=3.4 -> capture 35 -> 36 = video 34 -> 35 = the only ~5-frame window where all four
  objects are simultaneously in free fall (natural "velocity" moment; prior given is g = 9.8).
- the observed 25->24 drop (double-length steps of box and soccer between video 35/36) matches
  capture = floor(v*25/24+0.5) phased to the clip start, i.e. consistent with an integer-second t0 if the
  conversion was done before trimming.
Alternatives: (end) clip = last 51 frames of a 3.44 s recording (t0=1.44); (ext) t0=0 and 3.0/3.4 s are unseen.
Distances are nearly the same under H2 and (end) (objects fall vertically); velocities are NOT (end gives
36-89 cm/s from the last frame pair). Under (ext) nothing at 3.0/3.4 s is observable.

## Camera / depth
f=711, cx=640, cy=360. Level camera, height H=0.875 m: far person (range 3.13, torso ~(380,293), feet rows 565-576)
-> H 0.88; near person (range 2.002, torso ~(987,320), feet ~671/>720) -> H 0.88; soccer bounce contact (parabola
intersection, centre 557.4 + r 22 -> floor row 579) with stated range 2.80 -> H 0.873.
Surface depths Z used (two+ routes each):
- soccer 2.749 (stated range 2.80 at (541.7,263)); floor contact -> centre 2.82; size 44 px both held and at v48.
- box 2.54: floor contact bottom row ~601 (v39/40) -> centre 2.58; box occludes the ball-holding forearm (near hand)
  and image offset of 61 px matches ~35 cm hand spacing at Z 2.53; free-fall energy route 2.45.
- tennis 2.18: bounce contact row 642 -> centre 2.21; FWHM diameter 21.5 px with 6.7 cm ball -> 2.22;
  free fall from rest at capture 25 with Z 2.2 reproduces displacements caps 29-35; arm geometry ~2.1.
- pineapple 1.92: first floor contact row ~691 (v36) -> 1.88-1.93; held in front of near person's body -> ~1.95;
  energy route ~1.93-2.13.

## Tracks (x render component centroids == main-render zoom clicks within 1-3 px)
video34(cap35) -> video35(cap36): box (485.6,351.4)->(486.6,381.8); soccer (538.4,331.0)->(538.2,356.6);
tennis (751.5,505.7)->(749.2,558.4); pineapple (861.1,502.8)->(860.9,556.4).
Held at video 24: box (481,265), soccer (541.7,263), tennis (762,249.5), pineapple (870,253).

## Values (label style, H2) - same for captured_0018, 0018s, 0018x
| q | label-style | 2nd route | physical |
|---|---|---|---|
| v box @3.4 (2302/2321/2340) | 272 cm/s | fit-fwd 265, energy-Z 262 | ~250 (instantaneous) |
| v soccer (2303/2322/2341) | 249 cm/s | fit-fwd 244 | ~225-235 |
| v tennis (2304/2323/2342) | 405 cm/s (Z 2.18) | fit-fwd 417, energy 418 | ~395 |
| v pineapple (2305/2324/2343) | 362 cm/s (Z 1.92) | 343 (Z1.82) .. 389 (fit) | ~350 |
| d box-soccer @3.0 (2306/2325/2344) | 28 cm | 25-34 for box Z 2.46-2.60; (end) hyp 29.5 | centre-centre 31 |
| d box-tennis (2308/2327/2346) | 101 cm | (end) hyp 96 | 103 |
| d tennis-soccer (2309/2328/2347) | 94.5 cm | 91-100 for tennis Z +-0.1; (end) 98 | 99 |
(end)-hyp velocities for reference: box ~73, soccer ~36, tennis ~89, pineapple ~38 cm/s.
Label noise: ToF on motion-blurred objects + click jitter can move a single forward difference by tens of cm/s.
