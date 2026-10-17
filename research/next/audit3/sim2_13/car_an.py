import json, numpy as np, sys
c=sys.argv[1]
R=json.load(open(f'research/next/audit3/sim2_13/cartrack_{c}_25.json'))
N=len(R)
ybike={'0085':(340,430),'0086':(450,500),'0087':(395,465)}[c]
car=[];bike=[]
for i,objs in enumerate(R):
    cs=[o for o in objs if o['area']>15000]
    car.append(max(cs,key=lambda o:o['area']) if cs else None)
    bs=[o for o in objs if ybike[0]<=o['cy']<=ybike[1] and 800<o['area']<15000]
    bike.append(max(bs,key=lambda o:o['area']) if bs else None)
# car front edge x0 (moving left)
fx=np.array([car[i]['x0'] if car[i] else np.nan for i in range(N)],float)
rx=np.array([car[i]['x1'] if car[i] else np.nan for i in range(N)],float)
t=np.arange(N)
def qfit(lo,hi,arr):
    m=(t>=lo)&(t<=hi)&np.isfinite(arr)
    p=np.polyfit(t[m],arr[m],2); r=arr[m]-np.polyval(p,t[m])
    return p, np.sqrt(np.mean(r**2))
for lo,hi in [(2,24),(2,35),(10,35),(24,45),(36,60)]:
    p,r=qfit(lo,hi,fx)
    print(f'front quad {lo}-{hi}: a_px={-2*p[0]:.4f} px/f2 (signed {2*p[0]:.4f}) vertex={-p[1]/(2*p[0]):.2f} rms={r:.2f}')
# local accel from front-edge second differences, smoothed
v=np.diff(fx)
print('front-edge v per frame (backward):', np.round(v,1).tolist())
# bike: full-visible frames
bc=[]; bl=[]
for i in range(N):
    b=bike[i]
    if b and b['x0']>2 and b['x1']<1917: bc.append((i,(b['x0']+b['x1'])/2,b['cy'])); bl.append(b['x1']-b['x0']+1)
bc=np.array(bc)
pb=np.polyfit(bc[:,0],bc[:,1],1); rb=bc[:,1]-np.polyval(pb,bc[:,0])
print(f'bike v={pb[0]:.3f} px/f rms={np.sqrt(np.mean(rb**2)):.2f}; bike len px median={np.median(bl):.1f} ({np.percentile(bl,10):.0f}-{np.percentile(bl,90):.0f}); bike y={np.median(bc[:,2]):.1f}')
p,_=qfit(2,24 if c!='0087' else 24,fx)
a1=-2*p[0]
sA=4.03/(a1*576); sB=5.07/(abs(pb[0])*24)
print(f'scale A (car acc early)={sA:.6f}  scale B (bike 5.07)={sB:.6f} ratio B/A={sB/sA:.4f}')
# car full extents
full=[(i,car[i]['x1']-car[i]['x0']+1,car[i]['y1']-car[i]['y0']+1, (car[i]['x0']+car[i]['x1'])/2,car[i]['cy']) for i in range(N) if car[i] and car[i]['x0']>2 and car[i]['x1']<1917]
for f in full[::3]: print('car full frame',f)
np.save if False else None
json.dump(dict(fx=fx.tolist(),rx=rx.tolist(),bike=[(b['x0'],b['x1'],b['cy']) if b else None for b in bike],cary=[(o['y0'],o['y1'],o['cy']) if o else None for o in car]),open(f'research/next/audit3/sim2_13/caran_{c}.json','w'))
