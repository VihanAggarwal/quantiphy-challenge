import json, numpy as np, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from geom import *
TRK = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'track.json')))
def cap(k): return k if k <= 11 else (k + 1 if k <= 35 else k + 2)
HB = 0.0146  # book top surface above the slope / table (book height 1.46)
def uv(tag, k, key='c'):
    r = TRK[tag][k]; return (r['cx'], r['cy']) if key == 'c' else (r['bx'], r['by'])
def model_pt(tag, k, key='c', h=HB):
    u, v = uv(tag, k, key)
    Xs = on_slope(u, v, h); Xt = on_plane(u, v, h)
    # on slope while along-slope coordinate > 0 (above the foot), else table
    return Xs if slope_coords(Xs)[1] > 0 else Xt
if __name__ == '__main__':
    for tag in ['o', 's', 'x']:
        print('== render', tag)
        for k in range(18, 37):
            u, v = uv(tag, k)
            Xs = on_slope(u, v, HB); Xt = on_plane(u, v, HB); sc = slope_coords(Xs)
            print('v%2d cap%2d t=%.2f (%.1f,%.1f) slope-range %.3f along %.1f | table-range %.3f' % (k, cap(k), cap(k) / 25, u, v, np.linalg.norm(Xs), sc[1], np.linalg.norm(Xt)))
