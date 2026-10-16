import numpy as np
from common import *
exec(open('wbplane.py').read().split('frames=[n')[0])
vp=np.array([467,1363.0]); d=np.r_[(vp-[CX,CY])/F,1]; nm_seam=d/np.linalg.norm(d)
for name,nm in [('board-normal',normal(38.93,8.53)),('seam-normal',nm_seam)]:
    dd=np.r_[(np.array([837.4,329.2])-[CX,CY])/F,1]; hb=3.307*(dd/np.linalg.norm(dd))@nm
    dd=np.r_[(np.array([704.8,409.8])-[CX,CY])/F,1]; hw=2.815*(dd/np.linalg.norm(dd))@nm
    for k,c in {'manual':[(771,313),(818,296),(895,344),(842,371)],'manual_b':[(770,314),(822,295),(896,345),(842,372)]}.items():
        s,cs,P=geom(np.array(c,float),nm,1.0)
        H=(s[0]+s[2])/2; Wd=(s[1]+s[3])/2
        print(name,k,'body height/h %.4f width/h %.4f | h(bag ToF)=%.3f -> %.1f x %.1f cm | h(board ToF)=%.3f -> %.1f x %.1f cm'%(H,Wd,hb,H*hb*100,Wd*hb*100,hw,H*hw*100,Wd*hw*100))
