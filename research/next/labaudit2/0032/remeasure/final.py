import numpy as np, json
exec(open('vel3.py').read().split("for f in [711,740,770,800]")[0])
f=770; K,n,h0=pose(f)
up=-n if n[1]>0 else n   # up direction has negative camera-y
Pc=backproj(f,n,h0,x,ysh)
cen=Pc+0.02*up
# label-style: clicked centre pixel ray, ToF range at surface = |centre|-r
u=np.c_[(x-640)/f,(yc-360)/f,np.ones_like(x)]; u/=np.linalg.norm(u,axis=1)[:,None]
lab=(np.linalg.norm(cen,axis=1)-0.02)[:,None]*u
print('up',up.round(4),'centre range cap38 %.4f'%np.linalg.norm(cen[0]))
for nm,P in [('centre',cen),('label-surface',lab)]:
    st=np.linalg.norm(np.diff(P,axis=0),axis=1)*2500
    print(nm,'steps cap38..50',st.round(1),' 40->41 = %.1f'%st[2])
    m=(c>=38)&(c<=44)
    V=np.array([np.polyval(np.polyder(np.polyfit(t[m],P[m,j],1)),40.5/25) for j in range(3)])*100
    print('   local lin 38-44 @40.5: %.1f  (vx %.1f vy %.1f vz %.1f)'%(np.linalg.norm(V),*V))
