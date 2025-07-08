import sys
import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QFileDialog, QTextEdit, QTabWidget, QSizePolicy
)
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Importamos nuestras funciones de graficado
from .gui_basic_plots import plot_speed_vs_time, plot_rpm_vs_time
from .gui_motec_plot import plot_motec_style_figure
from .gui_tire_temps import plot_tire_temperatures
from .gui_suspension import plot_suspension_behavior
from .gui_track import plot_track
from .gui_attitude import plot_attitude
from .gui_track_colored import plot_track_colored


class TelemetryViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Forza Telemetry Viewer")

        main_layout = QVBoxLayout()

        # Layout para selección de CSV y JSON
        file_layout = QHBoxLayout()
        self.csv_label = QLabel("CSV: (no seleccionado)")
        self.json_label = QLabel("JSON: (opcional)")

        btn_csv = QPushButton("Abrir CSV")
        btn_csv.clicked.connect(self.load_csv)

        btn_json = QPushButton("Abrir JSON")
        btn_json.clicked.connect(self.load_json)

        file_layout.addWidget(btn_csv)
        file_layout.addWidget(self.csv_label)
        file_layout.addWidget(btn_json)
        file_layout.addWidget(self.json_label)
        main_layout.addLayout(file_layout)

        # Etiqueta para mostrar el mejor tiempo global
        self.best_lap_label = QLabel("Best Lap: --:--.---")
        main_layout.addWidget(self.best_lap_label)

        # Combobox para vueltas
        lap_layout = QHBoxLayout()
        lap_layout.addWidget(QLabel("Vuelta:"))
        self.lap_combo = QComboBox()
        self.lap_combo.currentIndexChanged.connect(self.on_lap_changed)
        lap_layout.addWidget(self.lap_combo)
        main_layout.addLayout(lap_layout)

        # Botón para graficar
        plot_layout = QHBoxLayout()
        self.btn_plot = QPushButton("Graficar")
        self.btn_plot.clicked.connect(self.plot_telemetry)
        plot_layout.addWidget(self.btn_plot)
        main_layout.addLayout(plot_layout)

        # Pestañas para los gráficos
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Texto para estadísticas
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        main_layout.addWidget(self.stats_text)

        # Ajuste de estiramiento para que el tab_widget expanda antes que stats_text
        main_layout.setStretchFactor(self.tab_widget, 1)
        main_layout.setStretchFactor(self.stats_text, 0)

        self.df = None
        self.stats_json = None

        self.setLayout(main_layout)

    def format_time(self, seconds: float) -> str:
        """Convierte un valor en segundos a 'm:ss.xxx' (por ejemplo, 1:25.123)."""
        if seconds <= 0:
            return "--:--.---"
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{minutes}:{secs:02d}.{millis:03d}"

    def load_csv(self):
        csv_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar CSV", "", "CSV Files (*.csv)")
        if csv_path:
            self.csv_label.setText(os.path.basename(csv_path))
            try:
                self.df = pd.read_csv(csv_path)
                self.populate_laps()
            except Exception as e:
                self.df = None
                self.lap_combo.clear()
                self.csv_label.setText(f"Error al leer CSV: {e}")

    def load_json(self):
        json_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar JSON", "", "JSON Files (*.json)")
        if json_path:
            self.json_label.setText(os.path.basename(json_path))
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    self.stats_json = json.load(f)
            except Exception as e:
                self.stats_json = None
                self.json_label.setText(f"Error al leer JSON: {e}")

    def populate_laps(self):
        self.lap_combo.clear()
        if self.df is not None and "LapNumber" in self.df.columns:
            if "BestLap" in self.df.columns:
                valid_bestlaps = self.df[self.df["BestLap"] > 0]["BestLap"]
                if not valid_bestlaps.empty:
                    best_time = valid_bestlaps.min()
                    self.best_lap_label.setText(f"Best Lap: {self.format_time(best_time)}")
                else:
                    self.best_lap_label.setText("Best Lap: N/A")
            else:
                self.best_lap_label.setText("Best Lap: N/A")

            laps = sorted(self.df["LapNumber"].unique())
            for lap in laps:
                lap_df = self.df[self.df["LapNumber"] == lap]
                if "LastLap" in lap_df.columns:
                    last_lap_time = lap_df["LastLap"].iloc[-1]
                    time_str = self.format_time(last_lap_time)
                    self.lap_combo.addItem(f"{lap} - {time_str}")
                else:
                    self.lap_combo.addItem(str(lap))
        else:
            self.lap_combo.addItem("No LapNumber column")
            self.best_lap_label.setText("Best Lap: N/A")

    def on_lap_changed(self):
        self.tab_widget.clear()
        self.stats_text.clear()

    def plot_telemetry(self):
        if self.df is None:
            return

        lap_str = self.lap_combo.currentText()
        if not lap_str:
            return

        lap_number_str = lap_str.split("-")[0].strip()
        if not lap_number_str.isdigit():
            return

        lap_number = int(lap_number_str)
        lap_df = self.df[self.df["LapNumber"] == lap_number].copy()
        if lap_df.empty:
            return

        if "TimestampMS" in lap_df.columns:
            lap_df["TimeSec"] = lap_df["TimestampMS"] / 1000.0
            lap_df["RelativeTime"] = lap_df["TimeSec"] - lap_df["TimeSec"].iloc[0]
        else:
            lap_df["RelativeTime"] = range(len(lap_df))

        self.tab_widget.clear()

        # 1) Gráfico básico de Speed
        fig_speed = plot_speed_vs_time(lap_df, lap_number)
        speed_canvas = FigureCanvas(fig_speed)
        speed_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        speed_canvas.updateGeometry()
        self.tab_widget.addTab(speed_canvas, "Speed")
        speed_canvas.draw()

        # 2) Gráfico básico de RPM
        fig_rpm = plot_rpm_vs_time(lap_df, lap_number)
        rpm_canvas = FigureCanvas(fig_rpm)
        rpm_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        rpm_canvas.updateGeometry()
        self.tab_widget.addTab(rpm_canvas, "RPM")
        rpm_canvas.draw()

        # 3) Gráfico estilo MoTec
        fig_motec = plot_motec_style_figure(lap_df, lap_number)
        motec_canvas = FigureCanvas(fig_motec)
        motec_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        motec_canvas.updateGeometry()
        self.tab_widget.addTab(motec_canvas, "MoTec Style")
        motec_canvas.draw()

        # 4) Gráfico: Temperatura de neumáticos
        fig_tires = plot_tire_temperatures(lap_df, lap_number)
        tire_canvas = FigureCanvas(fig_tires)
        tire_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tire_canvas.updateGeometry()
        self.tab_widget.addTab(tire_canvas, "Tire Temps")
        tire_canvas.draw()

        # 5) Gráfico: Comportamiento de la suspensión
        fig_suspension = plot_suspension_behavior(lap_df, lap_number)
        susp_canvas = FigureCanvas(fig_suspension)
        susp_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        susp_canvas.updateGeometry()
        self.tab_widget.addTab(susp_canvas, "Suspension")
        susp_canvas.draw()

        # 6) Gráfico: Trazada en el Circuito
        fig_track = plot_track(lap_df, lap_number)
        track_canvas = FigureCanvas(fig_track)
        track_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        track_canvas.updateGeometry()
        self.tab_widget.addTab(track_canvas, "Track")
        track_canvas.draw()

        # 7) Gráfico: Trazada coloreada
        fig_track_colored = plot_track_colored(lap_df, lap_number)
        track_colored_canvas = FigureCanvas(fig_track_colored)
        track_colored_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        track_colored_canvas.updateGeometry()
        self.tab_widget.addTab(track_colored_canvas, "Track Colored")
        track_colored_canvas.draw()

        # 8) Gráfico: Actitud (Yaw, Pitch, Roll)
        fig_attitude = plot_attitude(lap_df, lap_number)
        attitude_canvas = FigureCanvas(fig_attitude)
        attitude_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        attitude_canvas.updateGeometry()
        self.tab_widget.addTab(attitude_canvas, "Attitude")
        attitude_canvas.draw()

        # Mostramos estadísticas si hay JSON
        self.display_stats_for_lap(lap_number)

    def display_stats_for_lap(self, lap_number):
        if not self.stats_json:
            self.stats_text.setText("No hay JSON de estadísticas cargado.")
            return

        msg = "=== Estadísticas Globales (JSON) ===\n"
        for param in ["Speed", "CurrentEngineRpm", "Accel", "Brake", "Gear"]:
            if param in self.stats_json:
                stat = self.stats_json[param]
                msg += f"\n{param}:\n"
                msg += f"  Count: {stat['count']}\n"
                msg += f"  Mean:  {stat['mean']:.2f}\n"
                msg += f"  Std:   {stat['std']:.2f}\n"
                msg += f"  Min:   {stat['min']}\n"
                msg += f"  Max:   {stat['max']}\n"

        self.stats_text.setText(msg)


def main():
    app = QApplication(sys.argv)
    viewer = TelemetryViewer()
    viewer.resize(1200, 800)
    viewer.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
