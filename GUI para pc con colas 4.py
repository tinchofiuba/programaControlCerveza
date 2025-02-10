#import smtplib 

from tkinter import *
from tkinter import font
from tkinter import ttk

import queue
import threading
import time
import serial
import numpy as np

import sqlite3 

#import xlsxwriter
#import pandas as pd

import matplotlib
from matplotlib import style
import matplotlib.pyplot as plt

import serial.tools.list_ports

puertos=0
if puertos<1:
    puertos+=1
    ports=list(serial.tools.list_ports.comports())

fecha_y_hora=("{}_{}_{}_{}_{}_{}".format(time.localtime().tm_year,time.localtime().tm_mon,time.localtime().tm_mday,time.localtime().tm_hour,time.localtime().tm_min,time.localtime().tm_sec))

datos_bbdd=("Datos_cerveza_"+fecha_y_hora)
seriales=[]
for i in ports:
    a=str(i)
    seriales.append(a)

def check(seriales, words): 
    res = [all([k in s for k in words]) for s in seriales] 
    return [seriales[i] for i in range(0, len(res)) if res[i]] 
      
words = ['CH340']
busqueda=(check(seriales,words))
busqueda=(busqueda[0]).split(" ")
direccion=busqueda[0]

datos_lista_xlsx=[]
datos_xlsx=[]

q_lectura_serial=queue.Queue(14) #cola para mostrar en la gui lo que manda arduino
q_escritura_serial=queue.Queue(13) #cola para enviar info a arduino
q_grafico=queue.Queue(7) #cola para graficar la performance del iq

precalentar=0
activar_precalentado=0
contador_comienzo_maceracion=0
contador_comunicacion_serial=0
contador_serial=0
tiempo_de_isoterma=0
tiempo_transcurrido=0
encendido_bomba_IQ=0
encendido_bomba_macerado=0
potencia=0
iteracion=0
diferencia_temporal=0
ploteo=0
bbdd=0
on_off=0
qip=0
qis=0
coneccion=1
tiempo_1=1
contador_isotermas=0
contador_isoterma_1=0
contador_isoterma_2=0
contador_isoterma_3=0
comenzar_maceracion=0
congirar_maceracion=0
fin_maceracion=0
contador1=0
contador2=0
contador3=0
eleccion_isotermas=1
datos_densidad=[]
densidad=0
gas_inicial=0
gas_final=0
PWM_ON=0
manual=0 
bomba_macerado=0
bomba_IQ=0
bomba_trasvase=0
muestreo_densidad=0
variable_grafico=0
habilitar_boton_guardar_gas=0

cantidad_isotermas=1

termistor1=0
termistor2=0
valor_pwm_PI=0
plt.style.use([ 'seaborn-bright'])

N = 1
largo=2
i=0
datos_serial=np.zeros((1,17))
datos_sql3=np.zeros((1,14))
#datos_densidad=np.zeros((2,20))

tiempo = np.zeros((N, 2))

fondo_label='light gray' 
prendido='red' 
apagado='blue'

raiz=Tk()
raiz.title("CONTROL DE PROCESO")
raiz.resizable(True,True)


#FUENTES
helvfont=font.Font(family="Helvetica",size=12,weight="bold")
helvfont_negrita=font.Font(family="Helvetica",size=12,weight="bold")
helvfont_sin_negrita=font.Font(family="Helvetica",size=12)

#DIMENSIONES DEL FRAME
ancho=780
alto=460
#alto=700

#CONFIG DE LOS FRAMES
miframe=Frame(raiz, width=ancho,height=alto,relief="ridge")
miframe.config(cursor="hand2",bd="5",bg=fondo_label)
miframe.pack()

    
menu=Menu(raiz)
raiz.config(menu=menu)
subMenu=Menu(menu)




def quit():
    raiz.destroy()

def conectar_con_arduino():
    global coneccion
    coneccion+=1

def PWM():
    global PWM_ON
    PWM_ON+=1
    
def funcManual():
    global manual
    manual+=1

def comenzar_el_macerado():
    global comenzar_maceracion
    comenzar_maceracion+=1
    
def configurar_el_macerado():
    global configurar_maceracion
    configurar_maceracion+=1   

def apagar_encender_bomba_macerado():
    global bomba_macerado
    bomba_macerado+=1
    
    if (bomba_macerado%2!=0):
        global encendido_bomba_macerado
        encendido_bomba_macerado=1
    else:
        encendido_bomba_macerado=0

def apagar_encender_bomba_IQ():
    global bomba_IQ
    bomba_IQ+=1
    if (bomba_IQ%2!=0):
        global encendido_bomba_IQ
        encendido_bomba_IQ=1
    else:
        encendido_bomba_IQ=0

def elegir_isotermas():
    global eleccion_isotermas
    eleccion_isotermas+=1
    if eleccion_isotermas>3:
        eleccion_isotermas=1

def precalentado():
    global precalentar
    precalentar+=1
    

def guardar_densidad():
    
    global muestreo_densidad

    info_densidad="{}".format(datos_serial[0,5])+","+"{}".format(entrada_densidad.get()) #guardfo el tiempo de proceso transcurrido
    info_densidad=info_densidad.split(",")
    datos_densidad.append(info_densidad)
    datos_vectoriales_densidad=np.asarray(datos_densidad) #[np.newaxis]
    densidad_a_excel= pd.DataFrame(datos_vectoriales_densidad)
    densidad_a_excel.to_excel("Datos_densidad_" +fecha_y_hora+ ".xlsx", sheet_name='Densidades')
    print(datos_vectoriales_densidad)

    datos_de_densidades_guardadas=Label(miframe,text="Datos almacenados: {}".format(muestreo_densidad+1),fg="green",bg=fondo_label)
    datos_de_densidades_guardadas.place(x=230,y=225)

    valor_anterior_densidad=Label(miframe,text="Densidad anterior: {}".format(datos_vectoriales_densidad[muestreo_densidad,1])+ " g/L",fg="blue",bg=fondo_label)
    valor_anterior_densidad.place(x=380,y=225)
    
    muestreo_densidad+=1
    entrada_densidad.delete(0, 'end')

def guardar_datos_costo_gas():
    global habilitar_boton_guardar_gas
    habilitar_boton_guardar_gas+=1
    print(habilitar_boton_guardar_gas)
    entrada_gas_inicial.delete(0, 'end')
    entrada_gas_final.delete(0, 'end')
    
def comenzar_proceso():      
    global comenzar
    comenzar+=1
    
raiz.config(menu=menu)
subMenu=Menu(menu)
subMenu.config(bg='lightsteelblue')

#CONFIGURACION DE LAS ETIQUEITAS DE LA GUI

label_progreso_1=Label(miframe,fg="blue",text="-",bg=fondo_label)
label_progreso_1.place(x=565,y=64)

label_progreso_2=Label(miframe,fg="blue",text="-",bg=fondo_label)
label_progreso_2.place(x=565,y=110)

label_progreso_3=Label(miframe,fg="blue",text="-",bg=fondo_label)
label_progreso_3.place(x=565,y=155)

label_tentrada_IQ=Label(miframe,fg="blue",text="0",bg=fondo_label)
label_tentrada_IQ.place(x=130,y=78)

label_tsalida_IQ=Label(miframe,fg="blue",text="0",bg=fondo_label)
label_tsalida_IQ.place(x=130,y=102)

label_xxx=Label(miframe,fg="blue",text="0",bg=fondo_label)
label_xxx.place(x=130,y=126)

label_pwm_resistencias=Label(miframe,fg="blue",text="0",bg=fondo_label)
label_pwm_resistencias.place(x=130,y=190)

label_tentrada_macerador=Label(miframe,fg="blue",text="0",bg=fondo_label)
label_tentrada_macerador.place(x=130,y=30)

label_tsalida_macerador=Label(miframe,fg="blue",text="0",bg=fondo_label)
label_tsalida_macerador.place(x=130,y=54)

label_tiempo_de_coneccion=Label(miframe,text="Conectado [min]: ",fg="black",bg=fondo_label)
label_tiempo_de_coneccion.place(x=10,y=375)

Encender_apagar_bombas=Label(miframe,text="BOMBAS",fg="black",bg=fondo_label,font=helvfont)
Encender_apagar_bombas.place(x=285,y=250)

datos_de_densidades_guardadas=Label(miframe,text="",fg="black",bg=fondo_label)
datos_de_densidades_guardadas.place(x=650,y=235)

tipo_de_control2=Label(miframe,text="MANEJO MANUAL",fg="black",bg=fondo_label,font=helvfont)
tipo_de_control2.place(x=10,y=250)

temp1=Label(miframe,text="Macerador IN: ",fg="red",bg=fondo_label)
temp1.place(x=15,y=30)

temp2=Label(miframe,text="Macerador OUT: ",fg="blue",bg=fondo_label)
temp2.place(x=15,y=54)

temp3=Label(miframe,text="Intercamb.IN: ",fg="red",bg=fondo_label)
temp3.place(x=15,y=78)

temp4=Label(miframe,text="Intercamb. OUT: ",fg="blue",bg=fondo_label)
temp4.place(x=15,y=102)

temp4=Label(miframe,text="Serpentin OUT: ",fg="red",bg=fondo_label)
temp4.place(x=15,y=128)


consumo=IntVar()
fin_maceracion=IntVar()
tiempo_conección=IntVar()
tiempo_parcial=IntVar()
tiempo_transcurrido=IntVar()
caudalimetro_servicio=IntVar()
caudalimetro_proceso=IntVar()

xencendidaPWM=350
PWM=100

## INICIO DE ESCALAS
fondo_scale='lightsteelblue'
y_isotermas=55

escalapotencia = Scale(miframe, from_=0, to=100, orient=HORIZONTAL,bg=fondo_scale,state='active')
escalapotencia.place(x=25,y=y_isotermas+265)

label_titulo_caudalimetros=Label(miframe,text="Q[L/min]",fg="black",bg=fondo_label,font=helvfont)
label_titulo_caudalimetros.place(x=175,y=y_isotermas+195)

label_caudalimetro_proceso=Label(miframe,text="Proceso",fg="black",bg=fondo_label)
label_caudalimetro_proceso.place(x=170,y=290)

label_caudalimetro_servicio=Label(miframe,text="Servicio",fg="black",bg=fondo_label)
label_caudalimetro_servicio.place(x=170,y=340)

valor_caudalimetro_proceso=Label(miframe,fg="black",bg=fondo_label,text="0")
valor_caudalimetro_proceso.place(x=220,y=290)
valor_caudalimetro_proceso.config(fg="blue",width=5)

valor_caudalimetro_servicio=Label(miframe,fg="black",bg=fondo_label,text="0")
valor_caudalimetro_servicio.place(x=220,y=340)
valor_caudalimetro_servicio.config(fg="blue",width=5)

label_transimicion_serial=Label(miframe,text="TX",fg="red",bg=fondo_label)
label_transimicion_serial.place(x=560,y=412)

label_recepcion_serial=Label(miframe,text="RX",fg="red",bg=fondo_label)
label_recepcion_serial.place(x=530,y=412) #y=415 x=370

label_escritura_bbdd=Label(miframe,text="BBDD",fg="red",bg=fondo_label)
label_escritura_bbdd.place(x=590,y=412)

label_densidad=Label(miframe,text="Densidad medida [g/L]",fg="black",bg=fondo_label)
label_densidad.place(x=230,y=200)

label_gas_inicial=Label(miframe,text="Gas inicial [m^3]:",fg="black",bg=fondo_label)
label_gas_inicial.place(x=600,y=64)

label_gas_final=Label(miframe,text="Gas final [m^3]:",fg="black",bg=fondo_label)
label_gas_final.place(x=600,y=100)

entrada_densidad=Entry(miframe,fg="blue")
entrada_densidad.place(x=360,y=200)
entrada_densidad.config(width=5)

entrada_gas_inicial=Entry(miframe,fg="blue")
entrada_gas_inicial.place(x=700,y=65)
entrada_gas_inicial.config(width=5)

entrada_gas_final=Entry(miframe,fg="blue")
entrada_gas_final.place(x=700,y=101)
entrada_gas_final.config(width=5)

boton_guardar_densidad=Button(miframe,text="Guardar",fg="blue",command=guardar_densidad,state='disable')
boton_guardar_densidad.place(x=410,y=195)
boton_guardar_densidad.config(width=15)

boton_precalentar=Button(miframe,text="Activar precalentado",fg="blue",command=precalentado)
boton_precalentar.place(x=170,y=375)
boton_precalentar.config(width=20)

boton_guardar_datos_gas=Button(miframe,text="Guardar consumo de gas",fg="blue",command=guardar_datos_costo_gas,state='disable')
boton_guardar_datos_gas.place(x=605,y=140)
boton_guardar_datos_gas.config(width=20)

boton_numero_de_isotermas=Button(miframe,text="Nº isotermas: ?",fg="blue",command=elegir_isotermas)
boton_numero_de_isotermas.place(x=630,y=20)
boton_numero_de_isotermas.config(width=15)

boton_salir=Button(miframe,text="SALIR",fg="red",command=quit)
boton_salir.place(x=650,y=410)
boton_salir.config(width=15)

boton_manejo_manual=Button(miframe,text="Activar manual",fg="black",command=funcManual)
boton_manejo_manual.place(x=40,y=280)
boton_manejo_manual.config(width=10)

boton_configurar_maceracion=Button(miframe,text="CONFIGURAR MACERACION",fg="black",command=configurar_el_macerado,bg="gray",state='disable')
boton_configurar_maceracion.place(x=170,y=410)
boton_configurar_maceracion.config(width=23,bg="green")

boton_conectar_con_arduino=Button(miframe,text="VINCULAR ARDUINO",fg="yellow",command=conectar_con_arduino,bg="gray")
boton_conectar_con_arduino.place(x=10,y=410)
boton_conectar_con_arduino.config(width=20,bg="OrangeRed4")

boton_comenzar_maceracion=Button(miframe,text="COMENZAR MACERACION",command=comenzar_el_macerado,fg="black",bg="gray",state='disable')
boton_comenzar_maceracion.place(x=350,y=410)
boton_comenzar_maceracion.config(width=23,bg="green")

boton_encender_bomba_macerador=Button(miframe,text="Encender",fg="black",command=apagar_encender_bomba_macerado,width=15)
boton_encender_bomba_macerador.place(x=270,y=340)

boton_encender_bomba_IQ=Button(miframe,text="Encender",fg="black",command=apagar_encender_bomba_IQ,width=15)
boton_encender_bomba_IQ.place(x=270,y=290)

consumo_electrico=Label(miframe,text="CONSUMO [kWh] :",fg="RED",bg=fondo_label)
consumo_electrico.place(x=15,y=160)

pwm_resistencias=Label(miframe,text="PWM Resistencias :",fg="BLUE",bg=fondo_label)
pwm_resistencias.place(x=15,y=190)

label_gasto_electricidad=Label(miframe,text="Gasto eléctrico [$]:",fg="BLUE",bg=fondo_label)
label_gasto_electricidad.place(x=15,y=220)

gasto_electricidad=Label(miframe,text="0",fg="green",bg=fondo_label)
gasto_electricidad.place(x=130,y=220)

label_consumo=Label(miframe,fg="blue",text="0",bg=fondo_label)
label_consumo.place(x=130,y=160)

label_tiempo_conección=Label(miframe,fg="blue",text="0",bg=fondo_label)
label_tiempo_conección.place(x=120,y=376)

configuracion_isotermas=Label(miframe,text="CONFIGURACION ISOTERMAS",fg="black",bg=fondo_label,font=helvfont)
configuracion_isotermas.place(x=280,y=5)

titulo_temperatura_isotermas=Label(miframe,text="Temperatura [ºC]",fg="black",bg=fondo_label)
titulo_temperatura_isotermas.place(x=255,y=y_isotermas-27)

titulo_tiempo_isotermas=Label(miframe,text="Tiempo [min]",fg="black",bg=fondo_label)
titulo_tiempo_isotermas.place(x=430,y=y_isotermas-27)

isoterma_1=Label(miframe,text="1°",fg="gray",bg=fondo_label,font=helvfont)
isoterma_1.place(x=200,y=y_isotermas+10)

isoterma_2=Label(miframe,text="2°",fg="gray",bg=fondo_label,font=helvfont)
isoterma_2.place(x=200,y=y_isotermas+55)

isoterma_3=Label(miframe,text="3°",fg="gray",bg=fondo_label,font=helvfont)
isoterma_3.place(x=200,y=y_isotermas+98)

margen_izquierdo=230

temperaturaIsoterma_1= Scale(miframe,from_=10, to=80, orient=HORIZONTAL,bg=fondo_scale,length=150)
temperaturaIsoterma_1.place(x=margen_izquierdo,y=y_isotermas)

temperaturaIsoterma_2= Scale(miframe, from_=10, to=80, orient=HORIZONTAL,bg=fondo_scale,length=150)
temperaturaIsoterma_2.place(x=margen_izquierdo,y=y_isotermas+45)

temperaturaIsoterma_3= Scale(miframe, from_=10, to=80, orient=HORIZONTAL,bg=fondo_scale,length=150)
temperaturaIsoterma_3.place(x=margen_izquierdo,y=y_isotermas+91)

tiempoIsoterma_1= Scale(miframe,from_=0, to=120, orient=HORIZONTAL,bg=fondo_scale,length=150)
tiempoIsoterma_1.place(x=margen_izquierdo+170,y=y_isotermas)

tiempoIsoterma_2= Scale(miframe, from_=0, to=60, orient=HORIZONTAL,bg=fondo_scale,length=150)
tiempoIsoterma_2.place(x=margen_izquierdo+170,y=y_isotermas+45)

tiempoIsoterma_3= Scale(miframe, from_=0, to=30, orient=HORIZONTAL,bg=fondo_scale,length=150)
tiempoIsoterma_3.place(x=margen_izquierdo+170,y=y_isotermas+91)



##### FIN DE ESCALAS

def escritura_bbdd():
    global iteracion

    miconeccion=sqlite3.connect("{}".format(datos_bbdd))
    cursor=miconeccion.cursor()

    if(iteracion==0):   
        print("tabla de bbdd creada")
        cursor.execute("CREATE TABLE {} (TEMPERATURA_ENTRADA_MACERADOR STRING,TEMPERATURA_SALIDA_MACERADOR STRING,TEMPERATURA_ENTRADA_IQ STRING, TEMPERATURA_SALIDA_IQ STRING,TEMPERATURA_SALIDA_SERPENTIN STRING, TIEMPO_CONECCION_TOTAL STRING, CAUDALIMETRO1 STRING, CAUDALIMETRO2 STRING, CONSUMO STRING, TIEMPO_DE_PROCESO STRING,VALOR_PWM_PI STRING,DTML STRING, QIP STRING, QIS STRING)".format(datos_bbdd))
        miconeccion.commit() #confirmamos la operacion
        miconeccion.close() #cerramos niculo con la base de datos
        iteracion=1
    if (maceracion==1):
        
        #print("volcando valores a bbdd")
        cursor.executemany("INSERT INTO {} VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)".format(datos_bbdd),datos_sql3)
        miconeccion.commit() #confirmamos la operacion
        miconeccion.close() #cerramos niculo con la base de datos
        label_escritura_bbdd.config(fg="green")
    else:
        label_escritura_bbdd.config(fg="red")
    miframe.after(500,escritura_bbdd)

#DEFINICION DE VARIABLES QUE INTERVIENEN EN LAS ENTRADAS
tEntradaMacerador=StringVar()
tEntradaIQ=StringVar()
tSalidaIQ=StringVar()
tSalidaMacerador=StringVar()
tempSerpentin=StringVar()
tempMaceracion=IntVar()
tiempoMaceracion=IntVar()
densidad=StringVar()
valor_pwm_PI=StringVar()
gas_inicial=StringVar()
gas_final=StringVar()
          
def hilo_principal():
    
    global comenzar_maceracion
    global contador_comienzo_maceracion
    if contador_comienzo_maceracion==0:
        contador_comienzo_maceracion+=1
        label_progreso_1.config(text="0%")
        label_progreso_2.config(text="0%")
        label_progreso_3.config(text="0%")

    if(encendido_bomba_IQ==1):
        boton_encender_bomba_IQ.config(bg="red",text="Apagar")
    else:
        boton_encender_bomba_IQ.config(bg="green",text="Encender")

    if(encendido_bomba_macerado==1):
        boton_encender_bomba_macerador.config(bg="red",text="Apagar")
    else:
        boton_encender_bomba_macerador.config(bg="green",text="Encender")

    
    if (muestreo_densidad>=19):
        boton_guardar_densidad.config(text="Sin espacio")
        boton_guardar_densidad.config(state='disable')        
    else:
        
        if (entrada_densidad.get()==''):
            boton_guardar_densidad.config(state='disable')
            
        else:
            boton_guardar_densidad.config(state='active')
            
    if(habilitar_boton_guardar_gas<1):
        if (entrada_gas_inicial.get()=='' or entrada_gas_final.get()==''):
            boton_guardar_datos_gas.config(state='disable')
            
        else:
            boton_guardar_datos_gas.config(state='active',text="Guardar consumo de gas")
            if (entrada_gas_final.get()<=entrada_gas_inicial.get()):
                boton_guardar_datos_gas.config(state='disable',text="Gasto nulo!")
    else:
        boton_guardar_datos_gas.config(state='disable',text="Gasto de gas guardado")
        gas_inicial.set("0")
        

    if (manual%2!=0):
        global valor_manual
        valor_manual=1 #valor que luego se envía a arduino mediante serial
        boton_manejo_manual.config(text="DESACTIVAR",width=10)
        escalapotencia.config(state='active')
        boton_manejo_manual.place(x=40,y=280)
    else:
        valor_manual=0 #valor que luego se envía a arduino mediante serial
        escalapotencia.set(0)
        boton_manejo_manual.config(text="ACTIVAR",width=10)
        escalapotencia.config(state='disable')
        boton_manejo_manual.place(x=40,y=280)

    if (comenzar_maceracion%2!=0):
        global maceracion
        maceracion=1
        
    else:  
        maceracion=0
        
    global precalentar
    if (precalentar%2==0):
        boton_precalentar.config(text="Activar precalentado",width=18)
    else:
        boton_precalentar.config(text="Desactivar precalentado",width=19)
        
     

    if (maceracion==1):
        boton_comenzar_maceracion.config(text="CONFIGURAR MACERACION",bg="forest green",fg="black")
        boton_configurar_maceracion.config(text="FINALIZAR MACERACION")

        if (eleccion_isotermas==1):
            isoterma_1.config(fg="green")
            isoterma_2.config(fg="gray")
            isoterma_3.config(fg="gray")
            global contador_isoterma_1
            global contador_isoterma_2
            global contador_isoterma_3
            contador_isoterma_1+=1
            contador_isoterma_2=0
            contador_isoterma_3=0
            temperaturaIsoterma_1.config(state='active') #-anulado
            tiempoIsoterma_1.config(state='active') #-anulado
            if (contador_isoterma_1<2):
                temperaturaIsoterma_1.set(65)  #seteo la temperatura de la unica isoterma                 
                tiempoIsoterma_1.set(120) #seteo el tiempo de la unica isoterma                     
            temperaturaIsoterma_2.set(0) #-anulado
            temperaturaIsoterma_3.set(0) #-anulado
            tiempoIsoterma_2.set(0) #-anulado
            tiempoIsoterma_3.set(0) #-anulado
            temperaturaIsoterma_2.config(state='disable') #-anulado
            temperaturaIsoterma_3.config(state='disable') #-anulado
            tiempoIsoterma_2.config(state='disable') #-anulado
            tiempoIsoterma_3.config(state='disable') #-anulado
            
        if (eleccion_isotermas==2):
            contador_isoterma_2+=1
            contador_isoterma_1=0
            contador_isoterma_3=0
            temperaturaIsoterma_1.config(state='active') #-anulado
            temperaturaIsoterma_2.config(state='active') #-anulado
            tiempoIsoterma_1.config(state='active') #-anulado
            tiempoIsoterma_2.config(state='active') #-anulado
            if (contador_isoterma_2<2):
                temperaturaIsoterma_1.set(62)  #seteo la temperatura de la primer isoterma                     
                tiempoIsoterma_1.set(80) #seteo el tiempo de la primer isoterma      
                temperaturaIsoterma_2.set(70)   #seteo la temperatura de la segunda isoterma                  
                tiempoIsoterma_2.set(30) #seteo el tiempo de la segunda isoterma                   
            isoterma_1.config(fg="green")                
            isoterma_2.config(fg="green")
            isoterma_3.config(fg="gray")
            temperaturaIsoterma_3.set(0) #-anulado
            tiempoIsoterma_3.set(0) #-anulado
            temperaturaIsoterma_3.config(state='disable') #-anulado
            tiempoIsoterma_3.config(state='disable') #-anulado
            
        if (eleccion_isotermas==3):
            contador_isoterma_3+=1
            contador_isoterma_1=0
            contador_isoterma_2=0
            temperaturaIsoterma_1.config(state='active') #-anulado
            temperaturaIsoterma_2.config(state='active') #-anulado
            temperaturaIsoterma_3.config(state='active') #-anulado
            tiempoIsoterma_1.config(state='active') #-anulado
            tiempoIsoterma_2.config(state='active') #-anulado
            tiempoIsoterma_3.config(state='active') #-anulado
            if (contador_isoterma_3<2):
                temperaturaIsoterma_1.set(62)                   
                tiempoIsoterma_1.set(60)
                temperaturaIsoterma_2.set(68)                   
                tiempoIsoterma_2.set(35)
                temperaturaIsoterma_3.set(74)                   
                tiempoIsoterma_3.set(20) 
            isoterma_1.config(fg="green") 
            isoterma_2.config(fg="green") 
            isoterma_3.config(fg="green")
    else:
        boton_comenzar_maceracion.config(text="CONFIGURAR MACERACION",bg="OrangeRed4",fg="yellow")
        boton_configurar_maceracion.config(text="INICIAR MACERACION")
        temperaturaIsoterma_1.set(0)            
        temperaturaIsoterma_2.set(0)
        temperaturaIsoterma_3.set(00)
        tiempoIsoterma_1.set(0)
        tiempoIsoterma_2.set(0)
        tiempoIsoterma_3.set(0)
        isoterma_1.config(fg="gray") 
        isoterma_2.config(fg="gray") 
        isoterma_3.config(fg="gray")
        temperaturaIsoterma_1.config(state='disable') #-anulado
        temperaturaIsoterma_2.config(state='disable') #-anulado
        temperaturaIsoterma_3.config(state='disable') #-anulado
        tiempoIsoterma_1.config(state='disable') #-anulado
        tiempoIsoterma_2.config(state='disable') #-anulado
        tiempoIsoterma_3.config(state='disable') #-anulado

            
    t0=threading.Thread(target=mostrar)
    t0.start()
    
    if q_lectura_serial.empty()==False:
        label_recepcion_serial.config(fg="green")
        label_tsalida_macerador.config(text="{}".format(q_lectura_serial.get()))    #temperatura 2
        label_tentrada_macerador.config(text="{}".format(q_lectura_serial.get()))    #temperatura 1
        label_xxx.config(text="{}".format(q_lectura_serial.get()))     #temperatura 5
        label_tsalida_IQ.config(text="{}".format(q_lectura_serial.get()))         #temperatura 4
        label_tentrada_IQ.config(text="{}".format(q_lectura_serial.get()))        #temperatura 3
        label_tiempo_conección.config(text="{}".format(round(q_lectura_serial.get()/60)))#tiempo transcurrido desde la conección con arduino, truncado a 1 decimal en minutos
        valor_caudalimetro_proceso.config(text="{}".format(q_lectura_serial.get())) #caudalimetro de proceso
        valor_caudalimetro_servicio.config(text="{}".format(q_lectura_serial.get())) #caudalimtro de servicio
        kwh=q_lectura_serial.get()/1000
        label_consumo.config(text="{}".format(round(kwh,4)))         #consumo electrico
        tiempo_de_isoterma=(q_lectura_serial.get()) #tiempo de isoterma transcurrido"
        global contador_isotermas
        contador_isotermas=q_lectura_serial.get() #contador de isoterma
        AWP_ON_OFF=q_lectura_serial.get()       
        label_pwm_resistencias.config(text="{}".format(q_lectura_serial.get()))
        gasto_electricidad.config(text="{}".format(round(kwh*3.3,4)))
        fin=q_lectura_serial.get()
        boton_numero_de_isotermas.config(text="Nº isotermas: {}".format(eleccion_isotermas))
        #print("Calor lado de procesos: {}  Calor lado de servicio: {}  DTML: {}  Fin {}".format(qip,qis,DTML,fin)+"/n")
        
        if fin==1:
            label_progreso_1.config(text="-")
            label_progreso_1.config(text="-")
            label_progreso_1.config(text="-")
            coneccion+=1
            comenzar_maceracion+=1
            
        if eleccion_isotermas==1:
            #print("una sola isoterma")
            if tiempoIsoterma_1.get()==0:
                label_progreso_1.config(text="0%")
            else:
                label_progreso_1.config(text="{}".format(round((tiempo_de_isoterma)*100/(tiempoIsoterma_1.get()*60),1))+"%")
            label_progreso_2.config(text="-")
            label_progreso_3.config(text="-")

        if eleccion_isotermas==2:
            if (tiempo_de_isoterma<=(tiempoIsoterma_1.get()*60) and contador_isotermas==1):
                #print("dos isotermas, 1era en proceso")
                if tiempoIsoterma_1.get()==0:
                    label_progreso_1.config(text="0%")
                else:
                    label_progreso_1.config(text="{}".format(round(tiempo_de_isoterma*100/(tiempoIsoterma_1.get()*60),1))+"%")
                label_progreso_2.config(text="0%")
                label_progreso_3.config(text="-")

            else:
                #print("dos isotermas, 2da en proceso")
                label_progreso_1.config(text="100%")
                if tiempoIsoterma_2.get()==0:
                    label_progreso_2.config(text="0%")
                else:
                    label_progreso_2.config(text="{}".format(round(tiempo_de_isoterma*100/(tiempoIsoterma_2.get()*60),1))+"%")
                label_progreso_3.config(text="-")
                
        if eleccion_isotermas==3:
            if (tiempo_de_isoterma<=tiempoIsoterma_1.get()*60 and contador_isotermas==1):
                if tiempoIsoterma_1.get()==0:
                    label_progreso_1.config(text="0%")
                else:
                    label_progreso_1.config(text="{}".format(round(tiempo_de_isoterma*100/(tiempoIsoterma_1.get()*60),1))+"%")
                label_progreso_2.config(text="0%")
                label_progreso_3.config(text="0%")
            else:
                if (tiempo_de_isoterma<=tiempoIsoterma_2.get()*60  and contador_isotermas==2):
                    print("tres isotermas, 2da en proceso")
                    label_progreso_1.config(text="100%")
                    if tiempoIsoterma_2.get()==0:
                        label_progreso_2.config(text="0%")
                    else:
                        label_progreso_2.config(text="{}".format(round(tiempo_de_isoterma*100/(tiempoIsoterma_2.get()*60),1))+"%")
                        label_progreso_3.config(text="0%")
                
                else:
                    print("tres isotermas, 3era en proceso")
                    label_progreso_1.config(text="100%")
                    label_progreso_2.config(text="100%")
                    if tiempoIsoterma_3.get()==0:
                        label_progreso_3.config(text="0%")
                    else:
                        label_progreso_3.config(text="{}".format(round(tiempo_de_isoterma*100/(tiempoIsoterma_3.get()*60),1))+"%")
    else:
        label_recepcion_serial.config(fg="red")
        
    miframe.after(200,hilo_principal)               

###
def escritura_serial():

    if (coneccion%2==0):

        if q_escritura_serial.empty()==True:
            q_escritura_serial.put(valor_manual)
            q_escritura_serial.put(escalapotencia.get())
            q_escritura_serial.put(eleccion_isotermas)
            q_escritura_serial.put(temperaturaIsoterma_1.get())
            q_escritura_serial.put(temperaturaIsoterma_2.get())
            q_escritura_serial.put(temperaturaIsoterma_3.get())
            q_escritura_serial.put(tiempoIsoterma_1.get())
            q_escritura_serial.put(tiempoIsoterma_2.get())
            q_escritura_serial.put(tiempoIsoterma_3.get())
            q_escritura_serial.put(maceracion) 
            q_escritura_serial.put(encendido_bomba_macerado)
            q_escritura_serial.put(encendido_bomba_IQ)
            q_escritura_serial.put(activar_precalentado)
            label_transimicion_serial.config(fg="green")   
    miframe.after(500,escritura_serial)
    

#FUNCION PRINCIPAL, ADQUIERE Y DEPURA LA INFORMACION RECOLECTADA EN EL PUERTO SERIAL
def mostrar():

    global tiempo
    global i
    global datos_serial
    global datos_sql3   
    global a
    global b
    global c
    global d
    global e
    global f
    global o
    
    global potencia          
    if (coneccion%2==0):

        global contador_comunicacion_serial
        if (contador_comunicacion_serial<1):
            global arduino
            arduino = serial.Serial(direccion, baudrate=9600)
            print("intentando vincular con arduino")
            arduino.setDTR(False)
            time.sleep(1)
            arduino.flushInput()
            arduino.setDTR(True)
            
            boton_numero_de_isotermas.config(state='active')
            boton_encender_bomba_macerador.config(state='active')
            boton_encender_bomba_IQ.config(state='active')
            boton_comenzar_maceracion.config(state='active')
            boton_manejo_manual.config(state='active')
            boton_conectar_con_arduino.config(text="DESVINCULAR ARDUINO",bg="forest green",fg="black")
            contador_comunicacion_serial+=1
            
        arduino.flush()
        while arduino.inWaiting():
            line = arduino.readline()
            if not line:
                label_recepcion_serial.config(fg="red")
                continue

            leer=(line.decode('ascii'))
            datos_arduino=leer.split(",") #separo los datos por el espacio entre datos
            datos_lista_xlsx=[]
            for i in range(len(datos_arduino)-1):
                datos_lista_xlsx.append(datos_arduino[i])
                datos_serial[0,i]=float(datos_arduino[i]) ## asigno variables de tipo flotante a los datos ingresados desde el arduino
                
            datos_xlsx.append(datos_lista_xlsx)
            print(datos_lista_xlsx)
            
            a=datos_serial[0,0] #t1
            b=datos_serial[0,1] #t2
            c=datos_serial[0,2] #t3
            d=datos_serial[0,3] #t4
            e=datos_serial[0,4] #t5
            f=datos_serial[0,5] #tiempo de coneccion
            g=datos_serial[0,6] #caudal1
            h=datos_serial[0,7] #caudal2
            i=datos_serial[0,8] #potencia (kWh)             
            k=datos_serial[0,9]#tiempo de proceso
            l=datos_serial[0,10]#contador de isotermas
            m=datos_serial[0,11]#error
            n=datos_serial[0,12]#integral ki
            o=datos_serial[0,13]#temperatura deseada
            p=datos_serial[0,14]#valor del pwm generado por el pi
            awp=datos_serial[0,15]#info acerca de si está o no el anti wind up
            fin=datos_serial[0,16]#fin

            delta_t_proceso=a-b
            delta_t_servicio=c-d
            global qip
            global qis
            qip=g*delta_t_proceso*1
            qis=g*delta_t_servicio*1
            global DTML
            DTML=((a-b)-(d-c))
            
            datos_sql3[0,0]=a #t1
            datos_sql3[0,1]=b #t2
            datos_sql3[0,2]=c #t3
            datos_sql3[0,3]=d #t4
            datos_sql3[0,4]=e #t5
            datos_sql3[0,5]=f #tiempo de coneccion
            datos_sql3[0,6]=g #caudal1
            datos_sql3[0,7]=h #caudal2
            datos_sql3[0,8]=i #consumo
            datos_sql3[0,9]=k #tiempo de proceso
            datos_sql3[0,10]=p#valor del pwm generado por el pi
            datos_sql3[0,11]=DTML#valor del DTML          
            datos_sql3[0,12]=qip#
            datos_sql3[0,13]=qis#valor del pwm generado por el pi
            print("Error:  {} Termino integral:  {} Valor de la temperatura deseada  {}".format(m,n,o))

            if q_lectura_serial.empty()==True: #la cola q regula la impresion de variables principales sobre la GUI
                #print("lectura serial correcta")
                q_lectura_serial.put(a) #entrada al macerador
                q_lectura_serial.put(b) #salida del macerador
                q_lectura_serial.put(c) #salida del serpentin
                q_lectura_serial.put(d) #salida del iq
                q_lectura_serial.put(e) #entrada al iq
                q_lectura_serial.put(f) #tiempo de coneccion              
                q_lectura_serial.put(g) #caudal1
                q_lectura_serial.put(h) #caudal2
                q_lectura_serial.put(i) #consumo             
                q_lectura_serial.put(k) #tiempo de proceso
                q_lectura_serial.put(l) #contador de isotermas
                q_lectura_serial.put(awp) #anti wind up si/no
                q_lectura_serial.put(p) #PWM
                q_lectura_serial.put(fin) #PWM
                
            else:
                print("error en cola de recepcion")
                            
            if q_escritura_serial.empty()==False:
                #print("escribiendo en serial")
                vector=('{}'.format(q_escritura_serial.get())    #manual/auto
                        +'b{}'.format(q_escritura_serial.get())  #valor_pwm
                        +'c{}'.format(q_escritura_serial.get())  #cantidad de isotermas
                        +'d{}'.format(q_escritura_serial.get())  #temperatura 1er iso
                        +'e{}'.format(q_escritura_serial.get())  #temperatura 2da iso
                        +'f{}'.format(q_escritura_serial.get())  #temperatura 3er iso
                        +'g{}'.format(q_escritura_serial.get())  #tiempo 1er iso
                        +'h{}'.format(q_escritura_serial.get())  #tiempo 2da iso
                        +'i{}'.format(q_escritura_serial.get())  #tiempo 3era iso
                        +'j{}'.format(q_escritura_serial.get()) #inicio/fin
                        +'k{}'.format(q_escritura_serial.get()) #bomba de maceado
                        +'l{}'.format(q_escritura_serial.get()) #bomba de IQ
                        +'m{}'.format(q_escritura_serial.get())) #bomba de IQ
                arduino.write(str(vector).encode())
            else:
                
                label_transimicion_serial.config(fg="red")
            
                
            
                
                
    else:
        #anulado de botones 
        boton_numero_de_isotermas.config(state='disable')
        boton_encender_bomba_macerador.config(state='disable')
        boton_encender_bomba_IQ.config(state='disable')
        boton_comenzar_maceracion.config(state='disable')
        boton_manejo_manual.config(state='disable')
        boton_conectar_con_arduino.config(text="VINCULAR ARDUINO",bg="OrangeRed4",fg="yellow")
        
        label_tsalida_macerador.config(text="0") 
        label_tentrada_macerador.config(text="0")    
        label_xxx.config(text="0")    
        label_tsalida_IQ.config(text="0")
        label_tentrada_IQ.config(text="0")   
        label_tiempo_conección.config(text="0")
        label_recepcion_serial.config(fg="red")
        label_pwm_resistencias.config(text="0")
        
        contador_serial=0

    
def programa():

    if fin_maceracion!=1:
        
        hilo_principal()
        
        t1=threading.Thread(target=escritura_serial,daemon=True)
        t1.start()
        
        t2=threading.Thread(target=escritura_bbdd,daemon=True)
        t2.start()        

 
## Programa

programa()

raiz.mainloop()




