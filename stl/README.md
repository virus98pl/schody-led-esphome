# Obudowa czujnika (druk 3D)

Tu trafią pliki obudowy podtynkowej czujnika VL53L5CX (otwór pod puszkę Ø60 w betonie, regulacja pod grubość płyty 0–45 mm, otwór w płycie Ø46–47 mm):

| Plik | Co to jest |
|---|---|
| `01_korpus_beton.stl` | korpus wklejany w otwór w betonie, z gwintem i przepustem na kabel |
| `02_kolnierz_regulacyjny.stl` | wkręcany kołnierz Ø62 – dociska płytę stopnia i zakrywa krawędź otworu |
| `03_wklad_ESP_czujnik_v2.stl` | wysuwany wkład z płytką ESP i pionowo wlutowanym czujnikiem |
| `06_test_okienka_i_plytki.stl` | szybki wydruk testowy do przymiarki płytki i okienka |
| `gen_czujnik_schodowy.py` | generator (parametry na początku pliku) |

Wkład był projektowany pod NodeMCU v3 (58,5 × 31,5 mm). ESP32-C3 SuperMini jest mniejszy i mieści się w tym samym korytku – przyklej go taśmą dwustronną albo zmień `ESP_W` / `ESP_L` w generatorze.

Druk: PETG, warstwa 0,2 mm, 4 obrysy, 25–30 % wypełnienia, bez podpór; brim tylko dla wkładu.
