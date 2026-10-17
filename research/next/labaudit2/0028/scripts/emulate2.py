import json, numpy as np
exec(open('/home/user/quantiphy-challenge/research/next/labaudit2/0028/scripts/emulate.py').read().split("print('=== v(1.3)")[0])
# robustness of v(1.3) choice to ToF noise and approach speed
print('=== v(1.3) robustness (x render, n13=33) ===')
V='captured_0028x'; u1,u2=uv(V,33),uv(V,34)
for sz in (0.01,0.02,0.03,0.04):
  for zdot in (0.45,0.6,0.75,0.9):
    uu1=u1+rng.normal(0,SPX,(N,2)); uu2=u2+rng.normal(0,SPX,(N,2))
    r2=1.4115-rng.normal(0,sz,N)-zdot*DT+rng.normal(0,sz,N)
    L=np.linalg.norm(unit(uu2)*r2[:,None]-unit(uu1)*1.4115,axis=1)/DT*100
    b,s=best(L)
    print(f'sz={sz:.2f} zdot={zdot:.2f}: median {np.median(L):5.1f} best {b:5.1f}  score 93.4={mra(93.375,L).mean():.3f} 71.9={mra(71.925,L).mean():.3f} 70={mra(70.0,L).mean():.3f} 60={mra(60.0,L).mean():.3f}')
print('=== v(1.0): forward difference n=25 (video 24) -> n=26 (video 25); stated 1.805 at n=25 ===')
for V in ['captured_0028x','captured_0028']:
    u1,u2=uv(V,25),uv(V,26)
    for R2 in (1.805,1.75,1.70,1.65,1.60):
        print(f'  {V[-5:]} ToF(n=26)={R2:.3f}: label {np.linalg.norm(P(u2,R2)-P(u1,1.805))/DT*100:6.1f}')
    # physical: true range ~1.60-1.66 at n=25, zdot 0.5-1.0, central-difference vertical velocity
    for Rt in (1.60,1.65):
      for zd in (0.5,1.0):
        uc=(uv(V,26)-uv(V,24))/2  # px per frame, central
        v_img=np.linalg.norm(uc)*Rt/F*25
        print(f'  physical R={Rt} zdot={zd}: central {np.hypot(v_img,zd)*100:5.0f}  forward(true ranges) {np.linalg.norm(P(u2,Rt-zd*DT)-P(u1,Rt))/DT*100:5.0f}')
print('=== distance 1.1 -> 1.3 s and height (stated depths at the 1.1 and 1.3 frames) ===')
for V in ['captured_0028x','captured_0028']:
  for n11 in (27,28):
    for n13 in (32,33):
        A=P(uv(V,n11),1.557); B=P(uv(V,n13),1.4115); d=B-A
        # path: intermediate frames with linearly interpolated ToF (+ noise MC)
        ns=list(range(n11,n13+1)); R=np.interp(ns,[n11,n13],[1.557,1.4115])
        U=np.array([uv(V,n) for n in ns])
        pts=unit(U)*R[:,None]; path=np.sum(np.linalg.norm(np.diff(pts,axis=0),axis=1))
        Lp=[]
        for it in range(4000):
            Rn=R+np.r_[0,rng.normal(0,SZ,len(ns)-2),0]; Un=U+np.r_[[[0,0]],rng.normal(0,SPX,(len(ns)-2,2)),[[0,0]]]
            q=unit(Un)*Rn[:,None]; Lp.append(np.sum(np.linalg.norm(np.diff(q,axis=0),axis=1)))
        Lp=np.array(Lp)*100
        print(f'  {V[-5:]} n11={n11}(video {VID[n11]}) n13={n13}(video {VID[n13]}): straight {np.linalg.norm(d)*100:5.1f}  camera-vertical {-d[1]*100:5.1f}  radial-ish dz {d[2]*100:5.1f}  path(smooth) {path*100:5.1f}  path MC median {np.median(Lp):5.1f} best {best(Lp)[0]:5.1f}')
