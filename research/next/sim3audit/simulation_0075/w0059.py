# Road (curb-to-curb) width in simulation_0059, scale from the stated bike speed 5.33 m/s.
# Curb lines (road-level edge of the curb face) fitted by column scanning of the grey road mask on frame 0 (curbs2.py):
#   left  v = -0.266013 u + 1042.227 (507 px, rms 1.0)   right v = 0.388278 u + 217.543 (546 px, rms 1.1)
#   -> main-road VP (1260.4, 706.9) = horizon row; camera yaw to the road ~4.8 deg.
# Bike: head template track (bike0059.py) frames 24-36 -> 11.916 px/frame lateral; tyre contact row 806.5 (frames 26-30).
import numpy as np
a1,b1=-0.266013,1042.227; a2,b2=0.388278,217.543
vb=806.5
uL=(vb-b1)/a1; uR=(vb-b2)/a2; du=uR-uL
pxs=(1182.99-1040.00)/12
f_est=2167.; psi=np.arctan((1260.4-1080)/f_est)
x_over_z=(1133-1080)/f_est
s=5.33/24/pxs*(np.cos(psi)+x_over_z*np.sin(psi))   # m per px at the bike's depth (motion along the cross street)
W=du*s*np.cos(psi)
print('uL %.1f uR %.1f du %.1f px; scale %.5f m/px; W = %.2f m'%(uL,uR,du,s,W))
for dv in (-2,2):
    v=vb+dv; d=(v-b2)/a2-(v-b1)/a1; print(' contact row %+d px -> W %.2f'%(dv,d*s*np.cos(psi)))
