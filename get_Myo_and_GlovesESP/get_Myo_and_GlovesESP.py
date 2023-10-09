# Copyright (C) 2015  Niklas Rosenstein, MIT License
# Last modified by Luigi Faxina (2023) 
# Code compilation based on the codes of Yi Jui Lee(2015) and Matheus Taborda(2022)


import sys
import os
import time 
import string
import serial
import myo
import json
import csv
import threading
import numpy as np
import pandas as pd
import matplotlib.pyplot  as plt
from myo.myo_ecn.listeners       import Collector, ConnectionChecker


EMG_SAMPLING_RATE = 200 #taxa de aquisição da Myo

#Conexão com os ESP's através das portas bluetooth do notebook
try:
    BL1 = serial.Serial('COM5',115200) #esp1
    print("Connected ESP32-LEFT")
except:
    print("Error when connecting to the ESP32-LEFT")
try:
    BL2 = serial.Serial('COM11',115200) #esp2
    print("Connected ESP32-RIGHT")
except:
    print("Error when connecting to the ESP32-RIGHT")

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
    
def leitura_myo(hub,listener,file_name,read_time):
    # Asynchrnous.
    with hub.run_in_background(listener.on_event):
        while hub.running:
            time.sleep(0.5)
            print('\rRecording ... %d percent done.' % (100 * listener.emg_data.shape[0]/read_time/EMG_SAMPLING_RATE), end='')  
        print()
    
    column_names = ["timestamp", "EMG_s0", "EMG_s1", "EMG_s2", "EMG_s3", "EMG_s4", "EMG_s5", "EMG_s6", "EMG_s7"]
    with open(file_name, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile)
        spamwriter.writerow(column_names)
        for row in listener.emg_data:
            if any(row):
                spamwriter.writerow(row)
    

def leitura_geral(hub,listener,file_name1, file_name2,read_time):
    t1 = threading.Thread(target=leitura_esp32_1e2,args=(file_name1,read_time))
    t1.start() #Thread que roda a coleta das ESPS
    # Asynchrnous.
    with hub.run_in_background(listener.on_event):
        while hub.running:
            time.sleep(0.5)
            print('\rRecording ... %d percent done.' % (100 * listener.emg_data.shape[0]/read_time/EMG_SAMPLING_RATE), end='')  
        print()
    column_names = ["timestamp", "EMG_s0", "EMG_s1", "EMG_s2", "EMG_s3", "EMG_s4", "EMG_s5", "EMG_s6", "EMG_s7"]
    with open(file_name2, 'w', newline='') as csvfile:  # Adicione 'newline=' para evitar linhas em branco entre as linhas.
        spamwriter = csv.writer(csvfile)
        spamwriter.writerow(column_names)
        for row in listener.emg_data:
            if any(row):
                spamwriter.writerow(row)
    t1.join()

def main():
    myo.init( sdk_path ='C:\\Users\\luigi\Documents\\2023\\TCC - Referências\\myo_ecn-46818fb4537d468befa69431d2e0452b953c9998\\myo_sdk' ) # Compile Python binding to Myo's API
    hub = myo.Hub() # Create a Python instance of MYO API
    if not ConnectionChecker().ok: # Check connection before starting acquisition:
        quit()
    #solicita informações do usuário e da coleta
    user_name = input("\n\n\nInsira o nome do usuário: ")
    description = input("Insira uma descrição para a coleta: ")
    read_time = input("Digite o tempo (em segundos) para executar a coleta: ")
    read_time = int(read_time)
    opcao = ""
    listener = Collector(read_time * EMG_SAMPLING_RATE)
    while opcao != '0':
        opcao = input("\nQual dispositivo utilizar para a coleta:\n(precione 0 para finalizar)\n[1] ESP32-LEFT\n[2] ESP32-RIGHT\n[3] ESP32-LEFT + ESP32-RIGHT\n[4] MYO\n[5] ESP32-LEFT + ESP32-RIGHT + MYO\n\n[9]Compilar Myo+Luvas\n[p1] Plot Myo\n[p2] Plot ESP32-LEFT\n[p3] ESP32-RIGHT\n\n:")
        if(opcao == '1'): #[1]ESP32-LEFT
            print("opcao 1 selecionada\n")
            device = "LG"
            file_name1 = f"Data\{user_name}_{description}_{read_time}s_device{device}.csv"
            print("Running...\n")
            leitura_esp32_1(file_name1,read_time)
        if(opcao == '2'): #[2]ESP32-RIGHT
            print("opcao 2 selecionada\n")
            device = "RG"
            file_name1 = f"Data\{user_name}_{description}_{read_time}s_device{device}.csv"
            print("Running...\n")
            leitura_esp32_2(file_name1,read_time)
        if(opcao == '3'): #[3]ESP32-LEFT + ESP32-RIGHT
            print("opcao 3 selecionada\n")
            device = "LG+RG"
            file_name1 = f"Data\{user_name}_{description}_{read_time}s_device{device}.csv"
            print("Running...\n")
            leitura_esp32_1e2(file_name1,read_time)            
        if(opcao == '4'):
            print("opcao 4 selecionada\n")
            device = "Myo"
            file_name2 = f"Data\{user_name}_{description}_{read_time}s_device{device}.csv"
            leitura_myo(hub,listener,file_name2,read_time)
        if(opcao == '5'): #[4]ESP32-LEFT + ESP32-RIGHT + MYO
            print("opcao 5 selecionada\n")
            device = "Myo+gloves"
            file_name2 = f"Data\{user_name}_{description}_{read_time}s_deviceMyo.csv"
            file_name1 = f"Data\{user_name}_{description}_{read_time}s_deviceLG+RG.csv"
            leitura_geral(hub,listener,file_name1,file_name2,read_time)               
        if(opcao == '9'):
            file_name_compilado = f"Data\{user_name}_{description}_{read_time}s_device{device}_[COMPILADO].csv"
            df_myo = pd.read_csv(file_name2)
            df_luvas = pd.read_csv(file_name1)

            #print("debug df luvas") #debbug
            #print(df_luvas) #debbug
            #print("debug df myo") #debbug
            #print(df_myo) #debbug
            df_compilado = pd.merge(df_myo,df_luvas, how = 'outer', on = 'timestamp')
            df_compilado = df_compilado.sort_values(by='timestamp') #testar se ordernou corretamente
            df_compilado = df_compilado.fillna(method= "ffill")
            df_compilado = df_compilado.drop_duplicates()
            df_compilado = df_compilado.dropna()
            df_compilado.to_csv(file_name_compilado,index= False) # Escreve o DataFrame no arquivo CSV
        if(opcao == '10'):
            file_name1 = f"Data\luigi_teste-novo-metodo_3s_deviceMyo.csv.csv"
            file_name2 = f"Data\luigi_teste-novo-metodo_3s_deviceLG+RG.csv"
            file_name_compilado = f"Data\[COMPILADO]_luigi_teste-novo-metodo_3s.csv"
            df_myo = pd.read_csv(file_name1)
            df_luvas = pd.read_csv(file_name2)
            
            df_compilado = pd.merge(df_myo,df_luvas, how = 'outer', on = 'timestamp')
            df_compilado = df_compilado.sort_values(by='timestamp') #testar se ordernou corretamente
            df_compilado = df_compilado.fillna(method= "ffill")
            df_compilado = df_compilado.drop_duplicates()
            df_compilado = df_compilado.dropna()
            df_compilado.to_csv(file_name_compilado,index= False) # Escreve o DataFrame no arquivo CSV
        if(opcao == 'p1'):
            df_myo = pd.read_csv(file_name2)
            df_myo.EMG_s0.plot()
            df_myo.EMG_s1.plot()
            df_myo.EMG_s2.plot()
            df_myo.EMG_s3.plot()
            df_myo.EMG_s4.plot()
            df_myo.EMG_s5.plot()
            df_myo.EMG_s6.plot()
            df_myo.EMG_s7.plot()
            plt.show()
        if(opcao == 'p2'):
            df_lg = pd.read_csv(file_name1)            
            df_lg.left_data_flex_1.plot()
            df_lg.left_data_flex_2.plot()
            df_lg.left_data_flex_3.plot()
            df_lg.left_data_flex_4.plot()
            df_lg.left_data_flex_5.plot()
            plt.show()
        if(opcao == 'p3'):
            df_rg = pd.read_csv(file_name1)            
            df_rg.right_data_flex_1.plot()
            df_rg.right_data_flex_2.plot()
            df_rg.right_data_flex_3.plot()
            df_rg.right_data_flex_4.plot()
            df_rg.right_data_flex_5.plot()
            plt.show()
if __name__ == '__main__':
    main()
