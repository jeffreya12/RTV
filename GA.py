from random import randint, random, choice
from copy import deepcopy
from RTVObjects import *

class Gen():
	def __init__(self, gen):
		self.fitness = 0
		self.gen = gen

	def setFitness(self, fitness):
		self.fitness = fitness

	def getFitness(self):
		return self.fitness

	def setGen(self, gen):
		self.gen = gen

	def getGen(self):
		return self.gen


class GeneticAlgorithm(threading.Thread):
	def __init__(self, queue, args):
		threading.Thread.__init__(self)
		self.queue = queue
		self.newGeneration = []
		self.maxGenerations = args[1]
		self.populationSize = args[0]
		self.lanes = args[2]
		for lane in self.lanes:
			lane.calculateWaitingTimeAndCars()
		self.vehicles = args[3]
		self.textbox = args[4]


	def getBest(self):
		bestGen = self.population[0]
		for gen in self.population:
			if gen.getFitness() <= bestGen.getFitness():
				bestGen = gen
		
		return bestGen

	
	def generatePopulation(self):
		population = []
		for p in range(self.populationSize):
			gen = [-1 for i in range(len(self.vehicles))]
			for idx, vehicle in enumerate(self.vehicles):
				lanesIds = [x for x in range(len(self.lanes))]
				randomLane = choice(lanesIds)
				vehicleType = vehicle.getType()
				while vehicle.getType() not in self.lanes[randomLane].getVehicleTypes():
					lanesIds.remove(randomLane)
					if len(lanesIds) == 0:
						break
					randomLane = choice(lanesIds)
				if vehicleType in self.lanes[randomLane].getVehicleTypes():
					gen[idx] = randomLane

			population.append(Gen(gen))
		return population
				
	def fitness(self, gen):
		lanesSize = len(self.lanes)
		averageWaitingTimes = [0 for x in range(lanesSize)]
		vehiclesPerLane = [0 for x in range(lanesSize)]
		latestVehicleAT = [0 for x in range(lanesSize)]
		latestVehicleWT = [0 for x in range(lanesSize)]

		for laneIndex in range(0, lanesSize):
			currentLane = self.lanes[laneIndex]

			averageWaitingTimes[laneIndex] = currentLane.waitingTime
			vehiclesPerLane[laneIndex] = currentLane.numberOfCars
			
			latestVehicleWT[laneIndex] = currentLane.lastWaitTime
			latestVehicleAT[laneIndex] = currentLane.lastRemainingTime


		for idx, vehicleLane in enumerate(gen.getGen()):
			if vehicleLane == -1:
				continue

			vehiclesPerLane[vehicleLane] += 1
			latestVehicleWT[vehicleLane] += latestVehicleAT[vehicleLane]
			averageWaitingTimes[vehicleLane] += latestVehicleWT[vehicleLane]
			#print(averageWaitingTimes)
			latestVehicleAT[vehicleLane] = self.vehicles[idx].getAttentionTime()

		#print(averageWaitingTimes, vehiclesPerLane)
			
		for laneIndex in range(0, lanesSize):
			if (vehiclesPerLane[laneIndex] == 0):
				continue
			averageWaitingTimes[laneIndex] /= vehiclesPerLane[laneIndex]

		gen.setFitness(sum(averageWaitingTimes) / len(averageWaitingTimes))


	def calculateFitness(self):
		for gen in self.population:
			self.fitness(gen)


	def cross(self, padres):
		if (padres[0].getGen() == padres[1].getGen()):
			self.textbox.insert(END, "The selected gens for crossover are identical, crossover will not be performed.\n\n", ("a"))
			return padres
		puntosCruce = []
		numCruces = randint(1, 2)
		randomNum = randint(1, len(self.vehicles) - 1)
		padres = [padres[0].getGen(), padres[1].getGen()]


		self.textbox.insert(END, "The following gens will be crossed with "+ str(numCruces) +" point(s):.\n", ("a"))
		self.textbox.insert(END, str(padres[0]) + "\n", ("a"))
		self.textbox.insert(END, str(padres[1]) + "\n", ("a"))

		if numCruces == 1:
			partePadre = padres[0][0:randomNum]
			parteMadre = padres[1][0:randomNum]
			padres[0][0:randomNum] = parteMadre
			padres[1][0:randomNum] = partePadre
			
		else:
			for i in range(2):
				while randomNum in puntosCruce:
					randomNum = choice(range(len(self.lanes)))
				puntosCruce.append(randomNum)
			puntosCruce.sort()
			partePadre = padres[0][puntosCruce[0]:puntosCruce[1]]
			parteMadre = padres[1][puntosCruce[0]:puntosCruce[1]]
			padres[0][puntosCruce[0]:puntosCruce[1]] = parteMadre
			padres[1][puntosCruce[0]:puntosCruce[1]] = partePadre

		self.textbox.insert(END, "\nThe children are: \n", ("a"))
		self.textbox.insert(END, str(padres[0]) + "\n", ("a"))
		self.textbox.insert(END, str(padres[1]) + "\n\n", ("a"))

		return [Gen(padres[0]), Gen(padres[1])]

	#Implementa el torneo determinístico       
	def tournament(self):
		first = choice(self.population)
		second = choice(self.population)
		third = choice(self.population)

		chosen = first

		if chosen.getFitness() > second.getFitness():
			chosen = second
		if chosen.getFitness() > third.getFitness():
			chosen = third

		return chosen
	 

	def selectParents(self):
		padre = self.tournament()
		madre = self.tournament()
		padres = deepcopy([padre,madre])
		return padres


	def mutate(self, son):
		if random() < 0.03:
			sonGen = son.getGen()
			self.textbox.insert(END, "The gen: " + str(sonGen) + " has been selected for mutation.\n")
			randomVehicle = randint(0, len(self.vehicles) - 1)
			if (sonGen[randomVehicle] == -1):
				self.textbox.insert(END, "The selected vehicle can not be allocated. No mutation is performed.\n\n")
				return

			moved = False

			for lane in range(len(self.lanes)):
				if self.vehicles[randomVehicle].getType() in self.lanes[lane].getVehicleTypes() and sonGen[randomVehicle] != lane:
					sonGen[randomVehicle] = lane
					self.textbox.insert(END, "The vehicle #"+ str(self.vehicles[randomVehicle].getId()) + " has been moved to Lane #" + str(lane) + "\n")
					moved = True
					break

			if not moved:
				self.textbox.insert(END, "The vehicle #"+ str(self.vehicles[randomVehicle].getId()) + " can't be moved anywhere. No mutation is performed\n\n")
			else:
				son.setGen(sonGen)
				self.textbox.insert(END, "New Gen: "+ str(son.getGen()) + "\n\n")



	def addChildren(self, parents):
		for child in self.cross(parents):
			self.mutate(child)
			self.newGeneration.append(child)

	def fitnessSum(self):
		suma = 0
		for gen in self.population:
			suma += gen.getFitness()

		return suma


	def run(self):
		self.population = self.generatePopulation()
		self.calculateFitness()
		self.textbox.tag_config("a", justify = CENTER, wrap = WORD)
		self.textbox.insert(END, "The initial population is: \n", ("a"))

		for gen in self.population:
			self.textbox.insert(END, str(gen.getGen()) + "\n", ("a"))

		for i in range(0, self.maxGenerations):
			#print("Generation number "+str(i)+": ")
			self.textbox.insert(END, "Generation number "+str(i+1)+": \n", ("a"))

			while len(self.newGeneration) < len(self.population):
				parents = self.selectParents()
				self.addChildren(parents)

			#print("Current Population Fitness Sum:", self.fitnessSum())
			self.textbox.insert(END, "Current Population Fitness Sum: " + str(round(self.fitnessSum(), 4)) + "\n", ("a"))

			self.population = deepcopy(self.newGeneration)

			self.calculateFitness()

			#print("New Generation Fitness Sum:", self.fitnessSum())
			self.textbox.insert(END, "New Generation Fitness Sum: " + str(round(self.fitnessSum(), 4)) + "\n", ("a"))

			self.newGeneration[:] = []

		bestGen = self.getBest()
		self.textbox.insert(END, "Best Solution is: " + str(bestGen.getGen()) + " with fitness " + str(round(bestGen.getFitness(), 5)), ("a"))
		self.queue.put(bestGen.getGen())