# Changelog

Wszystkie ważne zmiany w projekcie FVMerger będą dokumentowane w tym pliku.

## [1.0.0] - 2025-08-15

### Dodane
- ✨ Konfigurowalne okresy pobierania (`last_month`, `current_month`, `year`, `custom`)
- 📝 Inteligentne nazwy plików z datą i nadawcą
- 🔍 Szczegółowe logowanie procesu
- ⚙️ Plik konfiguracyjny `config.py`
- 📋 Argumenty wiersza poleceń
- 📄 Obsługa konwersji JPG do PDF
- 🧹 Automatyczne czyszczenie plików tymczasowych
- 📊 Zbiorczy PDF do podglądu
- 🛡️ Obsługa błędów i wyjątków

### Zmienione
- 🗓️ Domyślny okres zmieniony na `last_month` (poprzedni miesiąc)
- 📁 Uporządkowana struktura plików i katalogów
- 💬 Ulepszony tekst do wysłania księgowej

### Techniczne
- 🐍 Wsparcie dla Python 3.7+
- 📦 Zaktualizowane zależności w requirements.txt
- 🔧 Dodany setup.py dla łatwej instalacji
- 📖 Kompletna dokumentacja w README.md
- 🚀 Skrypt instalacyjny install.sh

## [0.1.0] - Wersja pierwotna

### Funkcje bazowe
- Pobieranie załączników z Gmail
- Łączenie PDF-ów w jeden plik
- Podstawowa konwersja JPG do PDF
- Ręczne ustawianie dat