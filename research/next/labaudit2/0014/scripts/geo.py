import numpy as np, json
F=711.0; CX=640.0; CY=360.0
def ray(u,v,f=F):
    d=np.array([(u-CX)/f,(v-CY)/f,1.0]); return d/np.linalg.norm(d)
def bp(u,v,r,f=F): return r*ray(u,v,f)
def proj(X,f=F): return np.array([f*X[0]/X[2]+CX,f*X[1]/X[2]+CY])
C=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0014/board_corners.json'))['o']
TR,BR,BL,TL=[np.array(p) for p in C]
def hom(p): return np.array([p[0],p[1],1.0])
def vp(a,b,c,d):
    l1=np.cross(hom(a),hom(b)); l2=np.cross(hom(c),hom(d)); v=np.cross(l1,l2); return v
def board_plane(f=F, rfar=1.854, rnear=1.701, anchor='far'):
    # direction along slope (top->bottom): VP of left and right edges
    v1=vp(TL,BL,TR,BR); v2=vp(TL,TR,BL,BR)
    Kinv=np.array([[1/f,0,-CX/f],[0,1/f,-CY/f],[0,0,1]])
    d1=Kinv@v1; d1/=np.linalg.norm(d1)
    d2=Kinv@v2; d2/=np.linalg.norm(d2)
    if d1[1]<0: d1=-d1   # down the slope -> +y image
    n=np.cross(d1,d2); n/=np.linalg.norm(n)
    tm=(TL+TR)/2; bm=(BL+BR)/2
    Pf=bp(*tm,rfar,f); Pn=bp(*bm,rnear,f)
    if n@Pf>0: n=-n  # normal toward camera: n.X = c with c<0? keep: camera side has n.(0-X)>0
    return dict(d1=d1,d2=d2,n=n,Pf=Pf,Pn=Pn,ortho=float(d1@d2))
def inter(u,v,n,c,f=F):
    d=ray(u,v,f); t=c/(n@d); return t*d
if __name__=='__main__':
    for f in [650,680,711,740]:
        B=board_plane(f)
        n=B['n']; Pf=B['Pf']; Pn=B['Pn']
        print('f',f,'d1.d2',round(B['ortho'],4),'n',np.round(n,3),'Pn dev from plane thru Pf (cm)',round(100*(n@(Pn-Pf)),2),
              'slope len stated',round(100*np.linalg.norm(Pf-Pn),2))
    B=board_plane()
    n=B['n']
    for anc,P in [('far',B['Pf']),('near',B['Pn'])]:
        c=n@P
        X=[inter(*p,n,c) for p in (TL,TR,BR,BL)]
        L=np.linalg.norm((X[0]+X[1])/2-(X[2]+X[3])/2); W1=np.linalg.norm(X[0]-X[1]); W2=np.linalg.norm(X[3]-X[2])
        print(anc,'plane c',round(c,4),'len mid-mid',round(100*L,2),'width top',round(100*W1,2),'bottom',round(100*W2,2),
              'ranges TL TR BR BL',[round(np.linalg.norm(x),3) for x in X],
              'angle edges', round(np.degrees(np.arccos(abs((X[0]-X[3])@(X[0]-X[1])/np.linalg.norm(X[0]-X[3])/np.linalg.norm(X[0]-X[1])))),1))
    print('d1 (down slope)',np.round(B['d1'],3))
