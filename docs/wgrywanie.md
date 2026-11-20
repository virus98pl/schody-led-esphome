# Wgrywanie programu

Są trzy urządzenia: **sterownik** (`schody-sterownik`, ESP32) i dwa **czujniki** (`schody-dol`, `schody-gora`, ESP32 DevKit V1). Każde wgrywasz raz przez USB, najlepiej na biurku. Potem aktualizacje idą przez Wi-Fi (OTA).

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

### ESP32 DevKit V1 (czujniki)
- Układ USB to CP2102 albo CH340 (napis na scalaku obok gniazda USB). Jeśli w Windows nie pojawia się port COM, zainstaluj sterownik do tego układu.
- Gdy wisi na „Connecting…” albo „Failed to connect”: **przytrzymaj BOOT** do pojawienia się postępu wgrywania (na wielu DevKit V1 automatyczny reset nie działa), ewentualnie trzymaj BOOT i kliknij EN.
- Na czas wgrywania przez USB odłącz przetwornicę 24 → 5 V od VIN.

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
