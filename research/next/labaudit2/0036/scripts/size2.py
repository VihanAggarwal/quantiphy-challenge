import cv2, numpy as np, json
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/f36/'
T=json.load(open('scripts/trk_bg.json'))
def sp(i,arr):
    if 0<i<len(arr)-1:
        a,b,c=arr[i-1],arr[i],arr[i+1]; den=a-2*b+c
        return i+(0.5*(a-c)/den if den!=0 else 0)
    return i
out={}
for v in ['captured_0036','captured_0036s','captured_0036x']:
    res={}
    for k in range(4,36):
        t=T[v]['%d'%k]
        im=cv2.imread(S+f'{v}/f{k:02d}.png').astype(float)
        g=im[...,0]  # blue channel: ball white, table dark in blue
        g=cv2.GaussianBlur(g,(0,0),0.7)
        u=t['cx']; vi=int(round(t['cy']))
        tops=[];bots=[]
        for du in range(-4,5):
            ui=int(round(u))+du
            ys=np.arange(vi-35,vi+45); col=g[vi-35:vi+45,ui]
            br=35-8+np.argmax(col[35-8:35+8])  # brightest near centroid
            gr=np.diff(col)
            it=np.argmax(gr[max(0,br-25):br])+max(0,br-25); top=ys[0]+sp(it,gr)+0.5
            seg=col[br:br+35]; ib=np.argmin(seg)+br; bot=ys[0]+sp(ib,-col)
            tops.append(top);bots.append(bot)
        top=float(np.median(tops)); bot=float(np.median(bots))
        res[k]=dict(u=u,v=t['cy'],top=top,bot=bot,d=bot-top)
    out[v]=res
json.dump(out,open('scripts/size2.json','w'))
for k in range(4,36):
    print(k,' '.join('%6.1f %6.1f %5.1f |'%(out[v][k]['top'],out[v][k]['bot'],out[v][k]['d']) for v in out))
