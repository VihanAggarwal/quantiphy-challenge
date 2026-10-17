import cv2, numpy as np, sys
v=sys.argv[1]
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/%s.mp4'%v)
def subedge(prof, y0, sign):
    # find strongest gradient of given sign, subpixel via parabola
    g=np.diff(prof)*sign
    k=int(np.argmax(g))
    if 0<k<len(g)-1:
        a,b,cc=g[k-1],g[k],g[k+1]; d=0.5*(a-cc)/(a-2*b+cc) if (a-2*b+cc)!=0 else 0
    else: d=0
    return y0+k+0.5+d
i=0; out=[]
while True:
    ok,f=c.read()
    if not ok: break
    f=f.astype(float).sum(axis=2)
    # box top: columns 830-930 (left of flap), search 60..330
    pb=f[60:330, 830:930].mean(axis=1); bt=subedge(pb,60,-1)
    # roof edge at outer columns 680-760 search 200..450 : white bg -> white truck? use orig too
    pr=f[200:450, 680:760].mean(axis=1); rt=subedge(pr,200,1 if 'segmented' not in v else -1)
    # yellow stripe top at 680-760 (cols inside stripe?) skip
    # door top at cols 880-1000 search 300-600: transition light->dark?
    pdd=f[250:650, 880:1000].mean(axis=1); dt=subedge(pdd,250,-1)
    out.append((i,bt,rt,dt))
    i+=1
o=np.array(out)
for r in o[::25]: print('%d box_top %.2f roof %.2f doortop %.2f'%tuple(r))
print('last', '%d box_top %.2f roof %.2f doortop %.2f'%tuple(o[-1]))
np.savetxt('/home/user/quantiphy-challenge/research/next/audit3/sim2_20/%s_track.txt'%v, o, fmt='%.3f')
