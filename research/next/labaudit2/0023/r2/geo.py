import numpy as np, json
F=711.; CX=640.; CY=360.
D='/home/user/quantiphy-challenge/research/next/labaudit2/0023/r2/'
def ray(u,v,f=F): return np.array([(u-CX)/f,(v-CY)/f,1.])
def unit(u,v,f=F): d=ray(u,v,f); return d/np.linalg.norm(d)
def bp(u,v,r,f=F): return unit(u,v,f)*r
Bd=json.load(open(D+'board.json'))['x20']
TL,TR,BL,BR=[np.array(Bd[k]) for k in ['TL','TR','BL','BR']]
def board_model(route,f=F):
    if route=='stated':
        tm=(TL+TR)/2; bm=(BL+BR)/2
        T=bp(*tm,1.201,f); B=bp(*bm,0.9555,f)
        w=bp(*TR,1.201,f)-bp(*TL,1.201,f); wb=bp(*BR,0.9555,f)-bp(*BL,0.9555,f)
    else:  # 24 cm width ruler at top and bottom edges
        def edge(Pl,Pr):
            dl=ray(*Pl,f); dr=ray(*Pr,f); z=0.24/np.linalg.norm(dr-dl); return dl*z,dr*z
        a,b=edge(TL,TR); c,d=edge(BL,BR); T=(a+b)/2; B=(c+d)/2; w=b-a; wb=d-c
    u=T-B; L=np.linalg.norm(u); u=u/L
    wv=(w+wb); wv=wv-(wv@u)*u; wv/=np.linalg.norm(wv)
    n=np.cross(wv,u); n/=np.linalg.norm(n)
    if n@B>0: n=-n  # toward camera
    return dict(T=T,B=B,u=u,n=n,wv=wv,L=L,wt=np.linalg.norm(w),wb=np.linalg.norm(wb),incl=np.degrees(np.arccos(abs(n@np.array([0,-1,0])))) )
def hit_plane(p0,n,u,v,f=F):
    d=ray(u,v,f); s=(n@p0)/(n@d); return d*s
YH=349.5
def table_pt(u,v,h,f=F,yh=YH):
    # level camera (no roll): plane y_cam = h in a frame rotated by pitch so horizon at yh
    K=np.array([[f,0,CX],[0,f,CY],[0,0,1.]])
    nT=K.T@np.array([0,1,-yh]); nT/=np.linalg.norm(nT)
    d=ray(u,v,f); return d*h/(nT@d)
if __name__=='__main__':
    for r in ['stated','ruler']:
        M=board_model(r); print(r,'T',M['T'].round(4),'B',M['B'].round(4),'L %.2f wt %.2f wb %.2f incl %.1f'%(M['L']*100,M['wt']*100,M['wb']*100,M['incl']),'n',M['n'].round(3))
    # board bottom-mid on table plane?
    bm=(BL+BR)/2
    for h in [0.169,0.171]:
        P=table_pt(*bm,h); print('board bottom-mid on table plane h=%.3f: range %.4f'%(h,np.linalg.norm(P)))
