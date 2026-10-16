import numpy as np, cv2
from common import *
exec(open('objrect.py').read().split('for f,(p,r)')[0])
bag=comp_at(837,329)
cs,_=cv2.findContours(bag,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); c=max(cs,key=cv2.contourArea).reshape(-1,2).astype(float)
ys,xs=np.nonzero(bag); allpix=np.c_[xs,ys].astype(float)
for f,(p,r) in {700:(39.34,8.43),711:(38.93,8.53),722:(38.50,8.66)}.items():
    nm=normal(p,r); e1,e2=floor_basis(nm)
    to2=lambda uv: (lambda P: np.c_[P@e1,P@e2])(backproj(np.atleast_2d(np.array(uv,float)),nm,1.0,f))
    Lc,Tc,Rc,Bc=to2([(771,313),(820,295.5),(895.5,344.5),(842,371.5)])
    # opening edge direction (T->R) and bottom edge (L->B)
    u=(Rc-Tc)+(Bc-Lc); u/=np.linalg.norm(u); v=np.array([-u[1],u[0]])
    Q=to2(allpix)
    pv=Q@v; pu=Q@u
    # bottom edge position along v
    bot=np.mean([Lc@v,Bc@v]); top=np.mean([Tc@v,Rc@v])
    if top<bot: v=-v; pv=-pv; bot=-bot; top=-top
    print(f,'body height %.4f  extent incl handles along v: %.4f (min %.4f max %.4f)  width extent along u %.4f'%(top-bot,pv.max()-bot,pv.min()-bot,pv.max()-bot,pu.max()-pu.min()))
