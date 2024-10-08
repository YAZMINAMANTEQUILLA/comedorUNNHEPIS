
from datetime import datetime

def fecha():
    hoy = datetime.now()
    dia = hoy.strftime('%d')
    mes = hoy.strftime('%m')
    año = hoy.strftime('%Y')

    text = dia + "/" + mes + "/"+ año
    return  text

def verificar_comida():
    hora_actual = datetime.now()
    tiempo_total = hora_actual.hour * 60 + hora_actual.minute

    desayuno_inicio = 6 * 60 + 30  # 6:30 AM en minutos
    desayuno_fin = 8* 60           # 8:00 AM en minutos

    almuerzo_inicio = 12 * 60   # 12:00 PM en minutos
    almuerzo_fin = 17* 60 + 30   # 2:30 PM en minutos

    cena_inicio = 00 * 60        # 5:30 PM en minutos
    cena_fin = 5 * 60         # 7:30 PM en minutos

    if desayuno_inicio <= tiempo_total <= desayuno_fin:
        return "DESAYUNO"
    elif almuerzo_inicio <= tiempo_total <= almuerzo_fin:
        return "ALMUERZO"
    elif cena_inicio <= tiempo_total <= cena_fin:
        return "CENA"
    else:
        return "Fuera de los tiempos de comida"
