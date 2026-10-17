import cv2, numpy as np
p='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0069.mp4'
cap=cv2.VideoCapture(p); G=[]
while True:
    ok,im=cap.read()
    if not ok: break
    G.append(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32))
bg=np.median(np.stack([G[i] for i in (96,100,104,108)]),0)
def sp(a,b,c):
    d=a-2*b+c; return 0 if d==0 else 0.5*(a-c)/d
# handle position at frame 69 ~1180 centre of template 1110-1250 (centre 1180)
hx69=1180.0
def track_template(reff, box, frames, xpred):
    x0,y0,x1,y1=box; T=G[reff][y0:y1,x0:x1]; w=x1-x0
    out={}
    for f in frames:
        cx=xpred(f); sx0=int(max(0,cx-w/2-60)); sx1=int(min(1920,cx+w/2+60))
        band=G[f][y0-20:y1+20, sx0:sx1]
        if band.shape[1]<w+3: continue
        r=cv2.matchTemplate(band,T,cv2.TM_CCOEFF_NORMED); _,mv,_,ml=cv2.minMaxLoc(r); x,y=ml
        dx=sp(r[y,x-1],r[y,x],r[y,x+1]) if 0<x<r.shape[1]-1 else 0
        out[f]=(sx0+x+dx+w/2, mv)
    return out
# rough predictor from handle track
d=np.loadtxt('/home/user/quantiphy-challenge/research/next/audit3/internet_07/tr69.txt')
fr=d[:,0]; m=(fr>=59)&(fr<=77); c=np.polyfit(fr[m],d[m,1],2)
xpred=lambda f: np.polyval(c,f)
frames=range(56,80)
res={}
for reff in (63,69,75):
    off=xpred(reff)-hx69
    box=(int(1110+off),540,int(1250+off),850)
    tr=track_template(reff,box,frames,lambda f,reff=reff: xpred(f)+(xpred(reff)-hx69)*0)
    # convert to handle-centre coordinate relative to frame reff: template centre at frame reff = box centre
    res['h%d'%reff]={f:(v[0]-(box[0]+box[2])/2+xpred(reff),v[1]) for f,v in tr.items()}
# knot-only template (small): around knot at frame 69 (1212,592)
for reff in (66,72):
    off=xpred(reff)-hx69
    box=(int(1185+off),555,int(1240+off),620)
    tr=track_template(reff,box,frames,lambda f: xpred(f)+(1212-1180))
    res['k%d'%reff]={f:(v[0]-(box[0]+box[2])/2+xpred(reff)+0,v[1]) for f,v in tr.items()}
# left edge of cup body, rows 560-760 (wall/baseboard background), threshold on diff
for f in frames:
    D=np.abs(G[f][560:760]-bg[560:760])
    col=(D>18).mean(0)
    idx=np.where(col>0.5)[0]
    L=np.nan
    if len(idx):
        runs=np.split(idx,np.where(np.diff(idx)>8)[0]+1); rr=max(runs,key=len); L=rr[0]
        # subpixel: 50% crossing of col profile at left edge
        if rr[0]>0:
            i=rr[0]; L=i-1+(0.5-col[i-1])/(col[i]-col[i-1]+1e-9)
    res.setdefault('L',{})[f]=(L,1)
keys=sorted(res)
print('f '+' '.join('%9s'%k for k in keys))
arr=[]
for f in frames:
    row=[f]+[res[k].get(f,(np.nan,0))[0] for k in keys]
    arr.append(row)
    print('%d '%f+' '.join('%6.1f(%.2f)'%(res[k].get(f,(np.nan,0))[0],res[k].get(f,(np.nan,0))[1]) for k in keys))
np.savetxt('/home/user/quantiphy-challenge/research/next/audit3/internet_07/tr69b.txt',np.array(arr),fmt='%.2f',header=' '.join(['f']+keys))
