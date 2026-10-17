import numpy as np, json
exec(open('fit3d.py').read().split("for name,imax in")[0])
# 1) predict post-drop frames from pre-drop fit
for name in ('white','green'):
    s,I,J,uv,P=fit(name,35,True)
    for vi,j in ((36,38),(37,39)):
        o=[x for x in obs[name] if x[0]==vi]
        if not o: continue
        pp=proj(traj(s.x,np.array([(j-25)/25.])))[0]
        pp37=proj(traj(s.x,np.array([(j-1-25)/25.])))[0]
        print(name,'fit<=v35 predicts v%d as c%d: (%.1f,%.1f) [as c%d: (%.1f,%.1f)] observed (%.1f,%.1f)'%(vi,j,pp[0],pp[1],j-1,pp37[0],pp37[1],o[0][1],o[0][2]))
# 2) joint fit with free gravity direction (both balls)
def joint(params,ret=False):
    th,ph=params[12:14]
    gd=np.array([np.sin(th)*np.cos(ph), np.cos(th), np.sin(th)*np.sin(ph)])
    rs=[]
    for k,(name,imax) in enumerate((('white',37),('green',36))):
        o=[x for x in obs[name] if x[0]<=imax]
        I=np.array([x[0] for x in o]); J=np.array([cap(i) for i in I]); uv=np.array([[x[1],x[2]] for x in o])
        t=(J-25)/25.
        P=traj(params[6*k:6*k+6],t,9.8,gd)
        rs.append((proj(P)-uv).ravel())
        i24=list(I).index(24)
        rs.append([(np.linalg.norm(P[i24])-anchor[name]-rad[name])*200])
    return np.concatenate([np.ravel(r) for r in rs])
sw,_,_,_,_=fit('white',37,True); sg,_,_,_,_=fit('green',36,True)
p0=np.r_[sw.x,sg.x,0.02,0.0]
s=least_squares(joint,p0)
th,ph=s.x[12:14]; gd=np.array([np.sin(th)*np.cos(ph), np.cos(th), np.sin(th)*np.sin(ph)])
print('joint free-gdir: gd=',gd.round(4),' VP-based down=',down.round(4),' angle diff deg=%.2f'%np.degrees(np.arccos(gd@down)),'rms=%.2f'%np.sqrt((s.fun**2).mean()))
for k,name in enumerate(('white','green')):
    x=s.x[6*k:6*k+6]
    V=lambda j: x[3:6]+9.8*gd*(j-25)/25.
    Pc=lambda j: traj(x,np.array([(j-25)/25.]),9.8,gd)[0]
    print('  ',name,'|v| c37.5=%.3f c38.5=%.3f  chord c38->39=%.3f c37->38=%.3f'%(np.linalg.norm(V(37.5)),np.linalg.norm(V(38.5)),np.linalg.norm(Pc(39)-Pc(38))*25,np.linalg.norm(Pc(38)-Pc(37))*25))
# 3) g magnitude check: free fit (no anchors) with g scaled -> find depth scale
