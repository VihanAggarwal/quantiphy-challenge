import cv2, numpy as np, json
def xmask(n):
    f=cv2.imread(f'frames/x_{n:02d}.png').astype(int)
    b,g,r=f[...,0],f[...,1],f[...,2]
    green=(g>150)&(g-r>80)&(g-b>80)
    m=(~green).astype(np.uint8)
    m[690:,1020:]=0  # watermark
    return m
if __name__=='__main__':
    for n in (0,12,24):
        m=xmask(n)
        k,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
        print('frame',n)
        for i in range(1,k):
            x,y,w,h,a=st[i]
            if a>200: print('  comp',i,'bbox x%d-%d y%d-%d w%d h%d area%d'%(x,x+w-1,y,y+h-1,w,h,a))
        cv2.imwrite(f'xmask_{n:02d}.png',m*255)
