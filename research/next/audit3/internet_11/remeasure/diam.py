import cv2, numpy as np
p='data/QuantiPhy/internet_0047.mp4'
c=cv2.VideoCapture(p); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
tr=np.loadtxt('research/next/audit3/internet_11/remeasure/track47.txt')
def edge(prof, lo, hi):
    # prof: values; find crossing of half between lo-level and hi-level
    pass
for row in tr:
    i,x,y,w,h,cx,cy=row; i=int(i)
    if i<4 or i>21: continue
    f=fr[i].astype(np.float32)
    xm=int(x+w/2)
    out=[]
    for dx in range(-30,31,5):
        col=f[:,xm+dx,:]
        # use red-blue: ball is orange-brown, wood is tan; use V channel brightness (sum)
        s=col.sum(axis=1)
        y0=int(y); y1=int(y+h)
        # top edge: search in [y0-30,y0+40] for max negative gradient
        sm=np.convolve(s,np.ones(3)/3,'same')
        gtop=sm[y0-30:y0+40]; 
        # half crossing
        outside=np.median(sm[y0-40:y0-15]); inside=np.median(sm[y0+30:y0+50])
        half=(outside+inside)/2
        seg=sm[y0-30:y0+40]
        k=np.nonzero((seg[:-1]-half)*(seg[1:]-half)<=0)[0]
        if len(k)==0: continue
        kk=k[0]; t=(half-seg[kk])/(seg[kk+1]-seg[kk]); top=y0-30+kk+t
        outside2=np.median(sm[y1+15:y1+40]); inside2=np.median(sm[y1-50:y1-30])
        half2=(outside2+inside2)/2
        seg=sm[y1-40:y1+30]
        k=np.nonzero((seg[:-1]-half2)*(seg[1:]-half2)<=0)[0]
        if len(k)==0: continue
        kk=k[-1]; t=(half2-seg[kk])/(seg[kk+1]-seg[kk]); bot=y1-40+kk+t
        out.append((dx,top,bot,bot-top))
    out=np.array(out)
    print(i,'xm',xm,'D max %.1f median %.1f'%(out[:,3].max(),np.median(out[:,3])), ' '.join('%.0f'%v for v in out[:,3]))
