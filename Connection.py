import cv2
import numpy as np
from keras.models import load_model
import tensorflow_hub as hub
import socket
import time

#Variable global de reconocimiento
global_variable = 0

#Clase para crear el socket y sus diferentes metodos.
class Kernel:

    def __init__(self, ipV4: str = "172.18.9.7", port: int = 6400, baud_rate: int = 9600) -> None:

        self.ipV4 = ipV4  # netstat -an, for view al ip address and port
        self.port = port
        self.__baud_rate = baud_rate

    def connect(self) -> str:

        self.ret = None

        self.kernel = socket.socket()

        try:
            self.kernel.connect((self.ipV4, self.port))
            self.ret = self.kernel.recv(1024)

        except TimeoutError:
            print(" -> Time up, try again later")

        except Exception as error:
            print(" -> An error has occurred " + type(error).__name__)

        return "Successful connection" if (self.ret is not None) else "Failed connection"

    # {message[0]}{message[1]}{message[2]}Tuple[str,...]
    def send(self, message: str = '000000000000') -> str:

        try:
            self.kernel.send(bytes(f"{message}", "utf-8"))  # type: ignore

            time.sleep(1)

        except ConnectionResetError:

            print(" -> An error has occurred: ConnectionResetError," + " Stablishing connection again")
            self.kill()
            self.connect()

        except Exception as error:
            print(type(error).__name__)
            self.kill()
            self.connect()
            return " -> Broken connection"

        return " -> Message sent"

    def kill(self):
        self.kernel.shutdown(socket.SHUT_WR)
        self.kernel.close()

# Carga el modelo entrenado
path = 'C:/Users/PATH/modelo_prueba1.h5' #Modelo de Keras, previamente entrenado
model = load_model(
    path,
    custom_objects={'KerasLayer': hub.KerasLayer}
)

# Define las clases
classes = ['Carnes', 'Lechugas', 'Panes', 'Tomates'] #Ingredientes Basicos de la Hamburguesa

# Abre la cámara
cap = cv2.VideoCapture(0)

#Funcion para en donde se le toma una foto y se analiza, para enviar el dato.
def Reconocimiento():
    while True:
        # Captura un frame de la cámara
        ret, frame = cap.read()

        # Muestra el frame en una ventana
        cv2.imshow('Camera', frame)

        # Espera a que se presione la tecla 'f' para hacer captura
        if cv2.waitKey(1) == ord('f'):
            # Guarda la foto en la ubicación del archivo Python
            cv2.imwrite('foto.png', frame)

            # Carga la imagen y la procesa para hacer la predicción
            img = cv2.imread('foto.png')
            img = cv2.resize(img, (224, 224))
            img = np.expand_dims(img, axis=0)
            img = img / 255.0

            # Hace la predicción usando el modelo
            predictions = model.predict(img)
            class_index = np.argmax(predictions)
            class_name = classes[class_index]
            percentage = predictions[0][class_index] * 100

            # asigna un valor de variable a cada clase
            carnes = 0
            lechugas = 1
            panes = 2
            tomates = 3

            # obtiene el valor de variable correspondiente a la clase con mayor probabilidad
            valor_clase = -1
            if class_name == 'Carnes':
                valor_clase = carnes
                print(valor_clase)
            elif class_name == 'Lechugas':
                valor_clase = lechugas
                print(valor_clase)
            elif class_name == 'Panes':
                valor_clase = panes
                print(valor_clase)
            elif class_name == 'Tomates':
                valor_clase = tomates
                print(valor_clase)

            # Muestra el resultado
            print(f'La imagen es de la clase ( {class_name} ) con un {percentage:.2f}% de confianza')

            #Envio de variable global
            global global_variable
            global_variable = valor_clase

            time.sleep(2)
            print("El programa se ha cerrado con exito")
            break

#Intancia de la clase Kernel
k = Kernel(ipV4="172.18.9.7", port=6400, baud_rate=9600) #IP y Puerto para la creacion del Socket
k.connect()

#Llamado a la funciones en orden de bucle
while True:
    for i in range(30): #Al menos 30 imagenes analizadas
        Reconocimiento() #Funcion Reconocimiento, permite tomar la imagen para analizarla.
        response = k.send(str(global_variable)) #Envio de variable al metodo Send, para enviar dato al RobotStudio
        print(f'La variable global almacenada es: {global_variable}') #Verificacion de la variable enviada.
        print(response) #Respuesta del Socket
        print(i) #Imprime la iteracion del bucle para llevar un control.
    # Libera la cámara y cierra las ventanas
    k.kill()
    cap.release()
    cv2.destroyAllWindows()
    break
