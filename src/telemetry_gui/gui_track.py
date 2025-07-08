# gui_track.py
import matplotlib.pyplot as plt


def plot_track(lap_df, lap_number):
    """
    Genera un gráfico que muestra la trazada (track trace) usando las columnas
    PositionX y PositionZ.

    :param lap_df: DataFrame filtrado para la vuelta seleccionada.
    :param lap_number: Número de vuelta, para incluir en el título.
    :return: Figura de matplotlib.
    """
    fig, ax = plt.subplots(figsize=(6, 6))

    if "PositionX" not in lap_df.columns or "PositionZ" not in lap_df.columns:
        ax.text(0.5, 0.5, "No se encuentran las columnas 'PositionX' y 'PositionZ'",
                ha='center', va='center')
        return fig

    ax.plot(lap_df["PositionX"], lap_df["PositionZ"], label="Trazada", color="blue")
    ax.set_xlabel("Position X (m)")
    ax.set_ylabel("Position Z (m)")
    ax.set_title(f"Vuelta {lap_number}: Trazada en el Circuito")
    ax.legend(loc="best")
    ax.grid(True)
    return fig
