import cv2,numpy as np
D='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0017/rm1657/frames/'
s=cv2.imread(D+'seg_bg.png').astype(float).min(2)   # white bg ~255
def first_cross(col,thr,rev=False):
    c=col[::-1] if rev else col
    idx=np.nonzero(c<thr)[0]
    if len(idx)==0: return np.nan
    k=idx[0]
    if k==0: return np.nan
    a,b=c[k-1],c[k]; x=k-1+(a-thr)/(a-b)
    return (len(col)-1-x) if rev else x
for name,(ua,ub) in (('R',(684,766)),('L',(312,390))):
    us=np.arange(ua,ub); top=[];bot=[]
    for u in us:
        col=s[440:630,u]
        top.append(440+first_cross(col,180)); bot.append(440+first_cross(col,180,rev=True))
    top=np.array(top);bot=np.array(bot)
    pt=np.polyfit(us,top,1); pb=np.polyfit(us,bot,1)
    print(name,'top slope %.4f (v %.2f..%.2f) bottom slope %.4f (v %.2f..%.2f)'%(pt[0],np.polyval(pt,ua),np.polyval(pt,ub),pb[0],np.polyval(pb,ua),np.polyval(pb,ub)))
    print('  height px at ends: %.2f  %.2f'%(np.polyval(pb,ua)-np.polyval(pt,ua),np.polyval(pb,ub)-np.polyval(pt,ub)))
# horizontal extents per row from segmented (subpixel)
for name,(ua,ub) in (('R',(655,800)),('L',(280,404))):
    print(name)
    for v in range(596,616):
        row=s[v,ua:ub]
        l=ua+first_cross(row,180); r=ua+first_cross(row,180,rev=True)
        print('  v%d  %.1f  %.1f  w=%.1f'%(v,l,r,r-l))
