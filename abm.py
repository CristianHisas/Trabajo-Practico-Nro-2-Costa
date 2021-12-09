import csv
import time
import determinacion_lote

def limpiar()-> None:
    print('\n' * 150)

def validar_opcion(opciones:list,opcion: str)-> str:
    ingresar_opcion: str = input(f'Ingrese {opcion}: ')
    
    while ingresar_opcion.lower() not in opciones:
        ingresar_opcion = input(f'{opcion} inválido/a, intente nuevamente: ')
    
    return ingresar_opcion.lower()

def validar_str(opcion)->str:
    ingrese_str: str = input(f'Ingrese {opcion}: ')
    
    while type(ingrese_str) != str or ingrese_str == '' or ingrese_str.isdigit():
        ingrese_str = input(f'{opcion} inválido/a, intente nuevamente: ')
    
    return ingrese_str

def validar_entero(opcion_min: int, opcion_max: int,opcion:str)-> int:
    entero: str = input(f'ingrese {opcion}: ')
    
    while not entero.isnumeric() or int(entero) < opcion_min or int(entero) > opcion_max:
        entero = input(f'{opcion} inválido/a, intente nuevamente: ')
    
    return int(entero)

def menu()-> int:
    limpiar()
    print('         MENÚ        ')
    print('1) Ingresar pedido')
    print('2) Rehacer pedido')
    print('3) Cancelar pedido')
    print('4) Mostrar estado de los pedidos')
    print('5) Terminar')
    opcion: int = validar_entero(1,5,'opcion')

    return opcion

def validar_color_producto(cod_producto)-> str:
    color = input('Ingrese el color del producto: ')
    colores = {1334: ['rojo','azul','verde','negro','amarillo'],
               568 : ['negro','azul']}
    
    while color.lower() not in colores[cod_producto]:
        color = input('Ese color no esta disponible, intente con otro color: ')

    return color.lower()

def mostrar_stock(stock: dict,cod_articulo: str)-> None:
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

def validar_color_stock(stock: dict,cod_articulo: str)-> tuple:

    color: str = validar_color_producto(cod_articulo)
    cantidad: int = validar_entero(1,100,'cantidaad')
    
    while stock[cod_articulo]['color'][color] - cantidad < 0:
        mostrar_stock(stock,cod_articulo)
        print('\nNo hay suficiente stock en ese color')
        print('Ingrese una cantidad menor o seleccione otro color')
        color = validar_color_producto(cod_articulo)
        cantidad = validar_entero(1,100,'cantidad')

    return color,cantidad

def validar_codigo_producto()-> int:
    codigo: str = input('Ingrese el codigo de producto: ')
    codigos: list = ['1334','568']
    
    while not codigo in codigos:
        codigo = input('Codigo de producto inválido, intente nuevamente: ')
    
    return int(codigo)

def ultimo_numero_pedido(estado_pedidos: dict)-> int:
    ultimo_pedido: str = 0
    for pedido in estado_pedidos['pedidos validados']:
        if int(pedido[0]) > ultimo_pedido:
            ultimo_pedido = int(pedido[0])
    
    for articulo in estado_pedidos['pedidos cancelados']:
        if int(articulo[0]) > ultimo_pedido:
            ultimo_pedido = int(articulo[0])
    
    return ultimo_pedido

def parse_pedidos_csv()-> list:
    '''
    - Lee los pedidos cargados en el .csv y retorna una lista con ellos
    '''
    pedidos: list = []
    
    with open('pedidos.csv','r') as f:
        reader = csv.reader(f)
        primera_linea: bool = True
        
        for pedido in reader:
            if primera_linea:
                primera_linea = False
                continue
            else:
                pedidos.append(pedido)
    
    return pedidos

def procesar_pedidos_csv(stock: dict,pedidos: list)->dict:
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

def ingresar_producto_a_pedido(stock,n_pedido,fecha,cliente,ciudad,provincia)-> tuple:
    pedido: list = []
    codigo_articulo: int = validar_codigo_producto()
    color,cantidad = validar_color_stock(stock,codigo_articulo)
    descuento: int = validar_entero(0,100,'descuento')
    pedido: list = [n_pedido,fecha,cliente,ciudad,provincia,codigo_articulo,color,cantidad,descuento]
    stock[codigo_articulo]['color'][color] -= cantidad

    return stock,pedido
    
def ingresar_pedido(stock,estado_pedidos: dict)-> tuple:
    ultimo_pedido: int = ultimo_numero_pedido(estado_pedidos)
    
    numero_pedido: int = str(ultimo_pedido + 1)
    fecha = time.strftime("%d/%m/%Y")
    limpiar()
    cliente: str = validar_str('nombre del cliente')
    ciudad: str = validar_str('ciudad')
    provincia: str = validar_str('provincia')
    stock,pedido = ingresar_producto_a_pedido(stock,numero_pedido,fecha,cliente,ciudad,provincia)
    estado_pedidos['pedidos validados'].append(pedido)
    
    seguir_agregando: bool = True
     
    while seguir_agregando:
        agregar_producto: str = print('Desea agregar otro producto al pedido? (y/n): ')
        opcion: str = validar_opcion(['y','n'],'opcion')
        if opcion == 'n':
            seguir_agregando = False
            continue
        
        else:
            stock,pedido = ingresar_producto_a_pedido(stock,numero_pedido,fecha,cliente,ciudad,provincia)
            estado_pedidos['pedidos validados'].append(pedido)

    return stock,estado_pedidos

def remover_pedido_cancelado(n_pedido: int,estado_pedidos: dict):
    lista_actualizada: list = []
    for pedido in estado_pedidos['pedidos cancelados']:
        if pedido[0] != n_pedido:
            lista_actualizada.append(pedido)
    
    estado_pedidos['pedidos cancelados'] = lista_actualizada

    return estado_pedidos

def remover_pedido_validado(n_pedido: int, estado_pedidos: dict):
    lista_actualizada: list = []
    for pedido in estado_pedidos['pedidos validados']:
        if pedido[0] != n_pedido:
            lista_actualizada.append(pedido)
    
    estado_pedidos['pedidos validados'] = lista_actualizada

    return estado_pedidos

def rehacer_pedido(stock: dict,estado_pedidos: dict)->tuple:
   
    ultimo_pedido = ultimo_numero_pedido(estado_pedidos)
    numero_pedido: str = str(validar_entero(1,ultimo_pedido,'numero de pedido'))
    limpiar()
    print('Añada un producto') 
    datos_pedido: list = []
    estado_previo_pedido = ''
    
    for pedido in estado_pedidos['pedidos validados']: #tomo los datos del pedido ya registrados
        if numero_pedido == pedido[0]:
            datos_pedido = pedido
            estado_pedidos = remover_pedido_validado(numero_pedido,estado_pedidos)
    
    for articulo in estado_pedidos['pedidos cancelados']: #quito el pedido de la lista de cancelados
        if numero_pedido == articulo[0]:
            datos_pedido = articulo
            estado_pedidos = remover_pedido_cancelado(numero_pedido,estado_pedidos)
                 
    fecha: str = datos_pedido[1]
    cliente: str = datos_pedido[2]
    ciudad: str = datos_pedido[3]
    provincia: str = datos_pedido[4]    
    stock,pedido = ingresar_producto_a_pedido(stock,numero_pedido,fecha,cliente,ciudad,provincia)
    estado_pedidos['pedidos validados'].append(pedido) 
 
    seguir: bool = True
    
    while seguir:
        print('Desea agregar otro producto al pedido? (y/n)')
        seguir_agregando: str = validar_opcion(['y','n'],'opcion')
        if seguir_agregando == 'n':
            seguir = False
            continue
        
        else:
            stock,pedido = ingresar_producto_a_pedido(stock,numero_pedido,fecha,cliente,ciudad,provincia)
            estado_pedidos['pedidos validados'].append(pedido)

    return stock,estado_pedidos

def numero_pedidos_validados(estado_pedidos: dict):
    '''
    - Retorna una lista con los numeros de pedidos validados
    '''
    n_pedidos_validados: list = []
    for pedido in estado_pedidos['pedidos validados']:
        n_pedidos_validados.append(pedido[0])
    
    return n_pedidos_validados

def baja_pedido(stock: dict,estado_pedidos: dict)-> tuple:
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
        estado_pedidos = remover_pedido_validado(n_pedido_baja,estado_pedidos)
        input('Se cancelo el pedido, pulse ENTER para volver al menú ')

    return stock,estado_pedidos      

def mostrar_pedidos_procesados(estado_pedidos:dict)->None:
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

def actualizar_csv(estado_pedidos: dict)->None:
    pedidos_validados: list = estado_pedidos['pedidos validados']
    header: list = [
        'Nro. Pedidio', 'Fecha', 'Cliente', 'Ciudad', 'Provincia', 'Cod. Articulo', 'Color', 'Cantidad', 'Descuento'
        ]
    pedidos_acomodados: list = pedidos_validados.sort(key=lambda x: x[0])#ordeno por numero de pedido antes de escribir el csv

    with open('pedidos.csv','w',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)   
        writer.writerows(pedidos_validados)

def main()-> dict:
    '''
    - Actualiza el archivo .csv con los pedidos procesados y validados
    - retorna un dict con los pedidos validados y cancelados:
    - estado_pedidos = {'pedidos validados': [[ ],[ ],[ ],[ ]], 'pedidos cancelados': [[ ],[ ],[ ],[ ]]}
    '''
    stock = determinacion_lote.main()
    condicion_menu: bool = True
    estado_pedidos: dict = {}
    pedidos_lista: list = parse_pedidos_csv()
    estado_pedidos: dict = procesar_pedidos_csv(stock,pedidos_lista) 
    mostrar_pedidos_procesados(estado_pedidos)
    
    while condicion_menu:
        opcion: int = menu() 
        limpiar()
        if opcion == 1:
            stock,estado_pedidos = ingresar_pedido(stock,estado_pedidos)    
        elif opcion == 2:
            stock,estado_pedidos = rehacer_pedido(stock,estado_pedidos) 
        elif opcion == 3:
            stock,estado_pedidos = baja_pedido(stock,estado_pedidos)
        elif opcion == 4:
            mostrar_pedidos_procesados(estado_pedidos)
        elif opcion == 5:
            actualizar_csv(estado_pedidos)
            condicion_menu = False
    
    return estado_pedidos

main()
