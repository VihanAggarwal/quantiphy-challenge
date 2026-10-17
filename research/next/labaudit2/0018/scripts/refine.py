"""Refined object centroids in the o render: clean background = per-pixel median over frames where the pixel is outside
the x-render matte; object = colour difference vs that background inside a window around the x-matte component."""
import sys, json
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0018/scripts')
from common import *
fo = frames('').astype(np.float32); fx = frames('x')
mat = np.abs(fx.astype(int) - 255).max(3) > 30          # 49 x H x W
mat = np.array([cv2.dilate(m.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0 for m in mat])
bg = np.zeros(fo.shape[1:], np.float32)
masked = np.ma.masked_array(fo, np.repeat(mat[..., None], 3, 3))
bg = np.ma.median(masked, axis=0).filled(np.nan)
np.save('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/bg0018.npy', bg)
print('nan bg px', np.isnan(bg[..., 0]).sum())
