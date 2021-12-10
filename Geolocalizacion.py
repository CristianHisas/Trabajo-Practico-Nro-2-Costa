import os 
import csv
from geopy.geocoders import SERVICE_TO_GEOCODER, Nominatim


def recoleccion_datos_ciudades()->dict:
    archivo_pedidos = open('pedidos.csv', 'r', encoding='utf-8')
    leectura = csv.reader(archivo_pedidos, dialect='excel',delimiter=',', quotechar='|')
    next(leectura)
    ciudades = {}
    for row in leectura:
        if row != []:
            if row[0] not in ciudades:
                ciudades[row[0]] = [row[3],[row[5],row[7]]]
    
            else:
                ciudades[row[0]].append([row[5],row[7]])
    archivo_pedidos.close()
    return ciudades

def ordenar_norte(zona_norte:dict)->list:
    orden_norte: list = sorted(zona_norte.items(), key=lambda x: x[1][1], reverse = True)
    lista_sin_coordenadas_norte: list = []
    for ciudad in orden_norte:
        lista_sin_coordenadas_norte.append(ciudad[0])
    return lista_sin_coordenadas_norte

def ordenar_centro(zona_centro:dict)->list:
    orden_centro: list = sorted(zona_centro.items(), key=lambda x: x[1][1],reverse = True)
    lista_sin_coordenadas_centro: list= []
    for ciudad in orden_centro:
        lista_sin_coordenadas_centro.append(ciudad[0])
    return lista_sin_coordenadas_centro

def ordenar_sur(zona_sur: dict)->list:
    orden_sur: list = sorted(zona_sur.items(), key=lambda x: x[1],reverse = True)
    lista_sin_coordenadas_sur: list= []
    for ciudad in orden_sur:
        lista_sin_coordenadas_sur.append(ciudad[0])
    return lista_sin_coordenadas_sur

def ordenar_camiones_pesos(dict_camiones: dict,dict_pesos:dict)->list:
    orden_camiones: list = sorted(dict_camiones.items(), key=lambda x: x[1],reverse = True)
    orden_pesos: list = sorted(dict_pesos.items(), key=lambda x: x[1],reverse = True)
    return orden_camiones,orden_pesos

def distribucion_zonas(lista_ciudad:list)->list: 
    geolocator = Nominatim(user_agent='API')
    lugar_coordenadas:dict = {}
    zona_norte:dict = {}
    zona_sur:dict = {}
    zona_centro:dict = {}
    zona_caba: list = []
    for indice in range(1,len(lista_ciudad)):
        buscar_ciudad = geolocator.geocode(lista_ciudad[indice],country_codes='AR',timeout=15)
        latitud_ciudad: float = buscar_ciudad.latitude
        longitud_ciudad: float = buscar_ciudad.longitude
        lugar_coordenadas[lista_ciudad[indice]] = [latitud_ciudad,longitud_ciudad]
    for ciudad in lugar_coordenadas.items():
        if ciudad[0] == 'CABA':
            zona_caba.append(ciudad[0])
        elif int(ciudad[1][0]) > -35:
            zona_norte[ciudad[0]] = ciudad[1]
        elif int(ciudad[1][0]) < -40:
            zona_sur[ciudad[0]] = ciudad[1]
        elif -35 >= int(ciudad[1][0]) >= -40:
            zona_centro[ciudad[0]] = ciudad[1]
    zona_norte = ordenar_norte(zona_norte)
    zona_centro = ordenar_centro(zona_centro)
    zona_sur = ordenar_sur(zona_sur)
    return zona_norte,zona_centro,zona_caba,zona_sur


def averiguar_peso(zona_norte:list ,zona_centro:list ,zona_caba:list ,zona_sur:list ,dict_pedidos:dict )-> float:
    codigo_botella: str = '1334'
    codigo_vaso: str = '568'
    peso_botella: int = 450
    peso_vaso: int = 350
    peso_sur: int = 0
    peso_norte: int = 0
    peso_centro: int = 0
    peso_caba: int = 0
    for ciudad in dict_pedidos.values():
        if ciudad[0] in zona_caba:
            for lista in ciudad:
                if lista[0] == codigo_botella:
                    peso_caba += (int(lista[1]) * peso_botella)
                elif lista[0] == codigo_vaso:
                    peso_caba += (int(lista[1]) * peso_vaso)
        elif ciudad[0] in zona_sur:
            for lista in ciudad:
                if lista[0] == codigo_botella:
                    peso_sur += (int(lista[1]) * peso_botella)
                elif lista[0] == codigo_vaso:
                    peso_sur += (int(lista[1]) * peso_vaso)
        elif ciudad[0] in zona_norte:
            for lista in ciudad:
                if lista[0] == codigo_botella:
                    peso_norte += (int(lista[1]) * peso_botella)
                elif lista[0] == codigo_vaso:
                    peso_norte += (int(lista[1]) * peso_vaso)
        elif ciudad[0] in zona_centro:
            for lista in ciudad:
                if lista[0] == codigo_botella:
                    peso_centro += (int(lista[1]) * peso_botella)
                elif lista[0] == codigo_vaso:
                    peso_centro += (int(lista[1]) * peso_vaso)
    peso_centro: int = peso_centro /1000
    peso_caba: int = peso_caba /1000
    peso_norte: int = peso_norte /1000
    peso_sur: int = peso_sur /1000
    return peso_norte,peso_centro,peso_caba,peso_sur



def hacer_viaje_optimo(dict_pedidos:dict,opcion: int)-> list:
    ciudades: list = []
    zona_norte_ciudades : list = []
    zona_centro_ciudades : list = []
    zona_caba_ciudades : list = []
    zona_sur_ciudades : list = []
    for datos in dict_pedidos.values():
        ciudades.append(datos[0])
    zona_norte,zona_centro,zona_caba,zona_sur = distribucion_zonas(ciudades) 
    for ciudad_en_zona in zona_norte:
        zona_norte_ciudades.append(ciudad_en_zona[0])
    for ciudad_en_zona in zona_centro:
        zona_centro_ciudades.append(ciudad_en_zona[0])
    for ciudad_en_zona in zona_sur:
        zona_sur_ciudades.append(ciudad_en_zona[0])
    zona_caba_ciudades.append(zona_caba[0])
    if opcion == 1 :
        return zona_norte_ciudades
    elif opcion == 2:
        return zona_centro_ciudades
    elif opcion == 3:
        return zona_caba_ciudades
    elif opcion == 4:
        return zona_sur_ciudades

def hacer_camiones(dict_pedidos:dict)-> list:
    pedidos_que_salen: list = []
    zona_norte:dict = {}
    zona_sur:dict = {}
    zona_centro:dict = {}
    zona_caba: list = []
    peso_zonas: list = {}
    camiones_disponible: dict = {'utilitero1':600,'utilitero2':1000,'utilitero3':500,'utilitero4':2000}
    ciudades: list = []
    for datos in dict_pedidos.values():
        ciudades.append(datos[0])
    zona_norte,zona_centro,zona_caba,zona_sur = distribucion_zonas(ciudades)
    peso_norte,peso_centro,peso_caba,peso_sur = averiguar_peso(zona_norte,zona_centro,zona_caba,zona_sur,dict_pedidos)
    peso_zonas['peso_norte'] = peso_norte
    peso_zonas['peso_centro'] = peso_centro
    peso_zonas['peso_caba'] = peso_caba
    peso_zonas['peso_sur'] = peso_sur
    camiones_disponible, peso_zonas = ordenar_camiones_pesos(camiones_disponible,peso_zonas)
    for indice in range(len(camiones_disponible)):
        if peso_zonas[indice][1] < camiones_disponible[indice][1]:
            pedidos_que_salen.append([camiones_disponible[indice][0],peso_zonas[indice][0],peso_zonas[indice][1]])
    for pedido in pedidos_que_salen:
        if 'norte' in pedido[1]:
            pedido.append(zona_norte)
            pedido.append('zona_norte')
        elif 'centro' in pedido[1]:
            pedido.append(zona_centro)
            pedido.append('zona_centro')
        elif 'caba' in pedido[1]:
            pedido.append(zona_caba)
            pedido.append('zona_caba')
        elif 'sur' in pedido[1]:
            pedido.append(zona_sur)
            pedido.append('zona_sur')

    return pedidos_que_salen

def escribir_txt(datos:list)-> None:
    if os.path.exists("salida.txt"):
        os.remove("salida.txt")
    archivo = open('salida.txt','a',encoding='utf-8',)
    for pedido in datos:
        archivo.write('\n')
        archivo.write(pedido[4] )
        archivo.write('\n')            
        archivo.write(pedido[0])
        archivo.write('\n')
        archivo.write(str(pedido[2]))
        archivo.write('\n')
        for ciudad in pedido[3]:
            archivo.write(ciudad)
            archivo.write('\n')
    archivo.close

        