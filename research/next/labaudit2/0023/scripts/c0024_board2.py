import cv2, numpy as np, json
D='/home/user/quantiphy-challenge/research/next/labaudit2/0023/'
def load(ph):
    im=cv2.imread(D+f'other/avg_0024x_{ph}.png').astype(np.float32); lum=im.mean(-1)
    white=(im.min(-1)>200); n,lab,st,cen=cv2.connectedComponentsWithStats(white.astype(np.uint8)); m=(lab==lab[420,760]); return lum,m
def subcross(prof,i0,dirn):
    out=prof[i0-5*dirn]; inn=prof[i0+4*dirn]; mid=0.5*(out+inn)
    for i in range(i0-5*dirn,i0+5*dirn,dirn):
        a,b=prof[i],prof[i+dirn]
        if (a-mid)*(b-mid)<=0 and a!=b: return i+dirn*(mid-a)/(b-a)
    return np.nan
def fitline(P):
    P=np.array(P); P=P[~np.isnan(P).any(1)]; c=P.mean(0); u=np.linalg.svd(P-c)[2][0]; nrm=np.array([-u[1],u[0]]); return c,u,np.std((P-c)@nrm),len(P)
lumS,mS=load('slope'); lumT,mT=load('table')
lines={}
for nm,(lum,m) in {'S':(lumS,mS),'T':(lumT,mT)}.items():
    Lp=[(subcross(lum[y],np.nonzero(m[y])[0].min(),1),y) for y in range(402,456)]
    Rp=[(subcross(lum[y],np.nonzero(m[y])[0].max(),-1),y) for y in range(372,425)]
    Tp=[(x,subcross(lum[:,x],np.nonzero(m[:,x])[0].min(),1)) for x in range(765,850)]
    Bp=[(x,subcross(lum[:,x],np.nonzero(m[:,x])[0].max(),-1)) for x in range(628,690)]
    for k,P in [('L',Lp),('R',Rp),('T',Tp),('B',Bp)]:
        lines[nm+k]=fitline(P); c,u,s,nn=lines[nm+k]; print(nm+k,np.round(c,2),np.round(u,4),'resid %.2f n %d'%(s,nn))
def inter(a,b):
    c1,u1,_,_=lines[a]; c2,u2,_,_=lines[b]; t=np.linalg.solve(np.array([u1,-u2]).T,c2-c1); return c1+t[0]*u1
C={'BL':inter('SB','SL'),'BR':inter('SB','TR'),'TR':inter('TT','TR'),'TL':inter('TT','SL')}
for k,v in C.items(): print(k,np.round(v,2))
json.dump({k:v.tolist() for k,v in C.items()},open(D+'scripts/c0024_corners2.json','w'))
img=np.array([C['BL'],C['BR'],C['TR'],C['TL']])
W=0.242
for f in [650,711,780]:
    K=np.array([[f,0,640],[0,f,360],[0,0,1.]]); best=None
    for Lb in np.arange(0.26,0.40,0.002):
        obj=np.array([[0,0,0],[W,0,0],[W,Lb,0],[0,Lb,0]],float)
        ok,rv,tv=cv2.solvePnP(obj,img,K,None,flags=cv2.SOLVEPNP_IPPE)
        proj,_=cv2.projectPoints(obj,rv,tv,K,None); err=np.sqrt(((proj.reshape(-1,2)-img)**2).sum(1)).max()
        if best is None or err<best[0]: Rm,_=cv2.Rodrigues(rv); best=(err,Lb,Rm,tv.ravel())
    err,Lb,Rm,tv=best; obj=np.array([[0,0,0],[W,0,0],[W,Lb,0],[0,Lb,0]],float); Pc=(Rm@obj.T).T+tv
    print('f',f,'0024 board length %.3f (err %.2f) range bot-mid %.3f top-mid %.3f (ToF 0.990/1.243)'%(Lb,err,np.linalg.norm((Pc[0]+Pc[1])/2),np.linalg.norm((Pc[2]+Pc[3])/2)))
