import cv2, numpy as np
fr=[cv2.imread(f'frames/o_{n:02d}.png').astype(float) for n in range(0,48)]
med=np.median(np.stack(fr),0)
g=cv2.GaussianBlur(med.mean(2),(0,0),0.8)
gx=np.zeros_like(g); gx[:,1:-1]=(g[:,2:]-g[:,:-2])/2
def sub(prof,i):
    a,b,c=prof[i-1],prof[i],prof[i+1]; d=a-2*b+c
    return i+(0.5*(a-c)/d if d!=0 else 0)
print('row  L  R  W  (gradient extrema)')
for y in range(398,452,2):
    pl=gx[y,540:562]; pr=gx[y,566:590]
    il=np.argmax(pl); ir=np.argmin(pr)
    xl=540+sub(pl,il) if 0<il<len(pl)-1 else np.nan
    xr=566+sub(pr,ir) if 0<ir<len(pr)-1 else np.nan
    print(y,'%.1f %.1f %.1f   gl %.0f gr %.0f'%(xl,xr,xr-xl,pl[il],pr[ir]))
for n in (0,10,20,34,47):
    im=cv2.imread(f'frames/x_{n:02d}.png').astype(int)
    m=~((im[...,1]>200)&(im[...,2]<80)&(im[...,0]<80))
    s=m[395:455,540:590]
    ys=np.where(s.any(1))[0]
    ws=[(int(r+395),int(np.where(s[r])[0].max()-np.where(s[r])[0].min()+1)) for r in ys]
    print('x',n,ws[::3])
