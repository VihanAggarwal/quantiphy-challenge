import numpy as np
f=711.0; cx=640.0; cy=360.0
def ray(u,v):
    d=np.array([(u-cx)/f,(v-cy)/f,1.0]); return d/np.linalg.norm(d)
pts={'book_top':(2.082*ray(666,618),0.02),'ball_centre':((2.925+0.116)*ray(986.5,369.3),0.116),'cup_click':(2.516*ray(564,424),0.11)}
def up(p,r):
    # pitch p down, roll r: start with up=(0,-1,0) in level cam, apply pitch then roll
    u=np.array([0,-np.cos(p),-np.sin(p)])
    c,s=np.cos(r),np.sin(r)
    R=np.array([[c,-s,0],[s,c,0],[0,0,1]])
    return R@u
for name,(p,r) in {'tof roll0':(35.6,0),'VP horizon':(38.9,10.3),'nadir':(33.3,11.8),'roll -10':(35.6,-10)}.items():
    U=up(np.radians(p),np.radians(r))
    # fit h by LS to book & ball
    hs=[hh-U@P for P,hh in [pts['book_top'],pts['ball_centre']]]
    h=np.mean(hs)
    print('%-11s pitch %.1f roll %.1f up %s  h(book)=%.3f h(ball)=%.3f -> cup click height %.3f'%(name,p,r,U.round(3),hs[0],hs[1],np.mean(hs)+U@pts['cup_click'][0]))

print('--- 3-point plane fits (book, ball, cup click) and resulting bin displacement')
T=np.load('bin_track_x.npy')
def solve3(hb,hball,hcup):
    # unknowns: up vector U (unit) and h: h + U.P = height. Solve linear for w=(U,h) with |U|=1 via scaling trick
    P=np.array([pts['book_top'][0],pts['ball_centre'][0],pts['cup_click'][0]])
    H=np.array([hb,hball,hcup])
    # h + U.P_i = H_i ; unknowns U (3), h (1): 3 eq + |U|=1 -> param by h: U = P^-1 (H - h)
    Pi=np.linalg.inv(P)
    a=Pi@H; b=Pi@np.ones(3)
    # |a - h b|^2 = 1
    A=b@b; B=-2*a@b; C=a@a-1
    disc=B*B-4*A*C
    sols=[(-B+s*np.sqrt(disc))/(2*A) for s in (1,-1)] if disc>=0 else []
    out=[]
    for h in sols:
        U=a-h*b
        if U[1]<0 and h>0: out.append((h,U))
    return out
for hb in [0.01,0.02,0.03]:
  for hcup in [0.08,0.10,0.12,0.14]:
    for h,U in solve3(hb,0.116,hcup):
        p=np.degrees(np.arcsin(-U[2])); r=np.degrees(np.arctan2(U[0],-U[1]))
        def C_at(u,v,hc):
            d=ray(u,v); t=(hc-h)/(U@d); return t*d
        bin10=C_at(T[10,1],T[10,2],0.125); bin34=C_at(T[34,1],T[34,2],0.125)
        print('book %.2f cup %.2f -> h %.3f pitch %.1f roll %.1f | bin range@t0.4 (h=.125) %.3f vs ToF 2.730 | disp %.3f m'%(hb,hcup,h,p,r,np.linalg.norm(bin10),np.linalg.norm(bin34-bin10)))
