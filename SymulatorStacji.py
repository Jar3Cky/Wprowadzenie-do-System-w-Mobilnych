import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import collections


class SymulatorStacjiBazowej:
    def __init__(self, root):
        self.root=root
        self.root.title("Symulator Stacji Bazowej")
        self.root.geometry("1300x850")

        self.czy_dziala = False
        self.resetuj_dane()
        self.buduj_interfejs()

    def resetuj_dane(self):
        #czyszczenie parametrów
        self.czas_aktualny=0
        self.suma_zgloszen=0
        self.zakonczone_rozmowy=0
        self.odrzucone_zgloszenia=0

        #kolejka przechowująca liste polaczen
        self.lista_nadchodzacych_zdarzen=collections.deque()
        #listy przechowujące dane
        self.stan_kanalow=[]
        self.kolejka_oczekujacych=collections.deque()
        self.historia_rho=[]
        self.historia_q=[]
        self.historia_w=[]
        self.suma_dlugosci_kolejki=0
        self.lista_zakonczonych_czekajacych=[]

    #funkcja tworzącąca panel parametrów
    def buduj_interfejs(self):
        panel_lewy=ttk.LabelFrame(self.root, text=" Parametry ", padding=10)
        panel_lewy.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        #ustawienie parametrów i ich wartości startowych
        self.parametry={
            "Liczba kanałów":tk.IntVar(value=10),
            "Nateżenie ruchu - Lambda":tk.DoubleVar(value=1.0),
            "Średnia długość rozmowy":tk.DoubleVar(value=30.0),
            "Odchylenie standardowe":tk.DoubleVar(value=5.0),
            "Minimalny czas połączenia":tk.IntVar(value=10),
            "Maksymalny czas połączenia":tk.IntVar(value=30),
            "Długość kolejki":tk.IntVar(value=10),
            "Czas symulacji": tk.IntVar(value=50)
        }

        for etykieta, zmienna in self.parametry.items():
            ttk.Label(panel_lewy, text=etykieta).pack(anchor="w")
            ttk.Entry(panel_lewy, textvariable=zmienna, width=15).pack(pady=(0, 5))

        self.etykieta_statystyk=ttk.Label(panel_lewy, text="", font=("Arial", 10, "bold"))
        self.etykieta_statystyk.pack(pady=10)

        #przycisk startowy
        tk.Button(panel_lewy, text="Start", bg="#28a745", fg="white", font=("Arial", 9, "bold"),
        command=self.przygotuj_i_start).pack(fill="x", pady=2)
        #przycisk do zatrzymania
        tk.Button(panel_lewy, text="Zatrzymaj", bg="#dc3545", fg="white", font=("Arial", 9, "bold"),
        command=self.stop).pack(fill="x", pady=2)

        #panel środkowy
        panel_srodek=ttk.Frame(self.root, padding=10)
        panel_srodek.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        #okno panelu kanałów
        ttk.Label(panel_srodek, text="Zajęte kanały", font=("Arial", 10, "bold")).pack()
        self.plotno_kanalow=tk.Canvas(panel_srodek, height=150, bg="#f8f9fa", relief="ridge", bd=2)
        self.plotno_kanalow.pack(fill="x", pady=5)

        #okno panelu kolejki
        ttk.Label(panel_srodek, text="Obciążenie kolejki", font=("Arial", 10, "bold")).pack(pady=(20, 0))
        self.plotno_kolejki=tk.Canvas(panel_srodek, height=100, bg="#f8f9fa", relief="ridge", bd=2)
        self.plotno_kolejki.pack(fill="x", pady=5)

        #panel zawierający wykresy
        self.figura, self.osie=plt.subplots(3, 1, figsize=(5, 8))
        self.figura.tight_layout(pad=3.5)
        self.plotno_wykresow=FigureCanvasTkAgg(self.figura, master=self.root)
        self.plotno_wykresow.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, padx=10)

    #funkcja pobierająca dane do symulacji
    def przygotuj_i_start(self):
        if self.czy_dziala: return
        self.resetuj_dane()
        lam=self.parametry["Nateżenie ruchu - Lambda"].get()
        t_max=self.parametry["Czas symulacji"].get()
        czas_teraz=0
        while czas_teraz < t_max:
            odstep=np.random.exponential(1/lam)
            czas_teraz += odstep
            if czas_teraz < t_max:
                dlugosc=int(np.clip(np.random.normal(
                self.parametry["Średnia długość rozmowy"].get(),
                self.parametry["Odchylenie standardowe"].get()),
                self.parametry["Minimalny czas połączenia"].get(),
                self.parametry["Maksymalny czas połączenia"].get()))
                self.lista_nadchodzacych_zdarzen.append((czas_teraz, dlugosc))

        self.stan_kanalow=[0]*self.parametry["Liczba kanałów"].get()
        self.czy_dziala=True
        self.petla_glowna()

    def stop(self):
        self.czy_dziala=False

    def zapis_do_pliku(self):
        try:
            with open("Wyniki.txt", "w") as f:
                f.write("Sekunda\tRho\tQ_Srednie\tW_Srednie\n")
                for i in range(len(self.historia_rho)):
                    rho=self.historia_rho[i]
                    q=self.historia_q[i]
                    w=self.historia_w[i]
                    f.write(f"{i + 1}\t{rho:.4f}\t{q:.2f}\t{w:.2f}\n")
            print("Zapisano dane do wyniki_stacji.txt")
        except Exception as e:
            print(f"Błąd zapisu: {e}")

    def petla_glowna(self):
        #sprawdzenie warunku zakończenia symulacji
        if not self.czy_dziala or self.czas_aktualny>=self.parametry["Czas symulacji"].get():
            if self.czy_dziala:
                self.zapis_do_pliku()
            self.czy_dziala = False
            return

        self.czas_aktualny += 1
        liczba_s=self.parametry["Liczba kanałów"].get()
        limit_k=self.parametry["Długość kolejki"].get()

        #obsługa nowych przychodzących zdarzeń
        while self.lista_nadchodzacych_zdarzen and self.lista_nadchodzacych_zdarzen[0][0]<=self.czas_aktualny:
            _, czas_rozmowy=self.lista_nadchodzacych_zdarzen.popleft()
            self.suma_zgloszen += 1
            wolny_kanal = -1
            for i in range(liczba_s):
                if self.stan_kanalow[i] <= 0:
                    wolny_kanal = i
                    break
            if wolny_kanal != -1:
                self.stan_kanalow[wolny_kanal]=czas_rozmowy
                self.lista_zakonczonych_czekajacych.append(0)
            elif len(self.kolejka_oczekujacych)<limit_k:
                self.kolejka_oczekujacych.append((self.czas_aktualny, czas_rozmowy))
            else:
                self.odrzucone_zgloszenia+=1

        #pętla obsługująca zwalnianie kanałów i obsługę kolejki
        for i in range(liczba_s):
            if self.stan_kanalow[i]>0:
                self.stan_kanalow[i]-=1
                if self.stan_kanalow[i]==0:
                    self.zakonczone_rozmowy+=1
                    if self.kolejka_oczekujacych:
                        moment_wejscia, trwanie=self.kolejka_oczekujacych.popleft()
                        self.stan_kanalow[i]=trwanie
                        self.lista_zakonczonych_czekajacych.append(self.czas_aktualny-moment_wejscia)

        #obliczanie statystyk dla wykresów
        zajete_teraz=sum(1 for k in self.stan_kanalow if k>0)
        rho_teraz=zajete_teraz/liczba_s if liczba_s>0 else 0
        self.suma_dlugosci_kolejki+=len(self.kolejka_oczekujacych)
        q_srednie=self.suma_dlugosci_kolejki/self.czas_aktualny
        w_srednie=np.mean(self.lista_zakonczonych_czekajacych) if self.lista_zakonczonych_czekajacych else 0

        self.historia_rho.append(rho_teraz)
        self.historia_q.append(q_srednie)
        self.historia_w.append(w_srednie)

        self.odswiez_widok(liczba_s, limit_k)
        self.root.after(500, self.petla_glowna)

    def rysuj_wykresy(self):
        tytuly=["Rho (Obciążenie)", "Q (Średnia dł. kolejki)", "W (Średni czas czekania)"]
        kolory=['#3498db', '#e74c3c', '#27ae60']
        for i, (dane, tytul) in enumerate(zip([self.historia_rho, self.historia_q, self.historia_w], tytuly)):
            self.osie[i].clear()
            self.osie[i].plot(dane, color=kolory[i], linewidth=2)
            self.osie[i].set_title(tytul, fontsize=8, fontweight='bold')
            self.osie[i].grid(True, alpha=0.3)
        self.plotno_wykresow.draw()

    #aktualizowanie wykresów, kanałów oraz kolejek po każdym kroku symulacji
    def odswiez_widok(self, liczba_s, limit_k):
        self.etykieta_statystyk.config(
            text=f"\nStatysyki:\nZgłoszenia: {self.suma_zgloszen}\nZakończone: {self.zakonczone_rozmowy}\nOdrzucone: {self.odrzucone_zgloszenia}")

        self.plotno_kanalow.delete("all")
        szerokosc_okna=self.plotno_kanalow.winfo_width()
        if szerokosc_okna<100: szerokosc_okna=600

        #aktualizacja widoku kanałów
        x_start, y_start, odstep_x, odstep_y=10, 20, 55, 65
        kolumny=max(1, (szerokosc_okna - 20)//odstep_x)
        for i in range(liczba_s):
            rzad, kol=i//kolumny, i%kolumny
            x, y=x_start+kol*odstep_x, y_start+rzad*odstep_y
            kolor = "#e74c3c" if self.stan_kanalow[i]>0 else "#2ecc71"
            self.plotno_kanalow.create_rectangle(x, y, x+45, y+40, fill=kolor, outline="#2c3e50")
            if self.stan_kanalow[i]>0:
                self.plotno_kanalow.create_text(x+22, y+20, text=str(self.stan_kanalow[i]), fill="white", font=("Arial", 8, "bold"))
            self.plotno_kanalow.create_text(x+22, y+50, text=f"S{i + 1}", font=("Arial", 7))
        self.plotno_kanalow.config(height=max(120, ((liczba_s - 1)//kolumny+1)*odstep_y+20))

        #aktualizacja widoku kolejki
        self.plotno_kolejki.delete("all")
        ile_czeka=len(self.kolejka_oczekujacych)
        procent=ile_czeka/limit_k if limit_k>0 else 0
        szer_paska=szerokosc_okna - 60
        self.plotno_kolejki.create_rectangle(20, 30, 20+szer_paska, 60, fill="#dfe6e9", outline="#b2bec3")
        kolor_p="#2ecc71"
        if ile_czeka>0:
            self.plotno_kolejki.create_rectangle(20, 30, 20+(szer_paska * procent), 60, fill=kolor_p, outline="#2c3e50")
        self.plotno_kolejki.create_text(20 + szer_paska/2, 45, text=f"Zapełnienie: {ile_czeka} / {limit_k}", font=("Arial", 10, "bold"))

        self.rysuj_wykresy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SymulatorStacjiBazowej(root)
    root.mainloop()