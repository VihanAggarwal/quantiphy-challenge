import sys, numpy as np; sys.path.insert(0,'scripts')
from models import M
def proj(m,X): return np.array([640+m.f*X[0]/X[2], 360+m.f*X[1]/X[2]])
def height_above(m,X0,target):
    # find h such that proj(X0 + h*up) closest to target (2D)
    hs=np.linspace(0,0.8,4001)
    d=[np.linalg.norm(proj(m,X0-h*m.dn)-target) for h in hs]
    i=int(np.argmin(d)); return hs[i], d[i]
def pt_at_height(m,uv,h):
    return m.fp(uv[0],uv[1],h)
frames={10:[[770,320],[863,362],[835,433],[782,427],[734,404],[742,360]],
        22:[[672,256],[749,306],[715,361],[666,351],[628,331],[636,290]],
        34:[[602,216],[671,258],[667,286],[642,313],[558,283],[564,246]],
        40:[[562,194],[631,234],[625,271],[605,287],[522,259],[528,221]]}
# vertex roles per frame: [far-top-left, far-top-right(top-right), right-mid, bottom-right, bottom-left, left-top]
for m in M:
    print(m.name)
    for n,p in frames.items():
        p=np.array(p,float)
        TL_far,TR,RM,BR,BL,LT=p
        if n==34: TL_far,TR,RM,BR,BL,LT=p[0],p[1],p[2],p[3],p[4],p[5]
        bl=m.fp(*BL,0.0); br=m.fp(*BR,0.0)
        L1=np.linalg.norm(br-bl)
        h,res=height_above(m,bl,LT)
        # far-top-left corner at height h
        ftl=pt_at_height(m,TL_far,h); lt=bl-h*m.dn
        D=np.linalg.norm(ftl-lt)
        # top-right corner at height h
        tr=pt_at_height(m,TR,h)
        L2=np.linalg.norm(tr-ftl)
        print('   n%d near-bottom edge %.3f | height(front-left vertical) %.3f (res %.1fpx) | depth(left-top edge) %.3f | far-top edge %.3f'%(n,L1,h,res,D,L2))
