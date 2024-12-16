import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import matplotlib.animation as animation

# --- Parametri iniziali ---
num_servos = 8  # 2 servomotori per ciascuna delle 4 zampe
initial_amplitude = 1.0  # Ampiezza iniziale della sinusoide
initial_phase = 0.0  # Fase iniziale della sinusoide

# --- Configurazione della figura ---
fig, ax = plt.subplots(4, 2, figsize=(10, 8))  # 4 zampe, 2 motori ciascuna
plt.subplots_adjust(left=0.1, bottom=0.35, right=0.9, top=0.95, hspace=0.5)

# Tempo simulato
x = np.linspace(0, 2 * np.pi, 1000)  # Dominio delle sinusoidi

# Array per memorizzare le linee delle sinusoidi e i punti di movimento
lines = []
points = []

# Genera le sinusoidi iniziali per ciascun servomotore
for i in range(num_servos):
    row = i // 2  # Riga del subplot (ci sono 4 righe per le 4 zampe)
    col = i % 2   # Colonna del subplot (ogni zampa ha 2 motori)
    
    label = 'Anca' if col == 0 else 'Piede'
    ax[row, col].set_title(f'Servo {i+1} ({label})')
    ax[row, col].set_xlim(0, 2 * np.pi)
    ax[row, col].set_ylim(-1.5, 1.5)
    
    line, = ax[row, col].plot(x, initial_amplitude * np.sin(x + initial_phase), lw=2)
    point, = ax[row, col].plot(0, 0, 'ro', markersize=8)  # Punto rosso mobile lungo la sinusoide
    
    lines.append(line)
    points.append(point)
    ax[row, col].grid(True)

# --- Aggiunta degli slider per controllare ampiezza e fase per ciascun servo ---
amp_sliders = []
phase_sliders = []

for i in range(num_servos):
    amp_slider_ax = plt.axes([0.1, 0.02 * (i + 1), 0.35, 0.015])
    phase_slider_ax = plt.axes([0.55, 0.02 * (i + 1), 0.35, 0.015])
    
    amp_slider = Slider(amp_slider_ax, f'Amp Servo {i+1}', 0.1, 2.0, valinit=initial_amplitude)
    phase_slider = Slider(phase_slider_ax, f'Fase Servo {i+1}', -np.pi, np.pi, valinit=initial_phase)
    
    amp_sliders.append(amp_slider)
    phase_sliders.append(phase_slider)

# --- Aggiunta dei pulsanti di start e stop ---
start_button_ax = plt.axes([0.35, 0.01, 0.1, 0.04])
start_button = Button(start_button_ax, 'Start')

stop_button_ax = plt.axes([0.45, 0.01, 0.1, 0.04])
stop_button = Button(stop_button_ax, 'Stop')

def start(event):
    """Funzione per avviare l'animazione."""
    ani.event_source.start()

def stop(event):
    """Funzione per interrompere l'animazione."""
    ani.event_source.stop()

start_button.on_clicked(start)
stop_button.on_clicked(stop)

# --- Funzione per aggiornare le sinusoidi ---
def update(val):
    """Aggiorna le sinusoidi in base ai valori dei cursori di ampiezza e fase."""
    for i, line in enumerate(lines):
        amplitude = amp_sliders[i].val
        phase = phase_sliders[i].val
        offset = (i // 2) * np.pi / 4  # Sfasamento tra le diverse zampe
        line.set_ydata(amplitude * np.sin(x + phase + offset))
    fig.canvas.draw_idle()

for slider in amp_sliders + phase_sliders:
    slider.on_changed(update)

# --- Funzione di animazione ciclica per simulare la camminata in avanti ---
def animate(frame):
    """Aggiorna le sinusoidi e i punti nel tempo per simulare il movimento della camminata."""
    for i, (line, point) in enumerate(zip(lines, points)):
        amplitude = amp_sliders[i].val
        phase = phase_sliders[i].val + frame * 0.1  # Incremento della fase nel tempo per simulare la camminata
        offset = (i // 2) * np.pi / 4  # Sfasamento tra le diverse zampe
        y_data = amplitude * np.sin(x + phase + offset)
        line.set_ydata(y_data)
        
        # Aggiorna la posizione del punto rosso mobile lungo la sinusoide
        t = frame % 1000  # Usato per determinare la posizione del punto mobile
        point.set_xdata(x[t])
        point.set_ydata(y_data[t])
    return lines + points

# --- Configurazione dell'animazione ---
ani = animation.FuncAnimation(fig, animate, frames=200, interval=50, blit=False, repeat=True)

plt.show()



