# Independent remeasure: qid 1116 (simulation_0027, person speed 1.0-2.0 s)

Scripts and crops are in `q1116_work/`: `blobtrack.py`, `person2.py`, `boat2.py`, `uniq.py` and `frames/`. I did not read anything else in this directory.

**Answer: 1.3 m/s.** Confidence: medium.

## Facts used
- The prior is height 1.75 m.
- Depth labels: 100.5638 m at t=1 s and 100.5996 m at t=2 s.
- In family priors (dataset, not inferred), the person's speed is 1.3 m/s in both 0025 and 0031.

## Key findings

1. **The person depth labels do not track the rendered person in this family.**
   - In every camera, |dR| over 1 s is tiny and always positive: 0026 +0.004 m, 0035 +0.001 m, 0031 +0.029 m, 0027 +0.036 m, 0039 +0.092 m.
   - In 0026, 0027 and 0039 the rendered person faces the camera and walks toward it (face blurred, feet descending in the image).
   - So R should drop by about 0.9-1.2 m per second, and it does not.
   - The boat and eagle labels behave normally (|dR| spread up to the full speed).
   - Conclusion: dR cannot be used for this person. The 0.5 m/s route (image-plane motion plus label dR) is not valid.
2. **The walk animation is the same in every clip.** Autocorrelation of the track gives a gait cycle of about 34-35 frames in 0027, 0031 and 0039 (0039 de-duplicated: 3 duplicate frames, so 24 fps content). 0027 has 75 unique frames and no duplicates. With planted feet, the same cycle means the same stride, which means the same speed.
3. **Steep-camera calibration in 0039** (least sensitive to ground slope):
   - Boat: 4 m/s (stated) and dR = +0.7916 m/s. Its optical-flow image velocity of (-192.6, -54.0) px/s gives f = 9061 px (1536 px frame) and a person-ray depression of 48.9 deg.
   - Check: the predicted projected height of the person is 66.3 px, against a measured median of 66 px.
   - The person's image velocity is (3.6, 51.5) px/s. On flat ground that gives 1.38 m/s. With about 5 deg of descent toward the water, it gives about 1.29 m/s.
   - Note on 0031: its own prior of 1.3 needs about 5 deg of descent, and the same slope brings 0039 to 1.3.
   - The step length is therefore about 0.93-0.99 m. The original agent assumed 0.66-0.78 m, and that assumption is what drove its 1.0.
4. **0027 own geometry:**
   - Image velocity is (0.466, 0.612) px/frame. Head-to-sole height is about 58 px.
   - Depression d27 comes from transferring the sun from 0039: the shadow angle relative to the walk direction gives 18.4 deg, and the shadow length gives 19 deg.
   - On flat ground this gives 1.39-1.44 m/s. At d = 20 deg it gives 1.32. With the 5 deg slope it gives about 1.3 at d of about 16 deg.
   - The original 1.0 needs d = 26 deg, which rests on the wrong step-length assumption.

## Conclusion
- The 0027 person is the same rig, with the same cycle and the same direction relative to the sun as in 0039. Its speed should equal the family's labelled 1.3 m/s.
- The render bounds are about 1.25-1.45.
- A hedge of about 1.33 would also keep the rendered-flat value of about 1.40 within 5%.
