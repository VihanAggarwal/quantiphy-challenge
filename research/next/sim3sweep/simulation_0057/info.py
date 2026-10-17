import cv2,sys
for v in ["simulation_0019","simulation_0019_segmented","simulation_0021","simulation_0021_segmented","simulation_0033","simulation_0052","simulation_0055","simulation_0056"]:
    c=cv2.VideoCapture(f"/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4")
    print(v,c.get(cv2.CAP_PROP_FRAME_WIDTH),c.get(cv2.CAP_PROP_FRAME_HEIGHT),c.get(cv2.CAP_PROP_FPS),c.get(cv2.CAP_PROP_FRAME_COUNT))
