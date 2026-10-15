# simulation_0104: phone on a charging post that lifts (2D view, 1920x1080, 24 fps, 31 frames)

## Scale
- The camera is effectively orthographic. The phone's top and bottom faces never appear, even though it rises 622 px, and its thickness stays constant.
- I tracked the phone/post top edge to sub-pixel accuracy. It is static at frames 0-1, then moves at a constant 23.94 px/frame (574.5 px/s) from frame 1 to frame 27, then stops.
- The prior of 0.2 m/s gives a scale of 3.481e-4 m/px (2873 px/m).

## Q208: phone diagonal = 0.204 m (medium confidence)
- The phone's horizontal extent is x = 689-1257, about 568 px, or 0.198 m.
- The left 101 px is the phone's bottom end face. It shows a SIM slit, a mic dot, a USB-C port at the exact centre of the face, and a speaker slot, a Samsung-style layout. Right-side buttons and back cameras confirm the orientation.
- So the phone is yawed: W·sinθ = 101 px and L·cosθ = 467 px. Its projected extent is L·cosθ + W·sinθ = D·cos(θ-φ), and for aspect ratios 1.9-2.2 that gives D = 568-571 px, or 0.198 m.
- The alternative reading is an edge-on phone with a typical aspect ratio of about 2.07, which gives D of about 0.219 m. I hedged slightly toward it and answered 0.204.

## Q209: gray truncated cone diameter = 0.115 m (medium confidence)
- There are two candidate light-gray chamfered or conical discs:
  - The top pad under the phone has a maximum width of 317-318 px, or 0.110 m. It is chamfered from 298 px and mostly cylindrical.
  - The fixed lower collar flares from 318 to 344 px, so its maximum is 0.120 m.
- The dark-gray band is a 280 px cylinder, so I ruled it out.
- I answered the midpoint, 330.5 px or 0.115 m, which is within about 4.3% of either candidate.

## Q210: extension at 0.5 s = 0.095 m (medium-high confidence)
- The displacement measured at frame 12 relative to rest is 263.3 px, or 0.0916 m.
- The nominal speed × time value is 0.2 × 0.5 = 0.100 m.
- I answered 0.095, between the two.
