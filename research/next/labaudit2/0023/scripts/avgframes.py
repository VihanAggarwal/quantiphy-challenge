import cv2, numpy as np
D='/home/user/quantiphy-challenge/research/next/labaudit2/0023/'
for V in ['captured_0023','captured_0023x','captured_0023s']:
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{V}.mp4')
    F=[]
    while True:
        ok,f=c.read()
        if not ok: break
        F.append(f.astype(np.float32))
    F=np.array(F)
    for a,b,name in [(0,21,'slope'),(38,49,'table')]:
        avg=F[a:b].mean(0); sd=F[a:b].std(0).mean(-1)
        cv2.imwrite(D+f'frames/avg_{V}_{name}.png',np.clip(avg,0,255).astype(np.uint8))
        np.save(D+f'frames/avg_{V}_{name}.npy',avg[300:560,400:760].astype(np.float32))
        print(V,name,'temporal sd in book region',sd[340:520,470:670].mean())
