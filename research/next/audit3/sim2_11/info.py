import cv2,sys
for v in ['simulation_0231','simulation_0232','simulation_0233','simulation_0233_segmented']:
    cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
    n=int(cap.get(7)); w=int(cap.get(3)); h=int(cap.get(4)); fps=cap.get(5)
    print(v,n,w,h,fps)
    for fi in [0,24]:
        cap.set(1,fi); ok,f=cap.read()
        cv2.imwrite(f'crops/{v}_f{fi}.png', cv2.resize(f,(960,540)))
