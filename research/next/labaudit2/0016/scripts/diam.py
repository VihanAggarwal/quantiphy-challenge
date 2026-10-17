# Ball diameter routes. (1) label-style: two edge clicks at video 36 back-projected at the stated 1.402;
# (2) sphere model with the stated surface range (centre range = 1.402 + R) and the matte/edge tangential size;
# (3) |g|=9.8 scale of the size-route 3D track (fit3d.py): D = 0.18*k.
import numpy as np
f=711.; pp=np.array([640.,360.])
def ray(p): v=np.array([p[0]-pp[0],p[1]-pp[1],f]); return v/np.linalg.norm(v)
c=np.array([812.2,77.2])
print('(1) label-style edge clicks at range 1.402 (video 36):')
for w,dirn in [(92.9,'perp-to-motion (matte 4sd)'),(89.1,'perp (matte pct)'),(98,'vertical bbox'),(118,'horizontal bbox incl. blur'),(105,'mean of axes')]:
    # perpendicular to motion direction (-25 deg) => direction ~ (sin25, cos25)
    if 'perp' in dirn: u=np.array([np.sin(np.radians(25)),np.cos(np.radians(25))])
    elif 'vertical' in dirn: u=np.array([0,1.])
    elif 'horizontal' in dirn: u=np.array([1.,0])
    else: u=np.array([0.7071,0.7071])
    Q1=1.402*ray(c-u*w/2); Q2=1.402*ray(c+u*w/2)
    print('   %-30s %5.1f px -> %.1f cm'%(dirn,w,100*np.linalg.norm(Q2-Q1)))
print('(2) sphere model, stated surface range 1.402 at video 36 (c38) or c37-interpolated size:')
th=np.arctan(np.hypot(*(c-pp))/f)
for b2,lab in [(92.9,'matte perp extent (model-converted below)'),]:
    pass
# from fit3d: matte d_centre(D=.18) at video 36 = 1.572 => D such that centre = 1.402+D/2 : D = 0.18*(1.402+D/2)/1.572
for dc,lab in [(1.572,'video36 matte (c38)'),(1.512,'c37 from size-route quadratic')]:
    D=0.18*1.402/(dc-0.09)   # solve D/0.18 = (1.402 + D/2)/dc  -> D = 0.18*1.402/(dc - 0.09)
    print('   %-32s D=%.1f cm'%(lab,100*D))
print('(3) |g|=9.8 scaling of size-route track: D = 0.18*1.071 = %.1f (36-40) / 0.18*1.063 = %.1f (33-40)'%(18*1.071,18*1.063))
