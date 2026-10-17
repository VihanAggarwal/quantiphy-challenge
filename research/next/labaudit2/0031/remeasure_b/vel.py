import numpy as np, sys, cv2
tag=sys.argv[1] if len(sys.argv)>1 else 'a'; f=float(sys.argv[2]) if len(sys.argv)>2 else 775.
res=np.load('/home/user/quantiphy-challenge/research/next/labaudit2/0031/remeasure_b/motion_%s_%d.npy'%(tag,int(f)),allow_pickle=True).item()
Rb={'t':3.35,'w':2.0}
def ray(u,v):
    d=np.array([(u-640)/f,(v-360)/f,1.0]); return d/np.linalg.norm(d)
for b in 't','w':
    A=res[b]
    for route,col in (('size',5),('ground',6)):
        # surface point at clicked centre: (Rc - R) * ray
        Ps=np.array([(row[col]-Rb[b])*ray(row[2],row[3]) for row in A])
        c=A[:,1]
        def fd(c0):
            i0=np.where(c==c0)[0]; i1=np.where(c==c0+1)[0]
            if len(i0) and len(i1): return 25*np.linalg.norm(Ps[i1[0]]-Ps[i0[0]])
        out=[]
        for lo,hi,deg in ((34,44,1),(36,43,1),(32,44,2),(30,43,1),(36,48,1),(38,50,1),(30,50,2)):
            if b=='t' and hi>43: continue
            sel=(c>=lo)&(c<=hi)
            if sel.sum()<4: continue
            coef=[np.polyfit(c[sel],Ps[sel,j],deg) for j in range(3)]
            p40=np.array([np.polyval(cc,40) for cc in coef]); p41=np.array([np.polyval(cc,41) for cc in coef])
            out.append('[%d-%d d%d] %.1f'%(lo,hi,deg,25*np.linalg.norm(p41-p40)))
        print(b,route,'raw fd(40->41)=%.1f'%fd(40),' fits:',' '.join(out))
