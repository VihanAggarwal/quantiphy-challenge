import cv2, numpy as np, json
exec(open('/home/user/quantiphy-challenge/research/next/labaudit2/0038/rm2/pnp2.py').read().split("for f in [711,750,780,800]")[0])
D='/home/user/quantiphy-challenge/research/next/labaudit2/0038/rm2/'
tm={r[0]:r for r in json.load(open(D+'tm_x_24.json'))}
YOFF=5.4
for f in [711,730,750]:
    K,R,t,err=solve(f)
    Cw=-R.T@t; up=np.sign(Cw[2])
    print('f',f)
    for i in [20,21,22,23,24,28,32,33,34,35,36,38,40]:
        px=(tm[i][1],tm[i][2]+YOFF)
        for Rb in [2.0]:
            P=table_pt(K,R,t,px,h=Rb*up)
            Pt=R.T@(P-t)
            print('  fr %d px (%.1f,%.1f) centre range %.1f surf %.1f  table(x,y)=(%.1f,%.1f)'%(i,px[0],px[1],np.linalg.norm(P),np.linalg.norm(P)-Rb,Pt[0],Pt[1]))
