import cv2, numpy as np
D='/home/user/quantiphy-challenge/research/next/labaudit/0024/'
im=cv2.imread(D+'frames/medo_rest.png').astype(float)
b,g,r=im[...,0],im[...,1],im[...,2]
br=b-r; L=im.mean(2)
for x in range(498,650,8):
    col_br=br[452:505,x]; col_L=L[452:505,x]
    # table: br strongly negative (< -35); teal: br > 0 ; pages: cream br ~ -10..-30 & L high
    s=''.join('T' if a>5 else ('t' if a>-5 else ('p' if (l>150 and a>-35) else ('.' if a<-35 else '-'))) for a,l in zip(col_br,col_L))
    print(x, s)
