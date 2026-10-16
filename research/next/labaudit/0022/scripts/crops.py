import cv2, numpy as np
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/'
D='/home/user/quantiphy-challenge/research/next/labaudit/0022/'
fr=np.load(S+'fr0022x.npy'); fo=np.load(S+'fr0022.npy')
def crop(im,u,v,h=60,z=5,name=''):
    c=im[v-h:v+h,u-h:u+h]; c=cv2.resize(c,None,fx=z,fy=z,interpolation=cv2.INTER_NEAREST)
    # grid every 10px
    for k in range(0,2*h,10):
        cv2.line(c,(k*z,0),(k*z,2*h*z-1),(0,0,255) if (u-h+k)%50==0 else (60,60,60),1)
        cv2.line(c,(0,k*z),(2*h*z-1,k*z),(0,0,255) if (v-h+k)%50==0 else (60,60,60),1)
    cv2.imwrite(D+name,c)
crop(fr[24],230,610,name='crop_x_nearleft.png')
crop(fr[24],665,520,name='crop_x_nearright.png')
crop(fr[24],290,415,name='crop_x_farleft.png')
crop(fr[24],600,365,name='crop_x_farright.png')
