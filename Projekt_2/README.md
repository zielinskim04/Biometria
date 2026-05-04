# Projekt 2 - Rozpoznawanie tęczówki

System biometryczny służący do identyfikacji osób na podstawie obrazu tęczówki oka, zrealizowany w języku Python.

## Dokumentacja projektu
Pełny opis implementacji, zastosowanych wzorów matematycznych oraz analiza wyników znajduje się w pliku: [Raport_2.pdf](Raport_2.pdf)

## Struktura projektu
* `iris.py` – główna logika matematyczna i implementacja klas.
* `demo.ipynb` – prezentacja działania poszczególnych etapów "krok po kroku".
* `tests.ipynb` – testy przeprowadzone na zbiorze MMU Iris Dataset.

## Wymagania i uruchomienie
Do poprawnego działania wymagane są biblioteki **NumPy** oraz **Pillow (PIL)**.
```bash
# Instalacja zależności
pip install numpy pillow

# Uruchomienie demonstracji
jupyter notebook demo.ipynb