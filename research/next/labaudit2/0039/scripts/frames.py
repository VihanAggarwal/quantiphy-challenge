"""Load all frames of a render into memory (no .npy dumps) and save selected PNGs/crops."""
import cv2, numpy as np, sys
D = '/home/user/quantiphy-challenge/data/QuantiPhy'
def load(r):
    c = cv2.VideoCapture(f'{D}/captured_{r}.mp4'); fr = []
    while True:
        ok, f = c.read()
        if not ok: break
        fr.append(f)
    return np.array(fr)
if __name__ == '__main__':
    out = '/home/user/quantiphy-challenge/research/next/labaudit2/0039/png'
    for r in ['0039', '0039s', '0039x']:
        fr = load(r)
        for i in [0, 20, 24, 30, 36, 40]:
            cv2.imwrite(f'{out}/{r}_{i:02d}.png', fr[i])
