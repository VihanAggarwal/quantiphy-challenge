import cv2, numpy as np
from geo import *
from slope3d import board_model, hit_plane
from bookmask import cover_mask
H=0.0146
def colext(m,x):
    c=np.nonzero(m[:,x-2:x+3].max(1))[0]
    return (c.min(),c.max()+1) if len(c) else None
for route in ['stated','ruler']:
    M=board_model(route); p0=M['B']+M['n']*H
    print(route)
    for fr in ['o10','o15','o20','x15','o23','o24','o25','o26','o27','x24','x25','x26','x27','o28','x28']:
        m=cover_mask(fr)
        out=[]
        for x in [550,570,590,610,630]:
            e=colext(m,x)
            if e is None: continue
            A=hit_plane(p0,M['n'],x,e[0]); B=hit_plane(p0,M['n'],x,e[1])
            out.append(np.linalg.norm(A-B)*100)
        ys,xs=np.nonzero(m)
        # length along the row through the centroid
        yc=int(round(ys.mean())); r=np.nonzero(m[yc-1:yc+2].max(0))[0]
        A=hit_plane(p0,M['n'],r.min(),yc); B=hit_plane(p0,M['n'],r.max()+1,yc)
        print(f'  {fr} width(cols)={np.round(out,2)} med={np.median(out):.2f}  len@row{yc}={np.linalg.norm(A-B)*100:.2f} ({r.max()+1-r.min()}px)')
