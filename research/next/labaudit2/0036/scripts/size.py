import cv2, numpy as np, json
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/f36/'
T=json.load(open('scripts/trk_bg.json'))
out={}
for v in ['captured_0036','captured_0036s','captured_0036x']:
    res={}
    for k in range(4,36):
        t=T[v][str(k)]
        im=cv2.imread(S+f'{v}/f{k:02d}.png').astype(float).mean(2)
        im=cv2.GaussianBlur(im,(0,0),0.8)
        u=t['cx']; vv=t['cy']; ui=int(round(u)); vi=int(round(vv))
        tops=[];bots=[]
        for du in range(-3,4):
            col=im[vi-35:vi+40,ui+du]; ys=np.arange(vi-35,vi+40)
            g=np.diff(col)  # g[i] = col[i+1]-col[i], at y+0.5
            # top: max positive gradient above centroid+3
            lim=35+3
            it=np.argmax(g[:lim]); 
            # subpixel by parabola
            def sp(i,arr):
                if 0<i<len(arr)-1:
                    a,b,c=arr[i-1],arr[i],arr[i+1]; den=a-2*b+c
                    return i+(0.5*(a-c)/den if den!=0 else 0)
                return i
            top=ys[0]+sp(it,g)+0.5
            # bottom: most negative gradient below centroid
            st=35
            ib=st+np.argmin(g[st:st+30]); bot=ys[0]+sp(ib,-g)+0.5
            tops.append(top);bots.append(bot)
        top=np.median(tops); bot=np.median(bots)
        res[k]=dict(u=u,v=vv,top=float(top),bot=float(bot),d=float(bot-top))
    out[v]=res
json.dump(out,open('scripts/size.json','w'))
for k in range(4,36):
    print(k,' '.join('%6.1f %6.1f %5.1f |'%(out[v][k]['top'],out[v][k]['bot'],out[v][k]['d']) for v in out))
