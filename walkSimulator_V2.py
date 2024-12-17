import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import matplotlib.animation as animation

# --- Parametri iniziali ---
NUM_SERVOS = 8  # 2 servomotori per ciascuna delle 4 zampe
INITIAL_AMPLITUDE = 1.0  # Ampiezza iniziale della sinusoide
INITIAL_PHASE = 0.0  # Fase iniziale della sinusoide
FRAMES = 200  # Numero di frame per animazione
INTERVAL = 50  # Intervallo di aggiornamento dell'animazione (ms)

# --- Configurazione della figura ---
fig, ax = plt.subplots(4, 2, figsize=(10, 8))  # 4 zampe, 2 motori ciascuna
plt.subplots_adjust(left=0.1, bottom=0.45, right=0.9, top=0.95, hspace=0.5)

# --- Riquadro per mostrare il frame corrente ---
frame_text_ax = plt.axes([0.85, 0.95, 0.1, 0.04])
frame_text = frame_text_ax.text(0.5, 0.5, 'Frame: 0', ha='center', va='center', transform=frame_text_ax.transAxes)
frame_text_ax.axis('off')

# --- Tempo simulato ---
x = np.linspace(0, 2 * np.pi, 1000)  # Dominio delle sinusoidi

# --- Linee e punti di movimento ---
lines = []
points = []

for i in range(NUM_SERVOS):
    row, col = divmod(i, 2)  # Determina la posizione della sottotrama
    label = 'Anca' if col == 0 else 'Piede'
    
    ax[row, col].set_title(f'Servo {i+1} ({label})')
    ax[row, col].set_xlim(0, 2 * np.pi)
    ax[row, col].set_ylim(-1.5, 1.5)
    ax[row, col].grid(True)
    
    line, = ax[row, col].plot(x, INITIAL_AMPLITUDE * np.sin(x + INITIAL_PHASE), lw=2)
    point, = ax[row, col].plot(0, 0, 'ro', markersize=8)  
    
    lines.append(line)
    points.append(point)

# --- Sliders per controllare ampiezza e fase per ciascun servo ---
amp_sliders = []
phase_sliders = []

for i in range(NUM_SERVOS):
    amp_slider_ax = plt.axes([0.1, 0.02 * (i + 1), 0.35, 0.015])
    phase_slider_ax = plt.axes([0.55, 0.02 * (i + 1), 0.35, 0.015])
    
    amp_slider = Slider(amp_slider_ax, f'Amp Servo {i+1}', 0.1, 2.0, valinit=INITIAL_AMPLITUDE)
    phase_slider = Slider(phase_slider_ax, f'Fase Servo {i+1}', -np.pi, np.pi, valinit=INITIAL_PHASE)
    
    amp_sliders.append(amp_slider)
    phase_sliders.append(phase_slider)

# --- Pulsanti di controllo ---
buttons = {
    'start': Button(plt.axes([0.15, 0.01, 0.1, 0.04]), 'Start'),
    'stop': Button(plt.axes([0.26, 0.01, 0.1, 0.04]), 'Stop'),
    'back': Button(plt.axes([0.37, 0.01, 0.1, 0.04]), 'Back'),
    'right': Button(plt.axes([0.48, 0.01, 0.1, 0.04]), 'Right'),
    'left': Button(plt.axes([0.59, 0.01, 0.1, 0.04]), 'Left'),
    'forward': Button(plt.axes([0.7, 0.01, 0.1, 0.04]), 'Forward')
}

ani = None  # Variabile globale per l'animazione

def start(event):
    global ani
    if ani is not None:
        ani.event_source.start()

def stop(event):
    global ani
    if ani is not None:
        ani.event_source.stop()

def back(event):
    start_animation(animate_backward)

def right(event):
    start_animation(animate_right)

def left(event):
    start_animation(animate_left)

def forward(event):
    start_animation(animate)

def start_animation(animate_func):
    global ani
    if ani is not None:
        ani.event_source.stop()
    ani = animation.FuncAnimation(fig, animate_func, frames=FRAMES, interval=INTERVAL, blit=False, repeat=True)

def update(val):
    for i, line in enumerate(lines):
        amplitude = amp_sliders[i].val
        phase = phase_sliders[i].val
        offset = (i // 2) * np.pi / 4
        line.set_ydata(amplitude * np.sin(x + phase + offset))
    fig.canvas.draw_idle()

for slider in amp_sliders + phase_sliders:
    slider.on_changed(update)

# --- Funzioni di animazione ---
def animate(frame):
    frame_text.set_text(f'Frame: {frame}')
    return update_movement(frame, 1, 0)

def animate_backward(frame):
    frame_text.set_text(f'Frame: {frame}')
    return update_movement(frame, -1, 0)

def animate_right(frame):
    frame_text.set_text(f'Frame: {frame}')
    return update_movement(frame, 1, np.pi / 2)

def animate_left(frame):
    frame_text.set_text(f'Frame: {frame}')
    return update_movement(frame, 1, -np.pi / 2)

def update_movement(frame, direction=1, lateral_shift=0):
    for i, (line, point) in enumerate(zip(lines, points)):
        amplitude = amp_sliders[i].val
        phase = phase_sliders[i].val + frame * 0.1 * direction + (i % 2) * lateral_shift
        offset = (i // 2) * np.pi / 4
        y_data = amplitude * np.sin(x + phase + offset)
        line.set_ydata(y_data)
        
        t = frame % 1000
        point.set_xdata(x[t])
        point.set_ydata(y_data[t])
    return lines + points

# --- Collegamenti ai pulsanti ---
buttons['start'].on_clicked(start)
buttons['stop'].on_clicked(stop)
buttons['back'].on_clicked(back)
buttons['right'].on_clicked(right)
buttons['left'].on_clicked(left)
buttons['forward'].on_clicked(forward)

ani = animation.FuncAnimation(fig, animate, frames=FRAMES, interval=INTERVAL, blit=False, repeat=True)

plt.show()
