"""Parametric Blender-F-curve model of the vacuum centre track -> speed and acceleration.
x: auto handles (time fraction 1/2.5614), keys at frames 0,39,69 (interior slope = mean chord slope)
y: flat handles at 0,39,69 with 1/3 time handles (cubic Hermite, flat ends)
"""
import numpy as np, sys
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/audit3/sim2_09/remeasure/scripts')
from bez import basis, HF

fn = sys.argv[1]
D = float(sys.argv[2])
hx = float(sys.argv[3]) if len(sys.argv) > 3 else HF
hy = float(sys.argv[4]) if len(sys.argv) > 4 else 1 / 3
T = [0, 39, 69]
s = 0.438 / D
fps = 24.0
t = np.loadtxt(fn, delimiter=',')
p = t[:, 1:3]
fr = np.arange(80)
excl = set()
if len(sys.argv) > 5 and sys.argv[5]:
    excl = set(int(v) for v in sys.argv[5].split(','))
use = np.array([f for f in fr if f not in excl])
Bx = basis(T, use, ['flat', 'avg', 'flat'], hx)
By = basis(T, use, ['flat', 'flat', 'flat'], hy)
kx, *_ = np.linalg.lstsq(Bx, p[use, 0], rcond=None)
ky, *_ = np.linalg.lstsq(By, p[use, 1], rcond=None)
rx = p[use, 0] - Bx @ kx
ry = p[use, 1] - By @ ky
print('keys x', np.round(kx, 2), 'y', np.round(ky, 2), 'rms x %.3f y %.3f' % (np.sqrt(np.mean(rx ** 2)), np.sqrt(np.mean(ry ** 2))))


def pos(tq):
    tq = np.atleast_1d(np.asarray(tq, float))
    return np.c_[basis(T, tq, ['flat', 'avg', 'flat'], hx) @ kx, basis(T, tq, ['flat', 'flat', 'flat'], hy) @ ky]


def vb(n, dt=1.0):  # backward-difference speed (m/s) at frame n
    a = pos([n - dt, n])
    return np.linalg.norm(a[1] - a[0]) / dt * s * fps


def v_an(n, e=1e-3):
    a = pos([n - e, n + e])
    return np.linalg.norm(a[1] - a[0]) / (2 * e) * s * fps


for n in [12, 24, 48]:
    a_an = (v_an(n + 1e-2) - v_an(n - 1e-2)) / 2e-2 * fps
    a_bb = (vb(n) - vb(n - 1)) * fps
    a_fb = (vb(n + 1) - vb(n)) * fps
    a_c = (vb(n + 1) - vb(n - 1)) / 2 * fps
    a_an_m1 = (v_an(n - 1 + 1e-2) - v_an(n - 1 - 1e-2)) / 2e-2 * fps
    a_an_p1 = (v_an(n + 1 + 1e-2) - v_an(n + 1 - 1e-2)) / 2e-2 * fps
    print('frame %d (t=%.3fs): v_back %.3f v_inst %.3f | a_inst %.3f a_inst(n-1) %.3f a_inst(n+1) %.3f | a_back(v_n-v_n-1) %.3f a_fwd %.3f a_central %.3f'
          % (n, n / fps, vb(n), v_an(n), a_an, a_an_m1, a_an_p1, a_bb, a_fb, a_c))
print('speed series (backward):', ' '.join('%d:%.3f' % (n, vb(n)) for n in range(1, 70)))


def vvec(n):
    a = pos([n - 1, n])
    return (a[1] - a[0]) * s * fps


for n in [24, 48]:
    print('frame %d: |dv_vec|/dt backward %.3f ; v-series window: ' % (n, np.linalg.norm(vvec(n) - vvec(n - 1)) * fps),
          ' '.join('%d:%.4f' % (k, vb(k)) for k in range(n - 3, n + 3)))
    print('   a_back at n-1,n,n+1: %.3f %.3f %.3f' % tuple((vb(k) - vb(k - 1)) * fps for k in [n - 1, n, n + 1]))
