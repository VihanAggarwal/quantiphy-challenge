import numpy as np, cv2
from common import frames
from tmpl import track
v='simulation_0285'
fr=frames(v, gray=True)
f0=30
# name: (x,y) center at f0, half-size
feats={'near_pod_tip':(1122,423,8),'far_pod_tip':(1138,452,8),'tailfin_top':(1765,322,10),'lower_tailfin_bot':(1780,470,10),
       'gear_wheel':(1227,510,9),'near_pod_rear':(1575,495,10),'far_pod_rear':(1545,517,9),'black_fin_top':(1420,315,12),'fan_ellipse':(1300,412,14)}
for name,(x,y,h) in feats.items():
    box=(x-h,y-h,x+h+1,y+h+1)
    ks=[];dxs=[];dys=[];q=[]
    for k in [-16,-12,-8,-4,4,8,12,16]:
        dx,dy,mv=track(fr,f0,box,f0+k,-42.5*k,search=25)
        ks.append(k);dxs.append(dx);dys.append(dy);q.append(mv)
    s=np.polyfit(ks,dxs,1)[0]; res=np.std(np.array(dxs)-np.polyval(np.polyfit(ks,dxs,1),ks))
    print('%-18s y=%d s=%.2f px/fr  resid=%.2f  dy-range=%.2f  minq=%.2f'%(name,y,-s,res,np.ptp(dys),min(q)))
