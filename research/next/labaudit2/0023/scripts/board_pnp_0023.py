import cv2, numpy as np
D='/home/user/quantiphy-challenge/research/next/labaudit2/0023/'
# 0023 table-phase board: side lines from subpixel fits rows 380-436 (raw), top edge y=356.5, bottom edge y = 482.0 - 0.0156*(x-590)
import importlib.util
spec=importlib.util.spec_from_file_location('w2',D+'scripts/width_geom2.py')
def edges(V,ph,y0,y1):
    A=np.load(D+f'frames/avg_{V}_{ph}.npy'); lum=A.mean(-1); out=[]
    for y in range(y0,y1):
        p=lum[y-300]
        xl=next(x for x in range(470,580) if p[x-400]>200); xr=next(x for x in range(720,600,-1) if p[x-400]>200)
        def subpix(xe,dirn):
            out_=p[xe-400-6*dirn]; inn=p[xe-400+4*dirn]; mid=0.5*(out_+inn)
            xs=np.arange(xe-6*dirn,xe+5*dirn,dirn); vals=p[xs-400]
            for i in range(len(xs)-1):
                if (vals[i]-mid)*(vals[i+1]-mid)<=0 and vals[i]!=vals[i+1]:
                    return xs[i]+dirn*(mid-vals[i])/(vals[i+1]-vals[i])
            return np.nan
        out.append((y,subpix(xl,1),subpix(xr,-1)))
    return np.array(out)
E=edges('captured_0023','table',380,437)
aL,bL=np.polyfit(E[:,0],E[:,1],1); aR,bR=np.polyfit(E[:,0],E[:,2],1)
for ytop in [356.5]:
    ybot=481.7
    img=np.array([[aL*ybot+bL,ybot],[aR*ybot+bR,ybot-0.0156*((aR*ybot+bR)-(aL*ybot+bL))],[aR*ytop+bR,ytop],[aL*ytop+bL,ytop]])
    print('corners',np.round(img,1).tolist())
    W=0.242
    for f in [650,711,780]:
        K=np.array([[f,0,640],[0,f,360],[0,0,1.]]); best=None
        for Lb in np.arange(0.26,0.40,0.002):
            obj=np.array([[0,0,0],[W,0,0],[W,Lb,0],[0,Lb,0]],float)
            ok,rv,tv=cv2.solvePnP(obj,img,K,None,flags=cv2.SOLVEPNP_IPPE)
            proj,_=cv2.projectPoints(obj,rv,tv,K,None); err=np.sqrt(((proj.reshape(-1,2)-img)**2).sum(1)).max()
            if best is None or err<best[0]: Rm,_=cv2.Rodrigues(rv); best=(err,Lb,Rm,tv.ravel())
        err,Lb,Rm,tv=best; obj=np.array([[0,0,0],[W,0,0],[W,Lb,0],[0,Lb,0]],float); Pc=(Rm@obj.T).T+tv
        print('f',f,'0023 board length %.3f (err %.2f) range bot-mid %.3f top-mid %.3f (ToF 0.9555/1.201)'%(Lb,err,np.linalg.norm((Pc[0]+Pc[1])/2),np.linalg.norm((Pc[2]+Pc[3])/2)))
