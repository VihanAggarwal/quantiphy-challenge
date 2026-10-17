from geom import *
tr=load_tr('b'); bb=tr['bb']; sb=tr['sb']
# 1) baseboard orthogonality: lines (dark centre lines)
mR=line_normal(0.1982,72.44); mL=line_normal(-0.5346,517.22)
def ortho_res(n):
    d1=np.cross(n,mR); d2=np.cross(n,mL); d1/=np.linalg.norm(d1); d2/=np.linalg.norm(d2); return d1@d2
# 2) bb centres from size, unblurred frames (rest 0-10, after collision 28-45)
fr_=[k for k in list(range(0,11))+list(range(28,46)) if k in bb]
P=np.array([size_range(bb[k])*ray(bb[k]['cx'],bb[k]['cy']) for k in fr_])
n_s,hc=fit_plane(P)
print('bb-size plane n',np.round(n_s,4),'centre-plane dist %.3f'%hc,'-> camera height %.3f'%(hc+0.116),'pitch %.1f deg'%np.degrees(np.arcsin(-n_s[2])) )
res=P@n_s+hc; print('  rms resid cm %.2f'%(100*np.sqrt((res**2).mean())), 'ortho cos(angle between baseboards) %.3f -> %.1f deg'%(ortho_res(n_s),np.degrees(np.arccos(abs(ortho_res(n_s))))))
# 3) family of normals satisfying orthogonality: parametrize by pitch/roll, find closest to n_s
def nvec(p):
    a,b=p; n=np.array([np.sin(b),-np.cos(a)*np.cos(b),-np.sin(a)*np.cos(b)]); return n/np.linalg.norm(n)
cands=[]
for a in np.radians(np.arange(20,50,0.05)):
    for b in np.radians(np.arange(-15,15,0.05)):
        n=nvec((a,b)); 
        if abs(ortho_res(n))<0.003: cands.append(n)
cands=np.array(cands); n_o=cands[np.argmax(cands@n_s)]; print('closest orthogonal-baseboard normal',np.round(n_o,4),'angle to bb-size normal %.2f deg'%np.degrees(np.arccos(n_o@n_s)))
# camera height with n_o from bb centres
hc_o=-np.mean(P@n_o); print('  with n_o: centre plane %.3f, camera height %.3f'%(hc_o,hc_o+0.116),'rms cm %.2f'%(100*np.std(P@n_o)))
np.save(f'{OUT}/plane_b.npy',np.array([*n_s,hc+0.116,*n_o,hc_o+0.116]))
for k in [0,5,10,22,30,34,40,45]:
    if k in bb: print(k,'bb size range %.3f'%size_range(bb[k]),'plane(n_s) range %.3f'%np.linalg.norm(plane_point(bb[k]['cx'],bb[k]['cy'],n_s,hc+0.116,0.116)),'plane(n_o) %.3f'%np.linalg.norm(plane_point(bb[k]['cx'],bb[k]['cy'],n_o,hc_o+0.116,0.116)))
