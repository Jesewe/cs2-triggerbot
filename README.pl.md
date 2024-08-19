<div align="center">
   <img src="src/img/icon.png" alt="CS2 TriggerBot" width="200" height="200">
   <h1>🎯 CS2 TriggerBot 🎯</h1>
   <p>Twój ostateczny asystent celowania do Counter-Strike 2</p>
   <a href="#funkcje"><strong>Funkcje</strong></a> •
   <a href="#instalacja"><strong>Instalacja</strong></a> •
   <a href="#użycie"><strong>Użycie</strong></a> •
   <a href="#personalizacja"><strong>Personalizacja</strong></a> •
   <a href="#rozwiązywanie-problemów"><strong>Rozwiązywanie problemów</strong></a> •
   <a href="#wnoszenie-wkładu"><strong>Wnoszenie wkładu</strong></a>
   <br><br>
   <p><strong>🌍 Tłumaczenia:</strong></p>
   <a href="README.ru.md"><img src="https://img.shields.io/badge/lang-Russian-purple?style=for-the-badge&logo=googletranslate"></a>
   <a href="README.fr.md"><img src="https://img.shields.io/badge/lang-French-purple?style=for-the-badge&logo=googletranslate"></a>
   <a href="README.es.md"><img src="https://img.shields.io/badge/lang-Spanish-purple?style=for-the-badge&logo=googletranslate"></a>
   <a href="README.uk-UA.md"><img src="https://img.shields.io/badge/lang-Ukrainian-purple?style=for-the-badge&logo=googletranslate"></a>
   <a href="README.pl.md"><img src="https://img.shields.io/badge/lang-Polish-purple?style=for-the-badge&logo=googletranslate"></a>
</div>

---

# Przegląd
CS2 TriggerBot to zautomatyzowane narzędzie zaprojektowane do Counter-Strike 2, które pomaga w precyzyjnym celowaniu poprzez automatyczne wyzwalanie kliknięcia myszą, gdy wróg zostanie wykryty w celowniku gracza.

## Funkcje
- **Automatyczne Strzelanie:** Automatycznie wyzwala kliknięcie myszą, gdy zostanie wykryty wróg.
- **Przyłączenie do procesu:** Łączy się z procesem `cs2.exe` i odczytuje wartości pamięci, aby podejmować decyzje w czasie rzeczywistym.
- **Konfigurowalny Klawisz Wyzwalacza:** Umożliwia użytkownikom zdefiniowanie własnego klawisza wyzwalacza do aktywacji.
- **Sprawdzanie Aktualizacji:** Automatycznie sprawdza najnowszą wersję i powiadamia użytkownika, jeśli dostępna jest aktualizacja.
- **Logowanie Błędów:** Loguje błędy i ważne zdarzenia do pliku dziennika w celach diagnostycznych.

## Instalacja
1. **Sklonuj repozytorium:**
   ```bash
   git clone https://github.com/Jesewe/cs2-triggerbot.git
   cd cs2-triggerbot
   ```

2. **Zainstaluj zależności:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Uruchom skrypt:**
   ```bash
   python main.py
   ```

## Użycie
1. Upewnij się, że Counter-Strike 2 jest uruchomiony.
2. Uruchom skrypt za pomocą powyższej komendy.
3. Skrypt automatycznie sprawdzi dostępność aktualizacji i pobierze niezbędne offsety z dostarczonych źródeł.
4. Po uruchomieniu skryptu naciśnij skonfigurowany klawisz wyzwalacza (domyślnie: `X`), aby aktywować TriggerBot.
5. Narzędzie automatycznie będzie symulować kliknięcia myszą, gdy wróg zostanie wykryty w celowniku.

## Personalizacja
- **Klawisz Wyzwalacza:** Możesz zmienić klawisz wyzwalacza, modyfikując zmienną `TRIGGER_KEY` w skrypcie.
- **Katalog Dzienników:** Pliki dzienników są domyślnie zapisywane w katalogu `%LOCALAPPDATA%\Requests\ItsJesewe\crashes`. Możesz to zmienić, modyfikując zmienną `LOG_DIRECTORY`.

## Rozwiązywanie problemów
- **Nie udało się pobrać offsetów:** Upewnij się, że masz aktywne połączenie z Internetem i że źródłowe URL-e są dostępne.
- **Nie udało się otworzyć `cs2.exe`:** Upewnij się, że gra jest uruchomiona i masz odpowiednie uprawnienia.
- **Nieoczekiwane błędy:** Sprawdź plik dziennika znajdujący się w katalogu dzienników, aby uzyskać więcej informacji.

## Wnoszenie wkładu
Wkłady są mile widziane! Otwórz issue lub wyślij pull request na [repozytorium GitHub](https://github.com/Jesewe/cs2-triggerbot).

## Zrzeczenie się odpowiedzialności
Ten skrypt jest przeznaczony wyłącznie do celów edukacyjnych. Używanie cheatów lub hacków w grach online jest sprzeczne z warunkami korzystania z większości gier i może skutkować banem lub innymi karami. Używaj tego skryptu na własne ryzyko.

## Licencja
Ten projekt jest licencjonowany na licencji MIT. Zobacz plik [LICENSE](LICENSE) po więcej szczegółów.