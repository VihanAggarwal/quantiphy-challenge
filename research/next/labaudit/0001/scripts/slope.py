import numpy as np
f=711.; cx=640.; cy=360.
def ray(u,v):
    d=np.array([(u-cx)/f,(v-cy)/f,1.]); return d/np.linalg.norm(d)
def bp(u,v,r): return r*ray(u,v)
# edges from mask fit (frame 48)
ys=np.arange(358,490,4)
Lx=np.array([569,568,567,566,565,564,563,562,561,560,559,559,558,557,556,555,554,553,552,551,550,549,548,547,546,546,545,544,543,542,541,540,539][:len(ys)])
Rx=np.array([721,722,722,723,723,723,724,724,725,725,725,726,726,727,727,727,728,728,727,729,729,730,731,731,731,732,732,732,733,733,734,734,735][:len(ys)])
pl=np.polyfit(ys,Lx,1); pr=np.polyfit(ys,Rx,1)
print('left dx/dy',pl,'right',pr)
# VP of side edges: x=a*y+b
yv=(pr[1]-pl[1])/(pl[0]-pr[0]); xv=pl[0]*yv+pl[1]
print('VP side', xv,yv)
d1=np.array([(xv-cx)/f,(yv-cy)/f,1.]); d1/=np.linalg.norm(d1)
print('dir up-slope',d1, 'angle to cam horizontal (deg)', np.degrees(np.arcsin(-d1[1])))
topy=353.5; boty=493.0
for f_ in [700,711,720]:
    f=f_
    # mid points
    tx=(np.polyval(pl,topy)+np.polyval(pr,topy))/2; bx=(np.polyval(pl,boty)+np.polyval(pr,boty))/2
    F=bp(tx,topy,1.136); N=bp(bx,boty,0.884)
    print('f',f,'top mid',tx,'bot mid',bx,'route1 |F-N| =',np.linalg.norm(F-N))
    d1=np.array([(xv-cx)/f,(yv-cy)/f,1.]); d1/=np.linalg.norm(d1)
    # route2: from N along d1, intersect with ray through top mid (least squares)
    rt=ray(tx,topy)
    A=np.stack([d1,-rt],1); s,t=np.linalg.lstsq(A,-N,rcond=None)[0]
    print('  route2 from N along VP dir: L=',s,' implied far range', t)
    rb=ray(bx,boty)
    A=np.stack([-d1,-rb],1); s2,t2=np.linalg.lstsq(A,-F,rcond=None)[0]
    print('  route2b from F along VP dir: L=',s2,' implied near range', t2)
    # widths
    for (y,r) in [(topy,1.136),(boty,0.884)]:
        a=bp(np.polyval(pl,y),y,r); b=bp(np.polyval(pr,y),y,r)
        print('  width at y',y, np.linalg.norm(a-b))
f=711.
