# Wireless Hand Light Control

## Video stream from a wireless camera
A small ESP32-CAM board is used to capture video and send it through WiFi and an HTTP API to the computer.
The code used was a stock code, that communicates with the camera board and hosts an HTTP server using an ESP32.
Reading the code I found the API endpoints to get the stream and control the camera.

## The video stream is processed with Python and OpenCV
The video is read with OpenCV on a PC with Python and processing can be applied.

## Detecting hands and counting fingers
MediaPipe library is used to run a pre-trained two-stage hand landmark detection inference model. 
First, the model finds the location of hands and feeds the ROI into the second stage, where different landmark points on a hand, e.g. base of the palm, finger joints and fingertips 
are inferred. From this the the model outputs relative coordinates of hand landmarks in the image.

Comparing relative distances between different hand landmarks allows to count the number of fingers. 
For example if we compare the distance from the base of the palm to the beginning of the index finger and the distance from the beginning of the index finger to the fingertip, 
if the distances are similar, we can assume the finger is up, while if the distance from the index base to index tip is relatively smaller, we can assume that the finger is down.
If we use absolute distances, the threshold is difficult to set because hand can appear as different sizes depending on the distance and individual, but the relative comparison has less variation.

## Controlling the light with fingers
Finally, depending on the number of fingers being up, commands are sent to a Philips Hue light through Wifi with a chosen mapping. For example [0,1,2,3,4,5] fingers -> [0,50,100,150,200,255] brightness



### Notes:
Too much time was used to try to filter banding noise artifacts in the fourier space unsuccesfully