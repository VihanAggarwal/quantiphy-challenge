import cv2, numpy as np
def load(v):
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{v}.mp4'); F=[]
    while True:
        ok,im=c.read()
        if not ok: break
        F.append(im)
    return F
A=load('0238'); B=load('0240')
out=[]
for i in range(49):
    a=A[i].astype(np.int16); b=B[i].astype(np.int16)
    d=np.abs(a-b).sum(2)
    m=(d>60).astype(np.uint8); m[:1000]=0; m[1090:]=0
    # rabbit is orange: require b's colour to be orange-ish (R>G>B, R-B>40)
    orange=((b[...,2]-b[...,0])>45)&(b[...,2]>110)
    m2=(m.astype(bool)&orange).astype(np.uint8)
    m2=cv2.morphologyEx(m2,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m2)
    if n<2: out.append(None); continue
    k=1+np.argmax(st[1:,4])
    out.append((i,int(st[k,0]),int(st[k,0]+st[k,2]-1),int(st[k,1]),int(st[k,1]+st[k,3]-1),int(st[k,4]),round(cen[k,0],1)))
for o in out: print(o)
v=[o for o in out if o]
t=np.array([o[0] for o in v]); cx=np.array([o[6] for o in v]); L=np.array([o[1] for o in v]); R=np.array([o[2] for o in v])
print('slope cx %.3f left %.3f right %.3f'%(np.polyfit(t,cx,1)[0],np.polyfit(t,L,1)[0],np.polyfit(t,R,1)[0]))
print('width median',np.median(R-L+1))
