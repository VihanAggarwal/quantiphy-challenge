import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0024/scripts')
from slopeplane import *
import geo
def bp(u,v,r): return ray(u,v)*r
start=on_slope(783.4,368.7,0.0073)          # rest at top (teal centroid)
foot_s=on_slope(617.7,470.2,0.0073)          # crossing the foot on slope plane (n32)
end=geo.on_plane(572.1,474.3,0.0073)          # rest on table
# foot point on the table plane: slope bottom edge midpoint region; use the centroid at n32 projected to the table plane too
foot_t=geo.on_plane(617.7,470.2,0.0073)
print('start range %.3f end range %.3f'%(np.linalg.norm(start),np.linalg.norm(end)))
print('slope leg %.1f cm, table leg (from slope foot pt) %.1f, polyline %.1f, straight %.1f'%(
    np.linalg.norm(start-foot_s)*100,np.linalg.norm(foot_s-end)*100,(np.linalg.norm(start-foot_s)+np.linalg.norm(foot_s-end))*100,np.linalg.norm(start-end)*100))
print('foot pts slope-plane vs table-plane gap %.1f cm'%(np.linalg.norm(foot_s-foot_t)*100))
# label-style: start/end clicks with depths? use the stated-depth line: 1.0 s 1.0685 at (749.7,393), 1.2 s 0.977 at (669.8,448.5)
A=bp(749.7,393,1.0685); B=bp(669.8,448.5,0.977)
print('stated-depth displacement 1.0->1.2 s: %.1f cm ; model: %.1f cm'%(np.linalg.norm(A-B)*100,np.linalg.norm(on_slope(749.7,393,0.0073)-on_slope(669.8,448.5,0.0073))*100))
