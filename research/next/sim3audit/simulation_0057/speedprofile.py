# stride-averaged lateral head velocity of the person in simulation_0021 (0033 == 0021 shifted by 27 frames)
import numpy as np
a=np.loadtxt('e21_head.txt'); b=np.loadtxt('e33_head.txt')
L=a[:,1].copy(); R=a[:,2].copy()
# lamp post occludes x~186..197.5: L valid while L<184 (f<=60) or L>198.5 (f>=69); R valid while R<185 (f<=50) or f>=61
f=np.arange(len(L))
Lv=np.where((f<=60)|(f>=69),L,np.nan)
# alignment check 0033 vs 0021+27
d=[abs(b[j,1]-a[j+27,1]) for j in range(len(b)) if j+27<len(a) and (j+27<=60 or j+27>=69)]
print('0033 vs 0021 (+27 frames) L-edge mean abs diff px: %.2f'%np.mean(d))
def Li(t):
    ok=~np.isnan(Lv); return np.interp(t,f[ok],Lv[ok])
k=1.87/215.4   # m/px at person depth (head-top 650 to sole ~865)
P=28.5          # stride period in frames (head-top minima at 0,14.5,28.5,43.5,57)
for c in [14.25,20,25,30,35,40,43,50,57,64,74]:
    if c-P/2<0 or c+P/2>88: continue
    v=(Li(c+P/2)-Li(c-P/2))/P
    print('frame %5.1f (0021 t=%.2fs, 0033 t=%.2fs): %.2f px/f -> %.3f m/s'%(c,c/30,(c-27)/30,v,v*30*k))
print('whole clip 0..88 mean: %.3f m/s'%((Li(88)-Li(0))/88*30*k))
# depth-pair check (constant Y,Z): X from head centre, cx=540
for (fa,fb,da,db,name) in [(0,30,13.882,13.768,'0021 0-1s'),(27,57,13.780,13.651,'0033 0-1s')]:
    xa=Li(fa)+12.4; xb=Li(fb)+12.4
    Xa=(xa-540)*k; Xb_pix=(xb-540)*k
    Xb=-np.sqrt(Xa**2-(da**2-db**2))
    print(name,': pixel displacement %.3f m, depth-implied displacement %.3f m'%(Xb_pix-Xa, Xb-Xa))
