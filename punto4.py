# Determinar todos los pedidos que se pudieron completar priorizando la
# fecha (los más antiguos primero). Mostar el listado y cuántos fueron. 

#Listo todos los pedidos completos desde el mas antiguo al mas reciente (indico cant de pedidos completos).
def listar_pedidos_completos(pedidos_terminados : dict):
    print(f"Pedidos completados: {len(pedidos_terminados)}")
    for numero, pedidos in pedidos_terminados.items():
        print(f"Numero pedido: {numero}, Fecha: {pedidos[0]}/{pedidos[1]}/{pedidos[2]}, Cliente: {pedidos[3]}, Ciudad: {pedidos[4]}, Provincia: {pedidos[5]}")
        print("     Artículos: ")
        for articulo in pedidos[6]:
            print(f"        Numero artículo: {articulo[0]}, Color: {articulo[1]}, Cantidad: {articulo[2]}, Descuento: {articulo[3]}")

#Ordeno los pedidos primero por dia despues por mes y por ultimo por fecha.
def ordenar_pedidos_fecha(pedidos_separados_fecha : dict):
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
def separar_fechas(pedidos_terminados : dict, pedidos_fechas_separada : dict):
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

def main():
    pedidos_fechas_separada : dict = {}
    pedidos_terminados_dict : dict = {}
    #dict de pedidos completados que utilizo como ej
    pedidos : dict = {
        1: ["01/11/2021","Juan Alvarez","Villa María","Córdoba",[["1334","Azul",36,5],["568","Azul",12,5]]],
        2: ["9/2/2021","Carlos Rodriguez","Parana","Santa Fe",[["1334","Azul",36,5],["568","Azul",12,5]]],
        3: ["02/11/2015","Juan Lopez","Santa Rosa","La Pampa",[["1334","Amarillo",12,10],["568","Azul",12,5]]],
        4: ["19/8/2001","Juan Lopez","Santa Rosa","La Pampa",[["1334","Amarillo",12,10],["568","Azul",12,5]]],
        5: ["02/11/2011","Juan Lopez","Santa Rosa","La Pampa",[["1334","Amarillo",12,10],["568","Azul",12,5]]],
        6: ["12/11/2021","Juan Lopez","Santa Rosa","La Pampa",[["1334","Amarillo",12,10],["568","Azul",12,5]]],
        7: ["12/3/2021","Juan Lopez","Santa Rosa","La Pampa",[["1334","Amarillo",12,10],["568","Azul",12,5]]],
    }

    pedidos_fechas_separada = separar_fechas(pedidos, pedidos_fechas_separada)
    pedidos_terminados_dict = ordenar_pedidos_fecha(pedidos_fechas_separada)
    listar_pedidos_completos(pedidos_terminados_dict)

main()

#lo unico que falta es saber como llega el input si es un dict con todos los pedidos o solo los terminados (ademas de saber su sintaxis)...