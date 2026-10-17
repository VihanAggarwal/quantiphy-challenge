import cv2,sys,os
out=os.path.dirname(os.path.abspath(__file__))+'/frames'
os.makedirs(out,exist_ok=True)
for v in ['captured_0053','captured_0053s','captured_0053x']:
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
    i=0
    while True:
        ok,f=c.read()
        if not ok: break
        if i%6==0 or i in (9,10,33,34):
            cv2.imwrite(f'{out}/{v}_{i:02d}.png',f)
        i+=1
    print(v,i)
