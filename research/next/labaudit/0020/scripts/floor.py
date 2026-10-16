import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0020/scripts')
import numpy as np
from geo import bp
F=711.; CX=640.; CY=360.
down=np.array([(895-CX)/F,(1600-CY)/F,1.]); down/=np.linalg.norm(down)
def ray(u,v): r=np.array([(u-CX)/F,(v-CY)/F,1.]); return r/np.linalg.norm(r)
def foot_under(P,uf,vf):
    # find s: P + s*down projects to (uf,vf); solve lstsq over s and lambda: P + s*down = lam*ray
    r=ray(uf,vf); A=np.c_[down,-r]; x,*_=np.linalg.lstsq(A,-P,rcond=None); s,lam=x
    Q=P+s*down; return Q, s, np.linalg.norm(Q-lam*r)
for far_click in [(705,115),(705,80),(710,150)]:
    Pf=bp(*far_click,3.237)
    Qf,s,err=foot_under(Pf,733,268)
    h=Qf@down   # camera height above floor along down
    # near foot on floor: ray(360,705) intersect plane {X: X.down = h}
    rn=ray(360,705); Qn=rn*h/(rn@down)
    # horizontal distance between feet
    dvec=Qf-Qn; dh=dvec-(dvec@down)*down
    print('far click',far_click,'torso height above floor %.2f m'%s,'cam height %.2f m'%h,'near foot range %.2f'%np.linalg.norm(Qn),'feet horiz dist %.1f cm'%(np.linalg.norm(dh)*100))
    # near person's vertical axis from near torso click at range 1.58
    for nc in [(165,450),(150,400),(200,500)]:
        Pn=bp(*nc,1.58); hn=h-Pn@down
        dv=Pf-Pn; dvh=dv-(dv@down)*down
        print('    near click',nc,'height above floor %.2f m'%hn,' horiz dist torso-torso %.1f  3D %.1f'%(np.linalg.norm(dvh)*100,np.linalg.norm(dv)*100))
