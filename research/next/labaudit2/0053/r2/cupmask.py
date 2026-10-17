import cv2,numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0053x.mp4')
ms=[]
while True:
    ok,f=c.read()
    if not ok: break
    crop=f[390:460,535:600].astype(int)
    b,g,r=crop[...,0],crop[...,1],crop[...,2]
    green=(g-np.maximum(r,b))   # greenness
    ms.append(green)
ms=np.array(ms)
gm=ms.mean(0)
mask=gm<60
for y in range(gm.shape[0]):
    xs=np.where(mask[y])[0]
    if len(xs):
        # subpixel edges: green threshold crossing at half of (bg ~ 200?) 
        print(390+y, 535+xs.min(), 535+xs.max(), xs.max()-xs.min()+1)
print('bg greenness', np.median(gm[:5]), 'fg', np.median(gm[30:40,25:40]))
alpha=np.clip(1-gm/252,0,1)
print('row  alphawidth')
for y in range(10,60):
    print(390+y, round(alpha[y].sum(),2), ' '.join(f'{a:.1f}' for a in alpha[y,14:46]))
