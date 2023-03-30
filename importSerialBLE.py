import serial
import json
import pandas as pd
from pandas import json_normalize
from io import BytesIO

#Conexão com os ESP's através das portas bluetooth do notebook
try:
    BL1 = serial.Serial('COM5',115200) #esp1
    print("Conectado ESP32-1")
except:
    print("Erro ao conectar ESP32-1")
try:
    BL2 = serial.Serial('COM7',115200) #esp2
    print("Conectado ESP32-2")
except:
    print("Erro ao conectar ESP32-2")

#Funções de leitura da serial + criação dos dataframes
def leitura_esp32_1():
    serial_data1 = BL1.readline()
    print("SERIAL ESP32-1:\n"+serial_data1.decode()) #debbug

    json_data1 = json.loads(serial_data1.decode()) #serial -> json

    df_data1 = pd.DataFrame.from_dict(json_data1) #json -> dataframe
    print("debbug df_data1\n")
    print(df_data1)
    df_data1.to_csv("df_data1.csv")
    df_data1.info()

def leitura_esp32_2():
    serial_data2 = BL2.readline()
    print("SERIAL ESP32-2:\n"+serial_data2.decode()) #debbug

    json_data2 = json.loads(serial_data2.decode()) #serial -> json

    df_data2 = pd.DataFrame.from_dict(json_data2) #json -> dataframe
    print("debbug df_data2\n")
    print(df_data2)
    df_data2.to_csv("df_data2.csv")
    df_data2.info()

def leitura_esp32_1e2():
    serial_data1 = BL1.readline()    
    serial_data2 = BL2.readline()
    print("SERIAL ESP32-1:\n"+serial_data1.decode()) #debbug
    print("SERIAL ESP32-2:\n"+serial_data2.decode()) #debbug

    json_data1 = json.loads(serial_data1.decode()) #serial -> json
    json_data2 = json.loads(serial_data2.decode()) #serial -> json

    df_data1 = pd.DataFrame.from_dict(json_data1) #json -> dataframe
    df_data2 = pd.DataFrame.from_dict(json_data2) #json -> dataframe
    frames = [df_data1, df_data2]
    df_data_1e2 = pd.concat(frames)
    df_data_1e2.info()
    print(df_data_1e2)

    
opcao = ""
while opcao != '0':
    opcao = input("\n\nInsira uma opção para iniciar a coleta:\n(precione 0 para finalizar a coleta)\n[1]ESP32-1\n[2]ESP32-2\n[3]ESP32-1 + ESP32-2\n\n:")
    if(opcao == '1'):        
        print("opcao 1 selecionada\n")
        leitura_esp32_1()
    if(opcao == '2'):
        print("opcao 2 selecionada\n")
        leitura_esp32_2()
    if(opcao == '3'):
        print("opcao 3 selecionada\n")
        leitura_esp32_1e2()