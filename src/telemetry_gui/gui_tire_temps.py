# gui_tire_temps.py
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def format_time_m_ss(x, pos):
    minutes = int(x // 60)
    seconds = int(x % 60)
    if minutes == 0:
        return f"{seconds}"
    else:
        return f"{minutes}.{seconds:02d}"

def plot_tire_temperatures(lap_df, lap_number):
    fig, ax = plt.subplots(figsize=(6,4))
    time_col = "RelativeTime"
    if time_col not in lap_df.columns:
        lap_df["RelativeTime"] = range(len(lap_df))
    # Usamos las columnas en Celsius que se han calculado en el parser
    tires = [
        ("TireTempFrontLeftCelsius", "Front Left"),
        ("TireTempFrontRightCelsius", "Front Right"),
        ("TireTempRearLeftCelsius", "Rear Left"),
        ("TireTempRearRightCelsius", "Rear Right")
    ]
    for col, label in tires:
        if col in lap_df.columns:
            ax.plot(lap_df[time_col], lap_df[col], label=label)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Tire Temp (°C)")
    ax.set_title(f"Lap {lap_number}: Tire Temperatures")
    ax.grid(True)
    ax.legend(loc="upper right")
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_time_m_ss))
    return fig
