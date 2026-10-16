import numpy as np
f=711.0; cx,cy=640.,360.
def ray(u,v):
    r=np.array([(u-cx)/f,(v-cy)/f,1.]); return r/np.linalg.norm(r)
TL,TR,BR,BL=np.load('board_corners.npy')
top=(TL+TR)/2; bot=(BL+BR)/2
Pt=1.854*ray(*top); Pb=1.701*ray(*bot)
L=np.linalg.norm(Pb-Pt); e=(Pb-Pt)/L
print('slope length (top-mid to bot-mid) cm %.1f'%(100*L))
def on_plane(u,v,P0,n):
    r=ray(u,v); s=(n@P0)/(n@r); return s*r
TL3=on_plane(*TL,Pt,e); TR3=on_plane(*TR,Pt,e); BL3=on_plane(*BL,Pb,e); BR3=on_plane(*BR,Pb,e)
print('top width %.1f bottom width %.1f'%(100*np.linalg.norm(TR3-TL3),100*np.linalg.norm(BR3-BL3)))
h=(BR3-BL3)+(TR3-TL3); h/=np.linalg.norm(h)
print('h.e',h@e)
n=np.cross(e,h); n/=np.linalg.norm(n)
if n@(-Pb)<0: n=-n   # toward camera
print('normal toward cam',n)
# angle between board and camera optical axis etc
# table plane? estimate gravity? unknown; print the board's e in camera coords
print('e',e)
np.save('model.npy',np.vstack([Pt,Pb,e,h,n]))
for r_cm in [3.0,3.25,3.5]:
    r=r_cm/100
    P0=Pb+r*n
    def ball3d(u,v): return on_plane(u,v,P0,n)
    print('r=%.2f: range at (547.8,361.0)=%.4f ; at frame0 (545,296)=%.4f'%(r,np.linalg.norm(ball3d(547.8,361.0)),np.linalg.norm(ball3d(545,296))))
