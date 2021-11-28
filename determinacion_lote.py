import cv2
import numpy as np
import os


'''
- Integracion de yolo con opencv 
- Reconocimiento de objetos en imagenes 
- Determinacion de color del objeto con RGB-HSV
'''


def load_yolo():
    net = cv2.dnn.readNet("TP_Arch_config/yolov3.weights", "TP_Arch_config/yolov3.cfg")
    classes: list = []
    with open("TP_Arch_config/coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]

    output_layers = [layer_name for layer_name in net.getUnconnectedOutLayersNames()]
    colors = np.random.uniform(0, 255, size=(len(classes), 3))

    return net, classes, colors, output_layers


def load_image(img_path):
    # image loading
    img = cv2.imread(img_path)
    img = cv2.resize(img, None, fx=0.4, fy=0.4)
    height, width, channels = img.shape

    return img, height, width, channels


def detect_objects(img, net, output_layers):
    blob = cv2.dnn.blobFromImage(img, scalefactor=0.00392, size=(320, 320), mean=(0, 0, 0), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward(output_layers)

    return blob, outputs


def get_box_dimensions(outputs, height, width):
    boxes: list = []
    config: list = []
    class_ids: list = []
    for output in outputs:
        for detect in output:
            scores = detect[5:]
            class_id = np.argmax(scores)
            conf = scores[class_id]
            if(conf > 0.3):
                center_x = int(detect[0] * width)
                center_y = int(detect[1] * height)
                w = int(detect[2] * width)
                h = int(detect[3] * height)
                x = int(center_x - w/2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                config.append(float(conf))
                class_ids.append(class_id)

    return boxes, config, class_ids


def draw_labels(boxes, config, colors, class_ids, classes, img, fle_name):
    indexes = cv2.dnn.NMSBoxes(boxes, config, 0.5, 0.4)
    font = cv2.FONT_HERSHEY_PLAIN
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            color = colors[i]
            cv2.rectangle(img, (x,y), (x+w, y+h), color, 2)
            cv2.putText(img, label, (x, y - 5), font, 1, color, 1)
    cv2.imshow(fle_name, img)


def image_detect(img_path, fle_name: str):
    model, classes, colors, output_layers = load_yolo()
    image, height, width, channels = load_image(img_path)
    blob, outputs = detect_objects(image, model, output_layers)
    boxes, config, class_ids = get_box_dimensions(outputs, height, width)
    draw_labels(boxes, config, colors, class_ids, classes, image, fle_name)

    cv2.waitKey(0)

'''
- Implementacion de funciones integradas
'''


def categorizar_archivos(dicionario_productos: dict, lista_productos_archivos: list)->dict:
    # integracion de yolo+opencv
    for i in range(len(lista_productos_archivos)):
        image_detect(f"TP_Arch_config/Lote0001/{lista_productos_archivos[i]}", lista_productos_archivos[i])


def recuperar_productos()->list:
    return os.listdir("TP_Arch_config/Lote0001")


def determinar_lote(diccionario_productos: dict)->None:
    lista_productos_archivos: list = recuperar_productos()

    categorizar_archivos(diccionario_productos, lista_productos_archivos)


def main():
    diccionario_productos: dict = {}

    determinar_lote(diccionario_productos)


main()




