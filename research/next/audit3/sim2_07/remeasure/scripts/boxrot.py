import cv2, numpy as np, json, sys
fi=int(sys.argv[1])
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0253.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
B={r[0]:r for r in json.load(open('box0253.json'))}
cx,cy=B[fi][1],B[fi][2]
# rotate so the slope direction is horizontal
M=cv2.getRotationMatrix2D((cx,cy),44.224,1.0)
rot=cv2.warpAffine(fr[fi],M,(1920,1080),flags=cv2.INTER_CUBIC)
H=75
crop=rot[int(cy)-H:int(cy)+H,int(cx)-H:int(cx)+H]
Z=5
z=cv2.resize(crop,(2*H*Z,2*H*Z),interpolation=cv2.INTER_NEAREST)
for k in range(0,2*H*Z,5*Z):
    col=(0,0,255) if (k//(5*Z))%2==0 else (255,0,0)
    cv2.line(z,(k,0),(k,2*H*Z-1),col,1); cv2.line(z,(0,k),(2*H*Z-1,k),col,1)
for k in range(0,2*H*Z,25*Z):
    cv2.putText(z,str(k//Z-H),(k+2,12),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,255,255),1)
    cv2.putText(z,str(k//Z-H),(2,k+12),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,255,255),1)
cv2.imwrite(f'boxrot_{fi}.png',z)
# also print row-averaged luma profile along the slope direction at several perpendicular offsets
Y=crop.astype(np.float32)@np.array([0.114,0.587,0.299],np.float32)
for off in range(-30,31,10):
    p=Y[H+off-2:H+off+3].mean(0)
    g=np.gradient(p)
    idx=np.argsort(-np.abs(g))[:6]
    print(off,'strong edges at x=',sorted([(int(j)-H, round(float(g[j]),1)) for j in idx]))
