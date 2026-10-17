import cv2,numpy as np
img=np.full((700,1100,3),255,np.uint8)
cols={'0303':(255,0,0),'0305':(0,0,255),'0307':(0,160,0)}
allp=np.concatenate([np.load(f'P3_{k}.npy') for k in cols])
fm=np.median(allp[:,0]); lm=np.median(allp[:,1])
S=45
def to(px):
    return (int(550+(px[1]-lm)*S), int(350-(px[0]-fm)*S))
for g in range(-12,13,2):
    cv2.line(img,(int(550+g*S),0),(int(550+g*S),700),(220,220,220),1)
    cv2.line(img,(0,int(350-g*S)),(1100,int(350-g*S)),(220,220,220),1)
    cv2.putText(img,str(g),(2,int(350-g*S)),cv2.FONT_HERSHEY_SIMPLEX,0.4,(120,120,120),1)
for k,col in cols.items():
    P=np.load(f'P3_{k}.npy')
    for p in P: cv2.circle(img,to(p),3,col,-1)
cv2.putText(img,'top view: up=fore(V), right=lateral(right). blue 0303 red 0305 green 0307; grid 2 m',(10,690),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),1)
cv2.imwrite('frames/topview.png',img)
img=np.full((400,1100,3),255,np.uint8)
for k,col in cols.items():
    P=np.load(f'P3_{k}.npy')
    for p in P: cv2.circle(img,(int(550+(p[1]-lm)*S),int(200-(p[2]-np.median(allp[:,2]))*S)),3,col,-1)
cv2.imwrite('frames/rearview.png',img)
