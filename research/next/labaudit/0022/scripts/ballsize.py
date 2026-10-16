import cv2, numpy as np, json
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/'
D='/home/user/quantiphy-challenge/research/next/labaudit/0022/'
T=json.load(open(S+'track_diff.json'))
fr=np.load(S+'fr0022x.npy').astype(float)
F=711.
crops=[]
for i in [5,15,20,25,30,35,40,44]:
    u,v=T['x'][i][:2]; u=int(round(u)); v=int(round(v))
    c=fr[i,v-16:v+17,u-16:u+17]
    # whiteness: min channel; table min channel ~ (blue) low
    w=c.min(2)
    tab=np.median(np.concatenate([w[0],w[-1],w[:,0],w[:,-1]]))
    top=np.percentile(w,99)
    frac=np.clip((w-tab)/(top-tab),0,1)
    A=frac.sum(); d_area=2*np.sqrt(A/np.pi)
    # width profile through centre at half max (horizontal)
    row=frac[16]; col=frac[:,16]
    wh=(row>0.5).sum(); hh=(col>0.5).sum()
    print(i,'area-diam %.1f px  half-max width %d height %d'%(d_area,wh,hh),' -> z(4cm, area) %.3f m'%(F*0.04/d_area))
    crops.append(cv2.resize(fr[i,v-16:v+17,u-16:u+17].astype(np.uint8),None,fx=8,fy=8,interpolation=cv2.INTER_NEAREST))
cv2.imwrite(D+'crop_ball_x.png',np.hstack(crops[:4])); cv2.imwrite(D+'crop_ball_x2.png',np.hstack(crops[4:]))
