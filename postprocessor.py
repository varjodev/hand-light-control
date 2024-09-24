import utils
import numpy as np
import cv2
from collections import deque

class PostProcessor():
    def __init__(self, parameter_dict):
        self.params = parameter_dict
        self.frame_buffer = deque()
        self.fourier_buffer = deque()

    def processing_stack(self, frame):
        if self.params["postprocess_bool"]:
            frame = self.crop_square(frame)
            frame = self.rotate(frame)

            if self.params["blur"]:
                frame = self.blur(frame)

            if self.params["edges"]:
                frame = self.edges(frame)

            if self.params["average"]:
                frame = self.average(frame)

            if self.params["threshold"]:
                frame = self.threshold(frame)

        return frame

            

    def cvt_gray(self, frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame

    def crop_square(self, frame, dest_dim=None):
        dims = frame.shape[:2]
        min_dim = np.argmin(dims)
        if min_dim==0:
            return frame[:,:dims[min_dim],...]
        elif min_dim==1:
            return frame[:dims[min_dim],:,...]

    def rotate(self, frame):
        if self.params["rotation"]==0:
            return frame
        elif self.params["rotation"]==90:
            method = cv2.ROTATE_90_CLOCKWISE
        elif self.params["rotation"]==180:
            method = cv2.ROTATE_180
        elif self.params["rotation"]==270:
            method = cv2.ROTATE_90_COUNTERCLOCKWISE
        else:
            print("angle must be a multiple of 90")
            return

        return cv2.rotate(frame, method)

    def blur(self, frame, ksize = 7, c=5):
        return cv2.GaussianBlur(frame,(ksize,ksize),c)

    def average(self, frame, n=10):
        if self.frame_buffer and len(self.frame_buffer[0].shape) != len(frame.shape):
            self.frame_buffer = deque()

        if len(self.frame_buffer) > n:
            self.frame_buffer.pop()
        self.frame_buffer.appendleft(frame)
        return np.mean(self.frame_buffer,axis=0).astype(np.uint8)
    
    def threshold(self, frame):
        frame = self.blur(frame, ksize=3,c=5)
        return cv2.adaptiveThreshold(self.cvt_gray(frame),255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,-25)

    def edges(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.Laplacian(gray, cv2.CV_64F, ksize=5) 
        return np.abs(frame).astype(np.uint8)
        

    def increment_rot(self):
        self.params["rotation"] += 90
        if self.params["rotation"] == 360:
            self.params["rotation"] = 0

    def toggle_param(self, name):
        self.params[name] = False if self.params[name] else True

    def fft_filter(self, frame):
        """ sad attempts at filtering banding noise in fourier domain
        """
        if dims is None:
            dims = frame.shape
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame
        # gray = ndimage.rotate(gray,2,reshape=False)
        # crop_amt = 20
        # frame = utils.crop_img(gray,[frame.shape[0]-crop_amt, frame.shape[1]-crop_amt])
        # gray = utils.crop_img(gray,[gray.shape[0]-crop_amt, gray.shape[1]-crop_amt])
        # gray = rgb_frame[:,:,2]
        fft_complex = utils.fft2d(gray)
        fft_phase = fft_complex.imag

        # complex_frame = np.empty(fft_complex.shape, dtype=complex)
        # complex_frame.real = fft_complex.real
        # complex_frame.imag = fft_phase
        # fft_frame = utils.ifft2d(complex_frame)
        # fft_frame = cv2.normalize(np.abs(fft_frame),None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX).astype(np.uint8)
            
        fft_frame = np.log(np.abs(fft_complex))
        # rrr = 3
        # fft_frame[dims[0]//2-rrr:dims[0]//2+rrr,dims[1]//2-rrr:dims[1]//2+rrr] = 0
        fft_frame = cv2.normalize(fft_frame,None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX).astype(np.uint8)
        
        # print(fft_frame.dtype)

        if self.params["fft_filter"]:
            thrs_in = cv2.normalize(np.log(np.abs(fft_complex)),None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX).astype(np.uint8)
            
            # ret, fft_thrs = cv2.threshold(thrs_in, 0.5, 1, cv2.THRESH_BINARY)
            fft_thrs = cv2.adaptiveThreshold(thrs_in,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,-25)
            if R is None:
                [X, Y] = np.meshgrid(np.linspace(1,dims[1],dims[1]),np.linspace(1,dims[0],dims[0]))-np.mean(np.linspace(1,dims[1],dims[1]))
                R = np.sqrt(X**2+Y**2)
                rad = round(dims[0]*0.05)
            
            # fft_thrs[:,dims[1]//2-rad:dims[1]//2+rad] = 0
            y_crop = 10
            # fft_thrs[:dims[0]//2-y_crop,:] = 0
            # fft_thrs[dims[0]//2+y_crop:,:] = 0
            # fft_thrs[dims[0]//2,:] = 0
            # # fft_thrs[~dims[0]//2,:] = 0
            # fft_thrs[:,dims[1]//2-rad:dims[1]//2+rad] = 0
            # fft_thrs[dims[1]//2-rad:dims[1]//2+rad,:] = 0
            fft_thrs[dims[0]//2-3:dims[0]//2+3, dims[0]//2-3:dims[0]//2+3] = 0
            peaks = np.argwhere(fft_thrs == 255)

            # print(peaks)
            # print(len(peaks))

            real_mean = np.mean(fft_complex.real)

            if np.any(peaks) and len(self.fourier_buffer) > 2:
                
                wnd_y = 5
                wnd_x = 5
                for peak in peaks:
                    # fft_complex.real[peak[0], peak[1]] = complex_frame.real[peak[0], peak[1]]
                    # vals = []
                    # for i in range(3):
                    #     vals.append(fourier_buffer[i][peak[0], peak[1]])
                    # fft_complex.real[peak[0], peak[1]] = np.mean(vals)
                    if 0  < peak[1] < dims[1]-1 and  dims[0]//2 -10 < peak[0] < dims[0]//2 + 10:
                        # print(peak)
                        h1 = peak[0]-wnd_y
                        h2 = peak[0]+wnd_y
                        w1 = peak[1]-wnd_x if peak[1]-wnd_x > wnd_x else wnd_x
                        w2 = peak[1]+wnd_x if peak[1]+wnd_x < dims[1]-wnd_x else dims[1]-wnd_x
                        # print(h1,h2,w1,w2)
                        # print(peak)
                        # fft_complex.real[h1:h2,w1:w2] = cv2.GaussianBlur(fft_complex.real[h1:h2,w1:w2], (3,3),0)
                        # fft_complex.real[peak[0],peak[1]] = np.mean(fft_complex.real[h1:h2,w1:w2])
                        fft_complex.real[peak[0],peak[1]] = fft_complex.real[peak[1],peak[0]]
                        # print(peaks)


            # Make complex
            complex_frame = np.empty(fft_complex.shape, dtype=complex)
            complex_frame.real = fft_complex.real
            complex_frame.imag = fft_phase
            fft_frame = utils.ifft2d(complex_frame) #fft_thrs

            if len(self.fourier_buffer) > 3:
                self.fourier_buffer.pop()
            self.fourier_buffer.appendleft(complex_frame.real)

            # Show thresholded filtered
            # processed = cv2.normalize(np.log(utils.fft2d(fft_frame).real),None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX).astype(np.uint8)
            # fft_thrs_processed = cv2.adaptiveThreshold(processed,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,-25)
            fft_thrs_processed = np.log(np.abs(complex_frame))
            fft_thrs_processed = cv2.normalize(np.abs(fft_thrs_processed),None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX).astype(np.uint8)
            # ret, fft_thrs_processed = cv2.threshold(fft_thrs_processed, 140, 255, cv2.THRESH_BINARY)
            fft_thrs_processed = cv2.adaptiveThreshold(fft_thrs_processed,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,-25)
            
            fft_thrs_processed = cv2.normalize(np.abs(fft_thrs_processed),None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX).astype(np.uint8)
            fft_thrs_processed = cv2.cvtColor(fft_thrs_processed, cv2.COLOR_GRAY2BGR) if len(frame.shape) == 3 else fft_frame
            
            
            fft_thrs = cv2.normalize(np.abs(fft_thrs),None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX).astype(np.uint8)
            fft_thrs = cv2.cvtColor(fft_thrs, cv2.COLOR_GRAY2BGR) if len(frame.shape) == 3 else fft_frame
            
            # print(fft_frame.shape, frame.shape)
            
            fft_frame = cv2.normalize(np.abs(fft_frame),None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX).astype(np.uint8)
            # print(fft_frame.dtype)
            fft_frame = cv2.cvtColor(fft_frame, cv2.COLOR_GRAY2BGR) if len(frame.shape) == 3 else fft_frame
            # print(fft_frame.shape, frame.shape)
            # print(fft_frame.dtype, frame.dtype)
            frame = cv2.hconcat([fft_frame, fft_thrs, fft_thrs_processed])

        else:
            # gray = ndimage.rotate(gray,-10,reshape=True)
            fft_frame = cv2.cvtColor(fft_frame, cv2.COLOR_GRAY2BGR) if len(frame.shape) == 3 else fft_frame
            # print(fft_frame.shape, frame.shape)
            # print(fft_frame.dtype, frame.dtype)
            frame = cv2.hconcat([frame, fft_frame])