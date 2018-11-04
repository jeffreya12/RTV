from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
import tkinter.scrolledtext as tkst
from tkinter import font as tkfont
from copy import copy
from RTVObjects import *
import threading
from GA import *
import time
import queue

## INSTRUCCIONES

class DistributeVehiclesWindow(Toplevel):
    def __init__(self, lanes, vehicles, distributionId, receiveDistribution):
        Toplevel.__init__(self)
        self.protocol("WM_DELETE_WINDOW", self.disableEvent)
        self.lanes = lanes
        self.vehicles = vehicles
        self.id = distributionId
        self.distribution = None
        self.sendDistribution = receiveDistribution
        self.executing = False
        self.title("Distribute Vehicles")
        self.initializeGUIElements()

    def initializeGUIElements(self):
        self.inputFrame = Frame(self)
        self.inputFrame.grid(row = 0, columnspan = 2)

        self.populationText = Label(self, text = "Population Size: ")
        self.populationText.grid(row = 0, column = 0)

        self.populationInput = Text(self, width = 10, height = 1)
        self.populationInput.grid(row = 0, column = 1)

        self.generationText = Label(self, text = "Number of Generations: ")
        self.generationText.grid(row = 1, column = 0)

        self.generationInput = Text(self, width = 10, height = 1)
        self.generationInput.grid(row = 1, column = 1)

        self.techInfoText = Label(self, text = "Technical Information About Vehicle Distribution")
        self.techInfoText.grid(row = 2, columnspan = 2)

        self.gaText = tkst.ScrolledText(self)
        self.gaText.tag_config("a", justify = CENTER, wrap = WORD)
        self.gaText.insert(END, "This distribution algorithm uses a technique called Genetic Algorithm.\n" + 
                        "The Gen is represented as a list of lanes. Each index represents a vehicle and contains the number of the lane "+
                        "in which the vehicle should be allocated.\nFor example: [0, 2, 1] means that vehicle 1 will be allocated in lane 0, "+
                        "vehicle 2 in lane 2 and vehicle 3 in lane 1.\nA lane represented with -1 means that the vehicle can not be allocated.\n", ("a"))

        self.vehiclesString = ""
        for idx, vehicle in enumerate(self.vehicles):
            self.vehiclesString += "Index " + str(idx) + " represents the vehicle with the id #" + str(vehicle.getId()) + ".\n"

        self.gaText.insert(END, self.vehiclesString, ("a"))

        self.gaText.grid(row = 3, columnspan = 2)

        self.executeButton = Button(self,
                                    command = self.executeDistribution,
                                    text = "Distribute",
                                    width = 10)
        self.executeButton.grid(row = 4, column = 0)

        self.finishButton = Button(self,
                                    command = self.finishDistribution,
                                    text = "Finish",
                                    width = 6)
        self.finishButton.grid(row = 4, column = 1)

    def disableEvent(self):
        if not self.executing:
            self.destroy()

    def executeDistribution(self):
        self.populationSize = self.populationInput.get(1.0, END)
        self.generations = self.generationInput.get(1.0, END)

        try:
            self.populationSize = int(self.populationSize)
        except:
            messagebox.showerror("Population Size Error", "Please check your input. Population size must be a number.", parent=self)
            return

        try:
            self.generations = int(self.generations)
        except:
            messagebox.showerror("Generation Error", "Please check your input. Number of generations must be a number.", parent=self)
            return

        if self.populationSize <= 0:
            messagebox.showerror("Population Error", "Population size must be greater than zero.", parent=self)
            return

        if self.generations <= 0:
            messagebox.showerror("Generation Error", "Number of generations must be greater than zero.", parent=self)
            return
        self.gaText.config(state = 'normal')
        self.gaText.delete(1.0, END)
        self.gaText.insert(END, "This distribution algorithm uses a technique called Genetic Algorithm.\n" + 
                        "The Gen is represented as a list of lanes. Each index represents a vehicle and contains the number of the lane "+
                        "in which the vehicle should be allocated.\nFor example: [0, 1, 2] means that vehicle 1 will be allocated in lane 0, "+
                        "vehicle 2 in lane 1 and vehicle 3 in lane 2.\nA lane represented with -1 means that the vehicle can not be allocated.\n", ("a"))
        self.gaText.insert(END, self.vehiclesString, ("a"))

        self.queue = queue.Queue()
        self.distributionAlgorithm = GeneticAlgorithm(self.queue, args = [self.populationSize, self.generations, self.lanes, self.vehicles, self.gaText]).start()
        self.executing = True
        self.executeButton.config(state = 'disabled')
        self.finishButton.config(state = 'disabled')
        self.after(10, self.processQueue)

        #self.distribution = self.distributionAlgorithm.execute(self.populationSize, self.generations, self.lanes, self.vehicles, self.gaText)
        #self.gaText.config(state = 'disabled')

    def processQueue(self):
        try:
            self.distribution = self.queue.get(0)
            self.gaText.config(state = 'disabled')
            self.executeButton.config(state = 'normal')
            self.finishButton.config(state = 'normal')
            self.executing = False
        except queue.Empty:
            self.after(10, self.processQueue)

    def finishDistribution(self):
        if self.distribution == None:
            messagebox.showerror("Distribution Error", "Distribution has not been performed, yet.", parent=self)
            return
        #Extraer texto
        self.algorithmExplained = self.gaText.get(1.0, END)

        #Generar y guardar archivo
        file = open("distributionLog #"+str(self.id)+".txt", 'w')
        file.write(self.algorithmExplained)
        file.close()
        
        #Guardar archivo
        self.sendDistribution(self.distribution)
        self.exit()

    def exit(self):
        self.destroy()



"""
Clase ChangeVehiclesWindow
Inicia una instancia de la ventana para cambiar el tipo de vehículos de una línea
Entradas:
    laneId: El número de línea que se va a cambiar
    currentCarTypes: Índices de los tipos de carros de la línea que se va a cambiar
    changeLaneMethod: Referencia al método de la ventana principal para ejecutar el cambio
Salidas:
    Ninguna
"""
class ChangeVehiclesWindow(Toplevel):
    def __init__(self, laneId, currentCarTypes, changeLaneMethod):
        Toplevel.__init__(self)
        self.vehicleTypes = ["Motorcycle > 5 Years", "Motorcycle <= 5 Years", "Vehicles > 5 Years", 
                            "Vehicles <= 5 Years", "Buses", "Two-Axle Truck", "Five-Axle Truck"]
        self.laneToChange = laneId
        self.changeLaneCars = changeLaneMethod
        self.currentCarTypes = currentCarTypes
        self.title("Change Vehicles")
        self.initializeGUIElements()

    def initializeGUIElements(self):
        self.selectTypesText = Label(self, text = "Change Vehicle Types for Lane "+str(self.laneToChange + 1))
        self.selectTypesText.grid(row = 0, columnspan = 2)

        self.vehicleTypesList = Listbox(self, selectmode = MULTIPLE, height = 7, exportselection = 0)

        self.vehicleTypesList.grid(row = 1, columnspan = 2)

        for item in self.vehicleTypes:
            self.vehicleTypesList.insert(END, item)

        for carType in self.currentCarTypes:
            self.vehicleTypesList.selection_set(carType)

        self.acceptButton = Button(self, 
                                    command = self.finish,
                                    text = "Accept",
                                    width = 6)
        self.acceptButton.grid(row = 2, column = 0)

        self.cancelButton = Button(self,
                                    command = self.exit,
                                    text = "Cancel",
                                    width = 6)
        self.cancelButton.grid(row = 2, column = 1)


    def finish(self):
        selectedItems = self.vehicleTypesList.curselection()
        if len(selectedItems) == 0:
            messagebox.showerror("Vehicle Type Not Selected", "At least one vehicle type must be selected.", parent=self)
            return

        self.changeLaneCars(self.laneToChange, selectedItems)
        self.exit()        

    def exit(self):
        self.destroy()


"""
Clase AddVehicleWindow
Inicia una instancia de la ventana para agregar vehículos a la lista de espera
Entradas:
    addVehiclesMaster: Referencia al método de la ventana principal para agregar los vehículos
Salidas:
    Ninguna
"""
class AddVehicleWindow(Toplevel):
    def __init__(self, addVehiclesMaster):
        Toplevel.__init__(self)
        self.masterAdd = addVehiclesMaster
        self.vehicleTypes = ["Motorcycle > 5 Years", "Motorcycle <= 5 Years", "Vehicles > 5 Years", 
                            "Vehicles <= 5 Years", "Buses", "Two-Axle Truck", "Five-Axle Truck"]
        self.title("Add Vehicles")
        self.loadImages()
        self.initializeGUIElements()
        

    def initializeGUIElements(self):
        self.explainText = Label(self, text = "Enter quantity of the vehicle, then press the corresponding button.")
        self.explainText.pack(side = TOP, fill = BOTH)


        self.vehicleCount = Text(self, height = 1, width = 10)
        self.vehicleCount.pack(side = LEFT)

        self.xLabel = Label(self, text = "X")
        self.xLabel.pack(side = LEFT)

        self.oldMotorcycleButton = Button(self,
                                        command = self.addOldMotorcycle,
                                        image = self.oldMotorcycleImage)
        self.oldMotorcycleButton.pack(side = TOP, fill = BOTH)

        self.newMotorcycleButton = Button(self,
                                        command = self.addNewMotorcycle,
                                        image = self.newMotorcycleImage)
        self.newMotorcycleButton.pack(side = TOP, fill = BOTH)

        self.oldVehicleButton = Button(self,
                                command = self.addOldVehicle,
                                image = self.oldVehicleImage)
        self.oldVehicleButton.pack(side = TOP, fill = BOTH)

        self.newVehicleButton = Button(self,
                                command = self.addNewVehicle,
                                image = self.newVehicleImage)
        self.newVehicleButton.pack(side = TOP, fill = BOTH)

        self.busButton = Button(self,
                                command = self.addBus,
                                image = self.busImage)
        self.busButton.pack(side = TOP, fill = BOTH)

        self.twoAxleTruckButton = Button(self,
                                command = self.addTwoAxleTruck,
                                image = self.twoAxleTruckImage)
        self.twoAxleTruckButton.pack(side = TOP, fill = BOTH)

        self.fiveAxleTruckButton = Button(self,
                                command = self.addFiveAxleTruck,
                                image = self.fiveAxleTruckImage)
        self.fiveAxleTruckButton.pack(side = TOP, fill = BOTH)
        

    def loadImages(self):
        self.oldMotorcycleImage = PhotoImage(file = "oldMotorcycle.png")
        self.newMotorcycleImage = PhotoImage(file = "newMotorcycle.png")
        self.oldVehicleImage = PhotoImage(file = "oldVehicle.png")
        self.newVehicleImage = PhotoImage(file = "newVehicle.png")
        self.busImage = PhotoImage(file = "bus.png")
        self.twoAxleTruckImage = PhotoImage(file = "twoAxleTruck.png")
        self.fiveAxleTruckImage = PhotoImage(file = "fiveAxleTruck.png")

    def getVehicleCount(self):
        vehicleCount = self.vehicleCount.get(1.0, END)

        try:
            vehicleCount = int(vehicleCount)
        except:
            messagebox.showerror("Vehicle Quantity Error", "Please check your input. Vehicle quantity must be a number.", parent=self)
            return 0

        if vehicleCount <= 0:
            messagebox.showerror("Vehicle Quantity Error", "Vehicle quantity must be greater than 0.", parent=self)
            return 0

        return vehicleCount

        

    def addOldMotorcycle(self):
        vehicleCount = self.getVehicleCount()
        if vehicleCount != 0:
            self.masterAdd(0, vehicleCount)

    def addNewMotorcycle(self):
        vehicleCount = self.getVehicleCount()
        if vehicleCount != 0:
            self.masterAdd(1, vehicleCount)

    def addOldVehicle(self):
        vehicleCount = self.getVehicleCount()
        if vehicleCount != 0:
            self.masterAdd(2, vehicleCount)

    def addNewVehicle(self):
        vehicleCount = self.getVehicleCount()
        if vehicleCount != 0:
            self.masterAdd(3, vehicleCount)

    def addBus(self):
        vehicleCount = self.getVehicleCount()
        if vehicleCount != 0:
            self.masterAdd(4, vehicleCount)

    def addTwoAxleTruck(self):
        vehicleCount = self.getVehicleCount()
        if vehicleCount != 0:
            self.masterAdd(5, vehicleCount)

    def addFiveAxleTruck(self):
        vehicleCount = self.getVehicleCount()
        if vehicleCount != 0:
            self.masterAdd(6, vehicleCount)


"""
Clase ConfigWindow
Inicia una instancia de la ventana para la configuración inicial de la simulación
Entradas:
    store: Referencia al método de la ventana principal para configurar
Salidas:
    Ninguna
"""
class ConfigWindow(Toplevel):
    def __init__(self, store):
        Toplevel.__init__(self)
        self.configurationLists = []
        self.vehicleTypes = ["Motorcycle > 5 Years", "Motorcycle <= 5 Years", "Vehicles > 5 Years", 
                            "Vehicles <= 5 Years", "Buses", "Two-Axle Truck", "Five-Axle Truck"]
        self.lanesConfiguration = {}
        self.masterStore = store
        self.title("RTV Configuration")
        self.initializeGUIElements()


    def initializeGUIElements(self):

        #Hacemos un canvas y lo agregamos al master para poder scrollear
        self.canvas = Canvas(self, width = 160)
        self.canvas.pack(side = LEFT)

        #Tenemos que agregarle scrollbar en Y por si son muchos carriles
        self.vScrollbar = Scrollbar(self, orient = VERTICAL, command = self.canvas.yview)
        self.vScrollbar.pack(side = LEFT, fill = Y)

        #Se le dice al canvas quien controla su y
        self.canvas.config(yscrollcommand = self.vScrollbar.set)

        #Ahora agregamos un frame al canvas para poder agregarle los widgets
        self.widgetsFrame = Frame(self.canvas, width = 160)
        self.canvas.create_window((0, 0), window=self.widgetsFrame, anchor="nw")

        #Para el scroll
        self.widgetsFrame.bind("<Configure>", self.OnFrameConfigure)
        self.bind('<MouseWheel>', self.onMouseWheelMove)

        #Ahora hacemos un frame para las opciones, esto con el fin de permitir un reseteo
        self.lanesFrame = Frame(self.widgetsFrame, width = 160)        

        #Agregamos la entrada en el widgetsFrame
        self.lanesLabel = Label(self.widgetsFrame, text="Number of Lanes: ")
        self.lanesLabel.grid(row = 0, column = 0, padx = (10, 0))

        self.lanesText = Text(self.widgetsFrame, height = 1, width=5)
        self.lanesText.grid(row = 0, column = 1, padx = (0, 10))
        self.lanesText.bind('<Tab>', self.focusNextInput)

        #Agregamos el boton de accept al frame.
        self.acceptButton = Button(self.widgetsFrame,
                              command = self.startConfiguration,
                              text = "Accept",
                              width = 6)
        self.acceptButton.grid(row = 1, columnspan = 2)

        #Creamos el boton de reset, pero todavía no lo mostramos
        self.resetButton = Button(self.widgetsFrame,
                              command = self.resetOptions,
                              text = "Reset",
                              width = 5)

        #Creamos el boton de inicio, pero todavía no lo mostramos
        self.startButton = Button(self.widgetsFrame,
                              command = self.startSimulation,
                              text = "Start",
                              width = 5)

        

    def OnFrameConfigure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def resetOptions(self):
        self.acceptButton['state'] = 'normal'
        self.resetButton['state'] = 'disabled'
        self.lanesConfiguration = {}
        self.maxCapacityWidgets = []
        self.configurationLists = []
        for child in self.lanesFrame.winfo_children():
            child.destroy()
        self.lanesFrame.grid_forget()
        self.startButton.grid_forget()
        self.resetButton.grid_forget()
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)


    def startConfiguration(self):
        self.lanes = self.lanesText.get(1.0, END)

        try:
            self.lanes = int(self.lanes)
        except:
            messagebox.showerror("Input Error", "Please check your input. Verify that you wrote only a number.", parent=self)
            return

        if self.lanes <= 0:
            messagebox.showerror(title = "Value Error", message = "You should have 1 lane at least.", parent=self)
            return

        if self.lanes > 50:
            messagebox.showerror(title = "Value Error", message = "You can have 50 lanes maximum.", parent=self)
            return
            
        self.acceptButton['state'] = 'disabled'
        self.resetButton['state'] = 'normal'        

        self.addLanesOptions()    

    def addLanesOptions(self):
        offset = 0
        self.lanesConfiguration = {}
        self.maxCapacityWidgets = []
        for i in range(1, self.lanes+1):
            self.lanesConfiguration[i] = []
            self.laneLabel = Label(self.lanesFrame, text="Lane "+str(i)+" Options")
            self.laneLabel.grid(row = i + offset, columnspan = 2, padx = (10, 0))
            
            offset += 1
            self.capacityLabel = Label(self.lanesFrame, text="Max Capacity: ")
            self.capacityLabel.grid(row = i + offset, column = 0)
            self.capacityText = Text(self.lanesFrame, height = 1, width = 5)
            self.capacityText.grid(row = i + offset, column = 1)
            self.maxCapacityWidgets.insert(i-1, self.capacityText)
           
            offset += 1
            self.vehicleTypesLabel = Label(self.lanesFrame, text = "Select Vehicle Types")
            self.vehicleTypesLabel.grid(row = i + offset, columnspan = 2)

            offset += 1
            vehicleTypesList = Listbox(self.lanesFrame, selectmode = MULTIPLE, height = 7, exportselection = 0)
            vehicleTypesList.grid(row = i + offset, columnspan = 2)

            for item in self.vehicleTypes:
                vehicleTypesList.insert(END, item)

            self.configurationLists.append(vehicleTypesList)

        self.lanesFrame.grid(row = 2, columnspan = 2)
        self.startButton.grid(row = 3, column = 0)
        self.resetButton.grid(row = 3, column = 1)

    def startSimulation(self):
        maxCapacities = []
        for key, conf in self.lanesConfiguration.items():
            try:
                maxCapacity = int(self.maxCapacityWidgets[key-1].get(1.0, "end-1c"))
            except:
                messagebox.showerror("Input Error", "Please check the max capacity of lane "+str(key)+". Verify that you wrote only a number.", parent=self)
                return

            if maxCapacity <= 0:
                messagebox.showerror("Invalid Max Capacity", "Max Capacity of lane "+str(key)+" can not be negative or zero.", parent=self)
                return

            maxCapacities.append(maxCapacity)

        for idx, confList in enumerate(self.configurationLists):
            selectedItems = confList.curselection()
            if len(selectedItems) == 0:
                messagebox.showerror("Vehicle Type Not Selected", "At least one vehicle type must be select for lane "+str(idx + 1)+".", parent=self)
                return
            self.lanesConfiguration[idx + 1] = [maxCapacities[idx], selectedItems]

        self.masterStore(self.lanesConfiguration)
        self.exit()


    def onMouseWheelMove(self, event):
        if self.vScrollbar.get() != (0, 1):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        ##Para que el tab funcione
    def focusNextInput(self, event):
        event.widget.tk_focusNext().focus()
        return("break")

    def exit(self):
        self.destroy()


"""
Clase MainWindow
Inicia una instancia de la ventana principal del programa
Entradas:
    master: Referencia a root, es decir, es la ventana principal
Salidas:
    Ninguna
"""
class MainWindow:
    def __init__(self, master):
        
        self.master = master

        master.title("RTV Dealer")
        self.boldFont = tkfont.Font(family="Helvetica", size=12, weight="bold")
        self.carId = 1
        self.distCount = 0
        self.distribution = None
        self.lanesConfiguration = None
        self.lanes = []
        self.waitingVehicles = []
        self.attentionTimes = [30, 20, 60, 40, 80, 100, 120]
        #self.attentionTimes = [15, 5, 20, 10, 15, 25, 30]
        self.vehiclesImages = []
        self.canvasbgColor = "white" #"#76a4ed"
        self.vehicleIdColor = "white"
        self.laneToRemoveVehicle = -1

        self.initializeGUIContainers()
        self.initializeGUIElements()
        self.loadImages()
        self.calculatePixels()

    def initializeGUIContainers(self):
        self.mainFrame = Frame(self.master)
        self.mainFrame.pack(expand = True, fill = BOTH, side = LEFT)

        self.boardFrame = Frame(self.mainFrame)
        self.boardFrame.pack(fill = BOTH, side = TOP, expand = True)

        self.waitingPanelFrame = Frame(self.master, width = 200)
        self.waitingPanelFrame.pack_propagate(0)
        self.waitingPanelFrame.pack(side = RIGHT, fill = BOTH)

        self.canvas = Canvas(self.boardFrame, bg = self.canvasbgColor)
        
        self.vScrollbar = Scrollbar(self.boardFrame, orient = VERTICAL)
        self.vScrollbar.pack(side = RIGHT, fill = Y)  
        
        self.hScrollbar = Scrollbar(self.boardFrame, orient = HORIZONTAL)
        self.hScrollbar.pack(side = BOTTOM, fill = X)

        self.vScrollbar.config(command = self.canvas.yview)
        self.hScrollbar.config(command = self.canvas.xview)

        self.canvas.config(xscrollcommand = self.hScrollbar.set,
                           yscrollcommand = self.vScrollbar.set)

        self.canvas.pack(side = LEFT, expand = True, fill = BOTH)

        self.canvas.bind('<MouseWheel>', self.onMouseWheelMove)

        self.optionsFrame = Frame(self.mainFrame)
        self.optionsFrame.pack(side = BOTTOM, fill = BOTH)

        self.simulationFrame = Frame(self.optionsFrame)
        self.simulationFrame.pack(side = LEFT, fill = BOTH, expand = True)

        Separator(self.optionsFrame, orient = VERTICAL).pack(side = LEFT, fill = Y)

        self.maintenanceFrame = Frame(self.optionsFrame)
        self.maintenanceFrame.pack(side = LEFT, fill = BOTH, expand = True)

        Separator(self.optionsFrame, orient = VERTICAL).pack(side = LEFT, fill = Y)

        self.pauseLanesFrame = Frame(self.optionsFrame)
        self.pauseLanesFrame.pack(side = LEFT, fill = BOTH, expand = True)

        Separator(self.optionsFrame, orient = VERTICAL).pack(side = LEFT, fill = Y)

        self.removeVehicleFrame = Frame(self.optionsFrame)
        self.removeVehicleFrame.pack(side = LEFT, fill = BOTH, expand = True)
        
    
    def initializeGUIElements(self):
        
        ##Widgets para el Panel de Espera
        self.waitingText = Label(self.waitingPanelFrame, text="Waiting Area")
        self.waitingText.pack(side = TOP)

        # Hacemos dos frames: Uno para carros en espera de ser distribuidos
        # Y otro para carros en espera de su carril, ya que estos tienen una capacidad máxima de fila

        # Esto primero para espera de distribución
        self.waitingCarsText = Label(self.waitingPanelFrame, text = "Waiting Cars for Distribution")
        self.waitingCarsText.pack(side = TOP)

        self.waitingCarsFrame = Frame(self.waitingPanelFrame)
        self.waitingCarsFrame.pack(side = TOP, expand = True, fill = BOTH)

        self.waitingCarsCanvas = Canvas(self.waitingCarsFrame)

        self.waitingCarsVScrollbar = Scrollbar(self.waitingCarsFrame, orient = VERTICAL)
        self.waitingCarsVScrollbar.pack(side = RIGHT, fill = Y, expand = True)
        self.waitingCarsVScrollbar.config(command = self.waitingCarsCanvas.yview)

        self.waitingCarsCanvas.config(yscrollcommand = self.waitingCarsVScrollbar.set)
        self.waitingCarsCanvas.pack(side = LEFT, expand = True, fill = BOTH)

        self.waitingCarsCanvas.bind('<MouseWheel>', self.onMouseWheelMoveWaitingPanel)

        # Esto para espera de carril
        self.waitingCarsText = Label(self.waitingPanelFrame, text = "Waiting Cars for Lane Availability")
        self.waitingCarsText.pack(side = TOP)

        self.waitingLaneCarsFrame = Frame(self.waitingPanelFrame)
        self.waitingLaneCarsFrame.pack(side = TOP, expand = True, fill = BOTH)

        self.waitingLaneCarsCanvas = Canvas(self.waitingLaneCarsFrame)

        self.waitingLaneCarsVScrollbar = Scrollbar(self.waitingLaneCarsFrame, orient = VERTICAL)
        self.waitingLaneCarsVScrollbar.pack(side = RIGHT, fill = Y, expand = True)
        self.waitingLaneCarsVScrollbar.config(command = self.waitingLaneCarsCanvas.yview)

        self.waitingLaneCarsCanvas.config(yscrollcommand = self.waitingLaneCarsVScrollbar.set)
        self.waitingLaneCarsCanvas.pack(side = LEFT, expand = True, fill = BOTH)

        self.waitingLaneCarsCanvas.bind('<MouseWheel>', self.onMouseWheelMoveWaitingLanePanel)

        # Ahora los botones del panel
        self.addVehicleButton = Button(self.waitingPanelFrame,
                                    command = self.addVehiclesButtonCommand,
                                    text = "Add Vehicles",
                                    width = 13)
        self.addVehicleButton.pack(side = LEFT)
        self.addVehicleButton.config(state = 'disabled')

        self.distributeVehicleButton = Button(self.waitingPanelFrame,
                                    command = self.distributeVehicles,
                                    text = "Distribute Vehicles",
                                    width = 17)
        self.distributeVehicleButton.pack(side = RIGHT)
        self.distributeVehicleButton.config(state = 'disabled')

        

        ##Widgets para las opciones de la simulación
        self.simulationText = Label(self.simulationFrame, text = "Simulation")
        self.simulationText.grid(row = 0, column = 1, columnspan = 2, sticky = N)

        self.instructionsButton = Button(self.simulationFrame,
                              command = self.showInstructions,
                              text = "Instructions",
                              width = 12)
        self.instructionsButton.grid(row = 1, column = 1, columnspan = 2)

        self.configureButton = Button(self.simulationFrame,
                                    text = "Configure Simulation",
                                    command = self.configureSimulation,
                                    width = 20)
        self.configureButton.grid(row = 2, column = 1, columnspan = 2)

        self.startButton = Button(self.simulationFrame,
                                command = self.startSimulation,
                                text = "Start",
                                width = 5)
        self.startButton.grid(row = 3, column = 1)

        self.resetButton = Button(self.simulationFrame,
                                command = self.resetSimulation,
                                text = "Reset",
                                width = 6,
                                state = 'disabled')
        self.resetButton.grid(row = 3, column = 2)

        self.exitButton = Button(self.simulationFrame,
                            command = self.exit,
                            text = "Exit",
                            width = 4)
        self.exitButton.grid(row = 4, column = 1, columnspan = 2)

        self.simulationFrame.grid_columnconfigure(0, weight=1)
        self.simulationFrame.grid_columnconfigure(3, weight=1)

        ##Widgets para las opciones de mantenimiento
        self.maintenanceFrame.grid_columnconfigure(0, weight=1)

        self.maintenanceText = Label(self.maintenanceFrame, text = "Maintenance")
        self.maintenanceText.grid(row = 0, columnspan = 2)


        self.laneComboBox = Combobox(self.maintenanceFrame, state = 'readonly')
        self.laneComboBox.grid(row = 1, columnspan = 2)

        self.changeVehicleTypesButton = Button(self.maintenanceFrame,
                                        command = self.changeLaneVehicleTypes,
                                        text = "Change Vehicles",
                                        width = 15)
        self.changeVehicleTypesButton.grid(row = 2, columnspan = 2)

        ##Widgets para las opciones de pausar líneas

        self.pauseLanesText = Label(self.pauseLanesFrame, text = "Pause Lanes")
        self.pauseLanesText.grid(row = 0, column = 1, columnspan = 2)

        self.lanesList = Listbox(self.pauseLanesFrame, selectmode = MULTIPLE, height = 5, exportselection = 0)
        self.lanesList.grid(row = 1, column = 1, columnspan = 2)

        self.lanesPauseTimeInput = Text(self.pauseLanesFrame, height = 1, width = 3)
        self.lanesPauseTimeInput.grid(row = 2, column = 1, sticky = E+W)

        self.lanesPauseTimeText = Label(self.pauseLanesFrame, text = "Seconds")
        self.lanesPauseTimeText.grid(row = 2, column = 2)

        self.lanesPauseButton = Button(self.pauseLanesFrame,
                                command = self.pauseLanes,
                                text =  "Pause",
                                width = 6)
        self.lanesPauseButton.grid(row = 3, column = 1, columnspan = 2)

        self.pauseLanesFrame.grid_columnconfigure(0, weight=1)
        self.pauseLanesFrame.grid_columnconfigure(3, weight=1)

        ##Widgets para las opciones de sacar vehículo
        self.removeVehicleFrame.grid_columnconfigure(0, weight=1)

        self.removeVehicleText = Label(self.removeVehicleFrame, text = "Remove Vehicle")
        self.removeVehicleText.grid(row = 0, columnspan = 2)

        self.laneComboBoxVehicle = Combobox(self.removeVehicleFrame, state = 'readonly')
        self.laneComboBoxVehicle.grid(row = 1, columnspan = 2)

        self.removeVehicleButton = Button(self.removeVehicleFrame,
                                    command = self.removeVehicle,
                                    text = "Remove Vehicle",
                                    width = 14)
        self.removeVehicleButton.grid(row = 2, columnspan = 2)

    def loadImages(self):
        self.vehiclesImages.append(PhotoImage(file = "oldMotorcycle.png"))
        self.vehiclesImages.append(PhotoImage(file = "newMotorcycle.png"))
        self.vehiclesImages.append(PhotoImage(file = "oldVehicle.png"))
        self.vehiclesImages.append(PhotoImage(file = "newVehicle.png"))
        self.vehiclesImages.append(PhotoImage(file = "bus.png"))
        self.vehiclesImages.append(PhotoImage(file = "twoAxleTruck.png"))
        self.vehiclesImages.append(PhotoImage(file = "fiveAxleTruck.png"))
        self.laneImage = PhotoImage(file = "lane.png")

    # Este método calcula cuántos pixeles debe moverse el tipo de carro en la línea cada 10 milisegundos
    def calculatePixels(self):
        self.pixelsPerSec = []
        for idx, image in enumerate(self.vehiclesImages):
            self.pixelsPerSec.append((625 + image.width()) / self.attentionTimes[idx])



    def showInstructions(self):
        messagebox.showinfo(title = "Instructions",
                            message = "Welcome to the MazeSolver. You can create your own maze and this program will solve it!\n\n"+
                                        "This program will help you find the optimal route from the start point (Black Square) " +
                                        "to the goal point (Green Square).\n\n" +
                                        "To create walls you can add blocks by clicking on a square, or " +
                                        "click, hold & drag the mouse to add blocks.\n\n" +
                                        "To move the start point (The agent which we call Agent101) just right click, hold & drag it around. " +
                                        "The same applies for the goal point.\n\nPlease, enjoy our program :).\n\n" +
                                        "- Kevin Lobo & Victor Chaves")
    
    ######## Métodos para la configuración inicial de la simulación ########

    # StoreConfiguration: Lo utiliza la ventana de configuración para comunicarse con la ventana principal
    def storeConfiguration(self, lanesConfiguration):
        self.lanesConfiguration = lanesConfiguration

    # ConfigureSimulation: Abre la ventana de configuración
    def configureSimulation(self):
        # Mostramos la ventana
        self.confWindow = ConfigWindow(self.storeConfiguration)
        self.confWindow.attributes('-topmost', 'true')
        self.configureButton.config(state = 'disabled')
        self.confWindow.wait_window()


        # Se verifica si la configuración fue enviada a la ventana principal
        if self.lanesConfiguration == None:
            self.configureButton.config(state = 'normal')
            return

        # Si todo está bien, generamos los carriles y llenamos los inputs.
        self.generateLanes()
        self.configureInputs()
        self.addVehicleButton.config(state = 'normal')
        self.distributeVehicleButton.config(state = 'normal')

    # GenerateLanes: Genera los carriles tanto los objetos como la interfaz
    def generateLanes(self):
        
        # Creamos y mostramos los objetos Lane
        ypos = 0
        greatestCapacity = 0
        for key, lane in self.lanesConfiguration.items():
            newLane = ServiceLane(key, lane[0], lane[1], self.laneImage)
            if newLane.capacity > greatestCapacity:
                greatestCapacity = newLane.capacity           
            x = self.canvas.canvasx(0)
            y = self.canvas.canvasy(ypos)
            self.canvas.create_text(x + 5, y, anchor = NW, font= self.boldFont, text = "Lane #"+str(key))
            self.canvas.create_text(x + 5, y + 15, anchor = NW, font= self.boldFont, text = "Capacity = "+ str(lane[0]))
            remainingTimeTextId = self.canvas.create_text(x + 5, y + 30, anchor = NW, font= self.boldFont, text = "Remaining Attention Time: ")
            remainingTimeId = self.canvas.create_text(x + 210, y + 30, anchor = NW, font = self.boldFont, text = "0")
            imageId = self.canvas.create_image(x, y + 50, anchor = NW, image = newLane.image)
            newLane.setRemainingTextId(remainingTimeId)
            newLane.setImageId(imageId)
            newLane.setPos(x, y + 50)
            ypos += 170
            self.lanes.append(newLane)

        ##Configuramos el scrollbar según el tamaño del laberinto
        self.canvas.config(xscrollcommand = self.hScrollbar.set,
                           yscrollcommand = self.vScrollbar.set,
                           scrollregion = (0, 0, 165+165*greatestCapacity,
                                           170*len(self.lanes)),
                           xscrollincrement = 50,
                           yscrollincrement = 170)


    def startSimulation(self):
        if self.lanes == []:
            messagebox.showerror("Missing Lanes", "You must add at least one lane to start the simulation.")
            return

        self.resetButton.config(state = 'normal')
        self.startButton.config(state = 'disabled')
        self.stop = False
        self.startTime = time.time()
        self.simulate()

    def resetSimulation(self):
        reset = messagebox.askokcancel("Reset Simulation", "Reset Simulation? This will delete every lane and vehicle.")

        if not reset:
            return

        #Detenemos la simulación
        self.stop = True

        #Limpiamos TODO y lo ponemos en los valores por defecto
        self.lanes = []
        self.carId = 1
        self.distCount = 0
        self.distribution = None
        self.lanesConfiguration = None
        self.lanes = []
        self.waitingVehicles = []

        #Reseteamos la interfaz
        self.addVehicleButton.config(state = 'disabled')
        self.distributeVehicleButton.config(state = 'disabled')
        self.configureButton.config(state = 'normal')
        self.startButton.config(state = 'normal')
        self.resetButton.config(state = 'disabled')

        self.lanesList.delete(0, END)

        self.laneComboBox['values'] = []
        self.laneComboBox.set("")
        self.laneComboBoxVehicle['values'] = []
        self.laneComboBoxVehicle.set("")

        self.canvas.delete('all')
        self.waitingCarsCanvas.delete("all")
        self.waitingLaneCarsCanvas.delete("all")

    # ConfigureInputs: Configura las entradas de las diferentes opciones de la simulación
    def configureInputs(self):
        # Lista de nombres de carriles para los ComboBox
        lanesNames = []

        # Se genera la lista de nombres y la lista de carriles para pausar
        for idx, lane in enumerate(self.lanes):
            lanesNames.append("Lane #"+str(idx+1))
            self.lanesList.insert(END, lanesNames[idx])

        # Se llena el combobox de mantenimiento
        self.laneComboBox['values'] = lanesNames
        self.laneComboBox.current(0)

        # Se llena el combobox de sacar vehículo
        self.laneComboBoxVehicle['values'] = lanesNames
        self.laneComboBoxVehicle.current(0)

    ######## Métodos para agregar vehículos a la simulación ########

    # AddVehiclesButtonCommand: Abre la ventana con botones para agregar vehículos
    def addVehiclesButtonCommand(self):
        self.addVehiclesWindow = AddVehicleWindow(self.addVehiclesToWaitingLine)
        self.addVehiclesWindow.attributes('-topmost', 'true')
        self.addVehicleButton.config(state = 'disabled')
        self.addVehiclesWindow.wait_window()
        self.addVehicleButton.config(state = 'normal')

    # AddVehiclesToWaitingLine: Con este método la ventana de agregar carros se comunica con la ventana principal
    def addVehiclesToWaitingLine(self, vehicleType, vehicleCount):
        for x in range(0, vehicleCount):
            # Creamos el nuevo objeto vehículo y lo agregamos a la lista de espera
            newVehicle = Vehicle(vehicleType, self.attentionTimes[vehicleType], self.carId)
            self.carId += 1
            self.waitingVehicles.append(newVehicle)

            waitingVehiclesLength = len(self.waitingVehicles)

            # Colocamos el vehículo en la interfaz: Se crea la imagen, se guarda el id de la imagen, y se recalcula el scroll del canvas
            imageId = self.waitingCarsCanvas.create_image(100, 60*(waitingVehiclesLength-1)+25, image = self.vehiclesImages[newVehicle.getType()])
            textId = self.waitingCarsCanvas.create_text(100, 60*(waitingVehiclesLength-1)+25, fill = self.vehicleIdColor, 
                                                        font = self.boldFont, text = str(newVehicle.getId()))
            self.waitingCarsCanvas.config(yscrollcommand = self.waitingCarsVScrollbar.set,
                                scrollregion = (0, 0, 0, 60*len(self.waitingVehicles)))

    

    ######## Métodos para distribuir los vehículos de la simulación ########
    
    # TODO: Este método debe abrir una ventana que ejecute el algoritmo genético
    # Esa ventana es la que debería instanciar el algoritmo, no la principal
    # Esperemos que trabaje con su propio hilo/proceso <- No :(
    def receiveDistribution(self, distribution):
        self.distribution = distribution

    def distributeVehicles(self):
        if self.waitingVehicles == []:
            messagebox.showinfo("No Waiting Vehicles", "There are no vehicles waiting for distribution. You must add vehicles first.")
            return
        self.distributeWindow = DistributeVehiclesWindow(self.lanes, self.waitingVehicles, self.distCount, self.receiveDistribution)
        self.distributeWindow.attributes('-topmost', 'true')
        self.distributeVehicleButton.config(state = 'disabled')
        self.distributeWindow.wait_window()
        self.distributeVehicleButton.config(state = 'normal')

        if self.distribution == None:
            return

        self.distCount += 1

        newWaitingVehicles = []
        for vehicleIndex, laneNumber in enumerate(self.distribution):
            if laneNumber != -1:
                currentLane = self.lanes[laneNumber]
                currentLane.addVehicle(self.waitingVehicles[vehicleIndex])
                self.canvas.itemconfig(currentLane.getRaiminingTextId(), text = currentLane.remainingAttentionTime)
            else:
                newWaitingVehicles.append(self.waitingVehicles[vehicleIndex])

        self.waitingVehicles = newWaitingVehicles

        self.distribution = None

        self.updateWaitingLaneImages()

        self.updateSimulation() 

    # UpdateWaitingLaneImages: Después de distribuir, se debe reacomodar la lista de espera
    def updateWaitingLaneImages(self):
        # Borramos todos los carros en interfaz
        self.waitingCarsCanvas.delete("all")

        # Validamos cuáles carros quedaron y los agregamos a la interfaz de la línea de espera
        for idx, vehicle in enumerate(self.waitingVehicles):
            imageId = self.waitingCarsCanvas.create_image(100, 60*idx+25, image = self.vehiclesImages[vehicle.getType()])
            textId = self.waitingCarsCanvas.create_text(100, 60*idx+25, fill = self.vehicleIdColor, 
                                                    font = self.boldFont, text = str(vehicle.getId()))

        # Actualizamos también el scrollbar
        self.waitingCarsCanvas.config(yscrollcommand = self.waitingCarsVScrollbar.set,
                            scrollregion = (0, 0, 0, 60*len(self.waitingVehicles)))

    def updateSimulation(self):
        for idx, lane in enumerate(self.lanes):
            # Caso en el que no hay nada en interfaz para el carril, o sea, está completamente vacío.
            # Cuando el carril ya no puede atender carros (no hay en espera), currentVehicle vuelve a ser None
            if lane.currentVehicle == None:
                xOff = 0
                for waitingVehicle in lane.getWaitingVehicles():
                    if lane.currentVehicle == None:
                        lane.currentVehicle = waitingVehicle
                    vehicleWidth = self.vehiclesImages[waitingVehicle.getType()].width()
                    vehicleImageId = self.canvas.create_image(625 + vehicleWidth / 2 + xOff, lane.y + 50, image = self.vehiclesImages[waitingVehicle.getType()])
                    vehicleTextId = self.canvas.create_text(625 + vehicleWidth / 2 + xOff, lane.y + 50, fill = self.vehicleIdColor, 
                                                        font = self.boldFont, text = str(waitingVehicle.getId()))
                    vehicleAttTimeTextId = self.canvas.create_text(625 + vehicleWidth / 2 + xOff, lane.y + 10, fill = "black",
                                                        font = self.boldFont, text = str(waitingVehicle.getRemainingAttentionTime()))
                    waitingVehicle.setImageAndTextId(vehicleImageId, vehicleTextId, vehicleAttTimeTextId)
                    xOff += vehicleWidth

            # Caso en el que la línea sólo puede atender un carro a la vez
            # Y hay un carro siendo atendido en el momento de distribuir
            elif lane.capacity >= 2:
                xOff = 0
                for waitingVehicle in lane.getWaitingVehicles():
                    vehicleType = waitingVehicle.getType()
                    vehicleWidth = self.vehiclesImages[vehicleType].width()
                    if waitingVehicle.getImageId() == None:
                        vehicleImageId = self.canvas.create_image(625 + vehicleWidth / 2 + xOff, lane.y + 50, image = self.vehiclesImages[vehicleType])
                        vehicleTextId = self.canvas.create_text(625 + vehicleWidth / 2 + xOff, lane.y + 50, fill = self.vehicleIdColor, 
                                                            font = self.boldFont, text = str(waitingVehicle.getId()))
                        vehicleAttTimeTextId = self.canvas.create_text(625 + vehicleWidth / 2 + xOff, lane.y + 10, fill = "black",
                                                        font = self.boldFont, text = str(waitingVehicle.getRemainingAttentionTime()))
                        waitingVehicle.setImageAndTextId(vehicleImageId, vehicleTextId, vehicleAttTimeTextId)
                    xOff += vehicleWidth

            if lane.currentVehicle in lane.waitingVehicles:
                lane.waitingVehicles.remove(lane.currentVehicle)

        self.drawWaitingLaneCars()

    def removeVehicle(self):
        lane = self.laneComboBoxVehicle.current()
        self.laneToRemoveVehicle = lane
        return
            
            
    def simulate(self):
        for idx, lane in enumerate(self.lanes):
            removed = False
            currentVehicle = lane.currentVehicle

            if currentVehicle != None:
                imageId = currentVehicle.getImageId()
                textId = currentVehicle.getTextId()
                attTimeId = currentVehicle.getAttTimeTextId()
                vehicleType = currentVehicle.getType()
                vehicleImageWidth = self.vehiclesImages[vehicleType].width()


                if self.laneToRemoveVehicle == idx:
                    remainingTime = currentVehicle.getRemainingAttentionTime()
                    currentVehicleXCoord = self.canvas.coords(imageId)[0]
                    lane.updateRemainingTime(remainingTime)
                    self.canvas.delete(imageId)
                    self.canvas.delete(textId)
                    self.canvas.delete(attTimeId)
                    self.laneToRemoveVehicle = -1
                    removed = True
                else:
                    endTime = time.time()
                    timeElapsed = round(endTime - self.startTime, 2)
                    if lane.isPaused():
                        lane.pausedTime -= timeElapsed

                    if lane.pausedTime <= 0:
                        currentVehicle.reduceRaminingTime(timeElapsed)
                        lane.updateRemainingTime(timeElapsed)
                        self.canvas.move(imageId, -self.pixelsPerSec[vehicleType] * timeElapsed, 0)
                        self.canvas.move(textId, -self.pixelsPerSec[vehicleType] * timeElapsed, 0)
                        self.canvas.move(attTimeId, -self.pixelsPerSec[vehicleType] * timeElapsed, 0)
                        self.canvas.itemconfig(attTimeId, text = currentVehicle.getRemainingAttentionTime())                        
                        self.canvas.itemconfig(lane.getRaiminingTextId(), text = lane.remainingAttentionTime)

                    currentVehicleXCoord = self.canvas.coords(imageId)[0]
                

                if len(lane.waitingVehicles) != 0:
                    firstWaitingVehicle = lane.waitingVehicles[0]
                    firstWaitingVehiclePos = self.canvas.coords(firstWaitingVehicle.getImageId())[0]
                    firstWaitingVehicleImageWidth = self.vehiclesImages[firstWaitingVehicle.getType()].width()
                    moveOffset = firstWaitingVehiclePos - (625 + firstWaitingVehicleImageWidth / 2)

                    if currentVehicleXCoord <= 625 - vehicleImageWidth / 2 and firstWaitingVehiclePos > 625 + firstWaitingVehicleImageWidth / 2 or removed:
                        for idx, waitingVehicle in enumerate(lane.waitingVehicles):
                            self.canvas.move(waitingVehicle.getImageId(), -moveOffset, 0)
                            self.canvas.move(waitingVehicle.getTextId(), -moveOffset, 0)
                            WVAttTimeId = waitingVehicle.getAttTimeTextId()
                            self.canvas.move(WVAttTimeId, -moveOffset, 0)
                            self.canvas.itemconfig(WVAttTimeId, text = waitingVehicle.getRemainingAttentionTime())
                
                if currentVehicleXCoord <= -vehicleImageWidth / 2 or removed:
                    if len(lane.getOutsideWaitingVehicles()) != 0:
                        lane.moveOutsideToLane()
                        self.drawNewWaitingCar(lane)
                    self.drawWaitingLaneCars()
                    lane.attendNextVehicle()

        if not self.stop:
            self.startTime = time.time()
            self.master.after(100, self.simulate)


    def drawWaitingLaneCars(self):
        # Borramos todos los carros en interfaz
        self.waitingLaneCarsCanvas.delete("all")

        carsCounter = 0
        for idx, lane in enumerate(self.lanes):
            if len(lane.getOutsideWaitingVehicles()) == 0:
                continue

            self.waitingLaneCarsCanvas.create_text(100, 60*carsCounter+15, text = "Vehicles waiting for lane #"+str(idx+1)+": ")
            for waitingVehicle in lane.getOutsideWaitingVehicles():      
                imageId = self.waitingLaneCarsCanvas.create_image(100, 60*carsCounter+45, image = self.vehiclesImages[waitingVehicle.getType()])
                textId = self.waitingLaneCarsCanvas.create_text(100, 60*carsCounter+45, fill = self.vehicleIdColor, 
                                                    font = self.boldFont, text = str(waitingVehicle.getId()))
                carsCounter += 1

        #Actualizamos el scrollbar
        self.waitingLaneCarsCanvas.config(yscrollcommand = self.waitingLaneCarsVScrollbar.set,
                            scrollregion = (0, 0, 0, 60*carsCounter+len(self.lanes)*10))


    def drawNewWaitingCar(self, lane):
        lastVehicle = lane.getLastWaitingVehicle()
        if lastVehicle == -1:
            return
        elif lastVehicle == 0:
            newestVehicle = lane.getNewestVehicle()
            newestVehicleWidth = self.vehiclesImages[newestVehicle.getType()].width()
            xPos = 625 + newestVehicleWidth / 2
        else:
            newestVehicle = lane.getNewestVehicle()
            newestVehicleWidth = self.vehiclesImages[newestVehicle.getType()].width()
            lastVehicleImageId = lastVehicle.getImageId()
            lastVehicleWidth = self.vehiclesImages[lastVehicle.getType()].width()
            lastVehicleXPos = self.canvas.coords(lastVehicleImageId)[0]
            xPos = lastVehicleXPos + lastVehicleWidth / 2 + newestVehicleWidth / 2

        vehicleImageId = self.canvas.create_image(xPos, lane.y + 50, image = self.vehiclesImages[newestVehicle.getType()])
        vehicleTextId = self.canvas.create_text(xPos, lane.y + 50, fill = self.vehicleIdColor, 
                                            font = self.boldFont, text = str(newestVehicle.getId()))
        vehicleAttTimeTextId = self.canvas.create_text(xPos, lane.y + 10, fill = "black",
                                                        font = self.boldFont, text = str(newestVehicle.getRemainingAttentionTime()))
        newestVehicle.setImageAndTextId(vehicleImageId, vehicleTextId, vehicleAttTimeTextId)


    
    ######## Métodos para el mantenimiento de carriles ########
    # ChangeLane: Método que utiliza la ventana de cambiar tipos para comunicarse con la ventana principal
    def changeLane(self, laneIndex, newTypesIndices):
        self.lanes[laneIndex].setVehicleTypes(newTypesIndices);
        
    # ChangeLaneVehicleTypes: Método utilizado por el botón de cambiar vehículos
    def changeLaneVehicleTypes(self):
        lane = self.laneComboBox.current()
        if lane == -1:
            return
        self.changeLaneCarsWindow = ChangeVehiclesWindow(lane, self.lanes[lane].getVehicleTypes(), self.changeLane)
        self.changeLaneCarsWindow.attributes('-topmost', 'true')
        self.changeVehicleTypesButton.config(state = 'disabled')
        self.changeLaneCarsWindow.wait_window()
        self.changeVehicleTypesButton.config(state = 'normal')

    ######## Métodos para pausar carriles ########
    # PauseLanes: Se encarga de pausar los carriles seleccionados
    def pauseLanes(self):
        # Obtenemos cuales carriles se han seleccionado para pausar
        # Si no se seleccionaron, no hacemos nada
        selectedItems = self.lanesList.curselection()
        if len(selectedItems) == 0:
            return

        # Se obtiene el texto en el tiempo de pausa
        pauseTime = self.lanesPauseTimeInput.get(1.0, END)

        # Se verifica si corresponde a un número
        try:
            pauseTime = int(pauseTime)
        except:
            messagebox.showerror("Pause Time Input Error", "Please check your pause time. Verify that you wrote only a number.")
            return

        # Se verifica que el número ingresado sea positivo.
        if pauseTime <= 0:
            messagebox.showerror("Pause Time Input Error", "Pause time must be greater than zero.")
            return

        # Esta lista solo lleva el número de las líneas que ya estaban pausadas para poder mostrar un mensaje
        pausedLanes = []

        # Ahora, de las líneas seleccionadas, pausamos las que no están pausadas
        for laneIndex in selectedItems:
            if self.lanes[laneIndex].isPaused():
                pausedLanes.append(str(laneIndex+1))
                continue

            self.lanes[laneIndex].pause(pauseTime)

        # Si ya habían pausadas, simplemente informamos al usuario.
        if len(pausedLanes) != 0:
            messagebox.showinfo("Paused Lanes", "Lane(s) "+" ".join(pausedLanes)+" was/were already paused. You must wait before trying to pause a lane again.")
    


    ##Para que el tab funcione
    def focusNextInput(self, event):
        event.widget.tk_focusNext().focus()
        return("break")


    def onMouseWheelMove(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def onMouseWheelMoveWaitingPanel(self, event):
        self.waitingCarsCanvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def onMouseWheelMoveWaitingLanePanel(self, event):
        self.waitingLaneCarsCanvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def exit(self):
        self.master.destroy()


root = Tk()
root.attributes("-fullscreen", True)
root.resizable(width=False, height=False)
my_gui = MainWindow(root)
root.mainloop()