import cv2, numpy as np, json
D='/home/user/quantiphy-challenge/research/next/labaudit2/0023/'
res={}
for ph in ['table','slope']:
    im=cv2.imread(D+f'other/avg_0024x_{ph}.png').astype(np.float32)
    lum=im.mean(-1)
    white=(im.min(-1)>200)
    n,lab,st,cen=cv2.connectedComponentsWithStats(white.astype(np.uint8))
    # choose component containing (760,420)
    k=lab[420,760]; m=(lab==k)
    ys,xs=np.nonzero(m); print(ph,'board bbox',xs.min(),xs.max(),ys.min(),ys.max())
    def subcross(prof,i0,dirn):
        # crossing of mid level near index i0 along a 1-D profile
        out=prof[i0-5*dirn]; inn=prof[i0+4*dirn]; mid=0.5*(out+inn)
        for i in range(i0-5*dirn,i0+5*dirn,dirn):
            a,b=prof[i],prof[i+dirn]
            if (a-mid)*(b-mid)<=0 and a!=b: return i+dirn*(mid-a)/(b-a)
        return np.nan
    # left edge (along slope): per row, first white from left, rows 372..450
    Lp=[];Rp=[]
    for y in range(372,452):
        xx=np.nonzero(m[y])[0]
        if len(xx)<5: continue
        Lp.append((subcross(lum[y],xx.min(),1),y))
    for y in range(368,425):   # right edge visible against black above book stack
        xx=np.nonzero(m[y])[0]
        if len(xx)<5: continue
        Rp.append((subcross(lum[y],xx.max(),-1),y))
    Tp=[]
    for x in range(765,850):
        yy=np.nonzero(m[:,x])[0]
        Tp.append((x,subcross(lum[:,x],yy.min(),1)))
    Bp=[]
    for x in range(625,690):
        yy=np.nonzero(m[:,x])[0]
        Bp.append((x,subcross(lum[:,x],yy.max(),-1)))
    Lp=np.array(Lp);Rp=np.array(Rp);Tp=np.array(Tp);Bp=np.array(Bp)
    def fitline(P):
        P=P[~np.isnan(P).any(1)]
        c=P.mean(0); u=np.linalg.svd(P-c)[2][0]; nrm=np.array([-u[1],u[0]])
        r=(P-c)@nrm; return c,u,np.std(r)
    lines={nm:fitline(P) for nm,P in [('L',Lp),('R',Rp),('T',Tp),('B',Bp)]}
    for nm,(c,u,s) in lines.items(): print('  ',nm,'pt',np.round(c,1),'dir',np.round(u,4),'resid %.2f'%s)
    def inter(a,b):
        c1,u1,_=lines[a]; c2,u2,_=lines[b]
        A=np.array([u1,-u2]).T; t=np.linalg.solve(A,c2-c1); return c1+t[0]*u1
    C={'TL':inter('T','L'),'TR':inter('T','R'),'BR':inter('B','R'),'BL':inter('B','L')}
    for k_,v in C.items(): print('  corner',k_,np.round(v,1))
    res[ph]={k_:v.tolist() for k_,v in C.items()}
json.dump(res,open(D+'scripts/c0024_board.json','w'),indent=1)
