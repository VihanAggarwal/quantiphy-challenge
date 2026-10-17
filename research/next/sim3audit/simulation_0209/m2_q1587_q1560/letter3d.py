import numpy as np
from cam import *
vA,vB,vV=np.load('vps.npy')
for f,thd,h in [(2652,13.38,1.25),(2620,13.3,1.25),(2690,13.5,1.25),(2652,13.38,1.235),(2652,13.38,1.265)]:
    th=np.radians(thd)
    # desk axes directions from VPs
    dA=to_world(ray(*vA[:2],f),th); dB=to_world(ray(*vB[:2],f),th)
    dA[2]=0; dB[2]=0; dA/=np.linalg.norm(dA); dB/=np.linalg.norm(dB)
    yawA=np.degrees(np.arctan2(dA[1],dA[0])); yawB=np.degrees(np.arctan2(dB[1],dB[0]))
    BL=on_plane(1315.78,624.35,h,f,th); FL=on_plane(1362.99,643.13,h,f,th)
    Fv=on_plane(1410,634.9,h,f,th)  # last visible point on front edge
    Bv=on_plane(1353,619.2,h,f,th)  # last visible on back edge (barrel)
    left=np.linalg.norm(BL-FL)
    e1=(FL-BL)/left; e2=(Fv-FL)/np.linalg.norm(Fv-FL)
    ang=np.degrees(np.arccos(abs(e1@e2)))
    print(f'f={f} th={thd} h={h} yawA={yawA:.1f} yawB={yawB:.1f} A.B={np.degrees(np.arccos(abs(dA@dB))):.1f}')
    print(f'  left(depth) side={left:.4f}  front visible={np.linalg.norm(Fv-FL):.4f} back visible={np.linalg.norm(Bv-BL):.4f} corner angle={ang:.1f}')
    print(f'  left dir yaw={np.degrees(np.arctan2(e1[1],e1[0])):.1f}  front dir yaw={np.degrees(np.arctan2(e2[1],e2[0])):.1f}')
    print('  BL',BL.round(3),'FL',FL.round(3),'range FL',np.linalg.norm(FL).round(3))
