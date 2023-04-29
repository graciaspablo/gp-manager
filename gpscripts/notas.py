from datetime import datetime, timedelta

def calculate(gp_time, mbd_time, drg_time, daily_ranking, streak, last_7_mbd):
    gp_time_obj = datetime.strptime(gp_time, '%H:%M')
    mbd_time_obj = datetime.strptime(mbd_time, '%H:%M')
    drg_time_obj = datetime.strptime(drg_time, '%H:%M')

    # --- TIEMPO DE RESPUESTA EN HORAS CON DECIMALES --- max 10, gp el mismo minuto que el mbd
    response_time_obj = gp_time_obj - mbd_time_obj

    #esto creo que es muy innecesario. hours_until_midnight podría ser siempre 24 y a la mierda
    midnight = mbd_time_obj.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    time_until_midnight = midnight - mbd_time_obj
    hours_until_midnight = int(time_until_midnight.total_seconds() / 3600)

    response_time_score = 10 - ((response_time_obj.total_seconds() / 3600) / hours_until_midnight) * 10

    # --- PUESTO DEL GP --- max: 10, puesto primero
    rank_score = 10 / daily_ranking

    # --- RACHAS --- max: 10, 31 días de racha
    streak_score = (((streak - 1) ** 2) / 100) + 1

    # --- DIFICULTAD ---
    # este valor es único para cada día independientemente del gp

    # --- TIEMPO ENTRE MBD Y DRG (esto divide!!!) ---
    legal_time_obj = drg_time_obj - mbd_time_obj
    legal_time_difficulty = 10 - ((legal_time_obj.total_seconds() / 3600) / hours_until_midnight) * 10
    print(legal_time_difficulty)
    

    # --- DIFICULTAD SEGÚN LA HORA ---
    # puntos:
    h1 = datetime.strptime("23:00", '%H:%M') #min dificultad y crece
    h2 = datetime.strptime("4:30", '%H:%M') #max dificultad y decrece
    h3 = datetime.strptime("15:00", '%H:%M') #min dificultad estancada
    h4 = datetime.strptime("22:00", '%H:%M') #min dificultad estancada

    if is_time_in_range(h1, h2, mbd_time_obj):
        # dificultad crece, hasta el pico h2
        mbd_difficulty = 1
    if is_time_in_range(h2, h3, mbd_time_obj):
        # desciende hasta h3
        mbd_difficulty = 1
    if is_time_in_range(h3, h4, mbd_time_obj):
        # se mantiene igual
        mbd_difficulty = 1
        
    # --- ESTABILIDAD DEL MBD ---
    mbd_stability = 1



def is_time_in_range(start, end, x):
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

def main():
    calculate(gp_time="9:00", mbd_time="8:00", drg_time="9:00", daily_ranking=1, streak=31, last_7_mbd=["10:00", "13:00", "13:00", "13:00", "11:30", "13:00", "13:00"])
    

if __name__ == "__main__":
    main()