# Projekt 1 Biometria
 
Jest to aplikacja okienkowa służąca do przetwarzania obrazów. Napisana jest w Pythonie z użyciem Tkinter i Pillow. Wszystkie funkcje są zaimplementowane, bez użycia dodatkowych bibliotek, poza Numpy.

 
## Struktura projektu
 
```
editor/
│
├── main.py                      # Punkt wejścia
├── requirements.txt
│
└── app/
    ├── main_frame.py            # Główne okno – łączy UI z logiką
    │
    ├── logic/
    │   ├── file.py              # Otwieranie i zapisywanie plików
    │   ├── filters.py           # Wszystkie operacje na obrazie
    │   └── history.py           # Mechanizm cofania zmian (Ctrl+Z)
    │
    └── ui/
        ├── menu.py              # Pasek menu górnego
        ├── canvas.py            # Obszar roboczy z obrazem i zoomem
        ├── sidebar.py           # Panel boczny (suwaki, info)
        └── projection_window.py # Osobne okno projekcji
```
 
## Wymagania
 
- Python 3.8+
- Pillow
- NumPy
- Matplotlib
 
 
## Uruchomienie
 
```bash
# Instalacja zależności
pip install -r requirements.txt
 
# Uruchomienie
python main.py
```
 
 
## Funkcjonalności
 
 
#### Operacje na pikselach
- **Skala szarości** – uśrednianie `(R+G+B)/3`
- **Skala szarości** – luminancja `0.2126·R + 0.7152·G + 0.0722·B`
- **Korekta jasności** – mnożenie przez współczynnik (suwak 0.0–3.0)
- **Korekta kontrastu** – rozciąganie wokół środka (suwak 0.0–3.0)
- **Negatyw** – `255 - piksel` dla każdego kanału
- **Binaryzacja** – progowanie z regulowanym progiem (suwak 0–255)
 
#### Filtry graficzne (bez gotowych bibliotek)
- **Filtr uśredniający** – każdy piksel = średnia z otoczenia (rozmiar jądra: 3×3, 5×5, 7×7)
- **Filtr Gaussa** – ważona średnia z jądrem gaussowskim (rozmiar + sigma)
- **Filtr wyostrzający** – trzy presety:
  - HP1 – łagodne wyostrzenie
  - HP2 – średnie wyostrzenie
  - HP3 – mocne wyostrzenie
- **Własny filtr** – edytowalna siatka wag (rozmiary 2×2 do 7×7)
 
#### Zapis pliku
- Zapis pod tą samą nazwą (`Ctrl+S`)
- Zapis jako nowy plik (`Ctrl+Shift+S`) – PNG, JPEG, BMP
 

#### Histogram
- Wyświetlany w panelu bocznym
- Obsługa trybu RGB (3 kanały) i skali szarości

 
#### Projekcje
- **Projekcja pozioma** – suma jasności pikseli w każdym wierszu
- **Projekcja pionowa** – suma jasności pikseli w każdej kolumnie
- Wyświetlane w osobnym oknie (matplotlib)
- Przełącznik: pozioma / pionowa / obie naraz
 
#### Wykrywanie krawędzi
- **Krzyż Robertsa** – gradient na przekątnych
- **Operator Sobela** – gradient poziomy i pionowy
 

 
#### Operacje nieliniowe
- **Potęgowanie** – `J^α`, regulowane α (rozjaśnia/przyciemnia)
- **Logarytmowanie** – `255 · log(1+J) / log(1+Jmax)`
- **Jasność addytywna** – `J ± b`
- **Rozciąganie histogramu** – normalizacja do pełnego zakresu 0–255
 
#### Operacje morfologiczne
Dostępne kształty elementu strukturyzującego: prostokąt, krzyż, elipsa, linia pozioma, linia pionowa. Rozmiary: 3×3, 5×5, 7×7, 9×9.
 
- **Erozja** – minimum z otoczenia, kurczy jasne obszary
- **Dylatacja** – maksimum z otoczenia, rozszerza jasne obszary
- **Otwarcie** – erozja → dylatacja – usuwa małe obiek  
- **Zamknięcie** – dylatacja → erozja – wypełnia małe dziury
- **Hit-or-Miss**  - wykrywanie wzorców (izolowany piksel, kwadrat 2x2, krzyż, przekątne)
- **Szkieletyzacja** – iteracyjne otwarcie + różnica