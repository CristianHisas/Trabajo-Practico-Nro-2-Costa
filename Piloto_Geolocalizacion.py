import os 
import csv
from geopy.geocoders import Nominatim


archivo_pedidos = open('pedidos.csv', 'r', encoding='utf-8')

def recoleccion_datos_ciudades(archivo_datos):
    spamreader = csv.reader(archivo_pedidos, dialect='excel',delimiter=',', quotechar='|')
    next(spamreader)
    ciudades = {}
    for row in spamreader:
        if row != []:
            if row[0] not in ciudades:
                ciudades[row[0]] = [row[3],[row[5],row[7]]]
    
            else:
                ciudades[row[0]].append([row[5],row[7]])
    return ciudades

def ordenar_norte(zona_norte):
    orden_norte: list = sorted(zona_norte.items(), key=lambda x: x[1][1], reverse = True)
    return orden_norte

def ordenar_centro(zona_centro):
    orden_centro: list = sorted(zona_centro.items(), key=lambda x: x[1][1],reverse = True)
    return orden_centro

def ordenar_sur(zona_sur):
    orden_sur: list = sorted(zona_sur.items(), key=lambda x: x[1],reverse = True)
    return orden_sur

def distribucion_zonas(lista_ciudad:list):#,opcion: int)-> list: 
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


def averiguar_peso(zona_norte,zona_centro,zona_caba,zona_sur,dict_pedidos):
    codigo_botella = '1334'
    codigo_vaso = '568'
    peso_botella = 450
    peso_vaso = 350
    peso_sur = 0
    peso_norte = 0
    peso_centro = 0
    peso_caba = 0
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
    peso_centro = peso_centro /1000
    peso_caba = peso_caba /1000
    peso_norte= peso_norte /1000
    peso_sur= peso_sur /1000
    return peso_norte,peso_centro,peso_caba,peso_sur



def hacer_viaje_optimo(dict_pedidos,opcion)-> list:
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

def hacer_camiones(dict_pedidos):
    zona_norte:dict = {}
    zona_sur:dict = {}
    zona_centro:dict = {}
    zona_caba: list = []
    camiones_disponible = [('utilitero1',600),('utilitero2',1000),('utilitero3',500),('utilitero4',2000)]
    #utilitero1 = 600
    #utilitero2 = 1000
    #utilitero3 = 500
    #utilitero4 = 2000
    ciudades = []
    for datos in dict_pedidos.values():
        ciudades.append(datos[0])
    zona_norte,zona_centro,zona_caba,zona_sur = distribucion_zonas(ciudades)
    print(zona_norte)
    print(zona_centro)
    print(zona_caba)
    print(zona_sur)
    peso_norte,peso_centro,peso_caba,peso_sur = averiguar_peso(zona_norte,zona_centro,zona_caba,zona_sur,dict_pedidos)
    #print(peso_norte)
    #print(peso_centro)
    #print(peso_caba)
    #print(peso_sur)
 

a =recoleccion_datos_ciudades(archivo_pedidos)
#hacer_camiones(a)
print(hacer_viaje_optimo(a,4))