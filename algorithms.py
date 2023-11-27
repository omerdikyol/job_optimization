# Gerekli kütüphaneleri içe aktar
import random
import math
from models import Timeline

# Tavlama benzetimi algoritmasını tanımla
class SimulatedAnnealing:
    def __init__(self, operations, setups, machines, maintenances, T, alpha, N, iter, start_time, timeline):
        self.operations = operations
        self.setups = setups
        self.machines = machines
        self.maintenances = maintenances
        self.T = T
        self.alpha = alpha
        self.N = N
        self.iter = iter
        self.start_time = start_time
        self.timeline = timeline

    def getOperationsOfJob(self, job):
        return [operation for operation in self.operations if operation.index == job]

    # Uygunluk fonksiyonunu tanımla
    def fitness(self, solution):
        # Makine sayısını al
        machine_count = len(self.machines)

        # Makine ve iş atamalarını çözümden ayır
        machine_assignment = solution[:machine_count]
        job_assignment = solution[machine_count:]
        job_times = {}
        operation_times = {}

        # Timeline'ı oluştur
        current_time = self.start_time
        self.timeline = Timeline(self.start_time, current_time, self.machines, job_times, operation_times)

        # Her makine için başlangıç zamanını ayarla
        for machine in self.timeline.machines:
            machine.setCurrentTime(current_time)

        # Operasyonu bir makineye atayan bir fonksiyon tanımla
        def startOperation(operation):
            # Bir önceki operasyonu al
            previousOperation = None
            if not operation.order == 1:
                previousOperation = [op for op in self.operations if op.index == operation.index and op.order == operation.order - 1][0]
            else:
                # Yeni bir iş başladıysa, önceki işin son operasyonunu al
                currentIndex = job_assignment.index(operation.index)
                if currentIndex != 0:
                    previousJob = job_assignment[currentIndex - 1]
                    previousOperation = [op for op in self.operations if op.index == previousJob][-1]
        
            # Eğer önceki operasyon bitmemişse, önce onu bitir
            if previousOperation is not None and not previousOperation.checkFinished():
                if not startOperation(previousOperation):
                    return False

            # Operasyonu yapabilecek makineleri al
            machines = operation.getMachines()

            # Makine isimlerini makine objelerine çevir
            machines = [machine for machine in self.machines if f"M{machine.index}" in machines]

            # Boş olan makineleri al
            free_machines = [machine for machine in machines if not machine.isBusy]

            # Eğer boş makine varsa
            if len(free_machines) > 0:
                # Rastgele bir makine seç
                machine = random.choice(free_machines)
                # Makinenin bakımı var mı diye kontrol et
                maintenance = checkMaintenance(machine, operation)
                if (maintenance != False and not maintenance.isDone):
                    # Eğer bakım zamanı daha yakınsa, bakımı yap
                    self.timeline.add_maintenance(machine, maintenance)
                    maintenance.isDone = True
                    if not operation.checkFinished():
                        return startOperation(operation)
                
                # Setup zamanını al
                setup = 0
                if previousOperation != None:
                    setup = [setup for setup in self.setups if setup.fromOp == f"O{previousOperation.index}{previousOperation.order}" and setup.toOp == f"O{operation.index}{operation.order}"][0].duration
                # Operasyonu makineye ata
                machine.startOperation(operation, previousOperation)
                # Operasyonu timeline'a ekle
                self.timeline.add_operation(machine, operation, setup, previousOperation)
                operation.finish()

                return True
            
            # Eğer boş makine yoksa
            else:
                return False

        # Bakımı kontrol eden bir fonksiyon tanımla
        def checkMaintenance(machine, job):
            initialTime = machine.getCurrentTime()
            # Makine için en yakın bakım zamanını al
            maintenance = [maintenance for maintenance in self.maintenances if maintenance.machine == machine.index]
            if len(maintenance) > 0:
                maintenance = maintenance[0]
                
                # Toplam iş süresini hesapla
                jobDuration = 0
                for operation in self.operations:
                    if operation.index == job.index:
                        # Makine için operasyon süresini hesapla
                        jobDuration += sum([x for x in operation.duration if x != -1])
                # Eğer iş bakımı engelliyorsa, false döndür
                if (machine.getCurrentTime() + jobDuration*60) % 86400 > maintenance.startTime:
                    return maintenance
                
            return False

        # Operasyonları başlat
        for i in range(len(job_assignment)):
            # Operasyonları al
            operations = self.getOperationsOfJob(job_assignment[i])
            # Bitmemiş operasyonları al
            unfinished_operations = [operation for operation in operations if not operation.checkFinished()]
            # Operasyonu başlat
            while len(unfinished_operations) > 0:
                operation = unfinished_operations[0]
                if startOperation(operation): 
                    unfinished_operations.remove(operation)
                else:
                    break

        # Toplam zamanı hesapla
        total_time = self.timeline.calculateTotalTime()

        # Toplam zamanı döndür
        return total_time, self.timeline

    # Başlangıç çözümünü tanımla
    # Bu fonksiyon, rastgele bir çözüm oluşturur
    def initial_solution(self):
        # Makine ve iş sayısını al
        machine_count = len(self.machines)
        job_count = 0
        for operation in self.operations:
            if operation.index > job_count:
                job_count = operation.index

        # Makine ve iş atamalarını rastgele oluştur
        machine_assignment = list(range(1,machine_count+1))
        job_assignment = list(range(1,job_count+1))
        random.shuffle(machine_assignment)
        random.shuffle(job_assignment)
        # Çözümü bir liste olarak döndür
        return machine_assignment + job_assignment
    
    # Komşu çözümü tanımla
    # Bu fonksiyon, bir çözümün komşusunu oluşturur
    def neighbor_solution(self, solution):
        # Makine ve iş sayısını al
        machine_count = len(self.machines)
        job_count = 0
        for operation in self.operations:
            if operation.index > job_count:
                job_count = operation.index

        # Çözümü makine ve iş atamaları olarak ayır
        machine_assignment = solution[:machine_count]
        job_assignment = solution[machine_count:]
        # Makine veya iş atamalarından birini rastgele seç
        choice = random.randint(0, 1)
        if choice == 0: # Makine atamasını seçtiyse
            # Makine atamasının iki elemanını rastgele değiştir
            i = random.randint(0, machine_count-1)
            j = random.randint(0, machine_count-1)
            machine_assignment[i], machine_assignment[j] = machine_assignment[j], machine_assignment[i]
        else: # İş atamasını seçtiyse
            # İş atamasının iki elemanını rastgele değiştir
            i = random.randint(0, job_count-1)
            j = random.randint(0, job_count-1)
            job_assignment[i], job_assignment[j] = job_assignment[j], job_assignment[i]
        # Yeni çözümü bir liste olarak döndür
        return machine_assignment + job_assignment
    
    # Kabul kriterini tanımla
    # Bu fonksiyon, bir komşu çözümün kabul edilip edilmeyeceğine karar verir
    def acceptance_criterion(self, current_fitness, neighbor_fitness, T):
        # Komşu çözüm daha iyiyse, kabul et
        if neighbor_fitness < current_fitness:
            return True
        # Komşu çözüm daha kötüyse, olasılıkla kabul et
        else:
            # Olasılığı hesapla
            p = math.exp((current_fitness - neighbor_fitness) / T)
            # Rastgele bir sayı üret
            r = random.random()
            # Sayı olasılıktan küçükse, kabul et
            if r < p:
                return True
            # Sayı olasılıktan büyükse, reddet
            else:
                return False
    
    def simulated_annealing_algorithm(self):
        # Başlangıç çözümünü oluştur
        solution = self.initial_solution()
        # Başlangıç çözümünün uygunluk değerini hesapla
        current_fitness, current_timeline = self.fitness(solution)
        # Başlangıç sıcaklığını al
        T = self.T
        # Soğutma katsayısını al
        alpha = self.alpha
        # Komşuluk sayısını al
        N = self.N
        # Iterasyon sayısını al
        iter = self.iter
        # Verileri sıfırla (Sadece değiştirilmiş olab verileri)
        self.reset_data()
        # İterasyon sayısı kadar döngü yap
        for i in range(iter):
            # Komşu çözümü oluştur
            neighbor = self.neighbor_solution(solution)

            # Komşu çözümün uygunluk değerini hesapla
            neighbor_fitness, neighbor_timeline = self.fitness(neighbor)
            # Komşu çözümü kabul et
            if self.acceptance_criterion(current_fitness, neighbor_fitness, T):
                solution = neighbor
                current_timeline = neighbor_timeline
                current_fitness = neighbor_fitness
            # Sıcaklığı güncelle
            T *= alpha

            # Operasyonları, bakımları ve makineleri sıfırla
            self.reset_data()

        # Çözümü döndür
        return solution, current_timeline
    
    def reset_data(self):
        for operation in self.operations:
            operation.isFinished = False
        
        for maintenance in self.maintenances:
            maintenance.isDone = False

        for machine in self.machines:
            machine.isBusy = False
            machine.currentJob = None
            machine.currentTime = self.start_time

# Genetik algoritma'yı tanımla
class GeneticAlgorithm:
    def __init__(self, operations, setups, machines, maintenances, population_size, crossover_rate, mutation_rate, max_generations, start_time, timeline):
        self.operations = operations
        self.setups = setups
        self.machines = machines
        self.maintenances = maintenances
        self.population_size = population_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.max_generations = max_generations
        self.start_time = start_time
        self.timeline = timeline

    def getOperationsOfJob(self, job):
        return [operation for operation in self.operations if operation.index == job]

    # Uygunluk fonksiyonunu tanımla
    # Bu fonksiyon, tavlama benzetimi algoritmasındaki ile aynı
    def fitness(self, solution):
        # Makine sayısını al
        machine_count = len(self.machines)

        # Makine ve iş atamalarını çözümden ayır
        machine_assignment = solution[:machine_count]
        job_assignment = solution[machine_count:]
        job_times = {}
        operation_times = {}

        # Timeline'ı oluştur
        current_time = self.start_time
        self.timeline = Timeline(self.start_time, current_time, self.machines, job_times, operation_times)

        # Her makine için başlangıç zamanını ayarla
        for machine in self.timeline.machines:
            machine.setCurrentTime(current_time)

        # Operasyonu bir makineye atayan bir fonksiyon tanımla
        def startOperation(operation):
            # Bir önceki operasyonu al
            previousOperation = None
            if not operation.order == 1:
                previousOperation = [op for op in self.operations if op.index == operation.index and op.order == operation.order - 1][0]
            else:
                # Yeni bir iş başladıysa, önceki işin son operasyonunu al
                currentIndex = job_assignment.index(operation.index)
                if currentIndex != 0:
                    previousJob = job_assignment[currentIndex - 1]
                    previousOperation = [op for op in self.operations if op.index == previousJob][-1]

            # Eğer önceki operasyon bitmemişse, önce onu bitir
            if previousOperation is not None and not previousOperation.checkFinished():
                if not startOperation(previousOperation):
                    return False

            # Operasyonu yapabilecek makineleri al
            machines = operation.getMachines()

            # Makine isimlerini makine objelerine çevir
            machines = [machine for machine in self.machines if f"M{machine.index}" in machines]

            # Boş olan makineleri al
            free_machines = [machine for machine in machines if not machine.isBusy]

            # Eğer boş makine varsa
            if len(free_machines) > 0:
                # Rastgele bir makine seç
                machine = random.choice(free_machines)
                # Makinenin bakımı var mı diye kontrol et
                maintenance = checkMaintenance(machine, operation)
                if (maintenance != False and not maintenance.isDone):
                    # Eğer bakım zamanı daha yakınsa, bakımı yap
                    self.timeline.add_maintenance(machine, maintenance)
                    maintenance.isDone = True
                    if not operation.checkFinished():
                        return startOperation(operation)
                
                # Setup zamanını al
                setup = 0
                if previousOperation != None:
                    setup = [setup for setup in self.setups if setup.fromOp == f"O{previousOperation.index}{previousOperation.order}" and setup.toOp == f"O{operation.index}{operation.order}"][0].duration
                # Operasyonu makineye ata
                machine.startOperation(operation, previousOperation)
                # Operasyonu timeline'a ekle
                self.timeline.add_operation(machine, operation, setup, previousOperation)
                operation.finish()

                return True
            
            # Eğer boş makine yoksa
            else:
                return False


        # Bakımı kontrol eden bir fonksiyon tanımla
        def checkMaintenance(machine, job):
            initialTime = machine.getCurrentTime()
            # Makine için en yakın bakım zamanını al
            maintenance = [maintenance for maintenance in self.maintenances if maintenance.machine == machine.index]
            if len(maintenance) > 0:
                maintenance = maintenance[0]
                
                # Toplam iş süresini hesapla
                jobDuration = 0
                for operation in self.operations:
                    if operation.index == job.index:
                        # Makine için operasyon süresini hesapla
                        jobDuration += sum([x for x in operation.duration if x != -1])
                # Eğer iş bakımı engelliyorsa, false döndür
                if (machine.getCurrentTime() + jobDuration*60) % 86400 > maintenance.startTime:
                    return maintenance
                
            return False

        # Operasyonları başlat
        for i in range(len(job_assignment)):
            # Operasyonları al
            operations = self.getOperationsOfJob(job_assignment[i])
            # Bitmemiş operasyonları al
            unfinished_operations = [operation for operation in operations if not operation.checkFinished()]
            # Operasyonu başlat
            while len(unfinished_operations) > 0:
                operation = unfinished_operations[0]
                if startOperation(operation): # add not or dont add not?
                    unfinished_operations.remove(operation)
                else:
                    break

        # Toplam zamanı hesapla
        total_time = self.timeline.calculateTotalTime()

        # Toplam zamanı ve Timeline'ı döndür
        return total_time, self.timeline

    # Başlangıç popülasyonunu tanımla
    # Bu fonksiyon, rastgele çözümlerden oluşan bir popülasyon oluşturur
    def initial_population(self):
        # Popülasyonu boş bir liste olarak tanımla
        population = []
        # Popülasyon boyutu kadar döngü yap
        for i in range(self.population_size):
            # Rastgele bir çözüm oluştur
            solution = self.initial_solution()
            # Çözümü popülasyona ekle
            population.append(solution)
        # Popülasyonu döndür
        return population
    
    # Başlangıç çözümünü tanımla
    # Bu fonksiyon, tavlama benzetimi algoritmasındaki ile aynı
    def initial_solution(self):
        # Makine ve iş atamalarını rastgele oluştur
        machine_assignment = list(range(1,7))
        job_assignment = list(range(1,11))
        random.shuffle(machine_assignment)
        random.shuffle(job_assignment)
        # Çözümü bir liste olarak döndür
        return machine_assignment + job_assignment
    
    # Seçilim fonksiyonunu tanımla
    # Bu fonksiyon, popülasyondan en iyi çözümleri seçer
    def selection(self, population):
        # Popülasyondaki her çözümün uygunluk değerini hesapla
        fitness_values = []
        for solution in population:
            self.reset_data()
            fitness_values.append(self.fitness(solution)[0])
        self.reset_data()
        # En iyi iki çözümün indekslerini bul
        best_index = fitness_values.index(min(fitness_values))
        fitness_values[best_index] = max(fitness_values) + 1
        second_best_index = fitness_values.index(min(fitness_values))
        # En iyi iki çözümü döndür
        return population[best_index], population[second_best_index]

    
    def fix_duplicates(self, assignment, assignment1, assignment2):
        # Alınan atamaları birleştir
        unique_values = list(set(assignment1 + assignment2))
        
        # Atamada olmayan değerleri bul
        missing_values = [value for value in unique_values if value not in assignment]
        
        # Atamada tekrarlanan değerleri bul ve onları atamada olmayan değerlerle değiştir
        for i in range(len(assignment)):
            if assignment.count(assignment[i]) > 1:
                assignment[i] = missing_values.pop()
        
        return assignment
        
    # Çaprazlama fonksiyonunu tanımla
    # Bu fonksiyon, iki çözümü birleştirerek yeni bir çözüm oluşturur
    def crossover(self, parent1, parent2):
        # Makine sayısını al
        machine_count = len(self.machines)

        # Çözümleri makine ve iş atamaları olarak ayır
        machine_assignment1 = parent1[:machine_count]
        job_assignment1 = parent1[machine_count:]
        machine_assignment2 = parent2[:machine_count]
        job_assignment2 = parent2[machine_count:]
        # Rastgele bir sayı üret
        r = random.random()
        # Eğer sayı çaprazlama oranından küçükse, çaprazlama yap
        if r < self.crossover_rate:
            # Makine atamalarını çaprazla
            # Bir kesme noktası seç
            cut = random.randint(1, machine_count-1)
            # İlk yarımı birinci ebeveynden, ikinci yarımı ikinci ebeveynden al
            machine_assignment = machine_assignment1[:cut] + machine_assignment2[cut:]
            machine_assignment = self.fix_duplicates(machine_assignment, machine_assignment1, machine_assignment2)

            # İş atamalarını çaprazla
            # Bir kesme noktası seç
            # İş sayısını al
            job_count = 0
            for operation in self.operations:
                if operation.index > job_count:
                    job_count = operation.index
            cut = random.randint(1, job_count-1)
            # İlk yarımı birinci ebeveynden, ikinci yarımı ikinci ebeveynden al
            job_assignment = job_assignment1[:cut] + job_assignment2[cut:]
            # Tekrarlanan iş varsa, onları diğer ebeveynden al
            job_assignment = self.fix_duplicates(job_assignment, job_assignment1, job_assignment2)
        # Eğer sayı çaprazlama oranından büyükse, çaprazlama yapma
        else:
            # Makine ve iş atamalarını birinci ebeveynden al
            machine_assignment = machine_assignment1
            job_assignment = job_assignment1
        # Yeni çözümü bir liste olarak döndür
        return machine_assignment + job_assignment

    # Mutasyon fonksiyonunu tanımla
    # Bu fonksiyon, bir çözümde rastgele bir değişiklik yapar
    def mutation(self, solution):
        # Makine sayısını al
        machine_count = len(self.machines)

        # İş sayısını al
        job_count = 0
        for operation in self.operations:
            if operation.index > job_count:
                job_count = operation.index

        # Çözümü makine ve iş atamaları olarak ayır
        machine_assignment = solution[:machine_count]
        job_assignment = solution[machine_count:]

        # Rastgele bir sayı üret
        r = random.random()

        # Eğer sayı mutasyon oranından küçükse, mutasyon yap
        if r < self.mutation_rate:
            # Makine veya iş atamalarından birini rastgele seç
            choice = random.randint(0, 1)
            if choice == 0:  # Eğer makine ataması seçildiyse
                # Rasgele iki elemanı birbirleriyle değiştir
                i, j = random.sample(range(machine_count), 2)
                machine_assignment[i], machine_assignment[j] = machine_assignment[j], machine_assignment[i]
            else:  # Eğer iş ataması seçildiyse
                # Rasgele iki elemanı birbirleriyle değiştir
                i, j = random.sample(range(job_count), 2)
                job_assignment[i], job_assignment[j] = job_assignment[j], job_assignment[i]

        # Yeni çözümü bir liste olarak döndür
        return machine_assignment + job_assignment

    def reset_data(self):
        for operation in self.operations:
            operation.isFinished = False
        
        for maintenance in self.maintenances:
            maintenance.isDone = False

        for machine in self.machines:
            machine.isBusy = False
            machine.currentJob = None
            machine.currentTime = self.start_time

    def call_genetic_algorithm(self):
        # Başlangıç popülasyonunu oluştur
        population = self.initial_population()
        # Maksimum jenerasyon sayısı kadar döngü yap
        for i in range(self.max_generations):
            # Popülasyondan iki ebeveyn seç
            parent1, parent2 = self.selection(population)
            # Ebeveynleri çaprazla
            child = self.crossover(parent1, parent2)
            # Çocuğu mutasyona uğrat
            child = self.mutation(child)
            # Çocuğun uygunluk değerini hesapla
            child_fitness, child_timeline = self.fitness(child)
            # Popülasyondaki en kötü çözümün indeksini bul
            fitness_values = []
            for solution in population:
                self.reset_data()
                fitness_values.append(self.fitness(solution)[0])

            worst_index = fitness_values.index(max(fitness_values))

            # Eğer çocuk popülasyondaki en kötü çözümden iyiyse, onunla değiştir
            if child_fitness < fitness_values[worst_index]:
                population[worst_index] = child
            # Operasyonları, bakımları ve makineleri sıfırla
            self.reset_data()

        # Popülasyondaki en iyi çözümü ve zaman çizelgesini döndür
        best_index = fitness_values.index(min(fitness_values))
        return population[best_index], child_timeline

    def convert_seconds_to_time(self, total_seconds):
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return hours, minutes, seconds

    def print_time(self,time):
        hours = time // 3600
        minutes = (time % 3600) // 60
        seconds = time % 60
        # Eğer tek haneli ise başına 0 ekle
        hours = f"{hours:02d}"
        minutes = f"{minutes:02d}"
        seconds = f"{seconds:02d}"

        # Eğer saniye 0 ise sadece saat ve dakikayı döndür
        if seconds == "00":
            return hours + ":" + minutes
        
        return hours + ":" + minutes + ":" + seconds
