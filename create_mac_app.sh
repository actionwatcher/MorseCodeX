pyinstaller --noconfirm --onefile --windowed --add-binary "_sounddevice_data/portaudio-binaries/libportaudio.dylib:./_sounddevice_data/portaudio-binaries" --add-data "morse_table.json:./conf" --add-data "MASTER.SCP:./conf" --add-data "MASUSVE.SCP:./conf" --add-data "NAQPCW.txt:./conf" --add-data "ca_counties.txt:./conf" --add-data "MASTERDX.SCP:./conf" --add-data "states_provinces.txt:./conf" --add-data "letters.txt:./conf" --add-data "numbers.txt:./conf" --add-data "qrn.wav:./conf" MorseCodeX.py
