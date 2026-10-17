import cv2, numpy as np
im = cv2.imread('frames/f0010/simulation_0010_f058.png')
g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
g = cv2.GaussianBlur(g,(0,0),1.2)
gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
def edge_line(y0, x0, x1, sign, half=10, step=2):
    pts=[]
    for x in range(x0,x1,step):
        col = gy[y0-half:y0+half+1, x]*sign
        k = int(np.argmax(col))
        if 1<=k<len(col)-1 and col[k]>8:
            a,b,c = col[k-1],col[k],col[k+1]; off = 0.5*(a-c)/(a-2*b+c)
            pts.append((x, y0-half+k+off, col[k]))
    pts=np.array(pts)
    if len(pts)<10: return None
    # robust fit
    for it in range(3):
        A=np.c_[pts[:,0], np.ones(len(pts))]; m,c=np.linalg.lstsq(A,pts[:,1],rcond=None)[0]
        r=pts[:,1]-(m*pts[:,0]+c); s=np.median(np.abs(r))*1.5+0.3
        pts=pts[np.abs(r)<3*s]
    return m, c, len(pts), np.std(r)
# scan for horizontal edges in a vertical strip to find candidate rows
for xs in [(300,420),(480,560),(700,800)]:
    prof = np.abs(gy[700:1200, xs[0]:xs[1]]).mean(1)
    rows = [700+i for i in range(2,len(prof)-2) if prof[i]==prof[max(0,i-4):i+5].max() and prof[i]>12]
    print('strip',xs,'edge rows',rows)
print('---- beam fits (full-res coords)')
cands = [(752,220,880),(777,220,880),(860,250,880),(877,250,880),(1039,250,880),(1056,250,880),(1160,230,890)]
for (y0,x0,x1) in cands:
    for sign in (1,-1):
        r = edge_line(y0,x0,x1,sign,half=7)
        if r: print(y0, sign, 'slope %.5f  y@560 %.2f  n=%d  rms %.2f'%(r[0], r[0]*560+r[1], r[2], r[3]))
