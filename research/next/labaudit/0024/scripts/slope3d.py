import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0024/scripts')
from geo import *
def L(a,b): return np.linalg.norm(a-b)*100
BLp=(609,467); BRp=(705,493); TLp=(751,360); TRp=(857,361)
BL=on_plane(*BLp); BR=on_plane(*BRp)
print('bottom edge on table: %.1f cm, ranges BL %.3f BR %.3f'%(L(BL,BR),np.linalg.norm(BL),np.linalg.norm(BR)))
e=(BL-BR)/np.linalg.norm(BL-BR)
def corner_perp(P,base,up):
    r=ray(*P); s=(base@e)/(r@e)  # (s r - base).e=0
    return s*r
TR=corner_perp(TRp,BR,None); TL=corner_perp(TLp,BL,None)
print('TR range %.3f TL range %.3f'%(np.linalg.norm(TR),np.linalg.norm(TL)))
print('side lengths: right %.1f left %.1f ; top edge %.1f'%(L(TR,BR),L(TL,BL),L(TR,TL)))
print('heights above table: TR %.1f TL %.1f cm'%((n@(TR-T))*100,(n@(TL-T))*100))
mid_top=(TR+TL)/2; mid_bot=(BR+BL)/2
print('mid ranges top %.3f bottom %.3f ; mid-to-mid %.1f'%(np.linalg.norm(mid_top),np.linalg.norm(mid_bot),L(mid_top,mid_bot)))
ang=np.degrees(np.arcsin((n@(TR-BR))/np.linalg.norm(TR-BR))); print('incline angle %.1f deg'%ang)
# stated: slope far 1.243, near 0.990 -> where on the slope do those ranges lie?
