# Copyright (C) 2015  Niklas Rosenstein, MIT License
# Last modified by Luigi Faxina (2023) 
# Code compilation based on the codes of Yi Jui Lee(2015) and Matheus Taborda(2022)

from __future__ import division

import time
import os
from os.path import exists
import pandas as pd
import serial
import json
import myo
import threading
from myo.lowlevel import stream_emg
from myo.six import print_

#Conexão com os ESP's através das portas bluetooth do notebook
try:
    BL1 = serial.Serial('COM4',115200) #esp1
    print("Connected ESP32-LEFT")
except:
    print("Error when connecting to the ESP32-LEFT")
try:
    BL2 = serial.Serial('COM7',115200) #esp2
    print("Connected ESP32-RIGHT")
except:
    print("Error when connecting to the ESP32-RIGHT")

open('Emg', 'w').close()
'''
Melhorar o código para inserir os outros sensores da MYO
open('Acceleration.txt', 'w').close()
open('Gyroscope.txt','w').close()
open('Orientation.txt', 'w').close()
'''

last_t = 0
delta_t = []
timestamp_list = []
data_list = []

flag = True

df_myo = pd.DataFrame()

temp = []
with open('PythonVars.txt') as f:
    for val in f:
        temp.append(int(val))

samplerate = temp[0]
t_s = 1 / samplerate
print("\n\nSample rate is adjusted to " + str(samplerate) + " Hz")
print("Collecting emg data every " + str(t_s) + " seconds")

file_number = 0
r = "Data\Emg_" + str(file_number) + ".csv"
while (exists(r)):
    file_number = file_number + 1
    r = "Data\Emg_" + str(file_number) + ".csv"

T = temp[1]
print("\n\nThis program will terminate in " + str(T) + " seconds\n")

myo.init()
r"""
There can be a lot of output from certain data like acceleration and orientation.
This parameter controls the percent of times that data is shown.
"""


class Listener(myo.DeviceListener):
    # return False from any method to stop the Hub

    def on_connect(self, myo, timestamp):
        print_("Connected to Myo")
        myo.vibrate('short')
        myo.set_stream_emg(stream_emg.enabled)
        myo.request_rssi()
        global start
        start = time.time()

    def on_rssi(self, myo, timestamp, rssi):
        print_("RSSI:", rssi)

    def on_event(self, event):
        r""" Called before any of the event callbacks. """

    def on_event_finished(self, event):
        r""" Called after the respective event callbacks have been
        invoked. This method is *always* triggered, even if one of
        the callbacks requested the stop of the Hub. """

    def on_pair(self, myo, timestamp):
        print_('Paired')
        print_("If you don't see any responses to your movements, try re-running the program or making sure the Myo works with Myo Connect (from Thalmic Labs).")


    def on_disconnect(self, myo, timestamp):
        print_('on_disconnect')

    def on_emg(self, myo, timestamp, emg):
        global start
        global t2
        global t_s
        global r
        current = time.time()
        tdiff = current - start
        t2 = timestamp
        if 't1' not in globals():
            global t1
            t1 = timestamp

        start = time.time()
        show_output('emg', emg, r)

    def on_unlock(self, myo, timestamp):
        print_('unlocked')

    def on_lock(self, myo, timestamp):
        print_('locked')

    def on_sync(self, myo, timestamp):
        print_('synced')

    def on_unsync(self, myo, timestamp):
        print_('unsynced')


def show_output(message, data, r):
    global t2
    global t1
    global T
    global delta_t
    global df_myo
    global flag

    global timestamp_list
    global data_list
    if t2 - t1 < (T*1000000):
        timestamp = time.time_ns()
        df_myo = pd.concat([df_myo,pd.DataFrame({'timestamp': timestamp,
                                                    'EMG_s0': data[0],
                                                    'EMG_s1': data[1],
                                                    'EMG_s2': data[2],
                                                    'EMG_s3': data[3],
                                                    'EMG_s4': data[4],
                                                    'EMG_s5': data[5],
                                                    'EMG_s6': data[6],
                                                    'EMG_s7': data[7]}, index=[0])])
        #print("t2: " + t2)
     #   print("time_time: " + str(time_time))
        # print('t:{:<9}: '.format(
        #     (t2 - t1) / 1000000) + '[{:>8},  {:>8},  {:>8}, {:>8},  {:>8},  {:>8},  {:>8},  {:>8}]'
        #       .format(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]))
    else:
        if flag:
                print("End of data acquisition")
                print("Saving " + r + " ...")
                df_myo = df_myo.set_index('timestamp') #set o novo index
                df_myo.to_csv(r, index=True)
                print(r + " saved")
                flag = False
            # quit()

#Funções de leitura da serial + criação dos dataframesl
def leitura_esp32_1(file_name,read_time):
    start_time = time.time()
    while (time.time() - start_time) < read_time:
        timestamp_buffer = time.time_ns() #retorna em nanosegundos(int) no momento da leitura do buffer na serial
        dif_entre_coleta = 1000000 #1000000 nanosegundos = 1milisegundos
        vetor_timestamp_ajustado = []
        for i in range(4, -1, -1): # loop para gerar um vetor com o timestamp ajustado para cada posição do vetor, fazendo de trás para frente uma vez que o timestamp do buffer é mais proximo a última posição de coleta 
            timestamp_ajustado = timestamp_buffer - (i * dif_entre_coleta)
            vetor_timestamp_ajustado.append(timestamp_ajustado)
        serial_data1 = BL1.readline() # Lê a linha da porta serial          
        # Converte a linha para um objeto JSON
        try:
            json_data1 = json.loads(serial_data1.decode()) #serial -> json
            #print(json_data1) #debbug
        except ValueError: # Se linha inválida, ignorar
            print("Linha json inválida - obs: pode ser a alimentação da ESP")            
            continue
        df_data1 = pd.DataFrame.from_dict(json_data1) #json -> dataframe
        df_data1.insert(0,"timestamp",vetor_timestamp_ajustado) #insere o timestamp ajustado para cada leitura        
        df_data1.to_csv(file_name, mode='a', header=not os.path.exists(file_name)) # Escreve o DataFrame no arquivo CSV

def leitura_esp32_2(file_name,read_time):
    start_time = time.time()
    while (time.time() - start_time) < read_time:
        timestamp_buffer = time.time_ns() #retorna em nanosegundos(int) no momento da leitura do buffer na serial
        dif_entre_coleta = 1000000 #1000000 nanosegundos = 1milisegundos
        vetor_timestamp_ajustado = []
        for i in range(4, -1, -1): # loop para gerar um vetor com o timestamp ajustado para cada posição do vetor, fazendo de trás para frente uma vez que o timestamp do buffer é mais proximo a última posição de coleta 
            timestamp_ajustado = timestamp_buffer - (i * dif_entre_coleta)
            vetor_timestamp_ajustado.append(timestamp_ajustado)
        serial_data2 = BL2.readline() # Lê a linha da porta serial          
        # Converte a linha para um objeto JSON
        try:
            json_data2 = json.loads(serial_data2.decode()) #serial -> json
            #print(json_data2) #debbug
        except ValueError: # Se linha inválida, ignorar 
            print("Linha json inválida - obs: pode ser a alimentação da ESP") 
            continue
        df_data2 = pd.DataFrame.from_dict(json_data2) #json -> dataframe
        df_data2.insert(0,"timestamp",vetor_timestamp_ajustado) #insere o timestamp ajustado para cada leitura               
        df_data2.to_csv(file_name, mode='a', header=not os.path.exists(file_name)) # Escreve o DataFrame no arquivo CSV

def leitura_esp32_1e2(file_name,read_time):
    start_time = time.time()
    while (time.time() - start_time) < read_time:
        global df_data_1e2
        timestamp_buffer = time.time_ns() #retorna em nanosegundos(int) no momento da leitura do buffer na serial
        dif_entre_coleta = 1000000 #1000000 nanosegundos = 1milisegundos
        vetor_timestamp_ajustado = []
        for i in range(4, -1, -1): # loop para gerar um vetor com o timestamp ajustado para cada posição do vetor, fazendo de trás para frente uma vez que o timestamp do buffer é mais proximo a última posição de coleta 
            timestamp_ajustado = timestamp_buffer - (i * dif_entre_coleta)
            vetor_timestamp_ajustado.append(timestamp_ajustado)
        serial_data1 = BL1.readline() # Lê a linha da porta serial
        serial_data2 = BL2.readline() # Lê a linha da porta serial    
        #print("SERIAL ESP32-1:\n"+serial_data1.decode()) #debbug
        #print("SERIAL ESP32-2:\n"+serial_data2.decode()) #debbug      
        # Converte a linha para um objeto JSON
        try:
            json_data1 = json.loads(serial_data1.decode()) #serial -> json
        except ValueError: # Se linha inválida, ignorar 
            print("Linha json inválida - obs: pode ser a alimentação da ESP") 
            continue
        try:
            json_data2 = json.loads(serial_data2.decode()) #serial -> json
        except ValueError: # Se linha inválida, ignorar 
            print("Linha json inválida - obs: pode ser a alimentação da ESP") 
            continue
        df_data1 = pd.DataFrame.from_dict(json_data1) #json -> dataframe
        df_data2 = pd.DataFrame.from_dict(json_data2) #json -> dataframe
        df_data1.insert(0,"timestamp",vetor_timestamp_ajustado) #insere o timestamp ajustado para cada leitura  
        df_data2.insert(0,"timestamp",vetor_timestamp_ajustado) #insere o timestamp ajustado para cada leitura  
        df_data1 = df_data1.reset_index(drop=True) #remove o index
        df_data2 = df_data2.reset_index(drop=True)
        df_data1 = df_data1.set_index('timestamp') #set o novo index
        df_data2 = df_data2.set_index('timestamp')
        df_data_1e2 = pd.merge(df_data1,df_data2, how = 'outer', on = 'timestamp')
        df_data_1e2.to_csv(file_name, mode='a', header=not os.path.exists(file_name)) # Escreve o DataFrame no arquivo CSV

def leitura_2Xesp32_myo(file_name,read_time,hub):
    t1 = threading.Thread(target=leitura_esp32_1e2,args=(file_name,read_time))
    t1.start() #Thread que roda a coleta das ESPS
    hub.run(1000, Listener())  #Thread que roda a coleta da myo    
    t1.join() #aguarda finalizar a Thread das ESPS   
    #df_compilado = pd.merge(df_data_1e2,df_myo, how = 'outer', on = 'timestamp')
    #df_compilado = pd.concat([df_data_1e2, df_myo]).sort_values(by='timestamp')
    #df_compilado.to_csv(file_name,index= True) # Escreve o DataFrame no arquivo CSV
    #df_compilado.to_csv(file_name, mode='a', header=not os.path.exists(file_name)) # Escreve o DataFrame no arquivo CSV
    

def main():

    #solicita informações do usuário e da coleta
    user_name = input("Insira o nome do usuário: ")
    description = input("Insira uma descrição para a coleta: ")
    #read_time = input("Digite o tempo (em segundos) para executar a coleta: ")
    #read_time = int(read_time)
    read_time = T
    opcao = ""
    hub = myo.Hub()
    hub.set_locking_policy(myo.locking_policy.none)

    while opcao != '0':
        opcao = input("\nQual dispositivo utilizar para a coleta:\n(precione 0 para finalizar)\n[1]ESP32-LEFT\n[2]ESP32-RIGHT\n[3]ESP32-LEFT + ESP32-RIGHT\n[4]ESP32-LEFT + ESP32-RIGHT + MYO\n[5]MYO\n\n\n\n\n\n\n[9]Compilar Myo+Luvas\n\n:")
        if(opcao == '1'):
            print("opcao 1 selecionada\n")
            device = "LG"
            file_name = f"Data\{user_name}_{description}_{read_time}s_device{device}.csv"
            print("Running...\n")
            leitura_esp32_1(file_name,read_time)
        if(opcao == '2'):
            print("opcao 2 selecionada\n")
            device = "RG"
            file_name = f"Data\{user_name}_{description}_{read_time}s_device{device}.csv"
            print("Running...\n")
            leitura_esp32_2(file_name,read_time)
        if(opcao == '3'):
            print("opcao 3 selecionada\n")
            device = "LG+RG"
            file_name = f"Data\{user_name}_{description}_{read_time}s_device{device}.csv"
            print("Running...\n")
            leitura_esp32_1e2(file_name,read_time)
        if(opcao == '4'):
            print("opcao 4 selecionada\n")
            device = "LG+RG+Myo"
            file_name = f"Data\{user_name}_{description}_{read_time}s_device{device}.csv"
            print("Running...\n")
            leitura_2Xesp32_myo(file_name,read_time,hub)
            try:
                while hub.running:
                   myo.time.sleep(0.2)
            except KeyboardInterrupt:
                print_("Quitting ...")
                hub.stop(True)
        if(opcao == '5'):
            print("opcao 5 selecionada\n")
            device = "Myo"
            file_name = f"Data\{user_name}_{description}_{read_time}s_device{device}.csv"
            hub.run(1000, Listener())
            print("Running...\n")

                # Listen to keyboard interrupts and stop the
                # hub in that case.                
            try:
                while hub.running:
                   myo.time.sleep(0.2)
            except KeyboardInterrupt:
                print_("Quitting ...")
                hub.stop(True)

        if(opcao == '9'):
            file_name = f"Data\{user_name}_{description}_{read_time}s_device{device}.csv"
            file_name_compilado = f"Data\[COMPILADO]{user_name}_{description}_{read_time}s_device{device}.csv"
            df_luvas = pd.read_csv(file_name)

            print("debug df luvas") #debbug
            print(df_luvas) #debbug
            print("debug df myo") #debbug
            print(df_myo) #debbug
            df_compilado = pd.merge(df_myo,df_luvas, how = 'outer', on = 'timestamp')
            #df_compilado = df_compilado.sort_values(by='timestamp') #testar se ordernou corretamente
            df_compilado.to_csv(file_name_compilado,index= False) # Escreve o DataFrame no arquivo CSV

if __name__ == '__main__':
    main()
