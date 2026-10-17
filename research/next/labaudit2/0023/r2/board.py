import cv2, numpy as np, json
R1='/home/user/quantiphy-challenge/research/next/labaudit/0023/frames/'
def sub_cross(p,thr):
    k=np.nonzero(p>=thr)[0]
    if len(k)==0 or k[0]==0: return None
    k=k[0]; return k-1+(thr-p[k-1])/(p[k]-p[k-1])
def fit_xy(P):
    P=np.array(P,float); a,b=np.polyfit(P[:,1],P[:,0],1)
    r=P[:,0]-(a*P[:,1]+b); m=np.abs(r)<1.5; a,b=np.polyfit(P[m,1],P[m,0],1); return a,b,np.std(P[m,0]-(a*P[m,1]+b))
def fit_yx(P):
    P=np.array(P,float); a,b=np.polyfit(P[:,0],P[:,1],1)
    r=P[:,1]-(a*P[:,0]+b); m=np.abs(r)<1.5; a,b=np.polyfit(P[m,0],P[m,1],1); return a,b,np.std(P[m,1]-(a*P[m,0]+b)),m.sum()
def sides_bottom(fr):
    im=cv2.imread(R1+fr+'.png').astype(float); g=im.min(2)
    L=[];R=[]
    for y in range(392,476):
        p=g[y,440:600]; t=(np.median(p[:20])+np.median(p[-30:]))/2; xl=sub_cross(p,t)
        q=g[y,600:740][::-1]; t2=(np.median(q[:20])+np.median(q[-30:]))/2; xr=sub_cross(q,t2)
        if xl is not None: L.append((440+xl,y))
        if xr is not None: R.append((739-xr,y))
    B=[]
    for x in range(500,672,2):
        q=g[440:520,x][::-1]; t2=(np.median(q[:10])+np.median(q[-15:]))/2; yb=sub_cross(q,t2)
        if yb is not None: B.append((x,519-yb))
    return fit_xy(L),fit_xy(R),fit_yx(B)
def top(fr):
    im=cv2.imread(R1+fr+'.png').astype(float); g=im.min(2)
    T=[]
    for x in range(522,656,2):
        p=g[320:400,x]; t=(np.median(p[:10])+np.median(p[-15:]))/2; yt=sub_cross(p,t)
        if yt is not None: T.append((x,320+yt))
    return fit_yx(T)
def inter(a,b,c,d):
    y=(c*b+d)/(1-c*a); return np.array([a*y+b,y])
out={}
for frs,frt in [('x20','x44'),('x10','x40'),('o20','o44'),('x05','x48')]:
    (aL,bL,sL),(aR,bR,sR),(cB,dB,sB,nB)=sides_bottom(frs); cT,dT,sT,nT=top(frt)
    TL=inter(aL,bL,cT,dT); TR=inter(aR,bR,cT,dT); BL=inter(aL,bL,cB,dB); BR=inter(aR,bR,cB,dB)
    print(frs,frt,'sd L%.2f R%.2f T%.2f(n%d) B%.2f(n%d)'%(sL,sR,sT,nT,sB,nB),'TL',TL.round(1),'TR',TR.round(1),'BL',BL.round(1),'BR',BR.round(1),'top w %.1f bot w %.1f'%(TR[0]-TL[0],BR[0]-BL[0]))
    out[frs]=dict(TL=TL.tolist(),TR=TR.tolist(),BL=BL.tolist(),BR=BR.tolist(),L=(aL,bL),R=(aR,bR),B=(cB,dB),T=(cT,dT))
json.dump(out,open('board.json','w'),indent=1)
