import cv2
import numpy as np
import os


'''
- Integracion de yolo con opencv 
- Reconocimiento de objetos en imagenes 
- Determinacion de color del objeto en HSV
- Actualizacion de stock segun el reconocimiento de imagenes del lote
'''


def load_yolo()->tuple:
    net = cv2.dnn.readNet("TP_Arch_config/yolov3.weights", "TP_Arch_config/yolov3.cfg")
    classes: list = []
    with open("TP_Arch_config/coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]

    output_layers: list = [layer_name for layer_name in net.getUnconnectedOutLayersNames()]
    colors = np.random.uniform(0, 255, size=(len(classes), 3))

    return net, classes, colors, output_layers


def load_image(img_path: str)->tuple:
    # image loading
    img = cv2.imread(img_path)
    img = cv2.resize(img, None, fx=0.4, fy=0.4)
    height, width, channels = img.shape

    return img, height, width, channels


def detect_objects(img: list, net, output_layers: list)->tuple:
    blob: list = cv2.dnn.blobFromImage(img, scalefactor=0.00392, size=(320, 320), mean=(0, 0, 0), swapRB=True, crop=False)
    net.setInput(blob)
    outputs: list = net.forward(output_layers)

    return blob, outputs


def get_box_dimensions(outputs: list, height: int, width: int)->tuple:
    boxes: list = []
    config: list = []
    class_ids: list = []
    for output in outputs:
        for detect in output:
            scores: list = detect[5:]
            class_id = np.argmax(scores)
            conf: float = scores[class_id]
            if(conf > 0.3):
                center_x: int = int(detect[0] * width)
                center_y: int = int(detect[1] * height)
                w: int = int(detect[2] * width)
                h: int = int(detect[3] * height)
                x: int = int(center_x - w/2)
                y: int = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                config.append(float(conf))
                class_ids.append(class_id)

    return boxes, config, class_ids


def draw_labels(boxes: list, config: list, colors: list, class_ids: list, classes: list, img: list, fle_name: str)->str:
    indexes: list = cv2.dnn.NMSBoxes(boxes, config, 0.5, 0.4)
    font: int = cv2.FONT_HERSHEY_PLAIN
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label: str = str(classes[class_ids[i]])
            color: list = colors[i]
            cv2.rectangle(img, (x,y), (x+w, y+h), color, 2)
            cv2.putText(img, label, (x, y - 5), font, 1, color, 1)

    # Muesto imagen por 3 segundos
    cv2.imshow(fle_name, img)
    cv2.waitKey(2000)
    cv2.destroyWindow(fle_name)

    return label


def is_green(img: list)->bool:
    img_hsv: list = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([45, 100, 20])
    upper = np.array([65, 255, 255])

    mask: list = cv2.inRange(img_hsv, lower, upper)
    img_result: list = cv2.bitwise_and(img, img, mask=mask)

    has_green: float = np.sum(img_result) / np.sum(img_hsv)
    if(has_green > 0.07):
        return True
    else:
        return False


def is_red(img: list)->bool:
    img_hsv: list = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 155, 20])
    upper = np.array([10, 255, 255])

    mask: list = cv2.inRange(img_hsv, lower, upper)
    img_result: list = cv2.bitwise_and(img, img, mask=mask)

    has_red: float = np.sum(img_result) / np.sum(img_hsv)
    if (has_red > 0.07):
        return True
    else:
        return False


def is_blue(img: list)->bool:
    img_hsv: list = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([85, 150, 20])
    upper = np.array([120, 255, 255])

    mask: list = cv2.inRange(img_hsv, lower, upper)
    img_result: list = cv2.bitwise_and(img, img, mask=mask)

    has_blue: float = np.sum(img_result) / np.sum(img_hsv)
    if (has_blue > 0.07):
        return True
    else:
        return False


def is_black(img: list)->bool:
    img_hsv: list = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 0, 20])
    upper = np.array([0, 0, 255])

    mask: list = cv2.inRange(img_hsv, lower, upper)
    img_result: list = cv2.bitwise_and(img, img, mask=mask)

    has_black: float = np.sum(img_result) / np.sum(img_hsv)
    if (has_black > 0.07):
        return True
    else:
        return False


def is_yellow(img: list)->bool:
    img_hsv: list = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([25, 100, 20])
    upper = np.array([30, 255, 255])

    mask: list = cv2.inRange(img_hsv, lower, upper)
    img_result: list = cv2.bitwise_and(img, img, mask=mask)

    has_yellow: float = np.sum(img_result) / np.sum(img_hsv)
    if(has_yellow > 0.07):
        return True
    else:
        return False


def get_color(img_path: str)->list:
    img: list = cv2.imread(img_path)

    if(is_green(img)):
        return "verde"
    elif(is_red(img)):
        return "rojo"
    elif(is_blue(img)):
        return "azul"
    elif(is_yellow(img)):
        return "amarillo"
    elif(is_black(img)):
        return "negro"


def actualizar_stock(productos: dict, color: str, clasificacion: str)->None:
    if(clasificacion == "bottle"):
        print(f"Botella de color {color}")
        productos[1334]["color"][color] += 1
    else:
        print(f"Vaso de color {color}")
        productos[568]["color"][color] += 1


def image_detect(img_path: str, fle_name: str, productos: dict)->None:
    model, classes, colors, output_layers = load_yolo()
    image, height, width, channels = load_image(img_path)
    blob, outputs = detect_objects(image, model, output_layers)
    boxes, config, class_ids = get_box_dimensions(outputs, height, width)
    label: str = draw_labels(boxes, config, colors, class_ids, classes, image, fle_name)

    if(label.lower() != "bottle" and label.lower() != "cup"):
        print("PROCESO DETENIDO, se reanuda en 1 minuto")
    else:
        color: list = get_color(img_path)
        actualizar_stock(productos, color, label.lower())


'''
- Implementacion de funciones integradas
'''


def categorizar_archivos(productos: dict, productos_archivos: list)->dict:
    # integracion de yolo+opencv
    for i in range(len(productos_archivos)):
        image_detect(f"TP_Arch_config/Lote0001/{productos_archivos[i]}", productos_archivos[i], productos)


def recuperar_productos()->list:
    return os.listdir("TP_Arch_config/Lote0001")


def determinar_lote(productos: dict)->None:
    productos_archivos: list = recuperar_productos()
    categorizar_archivos(productos, productos_archivos)


# Punto 7) Archivo botellas.txt y vasos.txt
def generar_archivos(productos: dict)->None:
    color_botellas: dict = productos[1334]["color"]
    color_vasos: dict = productos[568]["color"]

    archivo_botellas = open("botellas.txt", "w")
    for color in range(len(color_botellas)):
        nombre_color: str = list(color_botellas.keys())[color]
        valor_color: str = list(color_botellas.values())[color]
        archivo_botellas.write(f"{nombre_color.capitalize()}: {valor_color} \n")
    archivo_botellas.close()

    archivo_vasos = open("vasos.txt", "w")
    for color in range(len(color_vasos)):
        nombre_color: str = list(color_vasos.keys())[color]
        valor_color: str = list(color_vasos.values())[color]
        archivo_vasos.write(f"{nombre_color.capitalize()}: {valor_color} \n")
    archivo_vasos.close()


def main():
    diccionario_productos: dict = {1334: {"precio": 15, "peso": 450, "color": {"verde": 0, "rojo": 0, "azul": 0, "negro": 0, "amarillo": 0}},
                                   568: {"precio": 8, "peso": 350, "color": {"azul": 0, "negro": 0}}
                                   }

    determinar_lote(diccionario_productos)
    print("Diccionario con stock traidos del lote")
    print(diccionario_productos)
    print("Generando botellas.txt y vasos.txt...")
    generar_archivos(diccionario_productos)
    print("Archivos generados")


main()




