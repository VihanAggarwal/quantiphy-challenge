# Measure the letter corners in A2 frontal clips and ratio to the table silhouette width at the same row.
import cv2, numpy as np, sys
SCR='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad'
def load(vid, fi=0):
    cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
    for i in range(fi+1): ok,fr=cap.read()
    return fr
for vid in sys.argv[1:]:
    im=load(vid,0).astype(np.float32)
    b,g,r=im[:,:,0],im[:,:,1],im[:,:,2]
    score=(r-b)  # beige paper: r-b large (~60+), table dark green (r-b ~0..10)
    y0,y1,x0,x1=960,1015,1170,1410
    S=score[y0:y1,x0:x1]
    # print a coarse profile to choose thresholds
    paper=np.percentile(S,99); tab=np.percentile(S,20)
    thr=(paper+tab)/2
    print(vid,'paper r-b ~%.1f table ~%.1f thr %.1f'%(paper,tab,thr))
    M=S>thr
    rows=np.where(M.sum(1)>20)[0]
    # left/right extents per row (subpixel by linear crossing)
    out=[]
    for yy in rows:
        row=S[yy]
        idx=np.where(row>thr)[0]
        xl=idx[0]; xr=idx[-1]
        # subpixel
        if xl>0: xl_s=xl-1+(thr-row[xl-1])/(row[xl]-row[xl-1])
        else: xl_s=xl
        if xr<len(row)-1: xr_s=xr+(row[xr]-thr)/(row[xr]-row[xr+1])
        else: xr_s=xr
        out.append((yy+y0,xl_s+x0,xr_s+x0))
    out=np.array(out)
    for o in out: print('  y=%d  xl=%.1f xr=%.1f  w=%.1f'%(o[0],o[1],o[2],o[2]-o[1]))
    np.save(f'{SCR}/{vid}_letter_rows.npy',out)
