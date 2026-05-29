# Projekt 3 - Rozpoznawanie odcisków palców
System biometryczny służący do ekstrakcji cech odcisku palca, zrealizowany w języku Python z użyciem wyłącznie bibliotek NumPy i Pillow.

## Dokumentacja projektu
Pełny opis implementacji, zastosowanych wzorów matematycznych oraz analiza wyników znajduje się w pliku: [Raport_3.pdf](Raport_3.pdf)

## Struktura projektu
* `image_utils.py` – konwersja obrazu i operacje morfologiczne.
* `preprocessor.py` – normalizacja, segmentacja ROI, filtr Gabora, binaryzacja.
* `skeletonizer.py` – szkieletyzacja (KMM, K3M, Zhang–Suen, morfologiczna).
* `skeleton_repair.py` – usuwanie szumu i łączenie przerw w szkielecie.
* `minutiae.py` – detekcja i wizualizacja minucji metodą liczby skrzyżowań.
* `tests.ipynb` – prezentacja działania poszczególnych etapów krok po kroku.

## Wymagania i uruchomienie
Do poprawnego działania wymagane są biblioteki **NumPy**, **Pillow (PIL)** oraz **SciPy**.

```bash
# Instalacja zależności
pip install numpy pillow scipy matplotlib

# Uruchomienie demonstracji
jupyter notebook tests.ipynb
```