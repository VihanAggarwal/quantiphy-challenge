from common import *
img=cv2.imread('fr/simulation_0064_000.png').astype(np.float32).mean(2)
m=cv2.blur(img,(7,7)); s=np.sqrt(np.maximum(cv2.blur(img*img,(7,7))-m*m,0))
cv2.imwrite('fr/std64.png', np.clip(s*10,0,255).astype(np.uint8)[::2,::2])
np.save('std64.npy', s.astype(np.float16))
