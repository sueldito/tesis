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
rawCapture = PiRGBArray(camera, size=(640, 480)) 

width = 640
height = 480


# Tiempo de espera para que la cámara arranque
time.sleep(0.5)

# Inicializamos el primer frame a vacío.
# Nos servirá para obtener el fondo
fondo = None
object_classifier = cv2.CascadeClassifier("models/fullbody_recognition_model.xml")

# Capturamos frame a frame de la cámara
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # Obtenemos el array en formato NumPy
    image = frame.array

    # Convertimos a escala de grises
    gris = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Aplicamos suavizado para eliminar ruido
    gris = cv2.GaussianBlur(gris, (21, 21), 0)

    # Si todavía no hemos obtenido el fondo, lo obtenemos
    # Será el primer frame que obtengamos
    if fondo is None:
            fondo = gris

    # Calculo de la diferencia entre el fondo y el frame actual
    resta = cv2.absdiff(fondo, gris)
 
    # Aplicamos un umbral
    #umbral = cv2.threshold(resta, 75, 255, cv2.THRESH_BINARY)[1]
    #umbral = cv2.adaptiveThreshold (resta, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 115, 1)[1]
    umbral = cv2.threshold(resta, 125,255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Dilatamos el umbral para tapar agujeros
    umbral = cv2.dilate(umbral, None, iterations=2)

    # Copiamos el umbral para detectar los contornos
    contornosimg = umbral.copy()

    # Buscamos contorno en la imagen
    _,contornos, hierarchy = cv2.findContours(contornosimg,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    
    #hist=cv2.calcHist([contornosimg],[0],None,[256],[0,256])
  
 
    # Recorremos todos los contornos encontrados
    for c in contornos:
        # Eliminamos los contornos más pequeños
        if cv2.contourArea(c) < 10000:
            continue

        # Obtenemos el bounds del contorno, el rectángulo mayor que engloba al contorno
        (x, y, w, h) = cv2.boundingRect(c)
        # Dibujamos el rectángulo del bounds
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        #Dibujamos el centroide
        m=cv2.moments(c)
        x0=int(m['m10']/m['m00'])
        y0=int(m['m01']/m['m00'])
        cv2.circle(image,(int(x0),int(y0)),2,(0, 255, 0),-1)#Dibujamos el centroide
        
        #Dibujamos el elipse
        ellipse=cv2.fitEllipse(c)#ellipse=((center),( width,height of bounding rect),angle)
        cv2.ellipse(image,ellipse,(0, 255, 0),2) # Dibujamos la elipse
        (xx, yy),(ma,MA),angulo=cv2.fitEllipse(c)#ellipse=((center),( width,height of bounding rect),angle)
        cv2.ellipse(image,((xx, yy),(ma,MA),angulo),(0, 255, 0),2) # Dibujamos la elipse
        
        
        #−−−−−−−−−−−−−−−−−−−−−− Aspect ratio y angulo−−−−−−−−−−−−−−−−−−−−−−−−−
        #aspectRatio=h/w
        #angle=ellipse[2]+90
        #if(angle>180) :
        #    angle=angle-180
        #if(angle>90) :
        #    angle=180-angle
        
        #−−−−−−−−−−−−−−−−−−−−−−Deteccion−−−−−−−−−−−−−−−−−−−−−−−−−
        #if (aspectRatio<1 and aspectRatio>-1) and (angle<=45 and angle>-1):
            # Condicines de centroide
         #   if((x0>25 and x0<width-25) and ( y0>20 and y0<height-20)):
          #      print("caida detectada")
                # Histograma
           
        
     
    # Mostramos las diferentes capturas
    cv2.imshow("Imagen Movimiento", image)
    cv2.imshow("Umbral", umbral)
    cv2.imshow("Resta", resta)
    cv2.imshow("Contornos", contornosimg)
    #cv2.imshow("Fondo", fondo) 
    key = cv2.waitKey(1) & 0xFF
    
    #plt.plot(hist,color='gray')
    #plt.xlabel ('intesidad de iluminacion')
    #plt.ylabel ('cantidad de pixeles')
    #plt.show()  
    
    
   
    
    

    # Reseteamos el archivo raw para la siguiente captura
    rawCapture.truncate(0)
    

    # Con la letra s salimos de la aplicación
    if key == ord("s"):
        cv2.destroyAllWindows()
        break