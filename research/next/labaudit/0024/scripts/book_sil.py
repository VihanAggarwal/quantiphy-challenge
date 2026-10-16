import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit/0024/scripts')
from slopeplane import *
# point on slope plane with slope coords (across, along, h) -> image
def img(ac,al,h):
    X=BR+e*ac/100+up_dir*al/100+ns*h/100
    return np.array([711*X[0]/X[2]+640,711*X[1]/X[2]+360])
# measured silhouette at x~780: top 353, pages bottom ~393
ac=11  # across position (cm) near the book middle
for W in [7,8,9,10,11.3]:
    top=img(ac,29.6,1.46); topfront=img(ac,29.6-W,1.46); botfront=img(ac,29.6-W,0)
    print('W=%.1f  top-face up edge v=%.1f, top-face down edge v=%.1f, pages bottom v=%.1f (u %.0f)'%(W,top[1],topfront[1],botfront[1],botfront[0]))
# find along of up edge so that v=353.5 at h=1.46, and along of the pages bottom at v=393 (h=0)
def along_for_v(v,h,ac=11):
    lo,hi=0,40
    for _ in range(60):
        m=(lo+hi)/2
        if img(ac,m,h)[1]>v: lo=m
        else: hi=m
    return m
for ac in [5,11,17]:
    a_up=along_for_v(353.5,1.46,ac); a_dn=along_for_v(383.5,1.46,ac); a_pg=along_for_v(393,0,ac)
    print('across %d: up edge along %.1f, top-face down edge %.1f -> W_top %.1f ; pages bottom %.1f -> W_sil %.1f'%(ac,a_up,a_dn,a_up-a_dn,a_pg,a_up-a_pg))
