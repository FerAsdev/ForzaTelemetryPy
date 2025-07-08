# gui_suspension.py
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def format_time_m_ss(x, pos):
    minutes = int(x // 60)
    seconds = int(x % 60)
    if minutes == 0:
        return f"{seconds}"
    else:
        return f"{minutes}.{seconds:02d}"

def plot_suspension_behavior(lap_df, lap_number):
    fig, ax = plt.subplots(figsize=(6,4))
    time_col = "RelativeTime"
    if time_col not in lap_df.columns:
        lap_df["RelativeTime"] = range(len(lap_df))
    suspensions = [
        ("SuspensionTravelMetersFrontLeft", "Front Left"),
        ("SuspensionTravelMetersFrontRight", "Front Right"),
        ("SuspensionTravelMetersRearLeft", "Rear Left"),
        ("SuspensionTravelMetersRearRight", "Rear Right")
    ]
    for col, label in suspensions:
        if col in lap_df.columns:
            ax.plot(lap_df[time_col], lap_df[col], label=label)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Suspension Travel (m)")
    ax.set_title(f"Lap {lap_number}: Suspension Behavior")
    ax.grid(True)
    ax.legend(loc="upper right")
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_time_m_ss))
    return fig
