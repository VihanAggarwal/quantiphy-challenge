import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0024/scripts')
from geo import *
BLp=(609,467); BRp=(705,493); TLp=(751,360); TRp=(857,361)
BL=on_plane(*BLp); BR=on_plane(*BRp)
e=(BL-BR)/np.linalg.norm(BL-BR)
def corner_perp(P,base):
    r=ray(*P); s=(base@e)/(r@e); return s*r
TR=corner_perp(TRp,BR); TL=corner_perp(TLp,BL)
# slope plane
P0=(BL+BR+TL+TR)/4
ns=np.cross(TR-BR,BL-BR); ns/=np.linalg.norm(ns)
if ns@(-P0)<0: ns=-ns   # normal toward camera
up_dir=(TR-BR)/np.linalg.norm(TR-BR)  # along incline, upward
def on_slope(u,v,h=0.0):
    d=ray(u,v); s=(ns@P0+h)/(ns@d); return s*d
def slope_coords(X):
    """(across, along-incline-from-bottom-edge, height) in cm"""
    rel=X-BR; return np.array([rel@e, rel@up_dir, rel@ns])*100
if __name__=='__main__':
    print('slope normal',np.round(ns,3),'view angle to slope normal at centre: %.1f deg'%np.degrees(np.arccos(abs(ns@(P0/np.linalg.norm(P0))))))
    for nm,X in dict(BL=BL,BR=BR,TL=TL,TR=TR).items(): print(nm,np.round(slope_coords(X),1),'range %.3f'%np.linalg.norm(X))
