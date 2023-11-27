# Gerekli kütüphaneleri içe aktar
import pandas as pd

# Makineyi tanımla
class Machine:
    def __init__(self, index, isBusy=False, currentOperation=None, currentTime=0):
        self.index = index
        self.isBusy = isBusy
        self.currentOperation = currentOperation
        self.currentTime = currentTime

    def __str__(self):
        return f"Machine {self.index}, Busy: {self.isBusy}, Current Job: {self.currentOperation}, Current Time: {self.currentTime}"

    def isBusy(self):
        return self.isBusy
    
    def getNumber(self):
        return self.index
    
    def setBusy(self, isBusy):
        self.isBusy = isBusy
    
    def startOperation(self, operation, previousOperation):
        # Önceki işi yapan makinenin zamanı, şu anki zamandan küçükse, şu anki zamanı önceki işi yapan makinenin zamanı olarak ayarla
        
        if previousOperation is not None:
            print(f"Previous operation: {previousOperation.index}{previousOperation.order}, Previous machine: {previousOperation.getUsedMachine().index}, Previous machine time: {previousOperation.getUsedMachine().getCurrentTime()}, Current Operation: {operation.index}{operation.order}, Current machine: {self.index}, Current machine time: {self.getCurrentTime()}")
            if previousOperation.getUsedMachine().getCurrentTime() > self.getCurrentTime():
                self.setCurrentTime(previousOperation.getUsedMachine().getCurrentTime())
                print("Current time changed to: ", self.getCurrentTime())
            
        self.isBusy = True
        self.currentOperation = operation

    def finishJob(self):
        self.isBusy = False
        self.currentOperation = None

    def getCurrentTime(self):
        return self.currentTime
    
    def setCurrentTime(self, currentTime):
        self.currentTime = currentTime

# Operasyonu tanımla
class Operation:
    def __init__(self, index, order, duration = [], machines= [], isFinished=False, usedMachine=None, startTime=0, endTime=0):
        self.index = index
        self.order = order
        self.duration = duration
        self.machines = machines
        self.isFinished = isFinished
        self.usedMachine = usedMachine
        self.startTime = startTime
        self.endTime = endTime

    def __str__(self):
        return f"Operation {self.index}{self.order}, Duration: {self.duration}, Machines = {self.machines}, Finished: {self.isFinished}"
    
    def checkFinished(self):
        return self.isFinished
    
    def getMachines(self):
        return [machine for machine in self.machines if machine != '']
    
    def finish(self):
        self.isFinished = True

    def setUsedMachine(self, machine):
        self.usedMachine = machine

    def getUsedMachine(self):
        return self.usedMachine
    
    def getStartTime(self):
        return self.startTime
    
    def getEndTime(self):
        return self.endTime
    
    def setStartTime(self, startTime):
        self.startTime = startTime
    
    def setEndTime(self, endTime):
        self.endTime = endTime

# Bakımı tanımla
class Maintenance:
    def __init__(self, type, name, machine, startTime, duration, isDone=False):
        self.type = type
        self.name = name
        self.machine = machine
        self.startTime = startTime
        self.duration = duration
        self.isDone = isDone

    def __str__(self):
        return f"Maintenance Type: {self.type}, Name: {self.name}, Machine: {self.machine}, Start Time: {self.startTime}, Duration: {self.duration}, Done: {self.isDone}"
    
    def isDone(self):
        return self.isDone

# Kurulumu tanımla
class Setup:
    def __init__(self, fromOp, toOp, duration):
        self.fromOp = fromOp
        self.toOp = toOp
        self.duration = duration

    def __str__(self):
        return f"Setup, From: {self.fromOp}, To: {self.toOp}, Duration: {self.duration}"

# Zaman çizelgesini tanımla
class Timeline:
    def __init__(self, startTime, currentTime, machines, job_times, operation_times):
        self.startTime = startTime
        self.currentTime = currentTime
        self.machines = machines
        self.machines = {machine: [] for machine in self.machines}
        self.job_times = job_times
        self.operation_times = {}


    def __str__(self):
        result = "Timeline:\n"
        result += f"Start Time: {self.startTime}, Current Time: {self.currentTime}\n"
        for machine in self.machines:
            result += f"{str(machine)}\n"
            for operation in self.machines[machine]:
                result += f"{str(operation)}\n"
        return result
    
    def setCurrentTime(self, currentTime):
        self.currentTime = currentTime

    def getCurrentTime(self):
        return self.currentTime

    def add_operation(self, machine, operation, setup, previousOperation):
        print(f"Machine {machine.index} started operation {operation.index}{operation.order} at {self.getCurrentTime()}, Duration: {operation.duration[machine.index-1]}, Setup: {setup}")
        if previousOperation is not None:
            print(f"Previous operation: {previousOperation.index}{previousOperation.order}")

        # Operasyonun başlangıç zamanını ve makineyi ayarla
        self.operation_times[f"{operation.index}-{operation.order}"] = [self.getCurrentTime() + setup*60, self.getCurrentTime() + setup*60, machine.index] 

        # Operasyonu makineye ekle
        self.machines[machine].append(operation)

        # Eğer start_time iş zamanları listesinde yoksa, başlangıç zamanını ekle
        if operation.index not in self.job_times:
            if previousOperation is not None and previousOperation.getUsedMachine().getCurrentTime() > self.getCurrentTime():
                self.job_times[operation.index] = [previousOperation.getUsedMachine().getCurrentTime() + setup*60, previousOperation.getUsedMachine().getCurrentTime() + setup*60]
            else:
                self.job_times[operation.index] = [self.getCurrentTime() + setup*60, self.getCurrentTime() + setup*60]

        # Makine için operasyon süresini bul
        machineIndex = machine.index
        durationIndex = operation.machines.index(f"M{machineIndex}")
        operationDuration = operation.duration[durationIndex]

        if previousOperation is not None and previousOperation.getUsedMachine().getCurrentTime() > self.getCurrentTime():
            machine.setCurrentTime(previousOperation.getUsedMachine().getCurrentTime() + setup*60 + operationDuration*60)
        else:
            machine.setCurrentTime(self.getCurrentTime() + setup*60 + operationDuration*60)
        machine.startOperation(operation, previousOperation)

        self.calculateCurrentTime(machine)
        print(f"Machine {machine.index} finished operation {operation.index}{operation.order} at {self.getCurrentTime()}")
        # Operasyonun bitiş zamanını ayarla
        self.operation_times[f"{operation.index}-{operation.order}"][1] = self.getCurrentTime()
        machine.setBusy(False)
        operation.setUsedMachine(machine)
        machine.finishJob()

        # job_times listesindeki bitiş zamanını güncelle
        self.job_times[operation.index][1] = machine.getCurrentTime()
    
    def add_maintenance(self, machine, maintenance, kestirimciMaintenance=None):
        # Bakımın süresini tanımla
        maintenanceDuration = maintenance.duration*60
        # Eğer makine henüz sözlükte yoksa, değer olarak boş bir liste ekleyin
        if maintenance.machine not in self.machines:
            self.machines[maintenance.machine] = []
        # Makine listesine bakımı ekle
        self.machines[maintenance.machine].append(maintenance)
        # Aynı makinenin kestirimci bakımı varsa, onu da ekleyin
        if kestirimciMaintenance is not None:
            self.machines[maintenance.machine].append(kestirimciMaintenance)
            # Eğer kestirimci bakım daha uzun sürüyorsa, onun zamanını esas al
            if kestirimciMaintenance.duration*60 > maintenanceDuration:
                maintenanceDuration = kestirimciMaintenance.duration*60

            kestirimciMaintenance.isDone = True

        maintenance.isDone = True
        machine.setCurrentTime(self.currentTime + maintenanceDuration)
        self.calculateCurrentTime(machine)

    def calculateTotalTime(self):
        return self.getCurrentTime() - self.startTime
    
    def calculateCurrentTime(self, machine):
        cT = self.currentTime
        mT = machine.getCurrentTime()
        if mT > cT:
            self.setCurrentTime(mT)

# Excel dosyasını oku
class ReadExcel:
    def __init__(self, fileName):
        self.fileName = fileName
        self.operations = []
        self.jobData = pd.read_excel(fileName, sheet_name="Job Times").values.tolist()
        self.setupData = pd.read_excel(fileName, sheet_name="Setup Times").values.tolist()
        self.setupData = [{f"{arr[0]}" : arr[1:]} for arr in self.setupData]
        self.maintenanceData = pd.read_excel(fileName, sheet_name="Maintenance Times").values.tolist()
        self.machine_names =pd.read_excel(fileName, sheet_name="Job Times").columns.values.tolist()[3:]

        # "Job Times" sayfasını okuyun ve Operation nesneleri oluşturun
        for arr in self.jobData:
            self.operations.append(Operation(
                                        arr[0], arr[1], 
                                        [arr[i] if arr[i] != "--" else -1 for i in range(3, 9)], 
                                        [self.machine_names[i-3] if arr[i] != "--" else "" for i in range(3, 9)] 
                                    ))

        self.operation_names = [arr[2] for arr in self.jobData]

        # "Setup Times" sayfasını okuyun ve Setup nesneleri oluşturun
        self.setups = []
        for i in range(len(self.setupData)):
            for j in range(len(self.setupData[i][f"{self.operation_names[i]}"])):
                self.setups.append(Setup(
                                        self.operation_names[i], 
                                        self.operation_names[j], 
                                        self.setupData[i][f"{self.operation_names[i]}"][j] if self.setupData[i][f"{self.operation_names[i]}"][j] != "--" else -1
                                    ))

        # Machine nesnelerini oluşturun
        self.machines = []
        for i in range(len(self.machine_names)):
            self.machines.append(Machine(int(self.machine_names[i][1:]), False, None))

        # Maintenance nesnelerini oluşturun
        self.maintenances = []
        for arr in self.maintenanceData:
            self.maintenances.append(Maintenance(
                                        arr[0], 
                                        arr[1], 
                                        int(arr[2][1:]), 
                                        arr[3].hour * 3600 + arr[3].minute * 60 + arr[3].second,  # arr[3]
                                        arr[4]
                                    ))

    
    def getData(self):
        return self.operations, self.setups, self.machines, self.maintenances
