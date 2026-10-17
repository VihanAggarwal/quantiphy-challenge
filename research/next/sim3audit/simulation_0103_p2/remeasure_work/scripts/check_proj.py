import numpy as np, cv2
from reg import *
from vio import frame
Q=np.load(W+'c2_footprint_boatframe.npy')
for n,v,k in [('C1','0027_segmented',30),('K22','0022_segmented',0)]:
    F=frame_of(n)
    uv,z=project(F,Q)
    print(n,'proj footprint x %.0f..%.0f  y %.0f..%.0f  depth %.1f..%.1f'%(uv[:,0].min(),uv[:,0].max(),uv[:,1].min(),uv[:,1].max(),z.min(),z.max()))
    img=frame(v,k)
    pts=np.round(uv).astype(np.int32)
    cv2.polylines(img,[pts],True,(0,0,255),2)
    cv2.imwrite(W+'frames/proj_c2fp_on_%s.png'%n,img)
