import numpy as np, cv2
D='/home/user/quantiphy-challenge/research/next/labaudit2/0023/'
res={}
for ph in ['slope','table']:
    A=np.load(D+f'frames/avg_captured_0023x_{ph}.npy')  # offset y300,x400
    gray=A.mean(-1)
    white=(A.min(-1)>215)  # board is near white
    # left/right edge per row of the white board region
    L=[];R=[]
    for y in range(365,478):
        row=white[y-300]
        xx=np.nonzero(row[60:300])[0]+60   # x 460..700
        if len(xx)<50: continue
        # subpixel: find crossing of gray at threshold between left bg and white
        xl=xx.min(); xr=xx.max()
        def sub(x0,dirn):
            # find gray crossing of mid level
            g=gray[y-300]
            lo=g[x0-4*dirn] if dirn==1 else g[x0+4]
            # simple: linear interp around threshold 0.5*(g_in+g_out)
            gin=g[x0+3*dirn] if dirn==1 else g[x0-3]
            return x0
        L.append((y,xl+400)); R.append((y,xr+400))
    L=np.array(L,float); R=np.array(R,float)
    # robust line fits x = a*y + b
    def fit(P):
        a,b=np.polyfit(P[:,0],P[:,1],1); r=P[:,1]-(a*P[:,0]+b)
        m=np.abs(r)<2; a,b=np.polyfit(P[m,0],P[m,1],1); return a,b,np.std(P[m,1]-(a*P[m,0]+b)),m.sum()
    aL,bL,sL,nL=fit(L); aR,bR,sR,nR=fit(R)
    yv=(bR-bL)/(aL-aR); xv=aL*yv+bL
    print(ph,'left x=%.4f y+%.1f (sd %.2f n %d)  right x=%.4f y+%.1f (sd %.2f n %d)  VP (%.1f, %.1f)'%(aL,bL,sL,nL,aR,bR,sR,nR,xv,yv))
    # bottom edge of board per column: last white row
    B=[]
    for x in range(500,670,5):
        col=white[:,x-400]; yy=np.nonzero(col[150:200])[0]+150+300
        if len(yy): B.append((x,yy.max()))
    B=np.array(B,float); c,d=np.polyfit(B[:,0],B[:,1],1)
    print('  bottom edge y=%.4f x+%.2f'%(c,d), B[::6].tolist())
    T=[]
    for x in list(range(505,535))+list(range(650,672)):
        col=white[:,x-400]; yy=np.nonzero(col[40:120])[0]+40+300
        if len(yy): T.append((x,yy.min()))
    print('  top white rows', T[::3])
    res[ph]=dict(aL=aL,bL=bL,aR=aR,bR=bR,vp=(xv,yv),bot=(c,d))
import json; json.dump(res,open(D+'scripts/board_edges.json','w'),indent=1)
