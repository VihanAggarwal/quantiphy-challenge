import cv2, numpy as np
out='/home/user/quantiphy-challenge/research/next/labaudit/0028/frames'
F=711;CX=640;CY=360
def width(fi,render='captured_0028x'):
    f=cv2.imread(f'{out}/{render}_{fi:02d}.png').astype(float)
    g=f.mean(2)
    m=(g>150); m[415:,:]=False if fi in (26,36,37,46,47) else m[415:,:]
    m[470:,:]=False
    n,lab,st,cen=cv2.connectedComponentsWithStats(m.astype(np.uint8))
    k=1+np.argmax(st[1:,4]); x0,y0,w,h,a=st[k]
    cx,cy=cen[k]
    # peak brightness inside
    pk=np.percentile(g[lab==k],90)
    ws=[]
    for y in range(y0+2,y0+h-2):
        row=g[y,x0-6:x0+w+6]; thr=pk/2
        idx=np.nonzero(row>thr)[0]
        if len(idx)<3: continue
        i0=idx[0]; i1=idx[-1]
        xl=i0-1+(thr-row[i0-1])/(row[i0]-row[i0-1]); xr=i1+(row[i1]-thr)/(row[i1]-row[i1+1])
        ws.append(xr-xl)
    ws=np.array(ws)
    return cx,cy,h,np.max(ws),np.percentile(ws,75),pk
for fi in list(range(0,12,2))+list(range(16,49)):
    cx,cy,h,wmax,w75,pk=width(fi)
    print(fi,f'c=({cx:.1f},{cy:.1f}) h={h} wmax={wmax:.2f} w75={w75:.2f} pk={pk:.0f}  range@wmax={0.040*F/wmax:.3f}')
