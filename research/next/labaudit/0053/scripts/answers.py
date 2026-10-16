import sys, numpy as np, json; sys.path.insert(0,'scripts')
from models import M
d=json.load(open('xcomps.json'))
cen={}
for n in range(48):
    b=[x for x in d[str(n)] if x['a']>4000 and not abs(x['cx']-986)<6][0]; cen[n]=(b['cx'],b['cy'])
quad=np.load('book_quad.npy')
C={'book':(666.4,617.9),'cup':(564.3,424.0),'bb':(985.8,369.6)}
R={'book':2.082,'cup':2.516,'bb':2.925}
for m in M:
    Ps={k:m.P(*C[k],R[k]) for k in C}
    cupbb=np.linalg.norm(Ps['cup']-Ps['bb']); cupbook=np.linalg.norm(Ps['cup']-Ps['book'])
    # book: plane through book centre, normal dn
    d0=Ps['book']@m.dn
    Q=np.array([m.ray(u,v)*d0/(m.ray(u,v)@m.dn) for u,v in quad])
    e=[np.linalg.norm(Q[(j+1)%4]-Q[j]) for j in range(4)]
    # cup rim 25.7 px at cup depth
    Xc=m.P(564.3,424,2.516)
    rim=25.7*np.linalg.norm(Xc)/m.f if m.mode=='range' else 25.7*Xc[2]/m.f
    # bin displacement: click-point height from ToF at n10, same height at n34
    X10=m.P(*cen[10],2.73); z=m.H-X10@m.dn
    X34=m.fp(*cen[34],z); disp=np.linalg.norm(X34-X10)
    same=np.linalg.norm(m.P(*cen[34],2.73)-X10)
    # tab route
    t10=(782.3,419.5); t34=(595.5,299.3)
    tab=np.linalg.norm(m.fp(*t34,0.01)-m.fp(*t10,0.01))
    # velocity at 0.4 (n10->n11), click-height model
    v=np.linalg.norm(m.fp(*cen[11],z)-X10)/0.04
    print(m.name,'H %.3f'%m.H)
    print('   cup-bb %.3f cup-book %.3f | book silhouette %.1f x %.1f | rim(25.7px) %.2f | bin z %.3f disp %.3f (depth34 %.3f) tab %.3f same-depth %.3f | v(0.4) %.3f'%(cupbb,cupbook,np.mean([e[0],e[2]])*100,np.mean([e[1],e[3]])*100,rim*100,z,disp,m.depth_of(X34),tab,same,v))
