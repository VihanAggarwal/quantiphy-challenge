import cv2, numpy as np
# sub-pixel silhouette width of the ball from the red channel (bg green R~40, ball R~200+)
def widths(i):
    f=cv2.imread(f'frames/f{i:02d}.png').astype(float)
    R=f[...,2]; G=f[...,1]
    sig=R-G   # bg strongly negative, ball positive (orange)
    out=[]
    for y in range(268,292):
        row=sig[y,595:640]
        bg=np.median(np.r_[row[:5],row[-5:]]); pk=np.percentile(row,90)
        lvl=(bg+pk)/2
        idx=np.nonzero(row>lvl)[0]
        if len(idx)<3: continue
        a=idx[0]; b=idx[-1]
        xa=a-1+(lvl-row[a-1])/(row[a]-row[a-1]); xb=b+(row[b]-lvl)/(row[b]-row[b+1])
        out.append((y,xb-xa,595+(xa+xb)/2))
    out=np.array(out)
    # vertical extent at the centre column
    xc=int(round(np.median(out[:,2])))
    col=sig[255:300,xc-1:xc+2].mean(1)
    return out,xc,col
for i in [0,12,24]:
    out,xc,col=widths(i)
    print('frame',i,'max width %.2f'%out[:,1].max(),'at y',out[np.argmax(out[:,1]),0],'xc',xc)
    print('  widths',np.round(out[:,1],1))
    print('  col',np.round(col).astype(int))
