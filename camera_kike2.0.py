# coding=utf-8
#Importamos los paquetes necesarios
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
from matplotlib import pyplot as plt  #para hacer los ejes del histograma

# Inicializamos la cámara con resolución 640x480
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640,480)) 

width = 640
height = 480

time.sleep(0)
#      ###Umbralización###
threshLim = 24
histLim = 4000
blurKernel = 2

fondo = None

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                
    # Obtenemos el array en formato NumPy
    image = frame.array

    # Convertimos a escala de grises
    gris = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Aplicamos suavizado para eliminar ruido
    #gris = cv2.GaussianBlur(gris, (21, 21), 0)
    gris=cv2.GaussianBlur(gris,(2*blurKernel+1,2*blurKernel+1),0)
    
    if fondo is None:
        fondo = gris
            
    # Calculo de la diferencia entre el fondo y el frame actual
    resta = cv2.absdiff(fondo, gris)
    
    # Histograma de diff
    hist=cv2.calcHist([resta],[0],None,[256],[0,256])
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
    
    # Descomponemos el frame actual en el espacio de color es HSV
	frameHSV =cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
	frameS=frameHSV[:,:,1]
	# Umbralizamos el canal de saturacion para indicar zonas de baja saturacion
	frameS=cv2.GaussianBlur(frameS,(2*blurKernel+1,2*blurKernel+1),0)
	_,frameSthresh = cv2.threshold(frameS,10,255,cv2.THRESH_BINARY_INV)
	# Aislamos las zonas de baja saturacion de diff
	diffLS=cv2.bitwise_and (resta, resta , mask=frameSthresh) #Zonas de bajasaturacion
	diffHS = resta-diffLS #Zonas de alta saturacion
	#--------------Umbralizacion
	# Si la diferencia entre el frame actual y el background es mayor que el umbral, el pixel está en el foreground
	_,threshImgHS =cv2.threshold(diffHS,thresh,255,cv2.THRESH_BINARY)
	_,threshImgLS =cv2.threshold(diffLS,thresh +10,255,cv2.THRESH_BINARY)
	threshImg =threshImgHS+threshImgLS
    #contornosimg = threshImg.copy()
    
    umbral = cv2.threshold(resta, 75, 255, cv2.THRESH_BINARY)[1]
    umbral = cv2.dilate(umbral, None, iterations=2)
    contornosimg = umbral.copy()
   
    _,contornos,hierarchy=cv2.findContours(contornosimg,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    
     for c in contornos:
        # Eliminamos los contornos más pequeños
        if cv2.contourArea(c) < 10000:
            continue

        # Obtenemos el bounds del contorno, el rectángulo mayor que engloba al contorno
        (x, y, w, h) = cv2.boundingRect(c)
        # Dibujamos el rectángulo del bounds
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
    cv2.imshow("Imagen Movimiento", image)
    #cv2.imshow("Umbral", umbral)
    cv2.imshow("Resta", resta)

    