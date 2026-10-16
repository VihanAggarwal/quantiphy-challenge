import numpy as np
FL,FR,BR=np.load('scripts/table_pts.npy')
front,right,back,left=np.load('scripts/table_lines.npy')
cx,cy=640.,360.
def run(f,verbose=True):
    K=np.array([[f,0,cx],[0,f,cy],[0,0,1.]])
    v1=np.cross(left,right); v1=v1/v1[2]
    d1=np.linalg.solve(K,v1); d1/=np.linalg.norm(d1)
    nF=K.T@front; d2=np.cross(nF,d1); d2/=np.linalg.norm(d2)
    n=np.cross(d1,d2); n/=np.linalg.norm(n)
    def ray(p): r=np.linalg.solve(K,[p[0],p[1],1.]); return r
    def onplane(p,h=1.0):  # plane n.X = h
        r=ray(p); return r*h/(n@r)
    A,B,C=onplane(FL),onplane(FR),onplane(BR)
    w=np.linalg.norm(B-A); dep=np.linalg.norm(C-B)
    # also check orthogonality of FL-FR vs FR-BR
    ang=np.degrees(np.arccos(((B-A)@(C-B))/w/dep))
    s=0.760/w  # metres per unit, using front = 76.0 cm
    if verbose:
        print(f'f={f}: width/depth={w/dep:.4f} (76/60.3={0.76/0.603:.4f}), angle={ang:.1f}, depth_cm={dep*s*100:.1f}, cam height above plane={s*1.0:.3f} m, n={n}')
    return n,s,K
for f in [650,680,700,711,720,740,770]:
    run(f)
print('--- front edge = 60.3 cm ---')
for f in [700,711,730]:
    n,s,K=run(f,False)
    FL,FR,BR=np.load('scripts/table_pts.npy')
    def P(p): r=np.linalg.solve(K,[p[0],p[1],1.]); return r/(n@r)
    w=np.linalg.norm(P(FR)-P(FL)); s=0.603/w
    dep=np.linalg.norm(P(BR)-P(FR))*s
    for nm,p in [('board bottom mid',(612,420)),('board bottom left',(563,422)),('board bottom right',(663,416)),('FL',FL),('FR',FR),('BR',BR)]:
        X=P(p)*s; print(f, nm, 'range %.4f'%np.linalg.norm(X), 'depth z %.4f'%X[2])
    print(f,'table depth edge (cm) %.1f'%(dep*100), 'cam height %.3f'%s)
