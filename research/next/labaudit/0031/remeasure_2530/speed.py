import numpy as np, json, sys
render=sys.argv[1]; fn=sys.argv[2]; D=float(sys.argv[3]); lo,hi=int(sys.argv[4]),int(sys.argv[5])
key=sys.argv[6] if len(sys.argv)>6 else 'd'
c=[r for r in json.load(open(fn)) if lo<=r['i']<=hi]
fps=24.0
for f in [711.0]:
  i=np.array([r['i'] for r in c],float); t=i/fps
  u=np.array([r['cx'] for r in c]); v=np.array([r['cy'] for r in c]); d=np.array([r[key] for r in c])
  R=(D/2)/np.sin(np.arctan(d/2/f))
  ray=np.c_[(u-640)/f,(v-360)/f,np.ones_like(u)]; ray/=np.linalg.norm(ray,axis=1)[:,None]
  P=R[:,None]*ray
  for deg in [2,3]:
    out=[]
    for tq in [36/fps,38/fps,1.6,40/fps]:
      vel=[np.polyval(np.polyder(np.polyfit(t,P[:,k],deg)),tq) for k in range(3)]
      out.append('t=%.3f |v|=%.1f (vx %.1f vy %.1f vz %.1f)'%(tq,np.linalg.norm(vel),*vel))
    print('f',f,'deg',deg,' ; '.join(out))
  # range at frames
  for k in range(len(i)):
    if i[k] in (34,36,38,40,42): print('  frame %d R=%.1f P=%s'%(i[k],R[k],P[k].round(1)))
