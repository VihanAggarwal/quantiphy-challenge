import cv2, numpy as np, json
f=711.; cx0,cy0=640.,360.
T=json.load(open('scripts/trk_o.json'))
n=np.load('scripts/plane_n.npy')
def orig(k): return k if k<=11 else (k+1 if k<=35 else k+2)
def ray(u,v):
    r=np.array([(u-cx0)/f,(v-cy0)/f,1.]); return r/np.linalg.norm(r)
out={}
for k in range(5,36):
    im=cv2.imread(f'frames/captured_0036/f{k:02d}.png').astype(float).mean(2)
    u,v=T[str(k)]['cx'],T[str(k)]['cy']
    # vertical extent: average 5 columns around centre
    ui=int(round(u)); vi=int(round(v))
    col=im[vi-35:vi+35,ui-2:ui+3].mean(1)
    peak=col[30:40].max()
    bgt=np.median(im[vi-35:vi-25,ui-2:ui+3]); bgb=np.median(im[vi+22:vi+30,ui-2:ui+3])
    def ext(prof,lo_bg,hi_bg,c):
        # half-max crossing from centre outward
        thr_top=(peak+lo_bg)/2; thr_bot=(peak+hi_bg)/2
        i=c
        while i>0 and prof[i]>thr_top: i-=1
        top=i+(prof[i+1]-thr_top)/(prof[i+1]-prof[i]+1e-9)
        j=c
        while j<len(prof)-1 and prof[j]>thr_bot: j+=1
        bot=j-(prof[j-1]-thr_bot)/(prof[j-1]-prof[j]+1e-9)
        return top,bot
    top,bot=ext(col,bgt,bgb,35)
    dv=bot-top
    # horizontal extent
    row=im[vi-2:vi+3,ui-60:ui+60].mean(0)
    pk=row[55:65].max(); bl=np.median(row[:10]); br=np.median(row[-10:])
    i=60
    while i>0 and row[i]>(pk+bl)/2: i-=1
    j=60
    while j<119 and row[j]>(pk+br)/2: j+=1
    dh=j-i
    r=ray(u,v); alpha=np.arccos(r[2])
    Zs=f*0.04/(dv)  # approx range from vertical extent
    t=0.157/(n@r)
    out[k]=dict(dv=dv,dh=dh,rs=Zs,rp=t)
    print('%2d orig %2d dv %.1f dh %.1f  range_size %.3f  range_plane %.3f  ratio %.3f'%(k,orig(k),dv,dh,Zs,t,Zs/t))
json.dump(out,open('scripts/size.json','w'))
