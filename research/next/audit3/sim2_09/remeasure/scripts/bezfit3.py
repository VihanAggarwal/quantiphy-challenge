import numpy as np, sys
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/audit3/sim2_09/remeasure/scripts')
from bez import basis, HF

t = np.loadtxt(sys.argv[1], delimiter=',')
p = t[:, 1:3]
fr = np.arange(80)


def rms(r):
    return np.sqrt(np.mean(r ** 2))


for h in [1 / 3, HF]:
    for T in [[0, 39, 69], [0, 38, 69], [0, 40, 69], [-1, 39, 69], [0, 39, 70], [1, 39, 69], [0, 39, 68]]:
        Bx = basis(T, fr, ['flat', 'avg', 'flat'], h)
        kx, *_ = np.linalg.lstsq(Bx, p[:, 0], rcond=None)
        rx = p[:, 0] - Bx @ kx
        out = ['h=%.4f T=%s x rms %.3f' % (h, T, rms(rx))]
        for ry_rule in [['flat', 'flat', 'flat'], ['flat', 'avg', 'flat']]:
            By = basis(T, fr, ry_rule, h)
            ky, *_ = np.linalg.lstsq(By, p[:, 1], rcond=None)
            ry = p[:, 1] - By @ ky
            A = np.c_[By, Bx @ kx]
            km, *_ = np.linalg.lstsq(A, p[:, 1], rcond=None)
            rm = p[:, 1] - A @ km
            out.append('y[%s] rms %.3f mixed %.3f (b=%.5f)' % (ry_rule[1], rms(ry), rms(rm), km[-1]))
        print(' | '.join(out))
