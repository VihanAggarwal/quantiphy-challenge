# Audit internet_01: family internet_0015 (0001, 0002, 0006, 0007, 0012, 0015)

All six are nadir drone views of roads with the prior "lane width = 3.66 m". They are not one piece of footage.
Two pairs share a scene:
- 0001 and 0002 are the same 6-lane freeway at 3840x2160. Lane spacing is 302-333 px, mean about 317 px.
- 0006 and 0007 are the same UK 2-lane road (with a SLOW marking) at 1080x1920. The road is 77-83 px wide, so a lane is about 39.5 px.

0012 (a bridge, 2160x3840) and 0015 (a 2-lane road, 1920x1080) stand alone.

## Step 1: family consistency
- **0001 and 0002:**
  - Scales: 0001 used 310 px per lane (its own-lane hedge, 0.01181 m/px). 0002 used 319 px (the mean, 0.01147 m/px). That is a 3% difference, and 0001 is not scored. Not a problem.
  - fps: the container fps is 20.6 for 0001 and 19.6 for 0002, but the dataset fps is 24. The frame motion is uniform, with no dropped or duplicated frames. Both agents used the dataset value of 24. I kept it, because nothing in the clip can tell which time base the labels used.
- **0006 and 0007:**
  - Scales: 39 px (0.0938 m/px) and 39.5 px (0.0927 m/px). These agree.
  - Cars come out large at this scale: 6-7 m long and about 2.5 m wide, because the real lane on this road is about 2.7 m. The prior defines the scale, so I applied no correction.
  - Car lengths differ between the clips (white 75 vs 60.5 px, black/dark 63 vs 71 px). The crops confirm these are different vehicles: 0006 has a white sedan with a sunroof and a black hatch; 0007 has a white small saloon and a blue estate.
- **0012:**
  - Lanes are 98.3 px centre to centre, measured at 6 heights on both carriageways. The agent used 98.2 px.
  - The video duplicates about 45% of its frames. A linear fit over all frames with t = frame/60 handles this.
- **0015:**
  - The lane-width convention is the main uncertainty:
    - 44.5 px from the edge line to the nearest stripe of the double line
    - 48.3 px to the centre of the double line
    - 48.8 px as the road width divided by 2
  - The agent used 47 px. That is within 5% of every convention.

## Step 2: agent notes
- No clip's notes describe a wrong method.
- Low-confidence flags:
  - 0015 motorcycle length (2077): low-medium. Shadow at the front; the apparent length varies from 28 to 34 px across frames.
  - 0015 spacing (2075): the question is ambiguous. Centre-to-centre gives 31.2 m; bumper gap gives 26.8 m. The current answer is a hedge at 30.5 m.

## Step 3: quick check of every scored row
My own scales:
- 0002: 317 px per lane, so 0.011546 m/px, at 24 fps.
- 0006 and 0007: 39.7 px (the road edges found by a saturation threshold, divided by 2), so 0.0922 m/px, at 30 fps.
- 0012: 98.3 px, so 0.03723 m/px, at 60 fps.
- 0015: 47 px (0.0779 m/px) at 30 fps. The range is 44.5-48.8 px.

Quick-check routes:
- Speeds come from background-median blob tracks: linear fits of the top edge, bottom edge and centroid. For 0015 I used the rear edge, which has no shadow.
- Lengths come from blob extents plus 4-8x crops with pixel rulers, which I looked at.

| qid | clip | quantity | current | quick-check px | quick-check value | diff |
|---|---|---|---|---|---|---|
| 2019 | 0002 | red pickup length | 6.0 | 523-531 px, including blur (crops f8, f15, f24) | 6.04-6.13 | 1-2% |
| 2020 | 0002 | red pickup width | 2.15 | 186 px body, 218 px with mirrors (f15) | 2.15 | 0% |
| 2021 | 0002 | red pickup speed | 29.0 | 106.4 px/frame, red centroid over frames 2-29 | 29.5 | 1.7% |
| 2034 | 0006 | motorcycle length | 2.91 | 30-31 px (crops f30, f60) | 2.77-2.86 | 2-5% |
| 2035 | 0006 | motorcycle speed | 26.42 | 9.30 px/frame, frames 0-123 | 25.7 (26.2 at the agent's scale) | 3% |
| 2036 | 0006 | white car length | 7.04 | 75-77 px (crop f30, blob median 76) | 6.9-7.1 | <2% |
| 2037 | 0006 | white car speed | 24.56 | 8.68 px/frame, frames 0-159 | 24.0 | 2.3% |
| 2038 | 0006 | black car length | 5.91 | 62-63 px (crops f60, f100; the blob's 70 px includes shadow) | 5.72-5.81 | 2-3% |
| 2039 | 0006 | black car speed | 23.79 | 8.39 px/frame, frames 0-156 (accelerating) | 23.2 | 2.5% |
| 2040 | 0007 | white car length | 5.61 | 60.5 px (crop f190) | 5.58 | 0.5% |
| 2041 | 0007 | white car speed | 26.96 | 9.72 px/frame, frames 100-291 | 26.9 | 0.3% |
| 2042 | 0007 | dark car length | 6.58 | 71 px (crop f40) | 6.55 | 0.5% |
| 2043 | 0007 | dark car speed | 32.94 | 11.9 px/frame, frames 5-85 | 32.9 | 0.2% |
| 2056 | 0012 | truck length | 17.6 | 460-466 px (crop f100) | 17.1-17.35 | 1.5-3% |
| 2057 | 0012 | truck speed | 13.9 | 6.16 px/frame from the cab front, f0 to f100 (370 px/s) | 13.8 | 0.7% |
| 2058 | 0012 | grey car length | 4.92 | 130 px (blob median, crop f60) | 4.84 | 1.7% |
| 2059 | 0012 | grey car speed | 20.4 | 9.18 px/frame (551 px/s) | 20.5 | 0.5% |
| 2060 | 0012 | leftmost-lane car length | 4.0 | 110-111 px (crop f60, blob) | 4.10-4.13 | 3% |
| 2061 | 0012 | leftmost-lane car speed | 11.5 | 5.04-5.11 px/frame (303-307 px/s) | 11.3-11.4 | 1.5% |
| 2062 | 0012 | white car in lane 2 length | 4.6 | 122-125 px (blob median 124) | 4.54-4.62 | <1.5% |
| 2063 | 0012 | white car in lane 2 speed | 14.0 | 6.21 px/frame (372.5 px/s) | 13.9 | 0.9% |
| 2075 | 0015 | average vehicle spacing | 30.5 | 400 px centre to centre (408/416/376); bumper gaps 346/357/332 (mean 345) | 31.1 centre to centre, 26.9 gap | 2% / 13% |
| 2076 | 0015 | black car length | 4.55 | 58.5-60 px (crops f0, f20; the rear edge is clean) | 4.56-4.67 | 0-2.6% |
| 2077 | 0015 | motorcycle length | 2.34 | 28-34 px across f0-f80, about 30 px (8x crops) | 2.34 (range 2.2-2.65) | 0% |
| 2078 | 0015 | motorcycle average speed | 28.2 | 12.12 px/frame from the rear edge, f0 to f90 | 28.3 | 0.4% |
| 2079 | 0015 | speed of car C (ahead of the motorcycle) at 1.0 s | 27.4 | 11.7 px/frame from the rear edge, f25 to f35 | 27.3 | 0.4% |

Lane identities in 0012 are checked against lane lines fitted on the background:
- The leftmost-lane car sits at x of about 828, straddling the lane 1/2 dash at about 837, mostly in lane 1.
- The white car is at x of about 873, in lane 2 (850-946).
- The grey car is in the middle lane of the right carriageway.
- The truck is in the rightmost lane.

## Result
- No row has a quick check that differs by 15% or more, so nothing needed a second-route re-measurement.
- **No fixes proposed.**

Residual risk is the same for every row in a clip: the lane-pixel convention the annotators used. That is about ±5% for 0006, 0007 and 0015, and ±2% for 0002 and 0012. For 0015 spacing (2075), the definition (centres vs gaps) adds a further ±13%.

The work folder holds the crops I looked at (`img/`), the blob tracks (`b*.json`), and the scripts (`scripts/`). It is under 8 MB.
