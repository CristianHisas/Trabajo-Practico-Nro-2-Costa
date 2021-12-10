# Librerias -----
import cv2
import numpy as np
import os
import csv
import time

'''
- Integracion de yolo con opencv 
- Reconocimiento de objetos en imagenes 
- Determinacion de color del objeto en HSV
- Actualizacion de stock segun el reconocimiento de imagenes del lote
'''


def load_yolo()->tuple:
    '''
    - Carga de archivos yolo y coco.names
    - Los objetos que pueden reconocerce en las imagenes los clasifico en mi lista classes
    '''
    # Cargo los archivos yolo y coco.names
    net = cv2.dnn.readNet("TP_Arch_config/yolov3.weights", "TP_Arch_config/yolov3.cfg")
    classes: list = []
    with open("TP_Arch_config/coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]

    output_layers: list = [layer_name for layer_name in net.getUnconnectedOutLayersNames()]
    colors = np.random.uniform(0, 255, size=(len(classes), 3))

    return net, classes, colors, output_layers


def load_image(img_path: str)->tuple:
    '''
    - Procesa imagen, se re configura su dimension y se devuelve informacion en forma de tupla
    '''

    img = cv2.imread(img_path)
    img = cv2.resize(img, None, fx=0.4, fy=0.4)
    height, width, channels = img.shape

    return img, height, width, channels


def detect_objects(img: list, net, output_layers: list)->tuple:
    '''
    - Deteccion de objetos en las imagenes
    - Se procesan y se hace una lectura de los pixeles en la imagen
    '''
    blob: list = cv2.dnn.blobFromImage(img, scalefactor=0.00392, size=(320, 320), mean=(0, 0, 0), swapRB=True, crop=False)
    net.setInput(blob)
    # se almacena en una variable outputs la informacion del objeto detectado dentro de la imagen
    outputs: list = net.forward(output_layers)

    return blob, outputs


def get_box_dimensions(outputs: list, height: int, width: int)->tuple:
    '''
    - Se detectan las dimensiones del objeto para poder armar las boxes que van a recuadrar y marcar al objeto en la imagen
    - Devuelve una tupla con las dimensiones y los respectivos identificadores de los objetos
    '''
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
    '''
    - Se dibuja el marco del dibujo con el identificador
    - Muestra la imagen por 2 segundos
    - Retorna el identificador del objeto de la imagen actual
    '''
    indexes: list = cv2.dnn.NMSBoxes(boxes, config, 0.5, 0.4)
    font: int = cv2.FONT_HERSHEY_PLAIN
    label: str = ""
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            color: list = colors[i]
            cv2.rectangle(img, (x,y), (x+w, y+h), color, 2)
            cv2.putText(img, label, (x, y - 5), font, 1, color, 1)

    cv2.imshow(fle_name, img)
    cv2.waitKey(2000)
    cv2.destroyWindow(fle_name)

    return label

'''
- Funciones para detectar colores
- Se recibe la imagen
- Se establece un rango de saturacion entre colores para verificar si el color de la imagen entra dentro de ese rango
- Se verifica que el color encontrado dentro del rango predomine en la mayor cantidad de pixeles dentro de la imagen
'''


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
    if(has_red > 0.07):
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
    if(has_blue > 0.07):
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

# ---------- Fin de funciones para detectar colores -------


def get_color(img_path: str)->str:
    '''
    - Funcion que ejecuta el proceso de reconocimiento de color en una imagen recibida por parametros
    - Retorna el color de la imagen detectada
    '''
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
    '''
    - Actualiza el stock del color de cada objeto segun lo que reciba por parametros
    '''
    if(clasificacion == "bottle"):
        print(f"Botella de color {color}")
        productos[1334]["color"][color] += 1
    else:
        print(f"Vaso de color {color}")
        productos[568]["color"][color] += 1


def image_detect(img_path: str, fle_name: str, productos: dict)->None:
    '''
    - Funcion que ejecuta todo el procesamiento de reconocimiento de imagenes y colores
    - Si el objeto no es un vaso o una botella, se muestra un mensaje de proceso detenido sino, se determina el color y se agrega al diccionario de stock
    '''
    model, classes, colors, output_layers = load_yolo()
    image, height, width, channels = load_image(img_path)
    blob, outputs = detect_objects(image, model, output_layers)
    boxes, config, class_ids = get_box_dimensions(outputs, height, width)
    label: str = draw_labels(boxes, config, colors, class_ids, classes, image, fle_name)

    if(label.lower() != "bottle" and label.lower() != "cup"):
        print("PROCESO DETENIDO, se reanuda en 1 minuto")
    else:
        color: str = get_color(img_path)
        actualizar_stock(productos, color, label.lower())


def categorizar_archivos(productos: dict, productos_archivos: list)->None:
    '''
    - Se recorre las imagenes para detectar los objetos dentro de ellas
    '''
    for i in range(len(productos_archivos)):
        image_detect(f"TP_Arch_config/Lote0001/{productos_archivos[i]}", productos_archivos[i], productos)


def recuperar_productos()->list:
    '''
    - Creo una lista con los nombres de todos los archivos dentro del lote
    '''
    return os.listdir("TP_Arch_config/Lote0001")


def determinar_lote(productos: dict)->None:
    '''
    - Se recibe el diccionario de productos por parametro
    - Se crea una lista de archivos a detectar imagenes
    - Se ejecuta la funcion para reconocimiento de imagenes, colores y actualizacion de stock
    '''
    productos_archivos: list = recuperar_productos()
    categorizar_archivos(productos, productos_archivos)

# ---------------- Fin de funciones para reconocimiento de imagenes y color --------------------


'''
- Funciones para procesar ABM de pedidos
'''
def limpiar()->None:
    print('\n' * 150)


def validar_entero(opcion_min: int, opcion_max: int, opcion: str)->int:
    entero: str = input(f'ingrese {opcion}: ')

    while not entero.isnumeric() or int(entero) < opcion_min or int(entero) > opcion_max:
        entero = input(f'{opcion} inválido/a, intente nuevamente: ')

    return int(entero)


def menu_pedidos()->int:
    limpiar()
    print('         MENÚ        ')
    print('1) Ingresar pedido')
    print('2) Rehacer pedido')
    print('3) Cancelar pedido')
    print('4) Mostrar estado de los pedidos')
    print('5) Terminar')
    opcion: int = validar_entero(1, 5, 'opcion')

    return opcion


def parse_pedidos_csv()->list:
    '''
    - Lee los pedidos cargados en el .csv y retorna una lista con ellos
    '''
    pedidos: list = []

    with open('pedidos.csv', 'r') as f:
        reader = csv.reader(f)
        primera_linea: bool = True

        for pedido in reader:
            if primera_linea:
                primera_linea = False
                continue
            else:
                pedidos.append(pedido)

    return pedidos


def procesar_pedidos_csv(stock: dict, pedidos: list)->dict:
    '''
    devuelve un dict con los datos de los pedidos validados y cancelados, y el stock actualizado
    '''
    estado_pedidos: dict = {}
    validados: list = []
    cancelados: list = []
    n_pedidos_cancelados: list = []
    for pedido in pedidos:

        if stock[int(pedido[5])]['color'][pedido[6].lower()] - int(pedido[7]) < 0 and not pedido in cancelados:
            cancelados.append(pedido)
            n_pedidos_cancelados.append(pedido[0])

        elif pedido[0] in n_pedidos_cancelados:
            cancelados.append(pedido)

        else:
            stock[int(pedido[5])]['color'][pedido[6].lower()] -= int(pedido[7])
            validados.append(pedido)

    estado_pedidos['pedidos cancelados'] = cancelados
    estado_pedidos['pedidos validados'] = validados

    return estado_pedidos


def mostrar_pedidos_procesados(estado_pedidos: dict)->None:
    validados: list = estado_pedidos['pedidos validados']
    cancelados: list = estado_pedidos['pedidos cancelados']
    header: str = ' Pedido     Fecha        Cliente         Datos de envio '
    n_pedidos_mostrados: list = []
    print('\n\n\n                 PEDIDOS PROCESADOS ')
    print(header)

    for pedido in validados:
        if pedido[0] not in n_pedidos_mostrados:
            print(f'  {pedido[0]}:     {pedido[1]}   {pedido[2]}     {pedido[3]} {pedido[4]}')
            n_pedidos_mostrados.append(pedido[0])

    input('\nPulse ENTER para mostrar los pedidos cancelados ')
    limpiar()
    print('\n\n           PEDIDOS CANCELADOS POR FALTA DE STOCK')
    print(header)
    n_pedidos_mostrados = []
    for articulo in cancelados:
        if articulo[0] not in n_pedidos_mostrados:
            print(f'  {articulo[0]}:     {articulo[1]}   {articulo[2]}     {articulo[3]} {articulo[4]}')
            n_pedidos_mostrados.append(articulo[0])

    input('\nIngrese ENTER para ver el menu ')


def ultimo_numero_pedido(estado_pedidos: dict)->int:
    ultimo_pedido: int = 0
    for pedido in estado_pedidos['pedidos validados']:
        if int(pedido[0]) > ultimo_pedido:
            ultimo_pedido = int(pedido[0])

    for articulo in estado_pedidos['pedidos cancelados']:
        if int(articulo[0]) > ultimo_pedido:
            ultimo_pedido = int(articulo[0])

    return ultimo_pedido


def validar_str(opcion)->str:
    ingrese_str: str = input(f'Ingrese {opcion}: ')

    while type(ingrese_str) != str or ingrese_str == '' or ingrese_str.isdigit():
        ingrese_str = input(f'{opcion} inválido/a, intente nuevamente: ')

    return ingrese_str


def validar_codigo_producto() -> int:
    codigo: str = input('Ingrese el codigo de producto: ')
    codigos: list = ['1334', '568']

    while not codigo in codigos:
        codigo = input('Codigo de producto inválido, intente nuevamente: ')

    return int(codigo)


def validar_color_producto(cod_producto) -> str:
    color: str = input('Ingrese el color del producto: ')
    colores: dict = {1334: ['rojo', 'azul', 'verde', 'negro', 'amarillo'],
                     568: ['negro', 'azul']}

    while color.lower() not in colores[cod_producto]:
        color = input('Ese color no esta disponible, intente con otro color: ')

    return color.lower()


def mostrar_stock(stock: dict, cod_articulo: str) -> None:
    limpiar()
    if cod_articulo == 1334:
        print(f"""\n\n      STOCK BOTELLAS      
  VERDE: {stock[1334]['color']['verde']}
  ROJO: {stock[1334]['color']['rojo']}
  AZUL: {stock[1334]['color']['azul']}
  NEGRO: {stock[1334]['color']['negro']}
  AMARILLO: {stock[1334]['color']['amarillo']}
  """)

    else:
        print(f"""\n\n      STOCK VASOS      
  AZUL: {stock[568]['color']['azul']}
  NEGRO: {stock[568]['color']['negro']}""")


def validar_color_stock(stock: dict, cod_articulo: str) -> tuple:
    color: str = validar_color_producto(cod_articulo)
    cantidad: int = validar_entero(1, 100, 'cantidaad')

    while stock[cod_articulo]['color'][color] - cantidad < 0:
        mostrar_stock(stock, cod_articulo)
        print('\nNo hay suficiente stock en ese color')
        print('Ingrese una cantidad menor o seleccione otro color')
        color = validar_color_producto(cod_articulo)
        cantidad = validar_entero(1, 100, 'cantidad')

    return color, cantidad


def ingresar_producto_a_pedido(stock, n_pedido, fecha, cliente, ciudad, provincia)-> tuple:
    pedido: list = []
    codigo_articulo: int = validar_codigo_producto()
    color, cantidad = validar_color_stock(stock,codigo_articulo)
    descuento: int = validar_entero(0,100,'descuento')
    pedido: list = [n_pedido, fecha, cliente, ciudad, provincia, codigo_articulo, color, cantidad, descuento]
    stock[codigo_articulo]['color'][color] -= cantidad

    return stock,pedido


def validar_opcion(opciones: list, opcion: str)->str:
    ingresar_opcion: str = input(f'Ingrese {opcion}: ')

    while ingresar_opcion.lower() not in opciones:
        ingresar_opcion = input(f'{opcion} inválido/a, intente nuevamente: ')

    return ingresar_opcion.lower()


def ingresar_pedido(stock, estado_pedidos: dict)->tuple:
    ultimo_pedido: int = ultimo_numero_pedido(estado_pedidos)

    numero_pedido: str = str(ultimo_pedido + 1)
    fecha = time.strftime("%d/%m/%Y")
    limpiar()
    cliente: str = validar_str('nombre del cliente')
    ciudad: str = validar_str('ciudad')
    provincia: str = validar_str('provincia')
    stock, pedido = ingresar_producto_a_pedido(stock, numero_pedido, fecha, cliente, ciudad, provincia)
    estado_pedidos['pedidos validados'].append(pedido)

    seguir_agregando: bool = True

    while seguir_agregando:
        print('Desea agregar otro producto al pedido? (y/n): ')
        opcion: str = validar_opcion(['y', 'n'], 'opcion')
        if opcion == 'n':
            seguir_agregando = False
            continue

        else:
            stock, pedido = ingresar_producto_a_pedido(stock, numero_pedido, fecha, cliente, ciudad, provincia)
            estado_pedidos['pedidos validados'].append(pedido)

    return stock, estado_pedidos


def remover_pedido_validado(n_pedido: int, estado_pedidos: dict) -> dict:
    lista_actualizada: list = []
    for pedido in estado_pedidos['pedidos validados']:
        if pedido[0] != n_pedido:
            lista_actualizada.append(pedido)

    estado_pedidos['pedidos validados'] = lista_actualizada

    return estado_pedidos


def remover_pedido_cancelado(n_pedido: int, estado_pedidos: dict) -> dict:
    lista_actualizada: list = []
    for pedido in estado_pedidos['pedidos cancelados']:
        if pedido[0] != n_pedido:
            lista_actualizada.append(pedido)

    estado_pedidos['pedidos cancelados'] = lista_actualizada

    return estado_pedidos


def rehacer_pedido(stock: dict, estado_pedidos: dict)->tuple:
    ultimo_pedido: int = ultimo_numero_pedido(estado_pedidos)
    numero_pedido: str = str(validar_entero(1, ultimo_pedido, 'numero de pedido'))
    limpiar()
    print('Añada un producto')
    datos_pedido: list = []

    for pedido in estado_pedidos['pedidos validados']:  # tomo los datos del pedido ya registrados
        if numero_pedido == pedido[0]:
            datos_pedido = pedido
            estado_pedidos = remover_pedido_validado(numero_pedido, estado_pedidos)

    for articulo in estado_pedidos['pedidos cancelados']:  # quito el pedido de la lista de cancelados
        if numero_pedido == articulo[0]:
            datos_pedido = articulo
            estado_pedidos = remover_pedido_cancelado(numero_pedido, estado_pedidos)

    fecha: str = datos_pedido[1]
    cliente: str = datos_pedido[2]
    ciudad: str = datos_pedido[3]
    provincia: str = datos_pedido[4]
    stock, pedido = ingresar_producto_a_pedido(stock, numero_pedido, fecha, cliente, ciudad, provincia)
    estado_pedidos['pedidos validados'].append(pedido)

    seguir: bool = True

    while seguir:
        print('Desea agregar otro producto al pedido? (y/n)')
        seguir_agregando: str = validar_opcion(['y', 'n'], 'opcion')
        if seguir_agregando == 'n':
            seguir = False
            continue

        else:
            stock, pedido = ingresar_producto_a_pedido(stock, numero_pedido, fecha, cliente, ciudad, provincia)
            estado_pedidos['pedidos validados'].append(pedido)

    return stock, estado_pedidos


def numero_pedidos_validados(estado_pedidos: dict):
    '''
    - Retorna una lista con los numeros de pedidos validados
    '''
    n_pedidos_validados: list = []
    for pedido in estado_pedidos['pedidos validados']:
        n_pedidos_validados.append(pedido[0])

    return n_pedidos_validados


def baja_pedido(stock: dict, estado_pedidos: dict)->tuple:
    n_pedidos_validados: list = numero_pedidos_validados(estado_pedidos)
    pedido_cancelado: list = []
    articulos_de_pedido: list = []

    n_pedido_baja: str = input('Ingrese el numero del pedido a dar de baja: ')

    if n_pedido_baja not in n_pedidos_validados:
        input('No se encontro ese numero de pedido, pulse ENTER para volver al menu')

    else:
        for pedido in estado_pedidos['pedidos validados']:
            if n_pedido_baja == pedido[0]:
                articulos_de_pedido.append(pedido)
                estado_pedidos['pedidos cancelados'].append(pedido)

        for articulo in articulos_de_pedido:
            stock[int(articulo[5])]['color'][articulo[6].lower()] += int(articulo[7])
        estado_pedidos = remover_pedido_validado(n_pedido_baja, estado_pedidos)
        input('Se cancelo el pedido, pulse ENTER para volver al menú ')

    return stock, estado_pedidos


def actualizar_csv(estado_pedidos: dict)->None:
    pedidos_validados: list = estado_pedidos['pedidos validados']
    header: list = [
        'Nro. Pedidio', 'Fecha', 'Cliente', 'Ciudad', 'Provincia', 'Cod. Articulo', 'Color', 'Cantidad', 'Descuento'
        ]
    # ordeno por numero de pedido antes de escribir el csv
    pedidos_validados.sort(key=lambda x: x[0])

    with open('pedidos.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(pedidos_validados)


def inicio_menu_pedidos(productos: dict)->dict:
    '''
    - Actualiza el archivo .csv con los pedidos procesados y validados
    - retorna un dict con los pedidos validados y cancelados:
    - estado_pedidos = {'pedidos validados': [[ ],[ ],[ ],[ ]], 'pedidos cancelados': [[ ],[ ],[ ],[ ]]}
    '''
    stock: dict = productos
    condicion_menu: bool = True
    pedidos_lista: list = parse_pedidos_csv()
    estado_pedidos: dict = procesar_pedidos_csv(stock, pedidos_lista)
    mostrar_pedidos_procesados(estado_pedidos)

    while(condicion_menu):
        opcion: int = menu_pedidos()
        limpiar()
        if opcion == 1:
            stock, estado_pedidos = ingresar_pedido(stock, estado_pedidos)
        elif opcion == 2:
            stock, estado_pedidos = rehacer_pedido(stock, estado_pedidos)
        elif opcion == 3:
            stock, estado_pedidos = baja_pedido(stock, estado_pedidos)
        elif opcion == 4:
            mostrar_pedidos_procesados(estado_pedidos)
        elif opcion == 5:
            actualizar_csv(estado_pedidos)
            condicion_menu = False

    return estado_pedidos

# ---- Fin de funciones para procesamiento de ABM de pedidos ------------------------------


def main()->None:
    diccionario_productos: dict = {1334: {"precio": 15, "peso": 450, "color": {"verde": 0, "rojo": 0, "azul": 0, "negro": 0, "amarillo": 0}},
                                   568: {"precio": 8, "peso": 350, "color": {"azul": 0, "negro": 0}}
                                   }
    estado_pedidos: dict = {}
    condicion_menu: bool = True


    print("Inicio de proceso para Lote 0001")
    determinar_lote(diccionario_productos)
    print("Procesamiento de Lote 0001 terminado. Iniciando programa ...")

    while(condicion_menu):
        print("Ingrese una de las siguientes opciones: ")
        print("1- ABM (Alta; Baja; Modificacion) de pedidos.")
        opcion: str = input("Opcion: ")

        if(not opcion.isnumeric() or int(opcion) > 7 or int(opcion) < 1):
            print("Ingrese unicamente las opciones solicitadas dentro del menu")
        else:
            if(int(opcion) == 1):
                estado_pedidos = inicio_menu_pedidos(diccionario_productos)



