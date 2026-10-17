import cv2, numpy as np, sys
from common import frames
from tmpl import track
v=sys.argv[1]
fr=frames(v, gray=True)
n=len(fr); print(v,n)
# box template: box face region at frame 0
bbox=(560,200,900,350)   # inside box face
rbox=(200,380,1400,440) # truck body upper part (white side + top edge region)
cab=(1560,560,1800,760)
wheel=(1480,840,1700,1040)
res=[]
for f in [0,40,80,120,160,200,240,280,320,360,399]:
    b=track(fr,0,bbox,f,0,search=30)
    r=track(fr,0,rbox,f,0,search=40)
    c=track(fr,0,cab,f,0,search=30)
    w=track(fr,0,wheel,f,0,search=20)
    res.append((f,b[1],r[1],c[1],w[1]))
    print(f,'box dy %.2f (%.3f)'%(b[1],b[2]),'body dy %.2f (%.3f)'%(r[1],r[2]),'cab dy %.2f'%c[1],'wheel dy %.2f'%w[1])
R=np.array(res); t=R[:,0]/120
print('box linear fit px/s',np.polyfit(t,R[:,1],1), 'quad',np.polyfit(t,R[:,1],2))
print('body quad fit',np.polyfit(t,R[:,2],2))
