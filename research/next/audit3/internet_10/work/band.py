import cv2,numpy as np
def fr(clip,k):
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/internet_{clip}.mp4'); c.set(cv2.CAP_PROP_POS_FRAMES,k); ok,f=c.read(); return f
for clip,k in [('0060',100),('0063',90),('0060',0),('0063',0)]:
    f=fr(clip,k); g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(float)
    out=[]
    for y in [100,300,500,700,900,1050]:
        row=g[y-3:y+4].mean(0)
        dark=np.where(row[1000:1700]<60)[0]+1000
        out.append((y,dark.min(),dark.max(),dark.max()-dark.min()))
    print(clip,k,out)
