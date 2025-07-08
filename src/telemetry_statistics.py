# telemetry_statistics.py
import math
import numpy as np
from dataclasses import fields
from forza_telemetry_data import ForzaTelemetryData

class TelemetryStatistics:
    def __init__(self):
        # Para cada campo numérico de ForzaTelemetryData,
        # almacenamos acumuladores para los momentos y una lista de valores para percentiles.
        self.stats = {}
        for f in fields(ForzaTelemetryData):
            # Solo para campos numéricos (int y float)
            self.stats[f.name] = {
                "count": 0,
                "mean": 0.0,
                "M2": 0.0,  # para varianza
                "M3": 0.0,  # para skewness
                "M4": 0.0,  # para curtosis
                "min": None,
                "max": None,
                "values": []  # para calcular mediana y percentiles
            }

    def update(self, telemetry: ForzaTelemetryData):
        # Para cada campo numérico, se actualizan los acumuladores usando el algoritmo online extendido
        for f in fields(ForzaTelemetryData):
            value = getattr(telemetry, f.name)
            if isinstance(value, (int, float)):
                stat = self.stats[f.name]
                stat["count"] += 1
                n = stat["count"]
                x = float(value)
                stat["values"].append(x)
                if n == 1:
                    stat["mean"] = x
                    stat["min"] = x
                    stat["max"] = x
                    stat["M2"] = 0.0
                    stat["M3"] = 0.0
                    stat["M4"] = 0.0
                else:
                    delta = x - stat["mean"]
                    delta_n = delta / n
                    delta_n2 = delta_n * delta_n
                    term1 = delta * delta_n * (n - 1)
                    mean_prev = stat["mean"]
                    stat["mean"] += delta_n
                    stat["M4"] += (term1 * delta_n2 * (n*n - 3*n + 3) +
                                   6 * delta_n2 * stat["M2"] - 4 * delta_n * stat["M3"])
                    stat["M3"] += (term1 * delta_n * (n - 2) - 3 * delta_n * stat["M2"])
                    stat["M2"] += term1
                    if x < stat["min"]:
                        stat["min"] = x
                    if x > stat["max"]:
                        stat["max"] = x

    def get_statistics(self):
        # Para cada campo, se calcula:
        # - varianza y desviación estándar
        # - skewness: (sqrt(n) * M3) / (M2^(3/2))
        # - kurtosis: (n * M4) / (M2^2) - 3
        # - mediana, percentiles 25 y 75 (usando numpy)
        result = {}
        for field_name, stat in self.stats.items():
            n = stat["count"]
            mean = stat["mean"]
            if n > 1 and stat["M2"] != 0:
                variance = stat["M2"] / (n - 1)
                std = math.sqrt(variance)
            else:
                variance = 0.0
                std = 0.0
            if n > 2 and stat["M2"] != 0:
                skewness = (math.sqrt(n) * stat["M3"]) / (stat["M2"] ** 1.5)
            else:
                skewness = 0.0
            if n > 3 and stat["M2"] != 0:
                kurtosis = (n * stat["M4"]) / (stat["M2"] * stat["M2"]) - 3
            else:
                kurtosis = 0.0
            # Calcular mediana y percentiles usando numpy
            values = stat["values"]
            if values:
                median = float(np.percentile(values, 50))
                p25 = float(np.percentile(values, 25))
                p75 = float(np.percentile(values, 75))
            else:
                median = p25 = p75 = None

            result[field_name] = {
                "count": n,
                "mean": mean,
                "std": std,
                "min": stat["min"],
                "max": stat["max"],
                "median": median,
                "percentile25": p25,
                "percentile75": p75,
                "skewness": skewness,
                "kurtosis": kurtosis
            }
        return result
