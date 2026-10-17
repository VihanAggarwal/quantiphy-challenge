import numpy as np,json
C=json.load(open('corners.json')); P={k:np.array(v+[1.0]) for k,v in C.items()}
def plane(f,cx=640,cy=360):
    Ki=np.linalg.inv(np.array([[f,0,cx],[0,f,cy],[0,0,1.]]))
    l=lambda a,b: np.cross(P[a],P[b])
    v1=np.cross(l('BL','BR'),l('FL','FR')); v2=np.cross(l('BL','FL'),l('BR','FR'))
    d1=Ki@v1; d2=Ki@v2; d1/=np.linalg.norm(d1); d2/=np.linalg.norm(d2)
    n=np.cross(d1,d2); n/=np.linalg.norm(n)
    if n[1]<0: n=-n   # normal pointing down (+y) ; plane n.X = h>0
    X={k:(Ki@P[k])/(n@(Ki@P[k])) for k in P}  # h=1
    L={'front':np.linalg.norm(X['FL']-X['FR']),'back':np.linalg.norm(X['BL']-X['BR']),'left':np.linalg.norm(X['BL']-X['FL']),'right':np.linalg.norm(X['BR']-X['FR'])}
    return n,X,L,np.degrees(np.arccos(abs(d1@d2))),Ki
for f in [690,699.2,711,725]:
    n,X,L,ang,Ki=plane(f)
    h_w=76.0/np.mean([L['front'],L['back']]); h_d=60.3/np.mean([L['left'],L['right']])
    print(f'f={f} n={n.round(4)} angle={ang:.2f} h(from76)={h_w:.2f} h(from60.3)={h_d:.2f}  lens(h=1) ' + ' '.join(f'{k}={v*h_w:.1f}' for k,v in L.items()))
