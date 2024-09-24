import cv2
import numpy as np
from numpy.fft import fft2, ifft2, ifftshift, fftshift

def cv2rotate90(img, angle):
    if angle==0:
        return img
    elif angle==90:
        method = cv2.ROTATE_90_CLOCKWISE
    elif angle==180:
        method = cv2.ROTATE_180
    elif angle==270:
        method = cv2.ROTATE_90_COUNTERCLOCKWISE
    else:
        print("angle must be a multiple of 90")
        return

    return cv2.rotate(img, method)

def crop_img(arr, dest_dim, debug=False):
        src_dim = arr.shape
        src_dim = np.array(src_dim)
        dest_dim = np.array(dest_dim)
        
        h1 = src_dim[0]//2-dest_dim[0]//2
        h2 = src_dim[0]//2+dest_dim[0]//2 + (0 if dest_dim[0] % 2 == 0 else 1)
        w1 = src_dim[1]//2-dest_dim[1]//2
        w2 = src_dim[1]//2+dest_dim[1]//2 + (0 if dest_dim[1] % 2 == 0 else 1)

        if debug:
            print("=Inside crop=")
            print("src_dims", src_dim)
            print("dest_dim", dest_dim)
            print("h_limits:", [h1,h2])
            print("w_limits:", [w1,w2])

        return arr[h1:h2,w1:w2]


def crop_square(arr):
    dims = arr.shape[:2]
    min_dim = np.argmin(dims)
    if min_dim==0:
        return arr[:,:dims[min_dim],...]
    elif min_dim==1:
        return arr[:dims[min_dim],:,...]
    
def fft2d(img):
    return fftshift(fft2(img))

def ifft2d(img):
    return ifft2(ifftshift(img))