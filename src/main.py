# main.py
import sys
import os
import asyncio
import threading
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel
)
from udp_receiver import UdpReceiver
from reference_data_repository import ReferenceDataRepository
from telemetry_gui.gui_main import TelemetryViewer


# Hilo que mantiene un event-loop de asyncio separado
class AsyncRunner(threading.Thread):
    def __init__(self):
        super().__init__()
        self.loop = asyncio.new_event_loop()

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)


class TelemetryGUI(QWidget):
    def __init__(self, receiver, async_runner):
        super().__init__()
        self.receiver = receiver
        self.async_runner = async_runner
        self._viewer = None            # se creará al primer uso
        self.init_ui()

    # ---------- UI ----------
    def init_ui(self):
        self.setWindowTitle("Forza Telemetry GUI")
        layout = QVBoxLayout()

        # Título
        self.title_label = QLabel("Forza Telemetry")
        layout.addWidget(self.title_label)

        # Botones principales
        btn_layout = QHBoxLayout()

        self.btn_race = QPushButton("Race")
        self.btn_race.clicked.connect(self.start_race)
        btn_layout.addWidget(self.btn_race)

        self.btn_practice = QPushButton("Practice")
        self.btn_practice.clicked.connect(self.start_practice)
        btn_layout.addWidget(self.btn_practice)

        self.btn_stop = QPushButton("Stop")
        self.btn_stop.clicked.connect(self.stop_receiver)
        btn_layout.addWidget(self.btn_stop)

        # --- NUEVO: botón para abrir el visor ---
        self.btn_viewer = QPushButton("Viewer")
        self.btn_viewer.clicked.connect(self.open_viewer)
        btn_layout.addWidget(self.btn_viewer)
        # ----------------------------------------

        self.btn_exit = QPushButton("Exit")
        self.btn_exit.clicked.connect(self.exit_app)
        btn_layout.addWidget(self.btn_exit)

        layout.addLayout(btn_layout)

        # Área de log
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        self.setLayout(layout)

    # ---------- utilidades ----------
    def log_message(self, msg: str):
        timestamp = time.strftime('%H:%M:%S')
        self.log.append(f"{timestamp} - {msg}")

    # ---------- handlers ----------
    def start_race(self):
        if not self.receiver.is_listening:
            self.async_runner.loop.call_soon_threadsafe(self.receiver.start_listening, True)
            self.log_message("Race mode started")
        else:
            self.log_message("Receiver already running")

    def start_practice(self):
        if not self.receiver.is_listening:
            self.async_runner.loop.call_soon_threadsafe(self.receiver.start_listening, False)
            self.log_message("Practice mode started")
        else:
            self.log_message("Receiver already running")

    def stop_receiver(self):
        if self.receiver.is_listening:
            self.async_runner.loop.call_soon_threadsafe(self.receiver.stop_listening)
            self.log_message("Receiver stopped")
        else:
            self.log_message("Receiver is not running")

    # ---------- visor de gráficas ----------
    def open_viewer(self):
        """
        Abre (o trae al frente) la ventana TelemetryViewer con las pestañas
        de gráficas. El usuario elige el CSV que quiere analizar allí.
        """
        if self._viewer is None:
            self._viewer = TelemetryViewer()
        self._viewer.show()
        self._viewer.raise_()
        self._viewer.activateWindow()

    # ---------- cierre ----------
    def exit_app(self):
        self.stop_receiver()
        self.async_runner.stop()
        if self._viewer is not None:
            self._viewer.close()
        QApplication.instance().quit()


def main():
    app = QApplication(sys.argv)

    # --- referencia de coches y pistas ---
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "Data", "referenceData.db")
    os.makedirs(os.path.join(base_dir, "Data"), exist_ok=True)

    car_csv_path = os.path.join(base_dir, "RepositoryCSV", "CarOrdinal.csv")
    track_csv_path = os.path.join(base_dir, "RepositoryCSV", "TrackOrdinal.csv")
    ReferenceDataRepository.ensure_database_and_populate(db_path, car_csv_path, track_csv_path)

    car_names = ReferenceDataRepository.load_car_names(db_path)
    track_names = ReferenceDataRepository.load_track_names(db_path)

    # --- receptor UDP ---
    receiver = UdpReceiver(car_names, track_names)

    # --- hilo para el event-loop async ---
    async_runner = AsyncRunner()
    async_runner.start()

    # --- GUI principal ---
    gui = TelemetryGUI(receiver, async_runner)
    gui.resize(650, 420)
    gui.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
