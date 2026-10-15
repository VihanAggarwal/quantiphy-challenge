# internet_0065 - basketball crossing a gym floor, camera looking straight down
- 1920x1080, 31 frames, 30 fps. Handheld camera tilts slowly (floor shifts about 50 px over the clip); this was removed with phase correlation against frame 28.
- The ball enters on the left at frame 3, crosses at a nearly constant 95 px/frame (about 2850 px/s; slows slightly from 97.6 to 92.6 px/frame) and leaves on the right at frame 24.
- No gravity acceleration can be seen in the image plane: gravity points along the optical axis, toward the floor, so the g prior cannot set the scale.
- Scale comes from the ball's known size instead: the vertical extent, which has little motion blur, is about 261 px. Assumed a size-7 basketball, 23.9 cm, giving 9.16e-4 m/px.
- Speeds: 97, 96, 94.5 and 93.5 px/frame at 0.2, 0.3, 0.4 and 0.5 s, so 2.67, 2.64, 2.60 and 2.57 m/s. Displacements are 0.1 s times the mean speed.
- The motion along the line of sight (from the ball's apparent size change) is small and was ignored.
- Confidence: diameter medium (it assumes a standard ball). Speeds are low-medium: the scale depends on the ball-size assumption, and the dataset's true labelling convention is unknown.
