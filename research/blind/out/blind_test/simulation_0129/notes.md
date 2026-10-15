# simulation_0129 — red ball dropped in front of warehouse facade, forklift driving left->right

Prior: g = 9.8 m/s^2 (ball free fall). 40 frames @ 24 fps, 1920x1080, static level camera.

## Scale from gravity
- Ball tracked by red threshold (centroid rms residual to parabola 0.3 px), x constant at 956 (falls straight down).
- Quadratic fit of y(t), frames 1..38 with various windows: g_px = 514-516 px/s^2 -> 515.
- s_ball = 9.8/515 = 0.01903 m/px (at the ball's depth).

## Ball diameter (qid 298)
- Coverage-based chord widths (full-res luma contrast frames on dark beams) ~19.7 px; half-max/R-G methods 19.5-20.0.
- D = 19.7 * 0.01903 = 0.375 m.  Confidence: good (+-3%).

## Depth of ball vs forklift (3D check)
- Horizon / principal point from 4 depth-direction parking stripes: VP ~(958,533) -> camera level, cy ~535.
- Ball is occluded by forklift mast at frame 39 (only a red glimpse through a plate window) -> ball behind forklift near side.
- Ball reflection in the centre-bay transom glass (frame 38): reflection centre ~717.9 vs ball 725.6 -> Z_glass/Z_ball = 1.021.
- Facade base y=909.9 vs near-wheel contact y=926.7 -> Z_glass/Z_near = 1.045; roof reflection (top 723.3 vs real far-edge top 736.2) agrees.
- => Z_ball/Z_near ~1.023; forklift width ~1.9% of Z (far posts/forks shifts), so ball ~1.3% behind forklift centre.
- Scale at forklift near face s_n = 0.01903/1.023 = 0.01860 m/px.

## Forklift length (qid 299)
- Rear (counterweight) edge 705.0 px, front (fork shank) 955.0 px in frame 38 (forklift near image centre); consistent across frames
  with small perspective model (rear silhouette ~centre depth, forks ~centre).
- L = 255.0*s_rear - 5*s_fork = 4.68 m (naive 2D: 4.76). Confidence: moderate (+-3%).

## Forklift height (qid 300)
- Wheel contact 926.8 (near side), roof top silhouette 736.2 (far edge, measured against the light concrete pillar, frames 36-37).
- Camera above roof -> far-edge correction: H = s_n*[(926.8-736.2) - (736.2-535)*0.019] = 3.48 m (naive 2D: 3.63).
- Confidence: moderate (+-4%).

Forklift is ~1.7x a real Toyota forklift (scene scaled); answers follow the gravity scale.
