# Gerekli kütüphaneleri içe aktar
import sys
import numpy as np
import pandas as pd
from PyQt5.QtCore import QTime
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QGridLayout, QWidget, QTextEdit, QTimeEdit, QTabWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QProgressDialog

# Modelleri ve algoritmaları içe aktar
from models import Timeline, ReadExcel
from algorithms import SimulatedAnnealing, GeneticAlgorithm

# Ana pencere sınıfını tanımla
class MainWindow(QMainWindow):
    # Başlatıcı fonksiyon
    def __init__(self):
        # Üst sınıfın başlatıcısını çağır
        QMainWindow.__init__(self)

        # Arayüz bileşenlerini oluştur
        self.create_widgets()
        # Arayüz düzenini oluştur
        self.create_layout()
        # Arayüz işlevlerini tanımla
        self.define_functions()
        # Arayüzü göster
        self.show()

    # Arayüz bileşenlerini oluşturan fonksiyon
    def create_widgets(self):
        # Etiketleri oluştur
        self.data_file_label = QLabel("Veri Dosyası (Uzantısı ile birlikte):")
        self.parameters_label = QLabel("Parametreler")
        self.iteration_label = QLabel("Iterasyon sayısı:")
        self.start_time_label = QLabel("Başlangıç zamanı:")

        # Giriş kutularını oluştur ve varsayılan değerleri ata
        self.data_file_edit = QLineEdit("Veri.v1.xlsx")
        self.iteration_edit = QLineEdit()
        self.iteration_edit.setText("100")
        self.start_time = QTimeEdit(self)
        self.start_time.setDisplayFormat("HH:mm")
        self.start_time.setTime(QTime.currentTime())

        # Tavlama benzetimi için etiket ve giriş kutusu
        self.simulated_annealing_label = QLabel("Tavlama Benzetimi")
        self.cooling_factor_label = QLabel("Soğutma katsayısı:")
        self.neighborhood_label = QLabel("Komşuluk sayısı:")
        self.temperature_label = QLabel("Başlangıç sıcaklığı:")
        self.cooling_factor_edit = QLineEdit()
        self.cooling_factor_edit.setText("0.98")
        self.cooling_factor_edit.setReadOnly(True)
        self.cooling_factor_edit.setStyleSheet("QLineEdit { background-color: #e0e0e0 }")
        self.neighborhood_edit = QLineEdit()
        self.neighborhood_edit.setText("100")
        self.temperature_edit = QLineEdit()
        self.temperature_edit.setText("1000")

        # Genetik algoritma için etiket ve giriş kutusu
        self.genetic_algorithm_label = QLabel("Genetik Algoritma")
        self.crossover_probability_label = QLabel("Çaprazlama olasılığı:")
        self.population_size_label = QLabel("Popülasyon büyüklüğü:")
        self.crossover_probability_edit = QLineEdit()
        self.crossover_probability_edit.setText("0.8")
        self.population_size_edit = QLineEdit()
        self.population_size_edit.setText("100")
        self.mutation_rate_label = QLabel("Mutasyon oranı:")
        self.mutation_rate_edit = QLineEdit("0.02")
        self.mutation_rate_edit.setReadOnly(True)
        self.mutation_rate_edit.setStyleSheet("QLineEdit { background-color: #e0e0e0 }")

        # Butonları oluştur
        self.simulated_annealing_button = QPushButton("Tavlama Benzetimi")
        self.genetic_algorithm_button = QPushButton("Genetik Algoritma")
        self.clear_button = QPushButton("Temizle")

        # Sonuç kutusunu oluştur
        self.result_textedit = QTextEdit()
        self.result_textedit.setReadOnly(True)

        # Kapatma düğmesini oluştur
        self.quitButton = QPushButton('Uygulamayı Kapat', self)
        self.quitButton.clicked.connect(QApplication.instance().quit)

    # Arayüz düzenini oluşturan fonksiyon
    def create_layout(self):
        # Pencere başlığını ayarla
        self.setWindowTitle("İş atölyesi planlama problemi")
        # Pencere boyutunu ayarla
        self.resize(800, 600)
        # Merkez widget'ını oluştur
        tab_widget = QTabWidget()
        # Izgara düzenini oluştur
        self.grid_layout = QGridLayout()

        # Sekmeleri oluştur ve tab_widget'a ekle
        tab1 = QWidget()
        tab_widget.addTab(tab1, "Hesapla")

        tab2 = QWidget()
        tab_widget.addTab(tab2, "Veriyi Görüntüle")

        # tab1 için düzen oluştur
        tab1_layout = QGridLayout(tab1)

        # Bileşenleri düzene ekle Tab 1

        # Ortak parametreler
        tab1_layout.addWidget(self.data_file_label, 0, 0)
        tab1_layout.addWidget(self.data_file_edit, 0, 1, 1, 3)
        tab1_layout.addWidget(self.parameters_label, 1, 0, 1, 4)
        tab1_layout.addWidget(self.iteration_label, 2, 0)
        tab1_layout.addWidget(self.iteration_edit, 2, 1)
        tab1_layout.addWidget(self.start_time_label, 2, 2)
        tab1_layout.addWidget(self.start_time, 2, 3)

        # Tavlama benzetimi için parametreler ve butonu
        tab1_layout.addWidget(self.simulated_annealing_label, 3, 0, 1, 2)
        tab1_layout.addWidget(self.temperature_label, 4, 0)
        tab1_layout.addWidget(self.temperature_edit, 4, 1)
        tab1_layout.addWidget(self.neighborhood_label, 5, 0)
        tab1_layout.addWidget(self.neighborhood_edit, 5, 1)
        tab1_layout.addWidget(self.cooling_factor_label, 6, 0)
        tab1_layout.addWidget(self.cooling_factor_edit, 6, 1)
        tab1_layout.addWidget(self.simulated_annealing_button, 7, 0, 1, 2)

        # Genetik algoritma için parametreler ve butonu
        tab1_layout.addWidget(self.genetic_algorithm_label, 3, 2, 1, 2)
        tab1_layout.addWidget(self.crossover_probability_label, 4, 2)
        tab1_layout.addWidget(self.crossover_probability_edit, 4, 3)
        tab1_layout.addWidget(self.population_size_label, 5, 2)
        tab1_layout.addWidget(self.population_size_edit, 5, 3)
        tab1_layout.addWidget(self.mutation_rate_label, 6, 2)
        tab1_layout.addWidget(self.mutation_rate_edit, 6, 3)
        tab1_layout.addWidget(self.genetic_algorithm_button, 7, 2, 1, 2)

        # Diğer butonlar ve çıktı alanı
        tab1_layout.addWidget(self.clear_button, 10, 0, 1, 4)
        tab1_layout.addWidget(self.result_textedit, 11, 0, 1, 4)
        tab1_layout.addWidget(self.quitButton, 12, 0, 1, 4)

        tab1.setLayout(tab1_layout)

        # tab2 için düzen oluştur
        tab2_layout = QVBoxLayout(tab2)
        
        # Veri dosyasını oku
        xls = pd.ExcelFile(self.data_file_edit.text())

        # Her bir sayfa için bir tab oluştur
        sheet_tabs = QTabWidget()
        sheet_tabs.setTabPosition(QTabWidget.South) # Tab'ları aşağıya yerleştir

        # Her bir sayfa için bir tab oluştur
        for i in range(3):
            sheet = xls.parse(i)  # Sayfayı oku
            table = QTableWidget()
            table.setRowCount(sheet.shape[0])  # Satır sayısı
            table.setColumnCount(sheet.shape[1])  # Sütun sayısı

            # Tabloya verileri ekle
            for row in sheet.iterrows():
                for col in range(sheet.shape[1]):
                    table.setItem(row[0], col, QTableWidgetItem(str(row[1][col])))

            sheet_widget = QWidget()
            sheet_layout = QVBoxLayout()
            sheet_layout.addWidget(table)
            sheet_widget.setLayout(sheet_layout)

            # Tab'ı tab_widget'a ekle
            sheet_tabs.addTab(sheet_widget, xls.sheet_names[i])

        # Tab'ı tab2_layout'a ekle
        tab2_layout.addWidget(sheet_tabs)

        self.grid_layout.addWidget(tab_widget)

        # Merkez widget'ını ayarla
        central_widget = QWidget()
        central_widget.setLayout(self.grid_layout)
        self.setCentralWidget(central_widget)

    # Arayüz işlevlerini tanımlayan fonksiyon
    def define_functions(self):
        # Butonlara işlevsellik ekle
        self.simulated_annealing_button.clicked.connect(self.simulated_annealing)
        self.genetic_algorithm_button.clicked.connect(self.genetic_algorithm)
        self.clear_button.clicked.connect(self.clear)

    # Tavlama benzetimi algoritmasını çalıştıran fonksiyon
    def simulated_annealing(self):
        # Verileri oku
        self.operations, self.setups, self.machines, self.maintenances = ReadExcel(self.data_file_edit.text()).getData()
        self.job_times = []
        self.operation_times = {}

        # Başlangıç zamanını al
        if not isinstance(self.start_time, int): 
            self.start_time = self.start_time.time()
            # Başlangıç zamanını saniyeye çevir
            self.start_time = self.start_time.hour() * 3600 + self.start_time.minute() * 60
        # Başlangıç sıcaklığı, soğutma katsayısı, komşuluk sayısı ve iterasyon sayısını al
        T = float(self.temperature_edit.text())
        alpha = float(self.cooling_factor_edit.text())
        N = int(self.neighborhood_edit.text())
        iter = int(self.iteration_edit.text())

        # Kullanıcıya bilgi vermek için bir mesaj oluştur
        progress = QProgressDialog("Tavlama Benzetimi algoritması çalışıyor...", None, 0, 0, self)
        progress.show()
        QApplication.processEvents()

        # Tavlama benzetimi algoritmasını çalıştır
        timeline = Timeline(self.start_time, self.start_time, self.machines, self.job_times, self.operation_times)
        solution, solTimeline = SimulatedAnnealing(self.operations, self.setups, self.machines, self.maintenances, T, alpha, N, iter, self.start_time, timeline).simulated_annealing_algorithm()
        # Sonucu ekle
        self.result_textedit.append("Tavlama benzetimi algoritması:")
        machineLen = len(self.machines)
        self.result_textedit.append("Makineler: " + str(sorted(solution[:machineLen])))
        self.result_textedit.append("İş Sırası: " + str(solution[machineLen:]))

        # Toplam süreyi hesapla
        total_time = solTimeline.calculateTotalTime()
        # Toplam süreyi saat, dakika ve saniyeye çevir
        total_time = self.print_time(int(total_time), True)

        # Toplam süreyi görüntüle
        self.result_textedit.append("\nToplam süre: " + total_time)

        # İşlerin başlangıç zamanı, bitiş zamanı ve tamamlanma süresini görüntüle
        self.result_textedit.append("\nİşlerin başlangıç zamanı, bitiş zamanı ve tamamlanma süresi:")
        for key, value in solTimeline.job_times.items():
            initial_time = self.print_time(int(value[0]))
            end_time = self.print_time(int(value[1]))
            duration = self.print_time(int(value[1]) - int(value[0]), show_unit=True)
            self.result_textedit.append(f"İş {key}: Başlangıç zamanı: {initial_time}, Bitiş zamanı: {end_time}, Tamamlanma süresi: {duration}")

            # Operasyonların başlangıç zamanı, bitiş zamanı ve tamamlanma süresini görüntüle
            for key2, val2 in solTimeline.operation_times.items():
                if str(key2.split('-')[0]) == str(key):
                    self.result_textedit.append(f"  Op. {key2.replace('-','')}: {self.print_time(val2[0])} - {self.print_time(val2[1])}, Süre: {self.print_time(int(val2[1]) - int(val2[0]), show_unit=True)}, Makine: {val2[2]}")

        self.result_textedit.append("\n\n")

        # Mesajı gizle
        progress.close()

    # Genetik algoritmayı çalıştıran fonksiyon
    def genetic_algorithm(self):
        # Verileri oku
        self.operations, self.setups, self.machines, self.maintenances = ReadExcel(self.data_file_edit.text()).getData()
        self.job_times = []

        # Başlangıç zamanını al
        if not isinstance(self.start_time, int): 
            self.start_time = self.start_time.time()
            # Başlangıç zamanını saniyeye çevir
            self.start_time = self.start_time.hour() * 3600 + self.start_time.minute() * 60
        # Popülasyon büyüklüğü, çaprazlama olasılığı, mutasyon olasılığı ve maksimum nesil sayısını al
        population_size = int(self.population_size_edit.text())
        crossover_rate = float(self.crossover_probability_edit.text())
        iter = int(self.iteration_edit.text())
        mutation_rate = 0.02

        # Kullanıcıya bilgi vermek için bir mesaj oluştur
        progress = QProgressDialog("Genetik algoritma çalışıyor...", None, 0, 0, self)
        progress.show()
        QApplication.processEvents()

        # Genetik algoritmayı çalıştır
        solution, solTimeline = GeneticAlgorithm(self.operations, self.setups, self.machines, self.maintenances, population_size, crossover_rate, mutation_rate, iter, self.start_time, None).call_genetic_algorithm()
        # Sonucu ekle
        self.result_textedit.append("Genetik algoritma:")
        machineLen = len(self.machines)
        self.result_textedit.append("Makineler: " + str(sorted(solution[:machineLen])))
        self.result_textedit.append("İş Sırası: " + str(solution[machineLen:]))

        # Toplam süreyi hesapla
        total_time = solTimeline.calculateTotalTime()
        # Toplam süreyi saat, dakika ve saniyeye çevir
        total_time = self.print_time(int(total_time), True)

        # Toplam süreyi görüntüle
        self.result_textedit.append("\nToplam süre: " + total_time)

        # İşlerin başlangıç zamanı, bitiş zamanı ve tamamlanma süresini görüntüle
        self.result_textedit.append("\nİşlerin başlangıç zamanı, bitiş zamanı ve tamamlanma süresi:")
        for key, value in solTimeline.job_times.items():
            initial_time = self.print_time(int(value[0]))
            end_time = self.print_time(int(value[1]))
            duration = self.print_time(int(value[1]) - int(value[0]), show_unit=True)
            self.result_textedit.append(f"İş {key}: Başlangıç zamanı: {initial_time}, Bitiş zamanı: {end_time}, Tamamlanma süresi: {duration}")

            # Operasyonların başlangıç zamanı, bitiş zamanı ve tamamlanma süresini görüntüle
            for key2, val2 in solTimeline.operation_times.items():
                if str(key2.split('-')[0]) == str(key):
                    self.result_textedit.append(f"  Op. {key2.replace('-','')}: {self.print_time(val2[0])} - {self.print_time(val2[1])}, Süre: {self.print_time(int(val2[1]) - int(val2[0]), show_unit=True)}, Makine: {val2[2]}")

        self.result_textedit.append("\n\n")
        
        # Mesajı gizle
        progress.close()

    def clear(self):
        # Giriş kutularını temizle
        self.temperature_edit.clear()
        self.neighborhood_edit.clear()
        self.iteration_edit.clear()
        self.crossover_probability_edit.clear()
        self.population_size_edit.clear()
        # Sonuç kutusunu temizle
        self.result_textedit.clear()

    def convert_seconds_to_time(self, total_seconds):
        hours = total_seconds // 3600
        # Eğer saat 24 ise 0 yap
        hours = hours % 24
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return hours, minutes, seconds

    def print_time(self,time, show_unit=False):
        hours, minutes, seconds = self.convert_seconds_to_time(time)
        # Eğer tek haneli ise başına 0 ekle
        hours = f"{hours:02d}"
        minutes = f"{minutes:02d}"
        seconds = f"{seconds:02d}"

        output = ""

        if show_unit:
            output += hours + " saat " + minutes + " dakika "
            if seconds != "00":
                output += seconds + " saniye"
        
        else:
            output += hours + ":" +  minutes
            if seconds != "00":
                output += ":" + seconds

        return output

# Ana fonksiyonu tanımla
def main():
    # PyQt5 uygulamasını oluştur
    app = QApplication(sys.argv)
    # Ana pencereyi oluştur
    window = MainWindow()
    # Ana pencereyi göster
    window.show()
    # Uygulamayı çalıştır
    sys.exit(app.exec_())

# Ana fonksiyonu çağır
if __name__ == "__main__":
    main()

