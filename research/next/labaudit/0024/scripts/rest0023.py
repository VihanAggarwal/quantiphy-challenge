import numpy as np
F=711.;CX=640.;CY=360.
p=np.load('/home/user/quantiphy-challenge/research/next/labaudit/0024/scripts/pose0023_60.npy'); R=p[:9].reshape(3,3); T=p[9:]
n=R[:,2]
if n@(-T)<0: n=-n
def ray(u,v):
    d=np.array([(u-CX)/F,(v-CY)/F,1.]); return d/np.linalg.norm(d)
def on_plane(u,v,h=0.):
    d=ray(u,v); s=(h+n@T)/(n@d); return s*d
print('cam height %.3f'%abs(n@T))
for x in [540,580,600,620]:
    for vb,vf,vs in [(487.5,496,507),(488,497,507.5),(487,495.5,506.5)]:
        A=on_plane(x,vb,0.0146); B=on_plane(x,vf,0.0146); C=on_plane(x,vs,0.0)
        print(x,vb,vf,vs,'top face depth-extent %.1f cm, silhouette (back top edge -> bottom line) %.1f cm, range at bottom %.3f'%(np.linalg.norm(A-B)*100,np.linalg.norm((A-n*0.0146)-C)*100,np.linalg.norm(C)))
# long side: teal 178 px across at stated 0.851
