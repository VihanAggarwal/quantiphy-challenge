import cv2, sys, numpy as np
# usage: prof.py clip frame axis(row|col) idx start end [band]
c=sys.argv[1]; fr=int(sys.argv[2]); ax=sys.argv[3]; idx=int(sys.argv[4]); a=int(sys.argv[5]); b=int(sys.argv[6]); band=int(sys.argv[7]) if len(sys.argv)>7 else 2
cap=cv2.VideoCapture(f'data/QuantiPhy/{c}.mp4'); cap.set(cv2.CAP_PROP_POS_FRAMES,fr); ok,f=cap.read()
f=f.astype(float)
if ax=='row': seg=f[idx-band:idx+band+1,a:b].mean(0)
else: seg=f[a:b,idx-band:idx+band+1].mean(1)
g=seg.mean(1)
d=np.abs(np.diff(g))
out=[]
for i in range(len(g)):
    out.append('%d:%d(%d,%d,%d)'%(a+i,g[i],seg[i,2],seg[i,1],seg[i,0]))
print(' '.join(out))
