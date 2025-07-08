# gui_motec_plot.py
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def format_time_m_ss(x, pos):
    minutes = int(x // 60)
    seconds = int(x % 60)
    if minutes == 0:
        return f"{seconds}"
    else:
        return f"{minutes}.{seconds:02d}"

def plot_motec_style_figure(lap_df, lap_number=None, time_col="RelativeTime"):
    if time_col not in lap_df.columns:
        lap_df["RelativeTime"] = range(len(lap_df))
        time_col = "RelativeTime"
    if "Speed" in lap_df.columns and "SpeedKph" not in lap_df.columns:
        lap_df["SpeedKph"] = lap_df["Speed"] * 3.6

    fig, axes = plt.subplots(nrows=5, ncols=1, sharex=True, figsize=(8,8))
    fig.suptitle(f"MoTec-Style Lap Data (Lap {lap_number})" if lap_number else "MoTec-Style Lap Data")

    ax_speed = axes[0]
    if "SpeedKph" in lap_df.columns:
        ax_speed.plot(lap_df[time_col], lap_df["SpeedKph"], color="green", label="Speed (kph)")
        ax_speed.set_ylabel("Speed (kph)")
        ax_speed.legend(loc="upper left")
        ax_speed.grid(True)
    else:
        ax_speed.text(0.5, 0.5, "No 'Speed' column", ha='center', va='center')
        ax_speed.set_ylabel("N/A")
    ax_speed.xaxis.set_major_formatter(ticker.FuncFormatter(format_time_m_ss))

    ax_rpm = axes[1]
    if "CurrentEngineRpm" in lap_df.columns:
        ax_rpm.plot(lap_df[time_col], lap_df["CurrentEngineRpm"], color="purple", label="RPM")
        ax_rpm.set_ylabel("RPM")
        ax_rpm.legend(loc="upper left")
        ax_rpm.grid(True)
    else:
        ax_rpm.text(0.5, 0.5, "No 'CurrentEngineRpm' column", ha='center', va='center')
        ax_rpm.set_ylabel("N/A")
    ax_rpm.xaxis.set_major_formatter(ticker.FuncFormatter(format_time_m_ss))

    ax_gear = axes[2]
    if "Gear" in lap_df.columns:
        ax_gear.step(lap_df[time_col], lap_df["Gear"], color="yellow", label="Gear", where='post')
        ax_gear.set_ylabel("Gear")
        ax_gear.legend(loc="upper left")
        ax_gear.grid(True)
    else:
        ax_gear.text(0.5, 0.5, "No 'Gear' column", ha='center', va='center')
        ax_gear.set_ylabel("N/A")
    ax_gear.xaxis.set_major_formatter(ticker.FuncFormatter(format_time_m_ss))

    ax_throttle = axes[3]
    if "Accel" in lap_df.columns:
        normalized_throttle = lap_df["Accel"] / 2.55
        ax_throttle.plot(lap_df[time_col], normalized_throttle, color="red", label="Throttle (%)")
        ax_throttle.set_ylabel("Throttle (%)")
        ax_throttle.legend(loc="upper left")
        ax_throttle.grid(True)
    else:
        ax_throttle.text(0.5, 0.5, "No 'Accel' column", ha='center', va='center')
        ax_throttle.set_ylabel("N/A")
    ax_throttle.xaxis.set_major_formatter(ticker.FuncFormatter(format_time_m_ss))

    ax_brake = axes[4]
    if "Brake" in lap_df.columns:
        normalized_brake = lap_df["Brake"] / 2.55
        ax_brake.plot(lap_df[time_col], normalized_brake, color="orange", label="Brake (%)")
        ax_brake.set_ylabel("Brake (%)")
        ax_brake.legend(loc="upper left")
        ax_brake.grid(True)
    else:
        ax_brake.text(0.5, 0.5, "No 'Brake' column", ha='center', va='center')
        ax_brake.set_ylabel("N/A")
    ax_brake.xaxis.set_major_formatter(ticker.FuncFormatter(format_time_m_ss))

    axes[-1].set_xlabel("Time (s)")
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    return fig
