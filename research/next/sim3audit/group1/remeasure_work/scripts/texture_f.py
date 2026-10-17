import numpy as np, cv2
bg=np.load('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/bg_tunnel.npy').astype(float)
yh=540.0
def acf_widths(p):
    p=p-cv2.GaussianBlur(p,(0,0),6)
    p=p-p.mean()
    win=np.outer(np.hanning(p.shape[0]),np.hanning(p.shape[1]))
    F=np.fft.fft2(p*win)
    A=np.fft.fftshift(np.real(np.fft.ifft2(np.abs(F)**2)))
    A/=A.max()
    cy,cx=np.array(A.shape)//2
    # half-width at half max along x and y (linear interp)
    def hw(prof):
        for k in range(1,len(prof)):
            if prof[k]<0.5:
                return k-1+(prof[k-1]-0.5)/(prof[k-1]-prof[k])
        return np.nan
    wx=(hw(A[cy,cx:])+hw(A[cy,cx::-1]))/2
    wy=(hw(A[cy:,cx])+hw(A[cy::-1,cx]))/2
    return wx,wy
for yc in [760,800,850,900,950,1000,1040]:
    for xc in [700,1000,1150]:
        h=20 if yc<850 else 30
        p=bg[yc-h:yc+h, xc-80:xc+80]
        wx,wy=acf_widths(p)
        r=wy/wx
        print(yc,xc,round(wx,2),round(wy,2),'ratio',round(r,3),'f_est',round((yc-yh)/r,0))
