# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 16:20:53 2023
interfac DM 
@author: esoria
"""

from tkinter import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
import hcipy
import numpy as np
from skimage import draw

from asdk38 import DM    
serialName = 'BOL105'
dm = DM( serialName)
circmask = draw.circle(5.5,5.5,5.5,(12,12))
array = np.zeros((12,12))
i=1
p=0
def connect_DM(): #Generate the DM88 mask and send the Reset position to the DM  
    dm.Reset()
    num_act=int( dm.Get('NBOfActuator') )
    plano=np.ones(num_act,)
    array[circmask] =  plano
    axs.imshow(array)
    canvas = FigureCanvasTkAgg(fig, master = frame)  #Creating the drawing area in TK
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=0)
    
def load_plane():#load the flatenning posicion and plot maintaining the cbar fixed
    sys.path.append('C:/Users/esoria.DOMAINT/Documents/testTWFs/')
    global plano
    global p
    plano=np.load('plano.npy') #from the flat position
    array[circmask] = plano
    dm.Send(plano)
    array[circmask] =  plano
    u=axs.imshow(array,vmin=-0.25, vmax=0.25) 
    plano=np.save('actual.npy',plano)
    cbar=fig.colorbar(u)
    cbar.mappable.set_clim(-0.35, 0.35)
    if p!=0:#just shows the cbar the first time you push the flat bottom
        cbar.remove()
    canvas = FigureCanvasTkAgg(fig, master = frame)  #Creating the drawing area in TK
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=0)
    fig.canvas.mpl_connect('button_press_event', click_event) #create the press botton event
    p+=1
def send(): #send pattern to generate a zernike distrubution
    plano=np.load('plano.npy') #from the flat position
    amp=float(valor2.get()) #amplitude
    zern=int(valor1.get()) #zernike number
    Z2C=hcipy.util.inverse_tikhonov(influ_M, rcond=0.05, svd=None) #calculating the P-I
    j= amp*Z2C[:,zern]+plano #generating the vector of act
    dm.Send(j) #sending
    array[circmask] = j #plotting
    u="u"+str(i)
    globals()[u]=axs.imshow(array,vmin=-0.25, vmax=0.25) 
    canvas = FigureCanvasTkAgg(fig, master = frame)  #Creating the drawing area in TK
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=0)   
    sys.path.append('C:/Users/esoria.DOMAINT/Documents/testTWFs')
    actual=j
    actual=np.save('actual.npy',actual) #saving the actual position
    fig.canvas.mpl_connect('button_press_event', click_event) #create the press botton event
def load_Influ_M():
    global influ_M
    influ_M=np.load('influ.npy') #load the influence matrix
    axs2.imshow(influ_M) # plotting
    canvas = FigureCanvasTkAgg(fig2, master = frame)  #Creating the drawing area in TK
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=2)

def anal_IM():
    u, s, vh = np.linalg.svd(influ_M, full_matrices=True) #calculating SVD decomposition
    x=np.arange(1,66)
    axs3.plot(x,np.log(s)) #plotting AV to check signal 
    axs3.grid()
    canvas = FigureCanvasTkAgg(fig3, master = frame)  # Creating the drawing area in TK
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=3)

def act_control():
    amp1=float(valor3.get()) #amplitude
    act=int(valor5.get()-1) #number of actuator
    actual=np.load('actual.npy') #from the actual position
    busc=actual.copy()
    busc[act]=amp1 
    dm.Send(busc)#sending
    np.save('actual.npy',busc) #saving actual
    array[circmask] = busc #plotting
    axs.imshow(array,vmin=-0.25, vmax=0.25) #Act limits
    canvas = FigureCanvasTkAgg(fig, master = frame)  # Creating the drawing area in TK
    fig.canvas.mpl_connect('button_press_event', click_event) #create the press botton event
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=0)

def click_event(e):
    actual=np.load('actual.npy') #from actual
    i=int(e.xdata+0.5) #saving x position in my plot
    j=int(e.ydata+0.5)  #saving y position in my plot
    import pandas as pd
    dic= pd.read_csv('dic_DM.csv') #load the dictionary to convert Matrix coords in Act_vect coords
    indM=12*j+i #index in matrix
    index=np.where(dic.matriz==indM) 
    index=index[0]
    index=index[0] #taking the index in my vector
    u=dic.vector[int(index)]
    select_act.set(u+1) #printing the actuator selected
    select_amp.set(np.round(actual[index],3)) #printing the amplitud of the actuator selected
            

ventana = Tk()
ventana.geometry('850x600')
ventana.wm_title('DM control')
ventana.minsize(width=950,height=325)
frame = Frame(ventana,  bg='white')
frame.place(x=0, y=0)
#figures on my window

fig, axs = plt.subplots(dpi=80, figsize=(4, 4), 
	sharey=True)

fig.suptitle('DM geometry')


fig2, axs2 = plt.subplots(dpi=80, figsize=(4, 4), 
	sharey=True)

fig2.suptitle('Interation Matrix')

fig3, axs3 = plt.subplots(dpi=80, figsize=(4, 4), 
	sharey=True)



fig3.suptitle('Eigenvalues IM')
#Botons on my window

boton = Button(ventana, text="Connect DM",command=connect_DM)
boton.place(x=100, y=350)

boton2 = Button(ventana, text="Load best plane",command=load_plane)
boton2.place(x=90, y=380)

boton3 = Button(ventana, text="Load Influ Matrix",command=load_Influ_M)
boton3.place(x=410, y=350)

boton5 = Button(ventana, text="Analize IM",command=anal_IM)
boton5.place(x=750, y=350)

boton4 = Button(ventana, text="Send",command=send)
boton4.place(x=500, y=470)

boton6 = Button(ventana, text="Send",command=act_control)
boton6.place(x=120, y=490)

#Variables on my window

valor1 = IntVar(value=1)
entrada_texto = Entry(ventana, width=5, textvariable=valor1)
entrada_texto.place(x=470, y=440)

valor2 = DoubleVar(value=0)
entrada_texto = Entry(ventana, width=5, textvariable=valor2)
entrada_texto.place(x=540, y=440)


valor5 = IntVar(value=1)
entrada_texto = Entry(ventana, width=5, textvariable=valor5)
entrada_texto.place(x=100, y=460)

valor3 = DoubleVar(value=0)
entrada_texto = Entry(ventana, width=5, textvariable=valor3)
entrada_texto.place(x=150, y=460)

#text messages on my window

etiqueta1 = Label(ventana, text="Zernike polinomial")
etiqueta1.place(x=410, y=415)

etiqueta2 = Label(ventana, text="Amplitude")
etiqueta2.place(x=520, y=415)

etiqueta3 = Label(ventana, text="Num act")
etiqueta3.place(x=80, y=440)

etiqueta4 = Label(ventana, text="Ampli")
etiqueta4.place(x=140, y=440)

#Showing data on my window

select_act=IntVar(value=0)
etiqueta5 = Label(ventana, textvariable=select_act,
                               foreground="white", background="steelblue",
                               borderwidth=5, anchor="e")
etiqueta5.place(x=230, y=325)


select_amp=DoubleVar(value=0.0)
etiqueta6 = Label(ventana, textvariable=select_amp,
                               foreground="white", background="steelblue",
                               borderwidth=5, anchor="e")
etiqueta6.place(x=260, y=325)

ventana.mainloop() #Finish



