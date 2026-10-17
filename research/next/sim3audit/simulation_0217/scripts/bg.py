import cv2, numpy as np
def frames(v):
    cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/%s.mp4'%v)
    out=[]
    while True:
        ok,f=cap.read()
        if not ok: break
        out.append(f)
    return out
a=frames('simulation_0211'); b=frames('simulation_0212')
# background from 0211: median over frames (cat moves)
bg=np.median(np.stack(a[::2]),axis=0).astype(np.uint8)
cv2.imwrite('frames/bg0211_median.png',bg)
d=np.abs(b[0].astype(int)-bg.astype(int)).sum(2)
print('diff stats in empty region', np.percentile(d[100:400,100:1200],[50,90,99]))
for i in [0,12,24,36,48]:
    d=np.abs(b[i].astype(int)-bg.astype(int)).sum(2)
    m=(d>40).astype(np.uint8)*255
    cv2.imwrite('frames/mask0212_%03d.png'%i,m)
