import cv2, numpy as np, json, sys
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0253.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
B={r[0]:r for r in json.load(open('box0253.json'))}
for fi in [int(x) for x in sys.argv[1].split(',')]:
    cx,cy=B[fi][1],B[fi][2]
    M=cv2.getRotationMatrix2D((cx,cy),44.224,1.0)
    rot=cv2.warpAffine(fr[fi],M,(1920,1080),flags=cv2.INTER_CUBIC).astype(np.float32)
    H=75
    crop=rot[int(cy)-H:int(cy)+H,int(cx)-H:int(cx)+H]
    Y=crop@np.array([0.114,0.587,0.299],np.float32)
    # find the dark contact line row: min of row-mean luma in y in [20,45]
    rows=Y[H+20:H+45, H-30:H+30].mean(1); yl=20+int(np.argmin(rows))
    prof=Y[H+yl-1:H+yl+2].mean(0)
    xs=np.arange(-H,H)
    # dark line: threshold at midway between line darkness and neighbours
    core=np.median(prof[(xs>-20)&(xs<20)]); outside=np.median(np.r_[prof[xs<-65],prof[xs>60]])
    half=(core+outside)/2
    inl=np.where(prof<half)[0]
    j0=np.argmin(np.abs(xs)); a=j0; b=j0
    while a>0 and prof[a-1]<half: a-=1
    while b<len(xs)-1 and prof[b+1]<half: b+=1
    ea=xs[a-1]+(prof[a-1]-half)/(prof[a-1]-prof[a]) if a>0 else xs[a]
    eb=xs[b]+(half-prof[b])/(prof[b+1]-prof[b]) if b<len(xs)-1 else xs[b]
    # front-face body: row at y=0..10 luma profile, find left edge (bg->box) and right edge
    print(f'frame {fi} s={B[fi][3]:.0f}: contact line row y={yl}, core={core:.0f} outside={outside:.0f}; line from {ea:.1f} to {eb:.1f} -> length {eb-ea:.1f} px')
    for yy in (-30,-20,-10,0,10,20):
        p=Y[H+yy-1:H+yy+2].mean(0); g=np.gradient(p)
        L=xs[(xs>-70)&(xs<-20)][np.argmax(np.abs(g[(xs>-70)&(xs<-20)]))]
        R=xs[(xs>20)&(xs<70)][np.argmax(np.abs(g[(xs>20)&(xs<70)]))]
        print(f'   row y={yy:+d}: strongest left edge x={L}, right edge x={R}, width={R-L}')
