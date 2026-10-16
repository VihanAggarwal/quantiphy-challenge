import numpy as np
from geo import *
from slope3d import board_model, hit_plane
from bookmask import cover_mask
from rest import onplane
H=0.0146; h=0.170
# rest top-face centre: image centre of top face. back edge ~482, front ~497 at x~566; centre in 3D = mid of back/front points
back=onplane(566,482.3,h-H); front=onplane(566,497.0,h-H); Prest=(back+front)/2
pix_rest=(566,489.0)
print('rest top-face centre geometric',Prest.round(4),'range %.4f'%np.linalg.norm(Prest))
for route in ['ruler','stated']:
    M=board_model(route); p0=M['B']+M['n']*H
    for fr in [23,24]:
        m=cover_mask(f'x{fr:02d}'); ys,xs=np.nonzero(m)
        P=hit_plane(p0,M['n'],xs.mean(),ys.mean())
        d_geo=np.linalg.norm(P-Prest)*100
        d_lab=np.linalg.norm(P-bp(*pix_rest,0.851))*100
        print(route,'f%d'%fr,'P',P.round(4),'range %.4f'%np.linalg.norm(P),' disp to geometric rest %.1f  to stated-range rest %.1f'%(d_geo,d_lab))
# path along slope + table as check
M=board_model('ruler'); 
