@echo off
title TIMDR-META-DYNAMICS -- GUI
color 0A
cls

:: Zawsze pracuj w katalogu, w ktorym faktycznie lezy ten plik .bat,
:: niezaleznie od tego, skad zostal uruchomiony (skrot, terminal, itp.)
cd /d "%~dp0"

echo ============================================================
echo   TIMDR-META-DYNAMICS: Uruchamianie GUI
echo   Katalog roboczy: %cd%
echo ============================================================
echo.

:: AKTYWACJA SRODOWISKA VENV (jesli istnieje)
if exist "venv\Scripts\activate.bat" (
    echo [OK] Aktywacja venv...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo [OK] Aktywacja .venv...
    call .venv\Scripts\activate.bat
) else (
    echo [INFO] Uzywanie systemowej instalacji Pythona.
)

:: AUTO-INSTALACJA WYMAGANYCH MODULOW
echo.
echo [1/2] Weryfikacja i instalacja pakietow pip...
python -m pip install --upgrade pip --disable-pip-version-check
python -m pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo [BLAD] Nie udalo sie zainstalowac wymaganych pakietow.
    pause
    exit /b 1
)

:: WERYFIKACJA PLIKOW WEJSCIOWYCH
if not exist "gui.py" (
    echo [BLAD] Nie znaleziono pliku "%cd%\gui.py"
    echo         Sprawdz, czy ten .bat lezy w tym samym folderze co gui.py.
    pause
    exit /b 1
)

:: URUCHOMIENIE GUI
echo.
echo [2/2] Uruchamianie GUI Tkinter...
echo Jesli zobaczysz blad "No module named tkinter" - tkinter to
echo standardowa biblioteka Pythona, ale w niektorych instalacjach
echo (np. minimalne) nie jest domyslnie dolaczona - doinstaluj pelna
echo wersje Pythona z python.org (tam tkinter jest wbudowany).
echo.

python gui.py

echo.
echo ============================================================
echo GUI zostalo zamkniete.
echo ============================================================
pause
