# simulation_0148 — notes

Scene: a fixed camera looks through an arched opening in a wall (with a central pillar). A subway car passes right-to-left behind the wall, between frames 3 and 20, and a far platform is visible behind it. The clip is 26 frames at 24 fps (1.08 s), 1920x1080.

## Camera
- I ran a vanishing-point search on the receding grout lines of the far-platform floor and the near floor. Both give a principal point of (960, 540), so the camera is level and points perpendicular to the track. The horizon is at y = 540.

## Scale (prior: side-window width = 1.8 m)
- Window in frame 14: the glass is 350.4 px wide, the outer edge of the dark gasket is about 363 px, and the outer bevel highlight is about 371.5 px. Frame 9 gives the same widths.
- I used 361 px for 1.8 m, which is 0.004986 m/px. This splits the difference between the glass-only and full-frame readings (±3%).
- The windows and doors lie on the near side plane of the train, so the same scale applies to everything that moves with the train.

## Motion
- I estimated the frame-to-frame shift with masked NCC on gradient images (Sobel-x), excluding static pixels and the pillar. Frames 5 to 18 give 353.2, 355.7, 359.1, 363.5, 366.0, 367.9, 371.5, 376.3, 378.6, 382.9, 386.0, 387.5, 391.0 px.
- The shifts grow linearly: dx(i->i+1) = 336.89 + 3.214*i px, with 0.70 px RMS residual. A quadratic or cubic fit shows the acceleration is constant (3.21–3.25 px/frame²).
- A panorama of the train side built from this motion model is sharp. That confirms the track.
- Speed at 0.5 s (frame 12, backward difference 11->12): 372.2 px/frame, which is **44.55 m/s**.
- Speed at 1.0 s (frame 24): the train leaves the view around frame 20, so I extrapolated at constant acceleration. dx(23->24) = 410.8 px/frame, which is **49.16 m/s**. The quadratic fit gives 49.0.
- Acceleration: 3.23 px/frame² × 576, which is **9.28 m/s²**.
- Confidence: medium-high. The main risk is the window-width convention (±3%). The 1 s value also assumes the train keeps accelerating at the same rate after it leaves the view.

## Door (qid 346)
- The double door is 342 px wide, which is 1.71 m. Its top is at y ≈ 447. Its bottom is hidden behind the arch sill throughout the clip.
- Estimating the car floor: horizon 540, far-platform edge at y = 824.5, and Z_far/Z_near ≈ 1.40 for the train. That ratio comes from the front-face far corner moving 248 px while the side moved 346.5 px between frames 3 and 4. Assuming the car floor is at platform height puts the floor at y ≈ 938, so the door is about 491 px tall, or 2.45 m.
- I can't tell whether "length" means the height (2.45 m) or the width (1.71 m), so I hedged toward the height: **2.3 m**. Confidence: low-medium.

## Pillar (qid 347)
- The visible pillar runs from y ≈ 203 (bottom of the arch ring) to y ≈ 868 (front edge of the sill top), which is 665 px. At the train's scale that is 3.32 m.
- The pillar is closer to the camera than the train. Assume the near floor (wall base at y = 979) and the far platform are at the same level. Then the depth ratio is Z_wall/Z_train ≈ (284.5/439) × 1.40 ≈ 0.905, which gives about 3.0 m.
- The pillar's bounding box may also extend into the arch ring or the beam, so I hedged between 3.0 and 3.3: **3.1 m**. Confidence: low-medium.
