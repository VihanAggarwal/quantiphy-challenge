import cv2, numpy as np
from geo import *
YH=349.5
K=np.array([[F,0,CX],[0,F,CY],[0,0,1.]])
nT=K.T@np.array([0,1,-YH]); nT/=np.linalg.norm(nT)
def onplane(u,v,hh):
    d=np.array([(u-CX)/F,(v-CY)/F,1.]); return d*hh/(nT@d)
# camera height from board bottom (24 cm ruler) and table front (60.3 ruler)
zbb=0.24*F/185.5; zf=0.603*F/643.4
hb=nT@(np.array([(584.5-CX)/F,(481.7-CY)/F,1.])*zbb); hf=nT@(np.array([(600-CX)/F,(530.0-CY)/F,1.])*zf)
print('h from board bottom %.4f, from table front %.4f'%(hb,hf))
def edges_rest(fr):
    im=cv2.imread(f'frames/{fr}.png').astype(float); v=im.max(2)
    out=[]
    for x in range(500,640,10):
        p=v[470:520,x-1:x+2].mean(1)
        # back edge: first drop from board white (~250) to cover (~217): threshold 233
        k=np.nonzero(p<233)[0][0]; yb=470+k-1+(p[k-1]-233)/(p[k-1]-p[k])
        # front edge of cover: first drop below 160 after back edge (dark line)
        k2=np.nonzero(p[k+3:]<160)[0][0]+k+3; yf=470+k2-1+(p[k2-1]-160)/(p[k2-1]-p[k2])
        # bottom contact: min of profile below yf+8
        k3=np.argmin(p[k2+8:])+k2+8; ybot=470+k3
        out.append((x,yb,yf,ybot))
    return np.array(out)
for fr in ['o40','o44','o48','s44','x44']:
    E=edges_rest(fr)
    for h in [hb,hf]:
        H=0.0146
        W=[np.linalg.norm(onplane(x,yb,h-H)-onplane(x,yf,h-H))*100 for x,yb,yf,_ in E]
        zf_=[onplane(x,yf,h-H)[2] for x,yb,yf,_ in E]
        zb_=[onplane(x,ybot,h)[2] for x,yb,yf,ybot in E]
        print(fr,'h=%.4f'%h,'back',np.round(E[:,1],1).tolist()[:6],'front',np.round(E[:,2],1).tolist()[:6],'W med %.2f (min %.2f max %.2f)'%(np.median(W),min(W),max(W)),'z_front_cover %.3f z_bottom %.3f'%(np.median(zf_),np.median(zb_)))
