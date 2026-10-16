import numpy as np

f=711.0; cx=640.0; cy=360.0
def ray(u,v):
    d=np.array([(u-cx)/f,(v-cy)/f,1.0]); return d/np.linalg.norm(d)
book=2.082*ray(666,618)
ballc=(2.925+0.116)*ray(986.5,369.3)
cupc=2.516*ray(564,424)
print('book',book.round(3),'ballc',ballc.round(3),'cup click',cupc.round(3))
# up vector u=(0,-cos p,-sin p) (roll 0). height(P)=h+u.P
def heights(p,h,P): u=np.array([0,-np.cos(p),-np.sin(p)]); return h+u@P
for tb in [0.01,0.02,0.03]:
    ps=np.radians(np.linspace(0,80,80001))
    g=-np.cos(ps)*(book[1]-ballc[1])-np.sin(ps)*(book[2]-ballc[2])-(tb-0.116)
    i=np.argmin(np.abs(g)); p=ps[i]
    h=tb+np.cos(p)*book[1]+np.sin(p)*book[2]
    print('book top %.2f -> pitch %.1f deg, cam height %.3f m; cup click height %.3f; cup-ball horiz' % (tb,np.degrees(p),h,heights(p,h,cupc)))

print('--- rim centre depth')
p=np.radians(35.6); h=1.735
u=np.array([0,-np.cos(p),-np.sin(p)])
r_cup=cupc/np.linalg.norm(cupc)
hor=r_cup-(r_cup@u)*u; hor/=np.linalg.norm(hor)
for H in [0.14,0.15,0.16]:
  for r in [0.040,0.045]:
    click_h=heights(p,h,cupc)
    rim=cupc+r*hor+(H-click_h)*u
    proj=(f*rim[0]/rim[2]+cx, f*rim[1]/rim[2]+cy)
    for w in [25.5,26.0]:
        print('H %.2f r %.3f rimZ %.3f proj rim centre (%.1f,%.1f) w %.1f -> D %.2f cm'%(H,r,rim[2],proj[0],proj[1],w,100*w*rim[2]/f))
# also: bottom centre on floor
for r in [0.035]:
    bot=cupc+r*hor+(0-heights(p,h,cupc))*u
    print('bottom centre proj',(f*bot[0]/bot[2]+cx, f*bot[1]/bot[2]+cy),'Z',bot[2])

print('--- route: cup base on floor plane (no cup ToF)')
for tb,p_deg,h in [(0.01,35.0,1.713),(0.02,35.6,1.735),(0.03,36.1,1.757)]:
    p=np.radians(p_deg); u=np.array([0,-np.cos(p),-np.sin(p)])
    for by in [441,442,444]:
        d=ray(563.5,by)
        # h + u.(t d) = 0
        t=-h/(u@d); B=t*d
        for H in [0.14,0.15,0.16]:
            R=B+H*u  # rim centre: up by H (u is up)
            print('tb %.2f base y %d -> base range %.3f Z %.3f; rim(H=%.2f) Z %.3f proj y %.1f; D(25.8px) %.2f cm'%(tb,by,t,B[2],H,R[2],f*R[1]/R[2]+cy,100*25.8*R[2]/f))
print('--- consistency: predicted ToF range of click (front surface at height hc) from floor-route base')
p=np.radians(35.6); h=1.735; u=np.array([0,-np.cos(p),-np.sin(p)])
d=ray(563.5,442); B=(-h/(u@d))*d
hor=B-(B@u)*u; hor/=np.linalg.norm(hor)
for hc in [0.08,0.10,0.12]:
    for r in [0.04,0.045]:
        P=B-r*hor+hc*u
        print('hc %.2f r %.3f -> front pt range %.3f pix (%.1f,%.1f)'%(hc,r,np.linalg.norm(P),f*P[0]/P[2]+cx,f*P[1]/P[2]+cy))
