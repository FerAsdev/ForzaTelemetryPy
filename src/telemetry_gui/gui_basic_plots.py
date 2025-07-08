# gui_basic_plots.py
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def format_time_m_ss(x, pos):
    """Formatea x (en segundos) a un string 'm.ss' si x >= 60, o solo segundos si x < 60."""
    minutes = int(x // 60)
    seconds = int(x % 60)
    if minutes == 0:
        return f"{seconds}"
    else:
        return f"{minutes}.{seconds:02d}"

def plot_speed_vs_time(lap_df, lap_number):
    fig, ax = plt.subplots(figsize=(6,4))
    if "RelativeTime" not in lap_df.columns:
        lap_df["RelativeTime"] = range(len(lap_df))
    if "Speed" in lap_df.columns:
        ax.plot(lap_df["RelativeTime"], lap_df["Speed"], label="Speed (m/s)", color='blue')
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Speed (m/s)")
        ax.set_title(f"Lap {lap_number}: Speed vs Time")
        ax.grid(True)
        ax.legend()
    else:
        ax.text(0.5, 0.5, "No 'Speed' column", ha='center', va='center')
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_time_m_ss))
    return fig

def plot_rpm_vs_time(lap_df, lap_number):
    fig, ax = plt.subplots(figsize=(6,4))
    if "RelativeTime" not in lap_df.columns:
        lap_df["RelativeTime"] = range(len(lap_df))
    if "CurrentEngineRpm" in lap_df.columns:
        ax.plot(lap_df["RelativeTime"], lap_df["CurrentEngineRpm"], label="RPM", color='red')
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("RPM")
        ax.set_title(f"Lap {lap_number}: RPM vs Time")
        ax.grid(True)
        ax.legend()
    else:
        ax.text(0.5, 0.5, "No 'CurrentEngineRpm' column", ha='center', va='center')
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_time_m_ss))
    return fig
