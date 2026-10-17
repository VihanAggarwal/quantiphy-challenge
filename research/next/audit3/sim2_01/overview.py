import cv2, sys
clips=['simulation_0210','simulation_0213','simulation_0214','simulation_0215','simulation_0216','simulation_0216_segmented','simulation_0217']
out='/home/user/quantiphy-challenge/research/next/audit3/sim2_01/png/'
for c in clips:
    cap=cv2.VideoCapture(f'data/QuantiPhy/{c}.mp4')
    n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fps=cap.get(cv2.CAP_PROP_FPS)
    w=cap.get(3); h=cap.get(4)
    print(c,n,fps,w,h)
    frames=[]
    i=0
    while True:
        ok,f=cap.read()
        if not ok: break
        if i in (0,24):
            frames.append(f)
        i+=1
    print(' read',i)
    for k,f in zip((0,24),frames):
        cv2.imwrite(out+f'{c}_f{k}_small.png', cv2.resize(f,(960,540)))
