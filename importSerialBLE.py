import serial
import datetime
import json
import pandas as pd
import time
import os

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

#Funções de leitura da serial + criação dos dataframes
def leitura_esp32_1(file_name,read_time):
    start_time = time.time()
    while (time.time() - start_time) < read_time:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") #Timestamp do domento da leitura
        serial_data1 = BL1.readline() # Lê a linha da porta serial          
        # Converte a linha para um objeto JSON
        try:
            json_data1 = json.loads(serial_data1.decode()) #serial -> json
            #print(json_data1) #debbug
        except ValueError: # Se linha inválida, ignorar            
            continue
        df_data1 = pd.DataFrame.from_dict(json_data1) #json -> dataframe
        df_data1.insert(0,"timestamp_leitura",timestamp) #insere o timestamp do momento da leitura ao dataframe                  
        df_data1.to_csv(file_name, mode='a', header=not os.path.exists(file_name)) # Escreve o DataFrame no arquivo CSV

def leitura_esp32_2(file_name,read_time):
    start_time = time.time()
    while (time.time() - start_time) < read_time:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") #Timestamp do domento da leitura
        serial_data2 = BL2.readline() # Lê a linha da porta serial          
        # Converte a linha para um objeto JSON
        try:
            json_data2 = json.loads(serial_data2.decode()) #serial -> json
            print(json_data2) #debbug
        except ValueError: # Se linha inválida, ignorar 
            continue
        df_data2 = pd.DataFrame.from_dict(json_data2) #json -> dataframe
        df_data2.insert(0,"timestamp_leitura",timestamp) #insere o timestamp do momento da leitura ao dataframe                  
        df_data2.to_csv(file_name, mode='a', header=not os.path.exists(file_name)) # Escreve o DataFrame no arquivo CSV

def leitura_esp32_1e2(file_name,read_time):
    start_time = time.time()
    while (time.time() - start_time) < read_time:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") #Timestamp do domento da leitura
        serial_data1 = BL1.readline() # Lê a linha da porta serial
        serial_data2 = BL2.readline() # Lê a linha da porta serial    
        print("SERIAL ESP32-1:\n"+serial_data1.decode()) #debbug
        print("SERIAL ESP32-2:\n"+serial_data2.decode()) #debbug      
        # Converte a linha para um objeto JSON
        try:
            json_data1 = json.loads(serial_data1.decode()) #serial -> json
        except ValueError: # Se linha inválida, ignorar 
            continue
        try:
            json_data2 = json.loads(serial_data2.decode()) #serial -> json
        except ValueError: # Se linha inválida, ignorar 
            continue
        df_data1 = pd.DataFrame.from_dict(json_data1) #json -> dataframe
        df_data2 = pd.DataFrame.from_dict(json_data2) #json -> dataframe
        df_data1.insert(0,"timestamp_leitura",timestamp) #insere o timestamp do momento da leitura ao dataframe
        df_data2.insert(0,"timestamp_leitura",timestamp) #insere o timestamp do momento da leitura ao dataframe
        df_data1 = df_data1.reset_index(drop=True)
        df_data2 = df_data2.reset_index(drop=True)
        df_data1 = df_data1.set_index('timestamp_leitura') 
        df_data2 = df_data2.set_index('timestamp_leitura')
        frames = [df_data1, df_data2]
        df_data_1e2 = pd.concat(frames)
        df_data_1e2.to_csv(file_name, mode='a', header=not os.path.exists(file_name)) # Escreve o DataFrame no arquivo CSV

def leitura_2Xesp32_myo(file_name,read_time):
    start_time = time.time()
    while (time.time() - start_time) < read_time:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f") #Timestamp do domento da leitura
        serial_data1 = BL1.readline() # Lê a linha da porta serial
        serial_data2 = BL2.readline() # Lê a linha da porta serial    
        print("SERIAL ESP32-1:\n"+serial_data1.decode()) #debbug
        print("SERIAL ESP32-2:\n"+serial_data2.decode()) #debbug      
        # Converte a linha para um objeto JSON
        try:
            json_data1 = json.loads(serial_data1.decode()) #serial -> json
        except ValueError: # Se linha inválida, ignorar 
            continue
        try:
            json_data2 = json.loads(serial_data2.decode()) #serial -> json
        except ValueError: # Se linha inválida, ignorar 
            continue
        df_data1 = pd.DataFrame.from_dict(json_data1) #json -> dataframe
        df_data2 = pd.DataFrame.from_dict(json_data2) #json -> dataframe
        df_myo = pd.read_csv(r'C:\Users\luigi\Documents\2023\TCC-Luigi\Data\Myo\Emg_0.csv') # le csv da MYO
        df_data1.insert(0,"timestamp_leitura",timestamp) #insere o timestamp do momento da leitura ao dataframe
        df_data2.insert(0,"timestamp_leitura",timestamp) #insere o timestamp do momento da leitura ao dataframe
        df_data1 = df_data1.reset_index(drop=True)
        df_data2 = df_data2.reset_index(drop=True)
        df_data1 = df_data1.set_index('timestamp_leitura') 
        df_data2 = df_data2.set_index('timestamp_leitura')   
        frames = [df_data1, df_data2,df_myo]
        df_data_1e2_myo = pd.concat(frames)
        df_data_1e2_myo.to_csv(file_name, mode='a', header=not os.path.exists(file_name)) # Escreve o DataFrame no arquivo CSV

#solicida informações do usuário e da coleta
user_name = input("Insira o nome do usuário: ")
description = input("Insira uma descrição para a coleta: ")
read_time = input("Digite o tempo (em segundos) para executar a coleta: ")
read_time = int(read_time)
opcao = ""

while opcao != '0':
    opcao = input("\nQual dispositivo utilizar para a coleta:\n(precione 0 para finalizar)\n[1]ESP32-LEFT\n[2]ESP32-RIGHT\n[3]ESP32-LEFT + ESP32-RIGHT\n[4]ESP32-LEFT + ESP32-RIGHT + MYO\n\n:")
    if(opcao == '1'):
        print("opcao 1 selecionada\n")
        device = "GL"
        file_name = f"{user_name}_{description}_{read_time}s_device{device}.csv"
        leitura_esp32_1(file_name,read_time)
    if(opcao == '2'):
        print("opcao 2 selecionada\n")
        device = "GR"
        file_name = f"{user_name}_{description}_{read_time}s_device{device}.csv"
        leitura_esp32_2(file_name,read_time)   
    if(opcao == '3'):
        print("opcao 3 selecionada\n")
        device = "GL+GR"
        file_name = f"{user_name}_{description}_{read_time}s_device{device}.csv"
        leitura_esp32_1e2(file_name,read_time) 
    if(opcao == '4'):
        print("opcao 4 selecionada\n")
        device = "GL+GR+Myo"
        file_name = f"{user_name}_{description}_{read_time}s_device{device}.csv"
        leitura_2Xesp32_myo(file_name,read_time)
print("\nArquivo gerado: ",file_name)