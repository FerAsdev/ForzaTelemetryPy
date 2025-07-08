# udp_receiver.py
import os
import socket
import asyncio
import datetime
import time
import threading
import json
from telemetry_parser import TelemetryDataParser
from forza_telemetry_data import ForzaTelemetryData
from telemetry_statistics import TelemetryStatistics

class UdpReceiver:
    DEFAULT_PORT = 5300
    WRITE_INTERVAL_MS = 100  # 80 milisegundos (~12.5 Hz)

    def __init__(self, car_name_dict: dict, track_name_dict: dict):
        self._car_name_dict = car_name_dict
        self._track_name_dict = track_name_dict
        self._csv_lock = threading.Lock()
        self._listening_task = None
        self._udp_socket = None
        self._stop_event = asyncio.Event()
        self.is_listening = False
        self._csv_filename = self.generate_csv_filename()
        self._statistics = TelemetryStatistics()  # Agregador de estadísticas

    def generate_csv_filename(self) -> str:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        telemetry_dir = os.path.join(base_dir, "Telemetry")
        os.makedirs(telemetry_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"forza_telemetry_{timestamp}.csv"
        return os.path.join(telemetry_dir, filename)

    def save_to_csv(self, data: ForzaTelemetryData):
        with self._csv_lock:
            file_exists = os.path.exists(self._csv_filename)
            mode = "a" if file_exists else "w"
            with open(self._csv_filename, mode, newline='', encoding='utf-8') as f:
                if not file_exists:
                    header = ForzaTelemetryData.get_csv_header()
                    f.write(header + "\n")
                line = data.to_csv_line()
                f.write(line + "\n")

    async def listen_loop(self, wait_for_lap_zero: bool):
        loop = asyncio.get_running_loop()
        last_write_time = time.time()
        has_started_logging = not wait_for_lap_zero

        while not self._stop_event.is_set():
            try:
                data_bytes, addr = await loop.sock_recvfrom(self._udp_socket, 1024)
                telemetry_data = TelemetryDataParser.parse(data_bytes)

                if telemetry_data.IsRaceOn == 0:
                    continue

                if wait_for_lap_zero and not has_started_logging:
                    if telemetry_data.LapNumber == 0:
                        has_started_logging = True
                        print("Lap 0 detectada, iniciando grabación de telemetría...")
                    else:
                        continue

                if telemetry_data.Speed < 0.5:
                    continue

                if telemetry_data.Gear == 11:
                    continue

                now = time.time()
                if (now - last_write_time) * 1000 >= UdpReceiver.WRITE_INTERVAL_MS:
                    telemetry_data.CarName = self._car_name_dict.get(
                        telemetry_data.CarOrdinal, f"UnknownCar_{telemetry_data.CarOrdinal}"
                    )
                    telemetry_data.TrackName = self._track_name_dict.get(
                        telemetry_data.TrackOrdinal, f"UnknownTrack_{telemetry_data.TrackOrdinal}"
                    )
                    self.save_to_csv(telemetry_data)
                    self._statistics.update(telemetry_data)
                    last_write_time = now

            except asyncio.CancelledError:
                print("Recepción cancelada, saliendo del bucle de escucha...")
                break
            except Exception as ex:
                print(f"Error en recepción/parsing: {ex}")

    def write_statistics_json(self):
        stats = self._statistics.get_statistics()
        json_filename = self._csv_filename.replace(".csv", ".json")
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=4)
        print(f"Estadísticas guardadas en {json_filename}")

    def start_listening(self, wait_for_lap_zero: bool):
        if self.is_listening:
            print("La recepción ya está en marcha. Usa 'stop' antes de iniciar de nuevo.")
            return
        self._csv_filename = self.generate_csv_filename()
        print(f"Creando un nuevo archivo CSV: {self._csv_filename}")

        self._udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._udp_socket.bind(("", UdpReceiver.DEFAULT_PORT))
        self._udp_socket.setblocking(False)

        self._stop_event.clear()
        self.is_listening = True
        self._listening_task = asyncio.create_task(self.listen_loop(wait_for_lap_zero))
        print(f"Recepción iniciada en el puerto {UdpReceiver.DEFAULT_PORT}.")

    def stop_listening(self):
        if not self.is_listening:
            print("La recepción ya está detenida.")
            return
        self.is_listening = False
        self._stop_event.set()
        if self._listening_task:
            self._listening_task.cancel()
        if self._udp_socket:
            self._udp_socket.close()
            self._udp_socket = None
        print("Recepción detenida.")
        self.write_statistics_json()
