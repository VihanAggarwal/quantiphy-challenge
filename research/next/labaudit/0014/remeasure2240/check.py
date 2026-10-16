import numpy as np
f=711.0; cx,cy=640.,360.
def ray(u,v):
    r=np.array([(u-cx)/f,(v-cy)/f,1.]); return r/np.linalg.norm(r)
Pt,Pb,e,h,n=np.load('model.npy')
r=0.0325; P0=Pb+r*n
def b3(u,v):
    R=ray(u,v); return (n@P0)/(n@R)*R
# pooled x/s track
tr={0:(544.2,297.6),8:(542.7,299.0),9:(543.0,300.3),10:(543.2,304.2),11:(544.0,309.0),12:(545.8,329.2),13:(546.6,340.8),14:(547.6,354.0),15:(548.3,370.0),16:(549.5,389.2)}
P={k:b3(*v) for k,v in tr.items()}
for k in sorted(P): print(k,'range %.4f'%np.linalg.norm(P[k]),'s %.2f'%(100*(P[k]-P[0])@e))
ks=sorted(P)
for a,b in zip(ks[:-1],ks[1:]):
    d=np.linalg.norm(P[b]-P[a]); print('%d->%d %.2f cm'%(a,b,100*d))
# label-style displacement 0->0.6 using stated ranges
for v06 in [354.0,360.4,370.0]:
    u06=547.6+(v06-354)/16*0.7
    A=1.818*ray(*tr[0]); B=1.7288*ray(u06,v06)
    print('label-style disp with ball@0.6 at y=%.1f: %.2f cm'%(v06,100*np.linalg.norm(B-A)))
# where along track does centre-range (or surface-range) equal 1.7288?
for off in [0,r]:
    ys=np.linspace(330,390,601); rr=np.array([np.linalg.norm(b3(547+(y-340)*0.05,y))-off for y in ys])
    print('offset %.4f -> y where range=1.7288: %.1f'%(off,ys[np.argmin(abs(rr-1.7288))]))
