# Segment dragon in 0302 (sky bg) per frame; save bbox + mask stats (not frames)
import cv2, numpy as np, json
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0302.mp4')
frames=[]
while True:
    ok,f=c.read()
    if not ok: break
    frames.append(f)
print(len(frames))
F=np.array(frames[::8]).astype(np.float32)
bg=np.median(F,axis=0)
out=[]
for i,f in enumerate(frames):
    d=np.abs(f.astype(np.float32)-bg).sum(2)
    m=(d>40).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    out.append((i,int(x),int(y),int(w),int(h),int(a)))
    if i in (24,51,60,71):
        mm=(lab==k).astype(np.uint8)*255
        cv2.imwrite(f'frames/m0302_{i:03d}.png', mm[y-20:y+h+20, x-20:x+w+20])
for o in out: print(o)
np.save('bg0302.npy', bg.astype(np.uint8))
