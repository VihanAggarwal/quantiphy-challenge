import cv2, numpy as np
exec(open('/home/user/quantiphy-challenge/research/next/labaudit2/0038/rm2/pnp2.py').read().split("for f in [711,750,780,800]")[0])
pts={'card':((570,542),68.67,'flat'),'cup':((759,436),87.4,(759,497)),'bottle':((664,403),99.98,(664,477)),'tower':((684,458),90.35,(684,500))}
for f in [711,750]:
    K,R,t,err=solve(f)
    print('f',f)
    for k,(c,rg,b) in pts.items():
        bb=c if b=='flat' else b
        P=table_pt(K,R,t,bb)
        u=np.linalg.solve(K,[c[0],c[1],1.]); u/=np.linalg.norm(u)
        # given clicked point 3D
        X=rg*u
        # height of clicked point above table plane (PnP plane)
        Cw=-R.T@t; up=np.sign(Cw[2])
        Xt=R.T@(X-t)
        print('  %-6s plane-pt range %.1f (z %.1f) | given %.1f (z %.1f) | given pt height above table %.1f cm, table-y %.1f'%(k,np.linalg.norm(P),P[2],rg,X[2],Xt[2]*up,Xt[1]))
