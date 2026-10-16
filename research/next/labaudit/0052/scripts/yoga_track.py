import cv2, numpy as np, json
FR='frames/%s_%02d.png'
def load(r,n): return cv2.imread(FR%(r,n)).astype(np.float32)
out={}
for r in ['o','s','x']:
    bg_early=np.median(np.stack([load(r,n) for n in range(0,13)]),0)   # ball at start pos
    bg_late=np.median(np.stack([load(r,n) for n in range(42,49)]),0)   # ball gone (left bottom)
    res={}
    for n in range(0,49):
        f=load(r,n)
        bg = bg_early if n>=22 else bg_late
        d=np.abs(f-bg).max(2)
        m=(d>28).astype(np.uint8)
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
        m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
        cv2.imwrite(f'frames/mask_{r}_{n:02d}.png',m*255)
    print(r,'done')
