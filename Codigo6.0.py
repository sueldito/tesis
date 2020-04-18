# coding=utf-8
import numpy as np
import math
import cv2
import time
from picamera.array import PiRGBArray
from picamera import PiCamera

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640,480)) 

def actBackground (buff):	#calculamos la media de la matris q entramos
	bufferOrdenado = np.sort(buff,axis=0) # Ordenamos elemento a elemento del buffer
	bg = bufferOrdenado [int(len(buff)/2)] # Cogemos el frame de la posicion interrmedia (mediana )
	return bg
#Funcion que actualiza el buffer
def actBuffer(buff,fr,n):
	buff = np.roll(buff,n,axis = 0) # Rotamos los frames del buffer
	buff[0]=fr # Actualizamos el primer frame
	return buff
    
def main ():
    buffSize = 26 #Tamaño del Buffer
    buffer=np.empty((buffSize,480,640),np.uint8)
    #Inicializa variables de actualizacion de background#
    nAct = 0
    nmax = 30 # Numero de frames por cada actualizacion
    #Umbralización###
    threshLim = 24
    histLim = 4000
    
    
    for cap in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        frame = cap.array
        frameGris1 = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        frameGris = cv2.GaussianBlur(frameGris1,(5,5),0) #en nuestro programa tenemos  cv2.GaussianBlur(gris, (21, 21), 0)
        for i in range(buffSize):
            buffer[i] = frameGris
        background = buffer[0]
        print ('Espere 15 segundos para generar el background')
        f = cv2.getTickFrequency() 
        t1 = cv2.getTickCount()  
        n = 15
        while(n>0):
            t2 = cv2.getTickCount()
            frame = cap.array
            ja = (t2-t1)/f
            if (ja >= 0.5):
                n = n - 0.5
                print(n)
                frameGris1=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                frameGris = cv2.GaussianBlur(frameGris1,(5,5),0)
                # Actualizo el backgound
                buffer = actBuffer(buffer,frameGris,1)
                background = actBackground (buffer)
            cv2.imshow('frame',frame)
            cv2.imshow('background',background)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("s"):
                cv2.destroyAllWindows()
                break
        print('Background creado')
        print('-----------------')      
        while (1) :   
            frame = cap.array
            act = 0
            nAct= nAct+1
            print ('contando', nAct) #borrar
            if nAct>=nmax :  #nmax=30
				nAct = 0
				act=1
            if act == 1:
                background = actBackground (buffer)
            frame2 = frame.copy()
            frame3 = frame.copy()
            frameGris1=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            frameGris=cv2.GaussianBlur(frameGris1,(5,5),0)
            diff=cv2.absdiff(frameGris,background)
            hist=cv2.calcHist([diff],[0],None,[256],[0,256])
            if(hist.max()>=histLim):
                i=hist.argmax()
				while(hist[i]>=histLim or i>=255):
					i=i+1
				if(i>=255):
					thresh=255
				else:
					thresh=i+threshLim
            else:
                thresh=threshLim
        
        
        
        rawCapture.truncate(0)
       
if __name__ == "__main__":
    main()        
        