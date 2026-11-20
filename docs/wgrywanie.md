# Wgrywanie programu

Są trzy urządzenia: **sterownik** (`schody-sterownik`, ESP32) i dwa **czujniki** (`schody-dol`, `schody-gora`, ESP32-C3). Każde wgrywasz raz przez USB, najlepiej na biurku. Potem aktualizacje idą przez Wi-Fi (OTA).

## Co potrzebne

- Home Assistant z dodatkiem **ESPHome Device Builder** (najlepiej aktualny; wymagane są komponenty `udp` i `packet_transport`)
- kabel USB **do transmisji danych** (nie tylko do ładowania)
- komputer z **Chrome albo Edge** (wgrywanie przez https://web.esphome.io)

## 1. Sekrety

ESPHome → ⋮ → **Secrets**. Wklej `esphome/secrets.example.yaml` i uzupełnij:
- `wifi_ssid`, `wifi_password`: sieć **2,4 GHz**
- `api_key`: wygeneruj na https://esphome.io/components/api/ (pole „encryption key”)
- `ota_password`, `ap_password`: dowolne hasła (AP min. 8 znaków)

Wszystkie trzy urządzenia muszą być w **tej samej sieci (tej samej podsieci)**, bo ruch z czujników idzie rozgłoszeniem UDP. Jeśli masz osobny VLAN dla IoT, wszystkie trzy wrzuć do niego.

## 2. Pliki w ESPHome

Do katalogu ESPHome w HA (`/homeassistant/esphome/` albo `/config/esphome/`, np. przez Samba lub Studio Code Server) skopiuj **całą zawartość** katalogu `esphome/` z repozytorium, razem z podkatalogiem `components/`:

```
esphome/
├── schody-sterownik.yaml
├── schody-dol.yaml
├── schody-gora.yaml
├── czujnik_wspolny.yaml
└── components/vl53l5cx_presence/   ← komponent czujnika
```

Pliki `.yaml` pojawią się w ESPHome jako urządzenia. `czujnik_wspolny.yaml` też się pokaże, ale **nie wgrywaj go** – to tylko wspólna część czujników.

Na każdym urządzeniu: ⋮ → **Validate** → ma być „Configuration is valid”.

## 3. Kompilacja i pierwsze wgranie

**Install → Manual download → Factory format**, potem https://web.esphome.io → **Connect** → port → **Install** → wskaż `.bin`.

Pierwsza kompilacja czujnika pobiera bibliotekę SparkFun VL53L5CX i trwa dłużej (5–15 min).

### ESP32-C3 SuperMini (czujniki)
- Ma wbudowany USB (bez CH340). Jeśli port się nie pojawia albo „Failed to connect”: **trzymaj BOOT**, wepnij USB (albo kliknij RESET), puść BOOT i dopiero wtedy Connect.
- Po wgraniu odłącz i podłącz USB, bo C3 czasem zostaje w trybie wgrywania.

### Sterownik ESP32
- Płytki z CH340/CP2102 potrzebują sterownika USB w Windows, jeśli nie widać portu COM.
- Jeśli nie łączy się samo: trzymaj **BOOT (IO0)**, kliknij **EN/RESET**, puść BOOT.

## 4. Dodanie do Home Assistant

Po wgraniu urządzenia same pojawią się w **Ustawienia → Urządzenia i usługi** jako wykryte ESPHome. Kliknij **Skonfiguruj** i wklej `api_key`.

## 5. Sprawdzenie

1. **Kolejność kolorów taśmy:** na encji Światło ustaw czysty czerwony. Jeśli świeci inny kolor albo biel nie jest bielą, zmień `channel_colors` w `schody-sterownik.yaml` (spróbuj `GRBW`, `RGBW`, `BRGW`) i wgraj ponownie.
2. **Liczba pikseli:** ustaw biel bez efektu. Wszystkie stopnie mają świecić na całej długości. Jeśli ostatni stopień jest krótszy, popraw `px_na_stopien` / `liczba_led`.
3. **Kierunek:** przycisk **Test od dołu** ma zapalać od stopnia 1. Jeśli zapala od góry, dane wchodzą od góry – zamień w `schody-sterownik.yaml` znaki przy `skad: 1` i `skad: -1`.
4. **Czujniki:** w logach czujnika ma być „VL53L5CX gotowy”. Potem kalibracja (README → Kalibracja czujników).
5. **Łączność UDP:** w logach sterownika przy przejściu przed czujnikiem pojawi się zmiana „Ruch dół / Ruch góra”. Ta sama encja jest w HA.
