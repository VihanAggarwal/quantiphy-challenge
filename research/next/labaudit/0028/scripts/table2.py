import cv2, numpy as np
out='/home/user/quantiphy-challenge/research/next/labaudit/0028/frames'
F=640;CX=640;CY=360
def lines(fi):
    f=cv2.imread(f'{out}/captured_0028x_{fi:02d}.png').astype(float)
    s=f.sum(2)
    # subpixel boundary along rows for left/right edges: threshold at half of table brightness
    L=[];R=[];B=[];Fr=[]
    for y in range(435,478):
        row=s[y,:]
        thr=0.5*np.median(row[640:700])
        xs=np.nonzero(row>thr)[0]
        # left boundary
        x=xs.min(); 
        xl=x-1+(thr-row[x-1])/(row[x]-row[x-1]); L.append((xl,y))
        x=xs[xs<1000].max(); xr=x+(row[x]-thr)/(row[x]-row[x+1]); R.append((xr,y))
    for x in range(600,830,4):
        col=s[:,x]; thr=0.5*np.median(col[440:470])
        ys=np.nonzero(col[400:480]>thr)[0]+400; y=ys.min()
        B.append((x,y-1+(thr-col[y-1])/(col[y]-col[y-1])))
        # front edge: strongest negative gradient (top bright -> face darker) between 478 and 505
        g=np.diff(cv2.GaussianBlur(f,(1,5),0).sum(2)[:,x])
    # front edge by gradient on V channel
    hsv=cv2.cvtColor(f.astype(np.uint8),cv2.COLOR_BGR2HSV).astype(float)
    v=cv2.GaussianBlur(hsv[:,:,2],(3,3),0)
    for x in range(480,950,5):
        ylo=int(484+(x-463)*(495-484)/(962-463))-8
        seg=v[ylo:ylo+16,x]; g=seg[1:]-seg[:-1]; k=np.argmin(g)
        Fr.append((x,ylo+k+0.5))
    return np.array(L),np.array(R),np.array(B),np.array(Fr)
def fitline(P,vertical=False):
    # returns (a,b,c) for a x + b y + c =0
    P=np.asarray(P,float); m=P.mean(0); u,sv,vt=np.linalg.svd(P-m); d=vt[0]; n=np.array([-d[1],d[0]])
    return np.array([n[0],n[1],-n@m])
def inter(l1,l2):
    p=np.cross(l1,l2); return p[:2]/p[2]
for fi in [5,10,40]:
    L,R,B,Fr=lines(fi)
    lL,lR,lB,lF=[fitline(p) for p in (L,R,B,Fr)]
    res=[np.abs(P@l[:2]+l[2]).max() for P,l in zip((L,R,B,Fr),(lL,lR,lB,lF))]
    c=[inter(lB,lL),inter(lB,lR),inter(lF,lR),inter(lF,lL)]
    print(fi,'corners BL,BR,FR,FL',np.round(c,1).tolist(),'maxres',np.round(res,2))
np.save('/home/user/quantiphy-challenge/research/next/labaudit/0028/scripts/corners.npy',np.array(c))
