#!/bin/bash
# Skrypt instalacyjny FVMerger

echo "🚀 Instalacja FVMerger..."

# Sprawdź czy Python jest zainstalowany
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 nie jest zainstalowany. Zainstaluj Python 3.7+ i spróbuj ponownie."
    exit 1
fi

echo "✅ Python 3 znaleziony: $(python3 --version)"

# Utwórz środowisko wirtualne
echo "📦 Tworzenie środowiska wirtualnego..."
python3 -m venv venv

# Aktywuj środowisko wirtualne
echo "🔄 Aktywacja środowiska wirtualnego..."
source venv/bin/activate

# Aktualizuj pip
echo "⬆️ Aktualizacja pip..."
pip install --upgrade pip

# Zainstaluj zależności
echo "📚 Instalacja zależności..."
pip install -r requirements.txt

echo "✅ Instalacja zakończona!"
echo ""
echo "📋 Następne kroki:"
echo "1. Skopiuj plik client_secret.json do katalogu projektu"
echo "2. Aktywuj środowisko: source venv/bin/activate"
echo "3. Uruchom skrypt: python main.py"
echo ""
echo "📖 Więcej informacji w README.md"