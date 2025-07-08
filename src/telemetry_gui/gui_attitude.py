# gui_attitude.py
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import mplcursors  # Importamos mplcursors

def format_time_m_ss(x, pos):
    minutes = int(x // 60)
    seconds = int(x % 60)
    if minutes == 0:
        return f"{seconds}"
    else:
        return f"{minutes}.{seconds:02d}"

def plot_attitude(lap_df, lap_number):
    fig, axes = plt.subplots(nrows=3, ncols=1, sharex=True, figsize=(8,6))
    fig.suptitle(f"Attitude (Yaw, Pitch, Roll) - Lap {lap_number}")

    # Gráfico de Yaw
    if "Yaw" in lap_df.columns:
        line_yaw, = axes[0].plot(lap_df["RelativeTime"], lap_df["Yaw"], color="blue", label="Yaw (rad)")
        axes[0].set_ylabel("Yaw (rad)")
        axes[0].legend(loc="upper left")
        axes[0].grid(True)
        # Agregamos cursor interactivo para Yaw
        mplcursors.cursor(line_yaw, hover=True)
    else:
        axes[0].text(0.5, 0.5, "No hay datos de Yaw", ha="center", va="center")

    # Gráfico de Pitch
    if "Pitch" in lap_df.columns:
        line_pitch, = axes[1].plot(lap_df["RelativeTime"], lap_df["Pitch"], color="green", label="Pitch (rad)")
        axes[1].set_ylabel("Pitch (rad)")
        axes[1].legend(loc="upper left")
        axes[1].grid(True)
        mplcursors.cursor(line_pitch, hover=True)
    else:
        axes[1].text(0.5, 0.5, "No hay datos de Pitch", ha="center", va="center")

    # Gráfico de Roll
    if "Roll" in lap_df.columns:
        line_roll, = axes[2].plot(lap_df["RelativeTime"], lap_df["Roll"], color="red", label="Roll (rad)")
        axes[2].set_ylabel("Roll (rad)")
        axes[2].set_xlabel("Tiempo (s)")
        axes[2].legend(loc="upper left")
        axes[2].grid(True)
        mplcursors.cursor(line_roll, hover=True)
    else:
        axes[2].text(0.5, 0.5, "No hay datos de Roll", ha="center", va="center")

    axes[-1].xaxis.set_major_formatter(ticker.FuncFormatter(format_time_m_ss))
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    return fig
