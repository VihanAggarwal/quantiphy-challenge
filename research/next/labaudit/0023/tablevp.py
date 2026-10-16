import cv2, numpy as np
from table import fitline, inter
def side_pts(fr, rows, side, mode):
    im=cv2.imread(f'frames/{fr}.png').astype(float)
    P=[]
    for y in rows:
        if mode=='mask':
            g=im[y].max(1)
        else:
            g=im[y].mean(1)  # o render: table brown vs blurred grey background; use red-blue contrast
            g=im[y,:,2]-im[y,:,0]
        if side=='L':
            seg=g[250:520]; lo=np.median(seg[:30]); hi=np.median(seg[-30:])
        else:
            seg=g[720:990][::-1]; lo=np.median(seg[:30]); hi=np.median(seg[-30:])
        t=(lo+hi)/2; k=np.nonzero(seg>t)[0][0]
        xs=k-1+(t-seg[k-1])/(seg[k]-seg[k-1])
        P.append((250+xs,y) if side=='L' else (989-xs,y))
    return np.array(P)
for fr,mode in [('x44','mask'),('x00','mask'),('o44','rb'),('o00','rb'),('s44','rb')]:
    rows=range(452,522)
    L=side_pts(fr,rows,'L',mode); R=side_pts(fr,rows,'R',mode)
    lL,eL=fitline(L); lR,eR=fitline(R)
    vp=inter(lL,lR)
    print(fr,mode,'resid',round(eL,2),round(eR,2),'VP',vp.round(1), 'slopes dx/dy', round(np.polyfit(L[:,1],L[:,0],1)[0],4), round(np.polyfit(R[:,1],R[:,0],1)[0],4))
