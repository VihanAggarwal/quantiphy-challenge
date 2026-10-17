import cv2, numpy as np
def load(v):
    c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4'); fr=[]
    while True:
        ok,f=c.read()
        if not ok: break
        fr.append(f)
    return fr
A = load('simulation_0141'); B = load('simulation_0143')
bg0 = cv2.imread('scripts/bg_corr.png').astype(np.float32)
frs = A[::2]+B[::2]
S = np.zeros(bg0.shape, np.float64); N = np.zeros(bg0.shape[:2], np.float64)
stack=[]; masks=[]
for f in frs:
    d = np.abs(f.astype(np.float32)-bg0).max(2)
    m = (d>25).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))
    n,lab,st,cen = cv2.connectedComponentsWithStats(m)
    keep = np.zeros_like(m)
    for k in range(1,n):
        if st[k,4] > 2000: keep[lab==k]=1
    keep = cv2.dilate(keep, np.ones((41,41),np.uint8))
    masks.append(keep.astype(bool))
# per-pixel median over unmasked frames: do in chunks of rows
H,W = bg0.shape[:2]
out = bg0.copy()
F = np.stack(frs).astype(np.uint8); M = np.stack(masks)
for y0 in range(0,H,60):
    blk = F[:,y0:y0+60].astype(np.float32); mk = M[:,y0:y0+60]
    blk[mk] = np.nan
    med = np.nanmedian(blk,0)
    bad = np.isnan(med)
    med[bad] = bg0[y0:y0+60][bad]
    out[y0:y0+60] = med
cv2.imwrite('scripts/bg_clean.png', out.astype(np.uint8))
print('done', (M.sum(0)==len(frs)).sum(), 'pixels never free')
