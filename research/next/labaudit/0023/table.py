import cv2, numpy as np
F=711.; CX=640.; CY=360.
K=np.array([[F,0,CX],[0,F,CY],[0,0,1.]])
def boundary_pts(fr):
    im=cv2.imread(f'frames/{fr}.png').astype(float)
    m=(im.max(2)>40).astype(float)
    L=[];R=[]
    for y in range(450,524):
        row=m[y,:1000]
        # subpixel boundary: first index where > .5 using raw intensity interpolation
        g=im[y,:1000].max(1)
        idx=np.nonzero(g>40)[0]
        x0=idx.min(); x1=idx[idx<1000].max()
        # interpolate at threshold 40 using left neighbour
        def sub(a,b):
            ga,gb=g[a],g[b]; return a+(40-ga)/(gb-ga)*(b-a)
        L.append((sub(x0-1,x0),y)); R.append((sub(x1+1,x1),y))
    # front edge: brown->dark transition, find where brightness drops below midpoint between top and face
    Fp=[]
    for x in range(310,900,4):
        col=im[500:560,x].mean(1)
        top=col[:20].mean(); face=np.median(col[35:50])
        thr=(top+face)/2
        k=np.nonzero(col<thr)[0]
        k=k[k>15]
        if len(k)==0 or top-face<40: continue
        k=k[0]
        y=500+k-1+(col[k-1]-thr)/(col[k-1]-col[k])
        Fp.append((x,y))
    B=[]
    for x in list(range(445,476,3))+list(range(700,766,3)):
        g=im[380:500,x].max(1); k=np.nonzero(g>40)[0][0]
        y=380+k-1+(40-g[k-1])/(g[k]-g[k-1]); B.append((x,y))
    return np.array(L),np.array(R),np.array(Fp),np.array(B)
def fitline(P):
    P=np.asarray(P,float); c=P.mean(0); u,s,vt=np.linalg.svd(P-c); d=vt[0]; n=np.array([-d[1],d[0]])
    res=(P-c)@n
    return np.array([n[0],n[1],-n@c]), np.abs(res).max()
def inter(l1,l2):
    p=np.cross(l1,l2); return p[:2]/p[2]
if __name__=='__main__':
    for fr in ['x00','x44','x48','s44']:
        L,R,Fp,B=boundary_pts(fr)
        lL,eL=fitline(L); lR,eR=fitline(R); lF,eF=fitline(Fp); lB,eB=fitline(B)
        FL=inter(lL,lF); FR=inter(lR,lF); BL=inter(lL,lB); BR=inter(lR,lB)
        print(fr,'res',round(eL,2),round(eR,2),round(eF,2),round(eB,2),'FL',FL.round(1),'FR',FR.round(1),'BR',BR.round(1),'BL',BL.round(1))
        img=np.array([FL,FR,BR,BL])
        for dims in [(60.3,76.0),(76.0,60.3)]:
            W,D=dims
            obj=np.array([[0,0,0],[W,0,0],[W,D,0],[0,D,0]],float)/100
            ok,rv,tv=cv2.solvePnP(obj,img,K,None,flags=cv2.SOLVEPNP_IPPE)
            pr,_=cv2.projectPoints(obj,rv,tv,K,None)
            err=np.abs(pr.reshape(-1,2)-img).max()
            Rm=cv2.Rodrigues(rv)[0]; n=Rm[:,2]; c=n@tv.ravel()
            cam=(Rm@obj.T).T+tv.ravel()
            print('  dims',dims,'maxerr',round(err,2),'normal',n.round(3),'offset',round(c,4),'corner ranges',np.linalg.norm(cam,axis=1).round(3))
        np.save(f'corners_{fr}.npy',img)
