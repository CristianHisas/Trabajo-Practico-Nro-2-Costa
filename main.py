# Librerias -----
import cv2
import numpy as np
import os
import csv
import time
import certifi
import ssl
import geopy
ctx = ssl.create_default_context(cafile=certifi.where())
geopy.geocoders.options.default_ssl_context = ctx
from geopy.geocoders import Nominatim

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
    - Procesa imagen, se re-configura su dimension y se devuelve informacion en forma de tupla
    '''

    img = cv2.imread(img_path)
    img = cv2.resize(img, None, fx=0.4, fy=0.4)
    height, width, channels = img.shape

    return img, height, width


def detect_objects(img: list, net, output_layers: list)->list:
    '''
    - Deteccion de objetos en las imagenes
    - Se procesan y se hace una lectura de los pixeles en la imagen
    - Re-definir el tamaño de la imagen permite al modelo pre-entrenado para detectar imagenes hacerlo de manera mas rapida
    '''
    blob: list = cv2.dnn.blobFromImage(img, scalefactor=0.00392, size=(320, 320), mean=(0, 0, 0), swapRB=True, crop=False)
    net.setInput(blob)
    # se almacena en una variable outputs la informacion del objeto detectado dentro de la imagen
    outputs: list = net.forward(output_layers)

    return outputs


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


# ---------- Fin de funciones para detectar colores -------


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
    image, height, width = load_image(img_path)
    outputs = detect_objects(image, model, output_layers)
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


def determinar_lote()->dict:
    '''
    - Se recibe el diccionario de productos por parametro
    - Se crea una lista de archivos a detectar imagenes
    - Se ejecuta la funcion para reconocimiento de imagenes, colores y actualizacion de stock
    '''
    diccionario_productos: dict = {1334: {"precio": 15, "peso": 450, "color": {"verde": 0, "rojo": 0, "azul": 0, "negro": 0, "amarillo": 0}},
                                    568: {"precio": 8, "peso": 350, "color": {"azul": 0, "negro": 0}}}

    productos_archivos: list = recuperar_productos()
    categorizar_archivos(diccionario_productos, productos_archivos)

    return diccionario_productos

# ---------------- Fin de funciones para reconocimiento de imagenes y color --------------------


'''
- Funciones para procesar ABM de pedidos
'''
def limpiar()->None:
    print('\n' * 150)


def validar_entero(opcion_min: int, opcion_max: int, opcion: str)->int:
    entero: str = input(f'ingrese {opcion}: ')

    while(not entero.isnumeric() or int(entero) < opcion_min or int(entero) > opcion_max):
        entero = input(f'{opcion} inválido/a, intente nuevamente: ')

    return int(entero)


def listar_pedidos_csv()->list:
    '''
    - Lee los pedidos cargados en el .csv y retorna una lista con ellos
    '''
    pedidos: list = []

    with open('pedidos.csv', 'r',encoding='UTF-8') as f:
        reader = csv.reader(f)
        primera_linea: bool = True

        for pedido in reader:
            if(primera_linea):
                primera_linea = False
                continue
            if(pedido[6].lower() == 'amarilla'):
                pedido[6] = 'Amarillo'
                pedidos.append(pedido)
            else:
                pedidos.append(pedido)

    return pedidos


def procesar_pedidos_csv(stock: dict)->dict:
    '''
    - Verifica segun el stock cuales son los pedidos que se pueden completar
    - Escribe en el .csv los pedidos que se pudieron validar 
    - Devuelve un dict con los pedidos validados y cancelados
    '''
    lista_pedidos: list = listar_pedidos_csv()
    estado_pedidos: dict = {}
    validados: list = []
    cancelados: list = []
    n_pedidos_cancelados: list = []
    for pedido in lista_pedidos:

        if(stock[int(pedido[5])]['color'][pedido[6].lower()] - int(pedido[7]) < 0 and not pedido in cancelados):
            cancelados.append(pedido)
            n_pedidos_cancelados.append(pedido[0])

        elif(pedido[0] in n_pedidos_cancelados):
            cancelados.append(pedido)

        else:
            stock[int(pedido[5])]['color'][pedido[6].lower()] -= int(pedido[7])
            validados.append(pedido)

    estado_pedidos['pedidos cancelados'] = cancelados
    estado_pedidos['pedidos validados'] = validados

    actualizar_csv(estado_pedidos)
    

    return estado_pedidos


def mostrar_pedidos_procesados(estado_pedidos: dict)->None:
    validados: list = sorted(estado_pedidos['pedidos validados'],key=lambda x: int(x[0]))
    cancelados: list = sorted(estado_pedidos['pedidos cancelados'],key=lambda x: int(x[0]))
    header: str = ' Pedido     Fecha        Cliente         Datos de envio '
    n_pedidos_mostrados: list = []
    print('\n\n\n                 PEDIDOS PROCESADOS ')
    print(header)

    for pedido in validados:
        if(pedido[0] not in n_pedidos_mostrados):
            print(f'  {pedido[0]}:     {pedido[1]}   {pedido[2]}     {pedido[3]} {pedido[4]}')
            n_pedidos_mostrados.append(pedido[0])

    input('\nPulse ENTER para mostrar los pedidos cancelados ')
    limpiar()
    print('\n\n           PEDIDOS CANCELADOS POR FALTA DE STOCK')
    print(header)
    n_pedidos_mostrados = []
    for articulo in cancelados:
        if(articulo[0] not in n_pedidos_mostrados):
            print(f'  {articulo[0]}:     {articulo[1]}   {articulo[2]}     {articulo[3]} {articulo[4]}')
            n_pedidos_mostrados.append(articulo[0])

    input('\nIngrese ENTER para ver el menu ')


def ultimo_numero_pedido(estado_pedidos: dict)->int:
    '''
    - Recibe por parametro los pedidos que se realizaron hasta el momento
    - Determina cual es el ultimo numero de pedido realizado y lo retorna
    '''
    ultimo_pedido: int = 0
    for pedido in estado_pedidos['pedidos validados']:
        if(int(pedido[0]) > ultimo_pedido):
            ultimo_pedido = int(pedido[0])

    for articulo in estado_pedidos['pedidos cancelados']:
        if(int(articulo[0]) > ultimo_pedido):
            ultimo_pedido = int(articulo[0])

    return ultimo_pedido


def validar_str(opcion)->str:
    ingrese_str: str = input(f'Ingrese {opcion}: ')

    while(type(ingrese_str) != str or ingrese_str == '' or ingrese_str.isdigit()):
        ingrese_str = input(f'{opcion} inválido/a, intente nuevamente: ')

    return ingrese_str


def validar_codigo_producto()->int:
    codigo: str = input('Ingrese el codigo de producto: ')
    codigos: list = ['1334', '568']

    while(not codigo in codigos):
        codigo = input('Codigo de producto inválido, intente nuevamente: ')

    return int(codigo)


def validar_color_producto(cod_producto: int)->str:
    color: str = input('Ingrese el color del producto: ')
    colores: dict = {1334: ['rojo', 'azul', 'verde', 'negro', 'amarillo'],
                     568: ['negro', 'azul']}

    while(color.lower() not in colores[cod_producto]):
        color = input('Ese color no esta disponible, intente con otro color: ')

    return color.lower()


def mostrar_stock(stock: dict, cod_articulo: int)->None:
    limpiar()
    if(cod_articulo == 1334):
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


def validar_color_stock(stock: dict, cod_articulo: int)->tuple:
    '''
    - Pide ingresar color y cantidad y valida si esta disponible esa cantidad en stock-
    '''
    color: str = validar_color_producto(cod_articulo)
    cantidad: int = validar_entero(1, 100, 'cantidad')

    while(stock[cod_articulo]['color'][color] - cantidad < 0):
        mostrar_stock(stock, cod_articulo)
        print('\nNo hay suficiente stock en ese color')
        print('Ingrese una cantidad menor o seleccione otro color')
        color = validar_color_producto(cod_articulo)
        cantidad = validar_entero(1, 100, 'cantidad')

    return color, cantidad


def ingresar_producto_a_pedido(stock: dict, n_pedido: str, fecha: str, cliente: str, ciudad: str, provincia: str)->tuple:
    '''
    - Se le pasa por parametros la informacion del pedido ya registrada anteriormente
    - Crea una lista donde se va a almacenar los datos del pedido
    - Pide los datos del producto a ingresar
    - Retorna una lista con el articulo del pedido con los datos completos y el stock actualizado
    '''
    pedido: list = []
    codigo_articulo: int = validar_codigo_producto()
    color, cantidad = validar_color_stock(stock, codigo_articulo)
    descuento: int = validar_entero(0, 100, 'descuento')
    pedido: list = [n_pedido, fecha, cliente, ciudad, provincia, codigo_articulo, color, cantidad, descuento]
    stock[codigo_articulo]['color'][color] -= cantidad

    return stock,pedido


def validar_opcion(opciones: list, opcion: str)->str:
    ingresar_opcion: str = input(f'Ingrese {opcion}: ')

    while(ingresar_opcion.lower() not in opciones):
        ingresar_opcion = input(f'{opcion} inválido/a, intente nuevamente: ')

    return ingresar_opcion.lower()

def validar_datos_envio()->tuple:
    '''
    - Solicita el ingreso de ciudad y provincia y con la libreria geopy
    - verifica que sean datos validos
    '''
    geolocator = Nominatim(user_agent='API')
    ciudad: str = validar_str('ciudad')
    provincia: str = validar_str('provincia')
    condicion: bool = True
    while(condicion):
        buscar_ciudad = geolocator.geocode(f'{ciudad},{provincia}', country_codes='AR', timeout=15)
        if(buscar_ciudad != None):
            condicion = False
            
        else:
            print('No se pudieron validar los datos de envio, intente nuevamente. ')
            ciudad: str = validar_str('ciudad')
            provincia: str = validar_str('provincia')

    return ciudad.title(),provincia.title()


def ingresar_pedido(stock: dict, estado_pedidos: dict)->tuple:
    ultimo_pedido: int = ultimo_numero_pedido(estado_pedidos)

    numero_pedido: str = str(ultimo_pedido + 1)
    fecha = time.strftime("%d/%m/%Y")
    limpiar()
    cliente: str = validar_str('nombre del cliente')
    ciudad,provincia = validar_datos_envio() 
    stock, pedido = ingresar_producto_a_pedido(stock, numero_pedido, fecha, cliente, ciudad, provincia)
    estado_pedidos['pedidos validados'].append(pedido)

    seguir_agregando: bool = True

    while(seguir_agregando):
        print('Desea agregar otro producto al pedido? (y/n): ')
        opcion: str = validar_opcion(['y', 'n'], 'opcion')
        if(opcion == 'n'):
            seguir_agregando = False
            continue

        else:
            stock, pedido = ingresar_producto_a_pedido(stock, numero_pedido, fecha, cliente, ciudad, provincia)
            estado_pedidos['pedidos validados'].append(pedido)

    return stock, estado_pedidos


def remover_pedido_validado(n_pedido: int, estado_pedidos: dict)->dict:
    '''
    - Se le pasa por parametro un numero de pedido
    - Remueve todos los articulos que contengan ese numero de pedido de estado_pedidos['pedidos validados'] 
    '''
    lista_actualizada: list = []
    for pedido in estado_pedidos['pedidos validados']:
        if(int(pedido[0]) != n_pedido):
            lista_actualizada.append(pedido)

    estado_pedidos['pedidos validados'] = lista_actualizada

    return estado_pedidos


def remover_pedido_cancelado(n_pedido: int, estado_pedidos: dict)->dict:
    '''
    - Se le pasa por parametro un numero de pedido
    - Remueve todos los articulos que contengan ese numero de pedido de estado_pedidos['pedidos cancelados'] 
    '''
    lista_actualizada: list = []
    for pedido in estado_pedidos['pedidos cancelados']:
        if(int(pedido[0]) != n_pedido):
            lista_actualizada.append(pedido)

    estado_pedidos['pedidos cancelados'] = lista_actualizada

    return estado_pedidos


def rehacer_pedido(stock: dict, estado_pedidos: dict)->tuple:
    '''
    - Se pide numero de pedido que desea rehacerse
    - Toma los datos del pedido ya registrados y los utiliza para ingresarle los articulos nuevos
    - Retorna el stock actualizado y 'estado_pedidos' actualizados
    '''
    ultimo_pedido: int = ultimo_numero_pedido(estado_pedidos)
    numero_pedido: int = validar_entero(1, ultimo_pedido, 'numero de pedido')
    limpiar()
    print('Añada un producto')
    datos_pedido: list = []

    # tomo los datos del pedido ya registrados
    for pedido in estado_pedidos['pedidos validados']:
        if(numero_pedido == int(pedido[0])):
            datos_pedido = pedido
            estado_pedidos = remover_pedido_validado(numero_pedido, estado_pedidos)

    # quito el pedido de la lista de cancelados
    for articulo in estado_pedidos['pedidos cancelados']:
        if(numero_pedido == int(articulo[0])):
            datos_pedido = articulo
            estado_pedidos = remover_pedido_cancelado(numero_pedido, estado_pedidos)

    fecha: str = datos_pedido[1]
    cliente: str = datos_pedido[2]
    ciudad: str = datos_pedido[3]
    provincia: str = datos_pedido[4]
    stock, pedido = ingresar_producto_a_pedido(stock, str(numero_pedido), fecha, cliente, ciudad, provincia)
    estado_pedidos['pedidos validados'].append(pedido)

    seguir: bool = True

    while(seguir):
        print('Desea agregar otro producto al pedido? (y/n)')
        seguir_agregando: str = validar_opcion(['y', 'n'], 'opcion')
        if(seguir_agregando == 'n'):
            seguir = False
            continue

        else:
            stock, pedido = ingresar_producto_a_pedido(stock, str(numero_pedido), fecha, cliente, ciudad, provincia)
            estado_pedidos['pedidos validados'].append(pedido)

    return stock, estado_pedidos


def numero_pedidos_validados(estado_pedidos: dict)->list:
    '''
    - Retorna una lista con los numeros de pedidos validados
    '''
    n_pedidos_validados: list = []
    for pedido in estado_pedidos['pedidos validados']:
        n_pedidos_validados.append(pedido[0])

    return n_pedidos_validados


def baja_pedido(stock: dict, estado_pedidos: dict)->tuple:
    '''
    - Remueve el pedido de 'estado_pedido['pedidos validados]'
    - Lo almacena en 'estado_pedidos['pedidos cancelados']'
    - Retorna una tupla con el stock actualizado y los estados de los pedidos
    '''
    
    n_pedidos_validados: list = numero_pedidos_validados(estado_pedidos)
    pedido_cancelado: list = []
    articulos_de_pedido: list = []

    n_pedido_baja: str = input('Ingrese el numero de pedido que desea cancelar: ')

    if(n_pedido_baja not in n_pedidos_validados):
        input('No se encontro ese numero de pedido, pulse ENTER para volver al menu')

    else:
        for pedido in estado_pedidos['pedidos validados']:
            if(n_pedido_baja == pedido[0]):
                articulos_de_pedido.append(pedido)
                estado_pedidos['pedidos cancelados'].append(pedido)

        for articulo in articulos_de_pedido:
            stock[int(articulo[5])]['color'][articulo[6].lower()] += int(articulo[7])
        estado_pedidos = remover_pedido_validado(int(n_pedido_baja), estado_pedidos)
        input('Se cancelo el pedido, pulse ENTER para volver al menú ')

    return stock, estado_pedidos


def actualizar_csv(estado_pedidos: dict)->None:
    '''
    - Funcion que al terminar la alta, baja y modificacion de pedidos
    - escribe los pedidos que se pudieron validar en el .csv
    '''
    pedidos_validados: list = estado_pedidos['pedidos validados']
    header: list = [
        'Nro. Pedidio', 'Fecha', 'Cliente', 'Ciudad', 'Provincia', 'Cod. Articulo', 'Color', 'Cantidad', 'Descuento'
        ]
    # ordeno por numero de pedido antes de escribir el csv
    pedidos_validados.sort(key=lambda x: int(x[0]))

    with open('pedidos.csv', 'w', newline='',encoding='UTF-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(pedidos_validados)


def inicio_ABM(productos: dict,estado_pedidos: dict)->dict:
    '''
    - Actualiza el archivo .csv con los pedidos procesados y validados
    - retorna un dict con los pedidos validados y cancelados:
    - estado_pedidos = {'pedidos validados': [[ ],[ ],[ ],[ ]], 'pedidos cancelados': [[ ],[ ],[ ],[ ]]}
    '''
    stock: dict = productos
    condicion_menu: bool = True

    while(condicion_menu):
        limpiar()
        print('         MENÚ        ')
        print('1) Ingresar pedido')
        print('2) Rehacer pedido')
        print('3) Cancelar pedido')
        print('4) Mostrar estado de los pedidos')
        print('5) Terminar')
        opcion: int = validar_entero(1, 5, 'opcion')
        limpiar()
        if(opcion == 1):
            stock, estado_pedidos = ingresar_pedido(stock, estado_pedidos)
        elif(opcion == 2):
            stock, estado_pedidos = rehacer_pedido(stock, estado_pedidos)
        elif(opcion == 3):
            stock, estado_pedidos = baja_pedido(stock, estado_pedidos)
        elif(opcion == 4):
            mostrar_pedidos_procesados(estado_pedidos)
        elif(opcion == 5):
            actualizar_csv(estado_pedidos)
            condicion_menu = False

    return estado_pedidos

# ---- Fin de funciones para procesamiento de ABM de pedidos ------------------------------


'''
- Funciones para la geolocalizacion 
- Determinacion de zona y optimizacion de recorrido
'''


def recoleccion_datos_ciudades()->dict:
    archivo_pedidos = open('pedidos.csv', 'r', encoding='utf-8')
    leectura = csv.reader(archivo_pedidos, dialect='excel', delimiter=',', quotechar='|')
   
    ciudades: dict = {}

    for row in leectura:
        if(row != []):
            if(row[0] not in ciudades):
                ciudades[row[0]] = [row[3], [row[5], row[7]]]
            else:
                ciudades[row[0]].append([row[5], row[7]])
    archivo_pedidos.close()

    return ciudades


def ordenar_norte(zona_norte: dict)->list:
    orden_norte: list = sorted(zona_norte.items(), key=lambda x: x[1][1], reverse = True)
    lista_sin_coordenadas_norte: list = []

    for ciudad in orden_norte:
        lista_sin_coordenadas_norte.append(ciudad[0])

    return lista_sin_coordenadas_norte


def ordenar_centro(zona_centro: dict)->list:
    orden_centro: list = sorted(zona_centro.items(), key=lambda x: x[1][1], reverse = True)
    lista_sin_coordenadas_centro: list = []

    for ciudad in orden_centro:
        lista_sin_coordenadas_centro.append(ciudad[0])

    return lista_sin_coordenadas_centro


def ordenar_sur(zona_sur: dict)->list:
    orden_sur: list = sorted(zona_sur.items(), key=lambda x: x[1], reverse = True)
    lista_sin_coordenadas_sur: list= []

    for ciudad in orden_sur:
        lista_sin_coordenadas_sur.append(ciudad[0])

    return lista_sin_coordenadas_sur


def ordenar_camiones_pesos(dict_camiones: dict, dict_pesos: dict)->tuple:
    orden_camiones: list = sorted(dict_camiones.items(), key=lambda x: x[1], reverse = True)
    orden_pesos: list = sorted(dict_pesos.items(), key=lambda x: x[1], reverse = True)

    return orden_camiones, orden_pesos


def distribucion_zonas(lista_ciudad: list)->tuple:
    geolocator = Nominatim(user_agent='API')
    lugar_coordenadas: dict = {}
    zona_norte: dict = {}
    zona_sur: dict = {}
    zona_centro: dict = {}
    zona_caba: list = []

    for indice in range(1, len(lista_ciudad)):
        buscar_ciudad = geolocator.geocode(lista_ciudad[indice], country_codes='AR', timeout=15)
        latitud_ciudad: float = buscar_ciudad.latitude
        longitud_ciudad: float = buscar_ciudad.longitude
        lugar_coordenadas[lista_ciudad[indice]] = [latitud_ciudad, longitud_ciudad]
    for ciudad in lugar_coordenadas.items():
        if(ciudad[0] == 'CABA'):
            zona_caba.append(ciudad[0])
        elif(int(ciudad[1][0]) > -35):
            zona_norte[ciudad[0]] = ciudad[1]
        elif(int(ciudad[1][0]) < -40):
            zona_sur[ciudad[0]] = ciudad[1]
        elif(-35 >= int(ciudad[1][0]) >= -40):
            zona_centro[ciudad[0]] = ciudad[1]

    lista_zona_norte: list = ordenar_norte(zona_norte)
    lista_zona_centro: list = ordenar_centro(zona_centro)
    lista_zona_sur: list = ordenar_sur(zona_sur)

    return lista_zona_norte, lista_zona_centro, zona_caba, lista_zona_sur


def averiguar_peso(zona_norte: dict, zona_centro: dict, zona_caba: list, zona_sur: dict, dict_pedidos: dict )->tuple:
    codigo_botella: str = '1334'
    codigo_vaso: str = '568'
    peso_botella: int = 450
    peso_vaso: int = 350
    peso_sur: int = 0
    peso_norte: int = 0
    peso_centro: int = 0
    peso_caba: int = 0

    for ciudad in dict_pedidos.values():
        if(ciudad[0] in zona_caba):
            for lista in ciudad:
                if(lista[0] == codigo_botella):
                    peso_caba += (int(lista[1]) * peso_botella)
                elif(lista[0] == codigo_vaso):
                    peso_caba += (int(lista[1]) * peso_vaso)
        elif(ciudad[0] in zona_sur):
            for lista in ciudad:
                if(lista[0] == codigo_botella):
                    peso_sur += (int(lista[1]) * peso_botella)
                elif(lista[0] == codigo_vaso):
                    peso_sur += (int(lista[1]) * peso_vaso)
        elif(ciudad[0] in zona_norte):
            for lista in ciudad:
                if(lista[0] == codigo_botella):
                    peso_norte += (int(lista[1]) * peso_botella)
                elif(lista[0] == codigo_vaso):
                    peso_norte += (int(lista[1]) * peso_vaso)
        elif(ciudad[0] in zona_centro):
            for lista in ciudad:
                if(lista[0] == codigo_botella):
                    peso_centro += (int(lista[1]) * peso_botella)
                elif(lista[0] == codigo_vaso):
                    peso_centro += (int(lista[1]) * peso_vaso)

    peso_centro: float = peso_centro / 1000
    peso_caba: float = peso_caba / 1000
    peso_norte: float = peso_norte / 1000
    peso_sur: float = peso_sur / 1000

    return peso_norte, peso_centro, peso_caba, peso_sur


def hacer_viaje_optimo(dict_pedidos:dict,opcion: str)->None:
    ciudades: list = []
    zona_norte_ciudades: list = []
    zona_centro_ciudades: list = []
    zona_caba_ciudades: list = []
    zona_sur_ciudades: list = []
    for datos in dict_pedidos.values():
        ciudades.append(datos[0])
    zona_norte, zona_centro, zona_caba, zona_sur = distribucion_zonas(ciudades)
    for ciudad_en_zona in zona_norte:
        zona_norte_ciudades.append(ciudad_en_zona)
    for ciudad_en_zona in zona_centro:
        zona_centro_ciudades.append(ciudad_en_zona)
    for ciudad_en_zona in zona_sur:
        zona_sur_ciudades.append(ciudad_en_zona)
    zona_caba_ciudades.append(zona_caba[0])
    if(opcion == "1"):
        if(zona_norte_ciudades == []):
            print('No hay pedidos en esta zona')
        else:
            print(zona_norte_ciudades)
    elif(opcion == "2"):
        if(zona_centro_ciudades == []):
            print('No hay pedidos en esta zona')
        else:
            print(zona_centro_ciudades)
    elif(opcion == "3"):
        if(zona_caba_ciudades == []):
            print('No hay pedidos en esta zona')
        else:
            print(zona_caba_ciudades)
    elif(opcion == "4"):
        if(zona_sur_ciudades == []):
            print('No hay pedidos en esta zona')
        else:
            print(zona_sur_ciudades)


def hacer_camiones(dict_pedidos: dict)->tuple:
    pedidos_que_salen: list = []
    lista_id_pedidos: list = []
    zona_norte: dict = {}
    zona_sur: dict = {}
    zona_centro: dict = {}
    zona_caba: list = []
    peso_zonas: dict = {}
    camiones_disponible: dict = {'utilitero1': 600, 'utilitero2': 1000, 'utilitero3': 500, 'utilitero4': 2000}
    ciudades: list = []
    for datos in dict_pedidos.values():
        ciudades.append(datos[0])
    zona_norte, zona_centro, zona_caba, zona_sur = distribucion_zonas(ciudades)
    peso_norte, peso_centro, peso_caba, peso_sur = averiguar_peso(zona_norte, zona_centro, zona_caba, zona_sur, dict_pedidos)
    peso_zonas['peso_norte'] = peso_norte
    peso_zonas['peso_centro'] = peso_centro
    peso_zonas['peso_caba'] = peso_caba
    peso_zonas['peso_sur'] = peso_sur
    camiones_disponible, peso_zonas = ordenar_camiones_pesos(camiones_disponible, peso_zonas)
    for indice in range(len(camiones_disponible)):
        if(peso_zonas[indice][1] < camiones_disponible[indice][1]):
            pedidos_que_salen.append([camiones_disponible[indice][0],peso_zonas[indice][0],peso_zonas[indice][1]])
    for pedido in pedidos_que_salen:
        if('norte' in pedido[1]):
            pedido.append(zona_norte)
            pedido.append('zona_norte')
        elif('centro' in pedido[1]):
            pedido.append(zona_centro)
            pedido.append('zona_centro')
        elif('caba' in pedido[1]):
            pedido.append(zona_caba)
            pedido.append('zona_caba')
        elif('sur' in pedido[1]):
            pedido.append(zona_sur)
            pedido.append('zona_sur')
    for id in dict_pedidos.items():
        for datos_camion_que_sale in pedidos_que_salen:
            print(datos_camion_que_sale)
            if(id[1][0] in datos_camion_que_sale[3]):
                lista_id_pedidos.append(id[0])

    return pedidos_que_salen, lista_id_pedidos


def escribir_txt(datos:list)->None:
    if(os.path.exists("salida.txt")):
        os.remove("salida.txt")
    archivo = open('salida.txt', 'a', encoding='utf-8')

    for pedido in datos:
        archivo.write('\n')
        archivo.write(pedido[4])
        archivo.write('\n')
        archivo.write(pedido[0])
        archivo.write('\n')
        archivo.write(str(pedido[2]))
        archivo.write('\n')
        for ciudad in pedido[3]:
            archivo.write(ciudad)
            archivo.write('\n')

    archivo.close()

# punto 2)


def menu_zonas(pedidos: dict)->None:
    condicion_menu: bool = True

    while(condicion_menu):
        print("Seleccione la zona que desea optimizar")
        print("1- Zona Norte")
        print("2- Zona Centro")
        print("3- Zona CABA")
        print("4- Zona Sur")
        print("5- Salir")

        opcion: int = validar_entero(1,5, 'opcion')
        if(opcion == 5):
            condicion_menu = False
            continue
        else:
            print(hacer_viaje_optimo(pedidos, str(opcion)))


# --- Fin de funciones de geolocalizacion y recorrido optimo --------


# Funciones para determinar pedidos procesados y ordenados por fecha. Opcion 4)


def listar_pedidos_completos(pedidos_terminados : dict)->None:
    print("|||PEDIDOS COMPLETADOS|||")
    print(f"Pedidos completados: {len(pedidos_terminados)}")
    for numero, pedidos in pedidos_terminados.items():
        print(f"Numero pedido: {numero}, Fecha: {pedidos[0]}/{pedidos[1]}/{pedidos[2]}, Cliente: {pedidos[3]}, Ciudad: {pedidos[4]}, Provincia: {pedidos[5]}")
        print("     Artículos: ")
        for articulo in pedidos[6]:
            print(f"        Numero artículo: {articulo[0]}, Color: {articulo[1]}, Cantidad: {articulo[2]}, Descuento: {articulo[3]}")


#Ordeno los pedidos primero por dia despues por mes y por ultimo por fecha.
def ordenar_pedidos_fecha(pedidos_separados_fecha : dict)->dict:
    pedidos_terminados_ordenado_dia : list = []
    pedidos_terminados_ordenado_dia = sorted(pedidos_separados_fecha.items(), key = lambda x: x[1][0], reverse = False)
    dict_ordenado_dia : dict = {}
    for pedido in pedidos_terminados_ordenado_dia:
        dict_ordenado_dia[pedido[0]] = pedido[1]

    pedidos_terminados_ordenado_mes : list = []
    pedidos_terminados_ordenado_mes = sorted(dict_ordenado_dia.items(), key = lambda x: x[1][1], reverse = False)
    dict_ordenado_mes : dict = {}
    for pedido in pedidos_terminados_ordenado_mes:
        dict_ordenado_mes[pedido[0]] = pedido[1]

    pedidos_terminados_ordenado_final : list = []
    pedidos_terminados_ordenado_final = sorted(dict_ordenado_mes.items(), key = lambda x: x[1][2], reverse = False)
    dict_ordenado_final : dict = {}
    for pedido in pedidos_terminados_ordenado_final:
        dict_ordenado_final[pedido[0]] = pedido[1]

    return dict_ordenado_final


#crea un dict que separa las fechas "12/10/2001" --- "12","10","2001"
def separar_fechas(pedidos_terminados : dict, pedidos_fechas_separada : dict)->dict:
    dia : int = 0
    mes : int = 0
    anio : int = 0
    for numero, pedido in pedidos_terminados.items():
        fecha_seperada = pedidos_terminados[numero][0].split("/")
        dia = fecha_seperada[0]
        mes = fecha_seperada[1]
        anio = fecha_seperada[2]
        pedidos_fechas_separada[numero] = [dia, mes, anio, pedido[1], pedido[2], pedido[3], pedido[4]]

    return pedidos_fechas_separada


#leo el csv y comparo con la lista de ids de pedidos completados que obtengo de la funcion hacer_camiones()
def pasar_listaCsv_dict(pedidos_procesados : dict, pedidos_que_salen : list, lista_csv : list)->dict:
    for objeto in lista_csv:
        if((objeto[0] not in pedidos_procesados.keys()) and (objeto[0] in pedidos_que_salen)):
            pedidos_procesados[objeto[0]] = [objeto[1], objeto[2], objeto[3], objeto[4], [[objeto[5],objeto[6],objeto[7],objeto[8]]]]
        elif((objeto[0] in pedidos_procesados.keys()) and (objeto[0] in pedidos_que_salen)):
            pedidos_procesados[objeto[0]][4].append([objeto[5],objeto[6],objeto[7],objeto[8]])

    return pedidos_procesados

# ---- Fin opcion 4 ------


# opcion 5)
def listar_pedidos_rosario(pedidos_rosario: dict) -> None:
    if (len(pedidos_rosario) > 0):
        print("|||PEDIDOS EN ROSARIO|||")
        print(f"Pedidos en Rosario: {len(pedidos_rosario)}")
        for numero, pedidos in pedidos_rosario.items():
            print(
                f"Numero pedido: {numero}, Fecha: {pedidos[0]}, Cliente: {pedidos[1]}, Ciudad: {pedidos[2]}, Provincia: {pedidos[3]}")
            print("     Artículos: ")
            for articulo in pedidos[4]:
                print(
                    f"        Numero artículo: {articulo[0]}, Color: {articulo[1]}, Cantidad: {articulo[2]}, Descuento: {articulo[3]}")
    else:
        print("No hay pedidos que se encuentren en Rosario")


def pedidos_en_rosario(pedidos_procesados: dict, pedidos_rosario: dict) -> dict:
    ciudad: str = ""
    valor_total: int = 0
    for numero, pedidos in pedidos_procesados.items():
        ciudad = pedidos[3]
        if (ciudad.lower() == "rosario"):
            pedidos_rosario[numero] = pedidos

    for numero, pedidos in pedidos_rosario.items():
        for articulo in pedidos[4]:
            if (articulo[0] == "1334"):
                valor_total += (int(articulo[2]) * 15)
            elif (articulo[0] == "568"):
                valor_total += (int(articulo[2]) * 8)

        pedidos_rosario[numero].append(valor_total)

    return pedidos_rosario

# --------- Fin opcion 5 -------------------------------


# opcion 6): ARTICULO MAS PEDIDO Y ARTICULOS ENTREGADOS

def articulo_mas_pedido(estado_pedidos: dict)->dict:
    '''
    - Recibe por parametro el diccionario donde se encuentran todos los pedidos realizados
    - Determina cual fue el articulo mas pedido
    - Retorna un diccionario con los datos del articulo
    '''
    pedidos_list: list = estado_pedidos['pedidos validados'] + estado_pedidos['pedidos cancelados']
    articulos: dict = {1334: { },568:{ }}
    cantidad_mas_pedida: int = 0
    articulo_mas_pedido: dict = {}
    
    for pedido in pedidos_list:
        if(pedido[6].lower() not in articulos[int(pedido[5])]):
            articulos[int(pedido[5])][pedido[6].lower()] = int(pedido[7])
        else:
            articulos[int(pedido[5])][pedido[6].lower()] += int(pedido[7])
    
    for color, cantidad in articulos[1334].items():
        if(int(cantidad) > cantidad_mas_pedida):
            cantidad_mas_pedida = int(cantidad)
            articulo_mas_pedido = {1334: [color, int(cantidad)]}
    
    for color, cantidad in articulos[568].items():
        if(int(cantidad) > cantidad_mas_pedida):
            cantidad_mas_pedida = int(cantidad)
            articulo_mas_pedido = {568: [color, int(cantidad)]}
    
    return articulo_mas_pedido


def lista_pedidos_entregados(n_pedidos_entregados: dict)->list:
    '''
    - Se recibe los N° de pedidos que se pudieron completar luego del proceso
    - de envios
    - Compara en el .csv cuales son esos articulos entregados y los junta en una lista
    - Retorna la lista con los articulos entregados
    ''' 
    
    lista_pedidos: list = listar_pedidos_csv()
    pedidos_entregados: list = []
 
    for pedido in lista_pedidos:
        if(pedido[0] in n_pedidos_entregados):
            pedidos_entregados.append(pedido)
    
    return pedidos_entregados
    

def cantidad_entregados(articulo_mas_pedido: dict, lista_entregados: list)->int:
    '''
    - Verifica cuantas unidades del articulo mas pedido se pudieron entregar
    - Retorna el resultado
    '''
    
    articulos_entregados: int = 0

    for entregado in lista_entregados:
        if(int(entregado[5]) in articulo_mas_pedido.keys()):
            if(entregado[6].lower() == articulo_mas_pedido[int(entregado[5])][0].lower()):
                articulos_entregados += int(entregado[7])
    
    return articulos_entregados


def articulos_entregados(estado_pedidos: dict, n_pedidos_entregados)->None:
    '''
    - Recibe 'estado_pedidos' diccionario donde se encuentran todos los pedidos realizados
    - Printea el articulo mas pedido y los que se lograron entregar
    '''
    mas_pedido = articulo_mas_pedido(estado_pedidos)
    lista_entregados: list = lista_pedidos_entregados(n_pedidos_entregados)
    entregados: int = cantidad_entregados(mas_pedido,lista_entregados)
    
    if(1334 in mas_pedido):
        print(f'El artículo mas pedido es la botella color {mas_pedido[1334][0]}')
        print(f'Se realizaron {mas_pedido[1334][1]} pedidos de este artículo, se lograron entregar {entregados}')
        input('Pulse ENTER para volver al menú')
    
    elif(568 in mas_pedido):
        print(f'El artículo mas pedido es el vaso color {mas_pedido[568][0]}')
        print(f'Se realizaron {mas_pedido[568][1]} pedidos de este artículo, se lograron entregar {entregados}')
        input('Pulse ENTER para volver al menú')

#-----------------------fin punto 6 --------------------------------#


# opcion 7)
def generar_archivos_productos(productos: dict)->None:
    '''
    Se crean archivos botellas.txt y vasos.txt
    '''
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


def main()->None:
    condicion_menu: bool = True

    print("Inicio de proceso para Lote 0001")
    diccionario_productos: dict = determinar_lote()
    print("Procesamiento de Lote 0001 terminado.")
   
    #----- PROCESAMIENTO DE PEDIDOS DEL .CSV ---#
    estado_pedidos: dict = procesar_pedidos_csv(diccionario_productos)
    #-------------------------------------------#
    
    input("\nPulse ENTER para ver los pedidos procesados")
    mostrar_pedidos_procesados(estado_pedidos)
    
    diccionario_pedidos: dict = recoleccion_datos_ciudades()

    while(condicion_menu):
        print("Ingrese una de las siguientes opciones: ")
        print("1- ABM (Alta; Baja; Modificacion) de pedidos.")
        print("2- Determinar recorrido optimo por zona")
        print("3- Procesar recorrido y listar recorridos por zona")
        print("4- Listar pedidos completados por fecha")
        print("5- Determinar pedidos realizados a Rosario y valorizarlos")
        print("6- Articulo mas pedido y cual de ellos fue entregado")
        print("7- Crear archivos de vasos y botellas procesadas por color")
        print("8- Salir")

        opcion: str = input("Opcion: ")

        if(not opcion.isnumeric() or int(opcion) > 8 or int(opcion) < 1):
            print("Ingrese unicamente las opciones solicitadas dentro del menu")
        else:
            if(int(opcion) == 1):
                estado_pedidos = inicio_ABM(diccionario_productos, estado_pedidos)
            elif(int(opcion) == 2):
                diccionario_pedidos = recoleccion_datos_ciudades()
                if(len(diccionario_pedidos) > 0):
                    menu_zonas(diccionario_pedidos)
                else:
                    print("No exiten pedidos para optimizar")
            elif(int(opcion) == 3):
                diccionario_pedidos = recoleccion_datos_ciudades()
                if(len(diccionario_pedidos) > 0):
                    camiones, id_pedidos = hacer_camiones(diccionario_pedidos)
                    escribir_txt(camiones)
                else:
                    print("No existen pedidos para procesar y listar")
            elif(int(opcion) == 4):
                print(4)
            elif(int(opcion) == 5):
                print(5)
            elif(int(opcion) == 6):
                if(len(estado_pedidos) > 0):
                    # hacer_camiones(a) = lista_ids_pedidos
                    lista_ids_pedidos: list = ['1', '2', '3', '4', '5']
                    articulos_entregados(estado_pedidos,lista_ids_pedidos)
                else:
                    print("No existen pedidos para verificar la opcion solicitada")
            elif(int(opcion) == 7):
                generar_archivos_productos(diccionario_productos)
            else:
                condicion_menu = False

        print("Fin del programa")

main()
