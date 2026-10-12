"""Zoomed crops (4x) around given points of a drawn overlay image, with 10 px ticks, for eye checks."""
import sys
import cv2
import numpy as np


def zoom_sheet(img, pts, out, half=30, k=4):
    tiles = []
    for (x, y) in pts:
        x, y = int(round(x)), int(round(y))
        X0, Y0 = max(x - half, 0), max(y - half, 0)
        c = img[Y0:Y0 + 2 * half, X0:X0 + 2 * half].copy()
        c = cv2.resize(c, None, fx=k, fy=k, interpolation=cv2.INTER_NEAREST)
        for t in range(0, 2 * half, 10):
            cv2.line(c, (t * k, 0), (t * k, 6), (0, 255, 0), 1)
            cv2.line(c, (0, t * k), (6, t * k), (0, 255, 0), 1)
        cv2.putText(c, f"{X0},{Y0}", (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        c = cv2.copyMakeBorder(c, 0, 2 * half * k - c.shape[0], 0, 2 * half * k - c.shape[1], cv2.BORDER_CONSTANT)
        tiles.append(c)
    cv2.imwrite(out, np.hstack(tiles))
