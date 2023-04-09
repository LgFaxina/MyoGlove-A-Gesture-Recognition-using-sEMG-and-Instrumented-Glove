import serial
import json
import pandas as pd
from pandas import json_normalize
from io import BytesIO

#Conexão com os ESP's através das portas bluetooth do notebook
try:
    BL1 = serial.Serial('COM5',115200) #esp1
    print("Connected ESP32-LEFT")
except:
    print("Error when connecting to the ESP32-LEFT")
try:
    BL2 = serial.Serial('COM7',115200) #esp2
    print("Connected ESP32-RIGHT")
except:
    print("Error when connecting to the ESP32-RIGHT")

#Funções de leitura da serial + criação dos dataframes
def leitura_esp32_1():
    serial_data1 = BL1.readline()
    print("SERIAL ESP32-1:\n"+serial_data1.decode()) #debbug

    json_data1 = json.loads(serial_data1.decode()) #serial -> json

    df_data1 = pd.DataFrame.from_dict(json_data1) #json -> dataframe
    print("debbug df_data1\n")
    print(df_data1)
    df_data1.to_csv(file_name)
    df_data1.info()

def leitura_esp32_2():
    serial_data2 = BL2.readline()
    print("SERIAL ESP32-2:\n"+serial_data2.decode()) #debbug

    json_data2 = json.loads(serial_data2.decode()) #serial -> json

    df_data2 = pd.DataFrame.from_dict(json_data2) #json -> dataframe
    print("debbug df_data2\n")
    print(df_data2)
    df_data2.to_csv(file_name)
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
    df_data_1e2.to_csv(file_name)
    df_data_1e2.info()
    print(df_data_1e2)

def leitura_2Xesp32_myo():
    serial_data1 = BL1.readline()    
    serial_data2 = BL2.readline()
    print("SERIAL ESP32-1:\n"+serial_data1.decode()) #debbug
    print("SERIAL ESP32-2:\n"+serial_data2.decode()) #debbug

    json_data1 = json.loads(serial_data1.decode()) #serial -> json
    json_data2 = json.loads(serial_data2.decode()) #serial -> json

    df_data1 = pd.DataFrame.from_dict(json_data1) #json -> dataframe
    df_data2 = pd.DataFrame.from_dict(json_data2) #json -> dataframe
    df_myo = pd.read_csv("Emg_0.csv")

    frames = [df_data1, df_data2,df_myo]
    df_data_1e2_myo = pd.concat(frames)
    df_data_1e2_myo.to_csv(file_name)
    df_data_1e2_myo.info()
    print(df_data_1e2_myo)

#solicida informações do usuário e da coleta
user_name = input("Insira o nome do usuário: ")
description = input("Insira uma descrição para a coleta: ")
read_time = input("Digite o tempo (em segundos) para executar a coleta: ")
read_time = int(read_time)
print("\nNome do arquivo de saída: ",description,"_",user_name,"_",read_time,".csv")


opcao = ""
while opcao != '0':
    opcao = input("\nQual dispositivo utilizar para a coleta:\n(precione 0 para finalizar)\n[1]ESP32-LEFT\n[2]ESP32-RIGHT\n[3]ESP32-LEFT + ESP32-RIGHT\n[4]ESP32-LEFT + ESP32-RIGHT + MYO\n\n:")
    if(opcao == '1'):        
        print("opcao 1 selecionada\n")
        device = "L"
        file_name = f"{description}_{user_name}_{read_time}_{device}.csv"
        leitura_esp32_1()
    if(opcao == '2'):
        print("opcao 2 selecionada\n")
        device = "R"
        file_name = f"{description}_{user_name}_{read_time}_{device}.csv"
        leitura_esp32_2()
    if(opcao == '3'):
        print("opcao 3 selecionada\n")
        device = "LR"
        file_name = f"{description}_{user_name}_{read_time}_{device}.csv"
        leitura_esp32_1e2()
    if(opcao == '4'):
        print("opcao 4 selecionada\n")
        device = "LRM"
        file_name = f"{description}_{user_name}_{read_time}_{device}.csv"
        leitura_2Xesp32_myo()
    