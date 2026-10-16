import numpy as np, json, sys
d='/home/user/quantiphy-challenge/research/next/labaudit/0032/'
G=np.load(d+'plane711.npy',allow_pickle=True).item()
n=-G['n']
f=711.; K=np.array([[f,0,640],[0,f,360],[0,0,1.]]); Ki=np.linalg.inv(K)
r_=sys.argv[1] if len(sys.argv)>1 else 'x'
T=json.load(open(d+'track_%s.json'%r_))
def ray(p): r=Ki@np.array([p[0],p[1],1.]); return r/np.linalg.norm(r)
out={}
for h in [0.1682,0.1730]:
    print('=== h',h)
    for name,key,rad in [('tennis','yel',0.0335),('ping','wht',0.02)]:
        X={}
        for i in range(49):
            t=T[str(i)][key]
            if t is None: continue
            u=ray((t['cx'],t['cy'])); X[i]=u*(h-rad)/(n@u)
        out[(h,name)]=X
        print(name)
        for i in range(28,49):
            if i in X and i+1 in X:
                v=np.linalg.norm(X[i+1]-X[i])*24*100
                print('  f%d range %.3f  fwd speed %.1f cm/s  dXYZ(cm/frame) %s'%(i,np.linalg.norm(X[i]),v,((X[i+1]-X[i])*100).round(2)))
    A=out[(h,'tennis')][36]; B=out[(h,'ping')][36]
    print('dist f36 %.2f cm'%(100*np.linalg.norm(A-B)))
