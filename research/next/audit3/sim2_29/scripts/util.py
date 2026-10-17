import cv2, numpy as np, sys, os
D='/home/user/quantiphy-challenge/data/QuantiPhy/'
W='/home/user/quantiphy-challenge/research/next/audit3/sim2_29/'
def frames(v, idx=None, gray=False):
    c=cv2.VideoCapture(D+v+'.mp4'); out={}; i=0
    while True:
        ok,f=c.read()
        if not ok: break
        if idx is None or i in idx:
            out[i]=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) if gray else f
        i+=1
    return out
def montage(v, idx, scale=0.25, name=None):
    fr=frames(v, set(idx))
    ims=[cv2.resize(fr[i],None,fx=scale,fy=scale) for i in idx if i in fr]
    for k,i in enumerate([i for i in idx if i in fr]):
        cv2.putText(ims[k],str(i),(5,25),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2)
    rows=[]; n=len(ims); cols=min(n,4)
    while len(ims)%cols: ims.append(np.zeros_like(ims[0]))
    for r in range(0,len(ims),cols): rows.append(np.hstack(ims[r:r+cols]))
    m=np.vstack(rows)
    p=W+(name or v+'_mont.png'); cv2.imwrite(p,m); return p
if __name__=='__main__':
    v=sys.argv[1]; idx=[int(x) for x in sys.argv[2].split(',')]; sc=float(sys.argv[3]) if len(sys.argv)>3 else 0.25
    print(montage(v,idx,sc))
