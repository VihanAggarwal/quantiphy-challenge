import numpy as np
r = np.load('t59b.npy'); fps = 30.
ii = r[:, 0]; x = r[:, 1] - r[:, 5]; y = r[:, 2] - r[:, 6]
pd = np.array([8.44233695, -61.18261274, 232.10185633])
for D in (0.229, 0.24, 0.249):
  for f in (0, 1450):
    t = ii / fps; d = np.polyval(pd, t)
    X = (x - 960) * D / d; Y = (y - 540) * D / d; Z = f * D / d if f else 0 * d
    P = np.stack([X, Y, Z], 1)
    def vel(fr, h=3):
        s = (ii >= fr - h) & (ii <= fr + h)
        v = [np.polyval(np.polyder(np.polyfit(t[s], P[s, k], 2)), fr / fps) for k in range(3)]
        return np.linalg.norm(v)
    def pos(fr): return P[ii == fr][0]
    v75, v90 = vel(75), vel(90)
    disp = np.linalg.norm(pos(90) - pos(75)); avg = np.linalg.norm(pos(96) - pos(75)) / 0.7
    # also global quad fit for velocities
    s = (ii >= 66) & (ii <= 97)
    vg = lambda fr: np.linalg.norm([np.polyval(np.polyder(np.polyfit(t[s], P[s, k], 2)), fr / fps) for k in range(3)])
    print('D=%.3f f=%d  v75=%.2f (glob %.2f)  v90=%.2f (glob %.2f)  disp75-90=%.3f  avg75-96=%.2f' % (D, f, v75, vg(75), v90, vg(90), disp, avg))
# constant-scale agent style for comparison
s0 = 0.001972
t = ii / fps
P = np.stack([x * s0, y * s0], 1)
def vel(fr, h=3):
    s = (ii >= fr - h) & (ii <= fr + h)
    return np.linalg.norm([np.polyval(np.polyder(np.polyfit(t[s], P[s, k], 2)), fr / fps) for k in range(2)])
pos = lambda fr: P[ii == fr][0]
print('const scale: v75=%.2f v90=%.2f disp=%.3f avg=%.2f' % (vel(75), vel(90), np.linalg.norm(pos(90) - pos(75)), np.linalg.norm(pos(96) - pos(75)) / 0.7))
