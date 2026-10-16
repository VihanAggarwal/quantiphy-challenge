import sys, cv2, numpy as np; sys.path.insert(0,'scripts')
exec(open('scripts/wb62b.py').read().split('for n in (24,40,48):')[0])
C40,_,_=board_corners(40); C48,_,_=board_corners(48)
def ray(u,v,f):
    d=np.array([(u-640)/f,(v-360)/f,1.0]); return d/np.linalg.norm(d)
def nvec(a,b): return np.array([np.sin(b)*np.cos(a), np.cos(b)*np.cos(a), np.sin(a)])
for f in (711,760):
    best=[]
    for a in np.radians(np.arange(25,45,0.25)):
        for b in np.radians(np.arange(-20,8,0.25)):
            dn=nvec(a,b); cost=0; E=[]
            for C in (C40,C48):
                Q=np.array([ray(u,v,f)/(ray(u,v,f)@dn) for u,v in C])
                for j in range(4):
                    p=Q[j-1]-Q[j]; q=Q[(j+1)%4]-Q[j]
                    cost+=(p@q/np.linalg.norm(p)/np.linalg.norm(q))**2
                E.append([np.linalg.norm(Q[(j+1)%4]-Q[j]) for j in range(4)])
            E=np.array(E)
            # size consistency between frames (relative), and opposite sides equal
            cost+=((E[0]-E[1])/E.mean(0)).__pow__(2).sum()
            cost+=(((E[:,0]-E[:,2])/E[:,0])**2).sum()+(((E[:,1]-E[:,3])/E[:,1])**2).sum()
            best.append((cost,np.degrees(a),np.degrees(b)))
    best.sort()
    print('f',f,'best (cost, pitch-ish, roll):',[tuple(np.round(x,3)) for x in best[:5]])
    vis=nvec(np.radians(90-np.degrees(np.arccos(0.56578))),np.arctan2(-0.14912,0.81096))
    print('   visual model pitch %.2f roll %.2f'%(90-np.degrees(np.arccos(0.56578)),np.degrees(np.arctan2(-0.14912,0.81096))))
