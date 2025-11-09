import tkinter as tk
from tkinter import ttk, messagebox
import re
import time

BLANK = "_" 

class TuringMachine:
    def __init__(self, transitions, start_state, accept_states, reject_states=None, tape=None):
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = set(accept_states)
        self.reject_states = set(reject_states or [])
        self.reset(tape or [])

    def load_input(self, w):
        self.reset(list(w))

    def reset(self, tape_list):
        self.tape = list(tape_list) if tape_list else [BLANK]
        self.head = 0
        self.state = self.start_state
        self.halted = False
        self.result = None

    def step(self):
        """Ejecuta un paso. Retorna estado ('running' | 'accept' | 'reject' | 'halt')."""
        if self.halted:
            return 'halt'

        # Aceptación o rechazo 
        if self.state in self.accept_states:
            self.halted, self.result = True, True
            return 'accept'
        if self.state in self.reject_states:
            self.halted, self.result = True, False
            return 'reject'

        # Extender cinta si es necesario
        if self.head < 0:
            self.tape.insert(0, BLANK)
            self.head = 0
        if self.head >= len(self.tape):
            self.tape.append(BLANK)

        current_symbol = self.tape[self.head] if 0 <= self.head < len(self.tape) else BLANK
        key = (self.state, current_symbol)

        if key not in self.transitions:
            # Si no hay transición rechazo por defecto
            self.halted, self.result = True, False
            return 'reject'

        write_symbol, move, next_state = self.transitions[key]

        # Escribir
        self.tape[self.head] = write_symbol
        # Mover
        if move == 'L':
            self.head -= 1
        elif move == 'R':
            self.head += 1
        # Cambiar estado
        self.state = next_state

        # aceptación/rechazo después de transición
        if self.state in self.accept_states:
            self.halted, self.result = True, True
            return 'accept'
        if self.state in self.reject_states:
            self.halted, self.result = True, False
            return 'reject'

        return 'running'


def build_example_machines():
    # 0*1*
    t1 = {}
    # En q0, los '0' se aceptan y seguimos en q0
    t1[('q0','0')] = ('0','R','q0')
    # Al ver primer '1', pasar a q1
    t1[('q0','1')] = ('1','R','q1')
    # Si BLANK en q0, aceptar (vacío o solo 0s)
    t1[('q0',BLANK)] = (BLANK,'S','qa')
    # En q1, solo 1s válidos
    t1[('q1','1')] = ('1','R','q1')
    # Si BLANK en q1, aceptar
    t1[('q1',BLANK)] = (BLANK,'S','qa')
    # Si en q1 aparece un '0', rechazo
    t1[('q1','0')] = ('0','S','qr')

    zero_one = dict(
        transitions=t1,
        start='q0',
        accept={'qa'},
        reject={'qr'},
    )

    # (ab)*
    t2 = {}
    # q0 es estado donde esperamos 'a' o BLANK para aceptar (vacío)
    t2[('q0','a')] = ('a','R','q1')
    t2[('q0',BLANK)] = (BLANK,'S','qa')  # vacío válido
    # Si en q0 llega 'b' primero, rechazo
    t2[('q0','b')] = ('b','S','qr')
    # q1 espera un 'b'
    t2[('q1','b')] = ('b','R','q0')
    # cualquier otra cosa en q1 => rechazo
    t2[('q1','a')] = ('a','S','qr')
    t2[('q1',BLANK)] = (BLANK,'S','qr')

    abab = dict(
        transitions=t2,
        start='q0',
        accept={'qa'},
        reject={'qr'},
    )

    return {
        '0*1*': zero_one,
        '(ab)*': abab,
    }


PREDEFINED_REGEX = [
    # 10 expresiones predefinidas 
    (r'(a|b)*abb',               'Sobre {a,b}: cualquier cadena que termine en "abb"'),
    (r'0*1*',                    'Cero o más 0 seguidos de cero o más 1 (incluye vacío)'),
    (r'(ab)*',                   'Secuencia de "ab" repetida (incluye vacío)'),
    (r'1(01)*0',                 'Empieza en 1, cero o más repeticiones de 01, termina en 0'),
    (r'(a|b)*a(a|b)*',           'Sobre {a,b}: contiene al menos una "a"'),
    (r'a*b*a*',                  'Cualquier número de a, luego b, luego a (cada bloque ≥0)'),
    (r'(0|1)+00(0|1)*',          'Binarias que contienen "00" en algún lugar'),
    (r'(aa|bb)*',                'Cadena de pares iguales (aa o bb) repetidos'),
    (r'(a|b){3,}',               'Largo al menos 3 sobre {a,b}'),
    (r'([ab])\1',                'Un par de símbolos iguales (aa o bb)'),
]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Máquina de Turing")
        self.geometry("1000x640")
        self.minsize(880, 560)

        self.example_machines = build_example_machines()
        self.tm = None
        self.auto_running = False
        self.auto_delay_ms = 300

        self._build_ui()

    # ---------- UI ----------
    def _build_ui(self):
        # Top frame: entrada y controles
        top = ttk.Frame(self, padding=8)
        top.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top, text="Cadena de entrada:").pack(side=tk.LEFT)
        self.entry_input = ttk.Entry(top, width=40)
        self.entry_input.pack(side=tk.LEFT, padx=6)
        self.entry_input.insert(0, "")

        ttk.Label(top, text="Máquina:").pack(side=tk.LEFT, padx=(10,0))
        self.machine_var = tk.StringVar(value='0*1*')
        machine_menu = ttk.OptionMenu(top, self.machine_var, '0*1*', *self.example_machines.keys())
        machine_menu.pack(side=tk.LEFT, padx=6)

        ttk.Button(top, text="Cargar Máquina", command=self.load_machine).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Reset", command=self.reset_machine).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Paso", command=self.step_machine).pack(side=tk.LEFT, padx=4)
        self.btn_auto = ttk.Button(top, text="Auto", command=self.toggle_auto)
        self.btn_auto.pack(side=tk.LEFT, padx=4)

        ttk.Label(top, text="Velocidad:").pack(side=tk.LEFT, padx=(16,0))
        self.speed_var = tk.IntVar(value=self.auto_delay_ms)
        speed = ttk.Scale(top, from_=50, to=1000, orient=tk.HORIZONTAL, command=self._on_speed)
        speed.set(self.auto_delay_ms)
        speed.pack(side=tk.LEFT, padx=6)

        # Estado actual
        state_frame = ttk.Frame(self, padding=(8,4))
        state_frame.pack(side=tk.TOP, fill=tk.X)
        self.state_label = ttk.Label(state_frame, text="Estado: —")
        self.state_label.pack(side=tk.LEFT)
        self.result_label = ttk.Label(state_frame, text="Resultado: —")
        self.result_label.pack(side=tk.LEFT, padx=16)

        # Cinta 
        tape_frame = ttk.LabelFrame(self, text="Cinta", padding=8)
        tape_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=4)

        self.tape_canvas = tk.Canvas(tape_frame, height=120)
        self.tape_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.tape_scroll_x = ttk.Scrollbar(tape_frame, orient=tk.HORIZONTAL, command=self.tape_canvas.xview)
        self.tape_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tape_canvas.configure(xscrollcommand=self.tape_scroll_x.set)

        # Contenedor interno para las celdas
        self.tape_inner = ttk.Frame(self.tape_canvas)
        self.tape_window = self.tape_canvas.create_window((0,0), window=self.tape_inner, anchor="nw")
        self.tape_inner.bind("<Configure>", lambda e: self._on_tape_configure())
        self.tape_canvas.bind("<Configure>", lambda e: self._on_canvas_configure())

        # Log
        log_frame = ttk.LabelFrame(self, text="Log", padding=8)
        log_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=False, padx=8, pady=4)
        self.log_text = tk.Text(log_frame, height=8, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Panel de expresiones regulares
        regex_frame = ttk.LabelFrame(self, text="Pruebas con Expresiones Regulares", padding=8)
        regex_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=4)

        self.regex_var = tk.StringVar(value=PREDEFINED_REGEX[0][0])
        ttk.Label(regex_frame, text="Regex:").pack(side=tk.LEFT)
        self.regex_menu = ttk.OptionMenu(regex_frame, self.regex_var, PREDEFINED_REGEX[0][0], *[p[0] for p in PREDEFINED_REGEX])
        self.regex_menu.pack(side=tk.LEFT, padx=6)
        ttk.Button(regex_frame, text="Probar Regex con la cadena", command=self.test_regex).pack(side=tk.LEFT, padx=6)
        self.regex_desc = ttk.Label(regex_frame, text="—")
        self.regex_desc.pack(side=tk.LEFT, padx=12)

        self.update_regex_desc()

        self.load_machine()  

    def _on_speed(self, val):
        try:
            self.auto_delay_ms = max(10, int(float(val)))
        except ValueError:
            pass

    def _on_tape_configure(self):
        self.tape_canvas.configure(scrollregion=self.tape_canvas.bbox("all"))

    def _on_canvas_configure(self):
        self.tape_canvas.itemconfig(self.tape_window, width=self.tape_canvas.winfo_width())

    def log(self, msg):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    # ---------- Máquina ----------
    def load_machine(self):
        name = self.machine_var.get()
        spec = self.example_machines.get(name)
        if not spec:
            messagebox.showerror("Error", f"No se encontró la máquina: {name}")
            return
        self.tm = TuringMachine(spec["transitions"], spec["start"], spec["accept"], spec["reject"])
        self.tm.load_input(self.entry_input.get())
        self._refresh_view(full=True)
        self.log(f"[LOAD] Máquina cargada: {name} | entrada='{self.entry_input.get()}'")

    def reset_machine(self):
        if not self.tm: return
        self.tm.load_input(self.entry_input.get())
        self.auto_running = False
        self.btn_auto.configure(text="Auto")
        self._refresh_view(full=True)
        self.log(f"[RESET] Entrada='{self.entry_input.get()}'")

    def step_machine(self):
        if not self.tm: return
        status = self.tm.step()
        self._refresh_view()
        self.log(f"[STEP] estado={self.tm.state} head={self.tm.head} status={status}")
        if status in ('accept','reject'):
            self.auto_running = False
            self.btn_auto.configure(text="Auto")
            messagebox.showinfo("Resultado", "ACEPTADA " if self.tm.result else "RECHAZADA ")

    def toggle_auto(self):
        if not self.tm: return
        self.auto_running = not self.auto_running
        self.btn_auto.configure(text=("Auto ⏸" if self.auto_running else "Auto"))
        if self.auto_running:
            self._auto_loop()

    def _auto_loop(self):
        if not self.auto_running or not self.tm:
            return
        status = self.tm.step()
        self._refresh_view()
        if status in ('accept','reject'):
            self.auto_running = False
            self.btn_auto.configure(text="Auto")
            messagebox.showinfo("Resultado", "ACEPTADA " if self.tm.result else "RECHAZADA ")
            return
        # programar siguiente paso
        self.after(self.auto_delay_ms, self._auto_loop)

    # ---------- Regex ----------
    def update_regex_desc(self, *_):
        sel = self.regex_var.get()
        for pat, desc in PREDEFINED_REGEX:
            if pat == sel:
                self.regex_desc.configure(text=desc)
                return
        self.regex_desc.configure(text="—")

    def test_regex(self):
        s = self.entry_input.get()
        pat = self.regex_var.get()
        self.update_regex_desc()
        ok = re.fullmatch(pat, s) is not None
        self.log(f"[REGEX] '{s}' ~ /{pat}/  ->  {'ACEPTADA' if ok else 'RECHAZADA'}")
        messagebox.showinfo("Regex", f"Cadena: '{s}'\nPatrón: {pat}\n\nResultado: {'ACEPTADA ' if ok else 'RECHAZADA '}")

    # ---------- cinta ----------
    def _refresh_view(self, full=False):
        if not self.tm:
            return
        # Estado
        self.state_label.configure(text=f"Estado: {self.tm.state}")
        res_text = "—"
        if self.tm.halted:
            res_text = "ACEPTADA" if self.tm.result else "RECHAZADA"
        self.result_label.configure(text=f"Resultado: {res_text}")

        # Asegurar visibilidad de head en cinta lógica
        if self.tm.head < 0:
            self.tm.tape.insert(0, BLANK)
            self.tm.head = 0
        if self.tm.head >= len(self.tm.tape):
            self.tm.tape.append(BLANK)

        # Redibujar celdas
        for w in self.tape_inner.winfo_children():
            w.destroy()

        # margen a ambos lados 
        left_pad = 3
        right_pad = 3
        symbols = [BLANK]*left_pad + self.tm.tape + [BLANK]*right_pad
        head_index = left_pad + self.tm.head

        cell_w = 36
        for i, sym in enumerate(symbols):
            frame = ttk.Frame(self.tape_inner, borderwidth=1, relief=tk.SOLID)
            frame.grid(row=0, column=i, padx=1, pady=6, sticky="nsew")
            lbl = ttk.Label(frame, text=sym, width=3, anchor="center", font=("Consolas", 16))
            lbl.pack(padx=6, pady=10)
            if i == head_index:
                frame.configure(style="Head.TFrame")
                # Triángulo indicador
                tri = ttk.Label(self.tape_inner, text="▲", anchor="center")
                tri.grid(row=1, column=i, pady=(0,4))

        # estilos
        style = ttk.Style()
        style.configure("Head.TFrame", background="#d1ecf1")

        self.tape_inner.update_idletasks()
        self._on_tape_configure()

        # Auto-scroll para centrar el cabezal
        x = max(0, (head_index * (cell_w+2)) - self.tape_canvas.winfo_width()//2)
        self.tape_canvas.xview_moveto(x / max(1, self.tape_canvas.bbox("all")[2]))


def main():
    app = App()
    # actualizar descripción cuando cambie el menú de regex
    app.regex_var.trace_add("write", app.update_regex_desc)
    app.mainloop()

if __name__ == "__main__":
    main()
