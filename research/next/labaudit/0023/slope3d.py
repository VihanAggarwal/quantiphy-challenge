import numpy as np
from geo import *
from bookmask import cover_mask
# board image features (frames 0-20 / 44): top edge y=356.3, bottom edge y ~482.6 (x=520) -> 480.4 (x=650)
TOPY=356.3
def boty(x): return 482.6+(x-520)*(480.4-482.6)/130.
lL=np.load('boardLR_x20.npy')[0]; lR=np.load('boardLR_x20.npy')[1]
def xat(l,y): return -(l[1]*y+l[2])/l[0]
TLp=(xat(lL,TOPY),TOPY); TRp=(xat(lR,TOPY),TOPY)
BLp=(xat(lL,boty(492)),boty(492)); BRp=(xat(lR,boty(677)),boty(677))
def board_model(route, f=F):
    if route=='stated':
        tm=((TLp[0]+TRp[0])/2,TOPY); bm=((BLp[0]+BRp[0])/2,(BLp[1]+BRp[1])/2)
        T=bp(*tm,1.201,f); B=bp(*bm,0.9555,f)
        TL=bp(*TLp,1.201,f); TR=bp(*TRp,1.201,f)
        w=TR-TL
    else: # 24 cm ruler at top and bottom (fronto-parallel approx -> solve z for the edge)
        def edge(Pl,Pr):
            dl=np.array([(Pl[0]-CX)/f,(Pl[1]-CY)/f,1.]); dr=np.array([(Pr[0]-CX)/f,(Pr[1]-CY)/f,1.])
            z=0.24/np.linalg.norm(dr-dl); return dl*z, dr*z
        TL,TR=edge(TLp,TRp); BL,BR=edge(BLp,BRp)
        T=(TL+TR)/2; B=(BL+BR)/2; w=TR-TL
    u=(T-B); L=np.linalg.norm(u); u/=L
    n=np.cross(w,u); n/=np.linalg.norm(n)
    if n[2]>0: n=-n   # normal toward camera
    return dict(T=T,B=B,u=u,n=n,L=L,w=w)
def hit_plane(p0,n,u,v,f=F):
    d=np.array([(u-CX)/f,(v-CY)/f,1.]); s=(n@p0)/(n@d); return d*s
if __name__=='__main__':
    for route in ['stated','ruler']:
        M=board_model(route)
        print(route,'T',M['T'].round(3),'B',M['B'].round(3),'len',round(M['L']*100,2),'width',round(np.linalg.norm(M['w'])*100,2),'n',M['n'].round(3),
              'incl',round(np.degrees(np.arctan2(-M['u'][1],M['u'][2])),1))
        H=0.0146
        p0=M['B']+M['n']*H   # plane of top face
        prev=None
        for i in range(18,34):
            m=cover_mask(f'x{i:02d}'); ys,xs=np.nonzero(m)
            P=hit_plane(p0,M['n'],xs.mean(),ys.mean())
            s=(P-M['B'])@M['u']
            sp='' if prev is None else round(np.linalg.norm(P-prev)*24*100,1)
            print(f'  f{i} t={i/24:.3f} cen=({xs.mean():.1f},{ys.mean():.1f}) range={np.linalg.norm(P):.4f} s_upslope={s*100:.1f}cm  step_speed={sp}')
            prev=P
