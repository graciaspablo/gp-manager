'''

|------GP-ENGINE------|

Programa para procesar un juego de gp. Toma como input un .txt directamente del chat de WhatsApp
y puede mostrar las puntuaciones de los jugadores, las faltas y algunas estadísticas generales.

Puede generar un .csv para ser abierto en un Excel y terminar de asignar manualmente el resto de
faltas y observaciones que requieran conocer el contexto (falso profeta, etc).

Features:
- Muestra la cantidad total de gp por jugador
- Procesa faltas:
    - "gp" fuera de periodo legal
    - 
- NO encuentra faltas donde el contexto es necesario para determinarlas

TODO: sistema por meses, para calcular estadísticas mensuales, (tarjetas rojas y eliminaciones)
TODO: tener en cuenta los mensaje de amarilla de aitor para verificar dudosas amarillas


'''
import pandas as pd
import numpy as np
import openpyxl
from datetime import datetime

import gp
import mbd
import drg

import config

class Player:

    def __init__(self, name, gp_amount=0, fouls=[], reds=0):
        self.name = name
        self.gp_amount = gp_amount
        self.fouls = fouls
        self.reds = reds #TODO: calcular rojas si hay dos amarillas el mismo mes

#Procesa toda la lógica del juego e intenta determinar faltas.
def run_days(df):
    print('Procesando lógica del juego...')

    #Crea una nueva columna vacía en el dataframe general para las faltas (NO SON AMARILLAS)
    df['FALTAS'] = np.nan

    df['FALTAS'] = np.empty((len(df), 0)).tolist()

    players = []            

    #CADA JUGADOR
    for player_name in config.PLAYER_NAMES:
        gp_amount = 0
        fouls = []

        try:
            #CADA DIA
            for i in range(1000):

                cdf = df.iloc[i]
                current_day = cdf.name.date()
                
                foul_today = False
                mbd_today = False #no usado
                drg_today = False
                
                #Chequear si ha habido MBD
                if str(cdf['HORA_MBD']) != 'nan':
                    mbd_today = True

                    #Chequear si ha habido DRG
                    if str(cdf['HORA_DRG']) != 'nan':
                        drg_today = True

                    #Chequear si se ha gpeado
                    if str(cdf[player_name]) != 'nan':
                        gp_amount += 1
                        
                        #Chequear si se ha gpeado más de una vez en el mismo día.
                        if ';' in str(cdf[player_name]):
                            fouls.append([str(current_day), '+1GP'])
                            foul_today = True

                            list_of_gps = str(cdf[player_name]).split("; ")

                            #Chequear si se ha gepeado antes del MBD por cada gp gepeado hoy (innecesario??????)
                            for gp in list_of_gps:
                                mbd_time = datetime.strptime(str(cdf['HORA_MBD']), '%H:%M:%S').time()
                                gp_time = datetime.strptime(gp, '%H:%M:%S').time()
                                if gp_time < mbd_time:
                                    if not foul_today:
                                        fouls.append([str(current_day), 'GPaMBD', str(gp_time)])
                                        foul_today = True
                                else:
                                    pass
                            #Chequear si ha gepeado después del DRG por cada gp gepeado hoy (?????????????)
                                if drg_today:
                                    drg_time = datetime.strptime(str(cdf['HORA_DRG']), '%H:%M:%S').time()
                                    if mbd_time > drg_time:
                                        if not foul_today:
                                            fouls.append([str(current_day), 'GPaMBD', str(gp_time)])
                                            foul_today = True
                                else:
                                    #Hoy no ha habido drg
                                    pass

                        #(se ha gepeado una sola vez, continuar...)                                
                        else:
                            #Chequear si se ha gepeado antes del MBD
                            mbd_time = datetime.strptime(str(cdf['HORA_MBD']), '%H:%M:%S').time()
                            gp_time = datetime.strptime(str(cdf[player_name]), '%H:%M:%S').time()

                            if gp_time < mbd_time:
                                if not foul_today:
                                    fouls.append([str(current_day), 'GPaMBD', str(gp_time)])
                                    foul_today = True
                            else:
                                #No se ha gepeado antes del MBD, no hay falta
                                pass

                            #Chequear si se ha gepeado después del DRG
                            if drg_today:
                                drg_time = datetime.strptime(str(cdf['HORA_DRG']), '%H:%M:%S').time()
                                gp_time = datetime.strptime(str(cdf[player_name]), '%H:%M:%S').time()

                                if gp_time > drg_time:
                                    if not foul_today:
                                        fouls.append([str(current_day), 'GPdDRG', str(gp_time)])
                                        foul_today = True
                            else:
                                #No ha habido drg hoy
                                pass
                else:
                    #Chequear si se ha gepeado sin MBD hoy
                    if str(cdf[player_name]) != 'nan':
                        if not foul_today:
                            fouls.append([str(current_day), 'GPsinMBD', str(gp_time)])
                            foul_today = True

                #df.loc[str(current_day), 'FALTAS'] = str(fouls)
                #print(str(current_day) + ' ' + str(fouls))

                #detiene dias
                if config.ONLY_ONE_RUN:
                    break                

        #esto debería hacerse de otra manera...                
        except IndexError:
            players.append(Player(player_name, gp_amount, fouls))

        #detiene jugadores
        if config.ONLY_ONE_RUN:
            break

    #TERMINADO
    #print(df.tail(50))
    for player in players:

        if config.PRINT_SUMMARY:
            print('---' + player.name + '---')
            print('CANTIDAD GP: ' + str(player.gp_amount))
            print('CANTIDAD AMARILLAS: ' + str(player.fouls))

        #Añadir faltas al df
        for foul in player.fouls:
            df.loc[foul[0], 'FALTAS'].append(player.name + ': ' + foul[1])

    return df

def main():

    print('GP-ENGINE')

    df_gp = gp.make_dataframe()
    df_mbd = mbd.make_dataframe()
    df_drg = drg.make_dataframe()

    df = pd.merge(df_mbd, df_gp, how='outer', on='new_date')
    df = pd.merge(df, df_drg, how='outer', on='new_date')

    df['FALTAS'] = np.empty((len(df), 0)).tolist()

    df.index.names = ['DATE']

    #Reordenar y modificar nombres de las columnas
    cols = df.columns.tolist()
    #los nombres de los jugadores podrían ser cogidos de config.PLAYER_NAMES para que sea más facil añadir jugadores nuevos
    cols = ['HORA_MBD', 'Aina', 'Aitor', 'Anton', 'Diego', 'Joaquín', 'Laura', 'Miranda', 'Nerea', 'Paula', 'Sergio', 'HORA_DRG', 'FALTAS', 'MBD_TIPO']
    df = df[cols]

    

    if config.RUN_DAYS:
        pdf = run_days(df)

        if config.MAKE_CSV:
            #Convierte la columna de faltas de lista a string. Solo debería usarse para exportar el csv
            df['FALTAS'] = df.FALTAS.apply(lambda x: ', '.join([str(i) for i in x]))
            #pdf.to_excel('EXCEL.xlsx', encoding='utf-8')
            pdf.to_csv('out.csv', encoding='utf-8')
            print('CSV EXPORTADO CON ÉXITO')

if __name__ == '__main__':
    main()

    