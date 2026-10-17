from load import load
import numpy as np, cv2, json
fr=load(gray=False)
D=json.load(open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/linefit.json'))
Rb=dict(zip(D['fr'],D['R']))
out={}
for i in range(55,80):
    f=cv2.GaussianBlur(fr[i].astype(np.float32),(0,0),1.2)
    g=np.abs(cv2.Sobel(f,cv2.CV_32F,1,0,ksize=3)).sum(2)
    pts=[]
    for r in range(660,772,3):
        p=g[r-1:r+2].mean(0)
        a=int(Rb[i]+12); b=int(min(1915,Rb[i]+200))
        if b-a<20: continue
        seg=p[a:b].copy()
        # find two strongest separated peaks
        pk=[]
        for _ in range(2):
            k=int(np.argmax(seg))
            if 0<k<len(seg)-1:
                y0,y1,y2=seg[k-1],seg[k],seg[k+1]; d=0.5*(y0-y2)/(y0-2*y1+y2)
                pk.append((a+k+d,y1))
            seg[max(0,k-12):k+13]=0
        pk.sort()
        pts.append((r,pk))
    out[i]=pts
# fit lines to inner (first) and outer (second) peaks
YR=720
def robline(y,x):
    w=np.ones_like(x)
    for _ in range(8):
        A=np.vstack([np.ones_like(y),y-YR]).T
        p=np.linalg.lstsq(A*w[:,None],x*w,rcond=None)[0]; r=x-A@p; s=1.4826*np.median(abs(r))+0.3; w=(abs(r)<2.5*s).astype(float)
    return p,int(w.sum()),np.sqrt(np.mean((r[w>0])**2))
res={}
for i,pts in out.items():
    yi=[];xi=[];xo=[];si=[]
    for r,pk in pts:
        if len(pk)==2: yi.append(r); xi.append(pk[0][0]); xo.append(pk[1][0]); si.append((pk[0][1],pk[1][1]))
    yi=np.array(yi,float); xi=np.array(xi); xo=np.array(xo)
    if len(yi)<10: continue
    pi,ni,ri=robline(yi,xi); po,no,ro=robline(yi,xo)
    res[i]=(pi[0],pi[1],ni,ri,po[0],po[1],no,ro,np.median(np.array(si),0).tolist())
    print(i,'inner %.2f sl %+.3f n%d rms %.2f | outer %.2f sl %+.3f n%d rms %.2f | str %s | inner-Rbody %.1f'%(pi[0],pi[1],ni,ri,po[0],po[1],no,ro,np.round(res[i][8]),pi[0]-Rb[i]))
json.dump({str(k):v for k,v in res.items()},open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/handle.json','w'),default=float)
