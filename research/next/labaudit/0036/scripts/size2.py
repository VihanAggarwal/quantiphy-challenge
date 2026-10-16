import cv2, numpy as np, json
f=711.; c0=np.array([640.,360.])
T=json.load(open('scripts/trk_o.json'))
n=np.load('scripts/plane_n.npy')
def orig(k): return k if k<=11 else (k+1 if k<=35 else k+2)
def ray(u,v):
    r=np.array([(u-c0[0])/f,(v-c0[1])/f,1.]); return r/np.linalg.norm(r)
res={}
for k in list(range(5,12))+list(range(13,36)):
    im=cv2.imread(f'frames/captured_0036/f{k:02d}.png').astype(float).mean(2)
    u,v=T[str(k)]['cx'],T[str(k)]['cy']; ui,vi=int(round(u)),int(round(v))
    col=im[vi-40:vi+45,ui-2:ui+3].mean(1); ys=np.arange(vi-40,vi+45)
    pk=np.argmax(col)
    # top: largest upward jump above pk
    g=np.diff(col[:pk+1]); it=np.argmax(g); top=ys[it]+0.5
    # bottom: min (shadow) below pk within 40px
    seg=col[pk:pk+40]; ib=pk+np.argmin(seg); bot=ys[ib]
    d=bot-top
    r=ray(u,(top+bot)/2); cosA=r[2]
    rs=f*0.04/d  # simple
    rp=0.157/(n@ray(u,v))
    res[k]=dict(top=float(top),bot=float(bot),d=float(d),rs=float(rs),rp=float(rp),u=u,vc=float((top+bot)/2))
    print('%2d orig %2d top %.1f bot %.1f d %.1f  range_size %.3f range_plane %.3f ratio %.3f'%(k,orig(k),top,bot,d,rs,rp,rs/rp))
json.dump(res,open('scripts/size2.json','w'))
