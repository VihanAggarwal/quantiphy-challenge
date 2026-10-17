import cv2, numpy as np
p='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0069.mp4'
cap=cv2.VideoCapture(p); G=[]
while True:
    ok,im=cap.read()
    if not ok: break
    G.append(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32))
d=np.loadtxt('/home/user/quantiphy-challenge/research/next/audit3/internet_07/tr69b.txt')
fr=d[:,0]; hx=d[:,3]  # h69
m=(fr>=59)&(fr<=76); c=np.polyfit(fr[m],hx[m],2)
hp=lambda f: np.polyval(c,f)
def edge(f, rows, off, sign, half=45):
    g=cv2.GaussianBlur(G[f],(0,0),2.0)
    gx=np.zeros_like(g); gx[:,1:-1]=(g[:,2:]-g[:,:-2])/2
    xs=[]
    for y in rows:
        cx=int(round(hp(f)+off)); lo=max(2,cx-half); hi=min(1917,cx+half)
        if hi-lo<20: continue
        prof=sign*gx[y,lo:hi]
        i=int(np.argmax(prof))
        if prof[i]<1.0: continue
        if 0<i<len(prof)-1:
            a,b,cc=prof[i-1],prof[i],prof[i+1]; dd=a-2*b+cc; s=0.5*(a-cc)/dd if dd!=0 else 0
        else: s=0
        xs.append(lo+i+s)
    xs=np.array(xs)
    if len(xs)<5: return np.nan,0
    med=np.median(xs); xs=xs[np.abs(xs-med)<6]
    return xs.mean(), len(xs)
out=[]
for f in range(57,79):
    L=edge(f,range(560,840,2),604-1180,-1)      # left edge: bright->dark (negative gradient)
    R=edge(f,range(640,760,2),1019-1180,+1,30)  # right body edge inside handle hole: dark->bright
    H=edge(f,range(640,780,2),1194-1180,-1,30)  # handle outer edge: bright handle -> darker bg
    out.append((f,L[0],R[0],H[0],L[1],R[1],H[1]))
    print('%d L %.1f(%d) R %.1f(%d) H %.1f(%d)'%(f,L[0],L[1],R[0],R[1],H[0],H[1]))
np.savetxt('/home/user/quantiphy-challenge/research/next/audit3/internet_07/edges69.txt',np.array(out),fmt='%.2f')
