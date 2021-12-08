import csv
import time
import os
import determinacion_lote

def limpiar()-> None:
    print('\n' * 150)

def validar_opcion(opciones:list,opcion: str)-> str:
    ingresar_opcion: str = input(f'Ingrese {opcion}: ')
    
    while ingresar_opcion.lower() not in opciones:
        ingresar_opcion = input(f'{opcion} invalido/a, intente nuevamente: ')
    
    return ingresar_opcion

def validar_str(opcion)->str:
    ingrese_str: str = input(f'Ingrese {opcion}: ')
    
    while type(ingrese_str) != str or ingrese_str == '':
        ingrese_str = input(f'{opcion} invalido/a, intente nuevamente: ')
    
    return ingrese_str

def validar_entero(opcion_min: int, opcion_max: int,opcion:str)-> int:
    entero: str = input(f'ingrese {opcion}: ')
    
    while not entero.isnumeric() or int(entero) < opcion_min or int(entero) > opcion_max:
        entero = input(f'{opcion} invalido/a, intente nuevamente: ')
    
    return int(entero)

def validar_color_producto(cod_producto)-> str:
    color = input('Ingrese el color del producto: ')
    colores = {1334: ['rojo','azul','verde','negro','amarillo'],
               568 : ['negro','azul']}
    
    while color.lower() not in colores[cod_producto]:
        color = input('Ese color no esta disponible, intente con otro color: ')

    return color.lower()

def actualizar_csv(pedidos:list)->None:
    header: list = [
        'Nro. Pedidio', 'Fecha', 'Cliente', 'Ciudad', 'Provincia', 'Cod. Articulo', 'Color', 'Cantidad', 'Descuento'
        ]
    pedidos_acomodados: list = pedidos.sort(key=lambda x: x[0])#ordeno por numero de pedido antes de escribir el csv

    with open('pedidos.csv','w',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)   
        writer.writerows(pedidos)

def mostrar_stock(stock: dict,cod_articulo: str)-> None:
    if cod_articulo == 1334:
        print(f"""\n\n| COLORES DE BOTELLA DISPONIBLES |     
  VERDE: {stock[1334]['color']['verde']}
  ROJO: {stock[1334]['color']['rojo']}
  AZUL: {stock[1334]['color']['azul']}
  NEGRO: {stock[1334]['color']['negro']}""")
    
    else:
        print(f"""\n\n| COLORES DE VASOS DISPONIBLES |     
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
        codigo = input('Codigo de producto invalido, intente nuevamente: ')
    
    return int(codigo)

def ultimo_numero_pedido(pedidos: list)-> int:
    ultimo_pedido: int = 0
    
    for pedido in pedidos:
        if int(pedido[0]) > ultimo_pedido:
            ultimo_pedido = int(pedido[0])
    
    return ultimo_pedido

def parse_pedidos_csv()-> list:
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

def menu()->int:
    limpiar()
    print('|        Menu        |')
    print('1) Ingresar pedido')
    print('2) Rehacer pedido')
    print('3) Cancelar pedido')
    print('4) Procesar y mostrar estado de los pedidos')
    print('5) Terminar')
    opcion: int = validar_entero(1,5,'opcion')

    return opcion

def ingresar_producto_a_pedido(stock,n_pedido,fecha,cliente,ciudad,provincia)-> tuple:
    pedido: list = []
    codigo_articulo: int = validar_codigo_producto()
    color,cantidad = validar_color_stock(stock,codigo_articulo)
    descuento: int = validar_entero(0,100,'descuento')
    pedido: list = [n_pedido,fecha,cliente,ciudad,provincia,codigo_articulo,color,cantidad,descuento]
    stock[codigo_articulo]['color'][color] -= cantidad

    return stock,pedido
    
def ingresar_pedido(stock,estado_pedidos: dict)-> tuple:
    pedidos: list = parse_pedidos_csv()
    ultimo_pedido: int = ultimo_numero_pedido(pedidos)
    
    numero_pedido: int = int(ultimo_pedido) + 1
    fecha = time.strftime("%d/%m/%Y")
    cliente: str = validar_str('nombre del cliente')
    ciudad: str = validar_str('ciudad')
    provincia: str = validar_str('provincia')
    stock,pedido = ingresar_producto_a_pedido(stock,numero_pedido,fecha,cliente,ciudad,provincia)
    estado_pedidos['pedidos validados'].append(pedido)
    
    with open('pedidos.csv','a+',newline='') as file:
        writer = csv.writer(file)
        writer.writerow(pedido)
    
    seguir_agregando: bool = True
    agregar_producto: str = input('Desea agregar otro producto al pedido? (y/n): ')
    
    while seguir_agregando:
        if agregar_producto.lower() == 'n':
            seguir_agregando = False
            continue
        
        else:
            stock,pedido = ingresar_producto_a_pedido(stock,numero_pedido,fecha,cliente,ciudad,provincia)
            estado_pedidos['pedidos validados'].append(pedido)
            
            with open('pedidos.csv','a+',newline='') as file:
                writer = csv.writer(file)
                writer.writerow(pedido)
            agregar_producto: str = input('Desea agregar otro producto al pedido? (y/n): ') 

    return stock,estado_pedidos


def rehacer_pedido(stock: dict,estado_pedidos: dict)->tuple:
    '''
    -
    '''
    pedidos: list = parse_pedidos_csv()
    pedidos_actualizados: list = []
    numero_pedido: str = input('Ingrese el numero del pedido a rehacer: ')
    print('Ingrese un producto') 
    datos_pedido: list = []
    
    for pedido in pedidos:
        if numero_pedido == pedido[0]:
            datos_pedido = pedido
        
        else:
            pedidos_actualizados.append(pedido)
    
    fecha: str = datos_pedido[1]
    cliente: str = datos_pedido[2]
    ciudad: str = datos_pedido[3]
    provincia: str = datos_pedido[4]    
    stock,pedido = ingresar_producto_a_pedido(stock,numero_pedido,fecha,cliente,ciudad,provincia)
    estado_pedidos['pedidos validados'].append(pedido) 
    pedidos_actualizados.append(pedido)
    
    actualizar_csv(pedidos_actualizados)

    pedidos_actualizados_canc: list = [] 
    for articulo in estado_pedidos['pedidos cancelados']:
        if  not numero_pedido == articulo[0]:
            pedidos_actualizados_canc.append(articulo)
    estado_pedidos['pedidos cancelados'] = pedidos_actualizados_canc
    
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
            pedidos_actualizados.append(pedido)
            actualizar_csv(pedidos_actualizados)
    
    return stock,estado_pedidos

def baja_pedido(estado_pedidos: dict)-> dict:
    n_pedidos_validados: list = []
    pedidos_actualizados: list = []
    
    for pedido in estado_pedidos['pedidos validados']:
        if pedido[0] not in n_pedidos_validados:
            n_pedidos_validados.append(pedido[0])
   
    pedido_baja: str = input('Ingrese el numero del pedido a dar de baja: ')
    
    if pedido_baja not in n_pedidos_validados:
        input('No se encontro ese numero de pedido, pulse ENTER para volver al menu')
    
    else:
        for pedido in estado_pedidos['pedidos validados']:
            if not pedido[0] == pedido_baja:
                pedidos_actualizados.append(pedido)
        input('Pedido cancelado, pulse ENTER para volver al menu')
        estado_pedidos['pedidos validados'] = pedidos_actualizados
        
        pedidos_actualizados_canc: list = []
        
        for articulo in estado_pedidos['pedidos cancelados']:
            if not pedido[0] == pedido_baja:
                pedidos_actualizados_canc.append(articulo)
        estado_pedidos['pedidos cancelados'] = pedidos_actualizados_canc
    
    return estado_pedidos
        

def procesar_pedidos_csv(stock: dict,pedidos: list)->dict:
    '''
    devuelve un dict con los datos de los pedidos validados y cancelados, y el stock actualizado
    '''
    estado_pedidos: dict = {}
    pedidos_validados: list = []
    pedidos_cancelados: list = []
    numeros_pedidos_cancelados: list = []
    for pedido in pedidos:
        
        if stock[int(pedido[5])]['color'][pedido[6].lower()] - int(pedido[7]) < 0 and not pedido in pedidos_cancelados:
            pedidos_cancelados.append(pedido)
            numeros_pedidos_cancelados.append(pedido[0])
        
        elif pedido[0] in numeros_pedidos_cancelados:
            pedidos_cancelados.append(pedido)
        
        else:
            stock[int(pedido[5])]['color'][pedido[6].lower()] -= int(pedido[7])
            pedidos_validados.append(pedido)
        
    estado_pedidos['pedidos cancelados'] = pedidos_cancelados
    estado_pedidos['pedidos validados'] = pedidos_validados
    
    return estado_pedidos

def mostrar_pedidos_procesados(estado_pedidos:dict)->None:
    pedidos_procesados: list = estado_pedidos['pedidos validados']
    pedidos_cancelados: list = estado_pedidos['pedidos cancelados']
    header: str = ' Pedido     Fecha        Cliente         Datos de envio '
    n_pedidos_mostrados: list = []
    print('\n\n\n| PEDIDOS PROCESADOS |')
    print(header)
    
    for pedido in pedidos_procesados:
        if pedido[0] not in n_pedidos_mostrados:
            print(f'  {pedido[0]}:     {pedido[1]}   {pedido[2]}     {pedido[3]} {pedido[4]}')
            n_pedidos_mostrados.append(pedido[0])
    
    input('\nPulse ENTER para mostrar los pedidos cancelados')
    
    print('\n\nPEDIDOS CANCELADOS')
    print(header)
    n_pedidos_mostrados = []
    for pedido in pedidos_cancelados:
        if pedido[0] not in n_pedidos_mostrados:
            print(f'  {pedido[0]}:     {pedido[1]}   {pedido[2]}     {pedido[3]} {pedido[4]}')
            n_pedidos_mostrados.append(pedido[0])
    
    input('Ingrese ENTER para volver al menu ')

def main()-> dict:
    '''
    - retorna un dict con los pedidos validados y cancelados:
    - estado_pedidos = {'pedidos validados': lista_validados, 'pedidos cancelados': lista_cancelado}
    '''
    
    stock = determinacion_lote.main()
    condicion_menu: bool = True
    estado_pedidos: dict = {}
    pedidos_lista: list = parse_pedidos_csv()
    estado_pedidos: dict = procesar_pedidos_csv(stock,pedidos_lista) 
    
    while condicion_menu:
           
        opcion: int = menu() 
        limpiar()
        if opcion == 1:
            stock,estado_pedidos = ingresar_pedido(stock,estado_pedidos)    
        elif opcion == 2:
            stock,estado_pedidos = rehacer_pedido(stock,estado_pedidos) 
        elif opcion == 3:
            estado_pedidos = baja_pedido(estado_pedidos)
        elif opcion == 4:
            mostrar_pedidos_procesados(estado_pedidos)
        elif opcion == 5:
            condicion_menu = False
    
    return estado_pedidos
main()