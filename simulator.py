import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import math
from datetime import datetime
from collections import deque
import threading
import queue

class DataPacket:
    """Represents a data packet from an edge device"""
    _counter = 0

    def __init__(self, device_id, data_type, size, priority, timestamp):
        DataPacket._counter += 1
        self.id = DataPacket._counter
        self.device_id = device_id
        self.data_type = data_type
        self.size = size      
        self.priority = priority  
        self.timestamp = timestamp
        self.processed_at = None
        self.processing_layer = None
        self.processing_time = 0

    def __repr__(self):
        return (f"Packet(#{self.id} Device:{self.device_id}, "
                f"Type:{self.data_type}, Size:{self.size}KB, Pri:{self.priority})")


class EdgeDevice:
    """Represents an edge device that generates data"""
    DEVICE_EMOJIS = {
        'IoT Sensor': '🌡️',
        'Camera': '📷',
        'Smart Device': '📱',
        'Industrial Sensor': '⚙️',
    }

    DATA_TYPES = {
        'IoT Sensor': ['temperature', 'humidity', 'motion', 'light'],
        'Camera': ['image', 'video_stream', 'motion_detection'],
        'Smart Device': ['status', 'telemetry', 'alert'],
        'Industrial Sensor': ['pressure', 'vibration', 'temperature', 'flow'],
    }

    SIZE_PRIORITY = {
        'temperature': (0.5, 2), 'humidity': (0.5, 2), 'motion': (1, 4),
        'light': (0.5, 1), 'image': (500, 3), 'video_stream': (2000, 4),
        'motion_detection': (10, 5), 'status': (1, 1), 'telemetry': (5, 2),
        'alert': (2, 5), 'pressure': (1, 3), 'vibration': (2, 4),
        'flow': (1, 2), 'generic': (10, 2),
    }

    def __init__(self, device_id, device_type):
        self.device_id = device_id
        self.device_type = device_type
        self.emoji = self.DEVICE_EMOJIS.get(device_type, '📟')
        self.total_data_generated = 0.0
        self.packets_sent = 0
        self.edge_count = 0
        self.fog_count = 0
        self.cloud_count = 0

    def generate_packet(self):
        types = self.DATA_TYPES.get(self.device_type, ['generic'])
        data_type = random.choice(types)
        size, priority = self.SIZE_PRIORITY.get(data_type, (10, 2))
        size = round(size * random.uniform(0.8, 1.2), 2)
        pkt = DataPacket(self.device_id, data_type, size, priority, datetime.now())
        self.total_data_generated += size
        self.packets_sent += 1
        return pkt


class ProcessingLayer:
    def __init__(self, name, capacity_kbps, latency_ms):
        self.name = name
        self.capacity = capacity_kbps
        self.latency = latency_ms
        self.packets_processed = 0
        self.total_data = 0.0
        self.total_latency = 0.0

    def process(self, packet):
        pt = round((packet.size / self.capacity) * 1000 + self.latency, 2)
        packet.processing_time = pt
        packet.processed_at = datetime.now()
        packet.processing_layer = self.name
        self.packets_processed += 1
        self.total_data += packet.size
        self.total_latency += pt
        return packet

    @property
    def avg_latency(self):
        return (self.total_latency / self.packets_processed) if self.packets_processed else 0.0


class EdgeLayer(ProcessingLayer):
    def __init__(self):
        super().__init__("Edge", capacity_kbps=100, latency_ms=5)

    @staticmethod
    def should_handle(pkt):
        if pkt.priority >= 4:
            return True
        if pkt.size < 10:
            return True
        if pkt.data_type in ('motion_detection', 'alert', 'motion'):
            return True
        return False


class FogLayer(ProcessingLayer):
    def __init__(self):
        super().__init__("Fog", capacity_kbps=1000, latency_ms=20)

    @staticmethod
    def should_handle(pkt):
        if pkt.size > 500:
            return False  
        if pkt.priority <= 2:
            return True
        if pkt.data_type in ('image', 'telemetry', 'temperature', 'humidity'):
            return True
        return True 


class CloudLayer(ProcessingLayer):
    def __init__(self):
        super().__init__("Cloud", capacity_kbps=5000, latency_ms=80)

class AnimatedDot:
    """A small circle that moves from (sx,sy) → (tx,ty) over `steps` frames."""
    def __init__(self, sx, sy, tx, ty, color, steps=20):
        self.sx, self.sy = sx, sy
        self.tx, self.ty = tx, ty
        self.color = color
        self.steps = steps
        self.step = 0
        self.alive = True

    def tick(self):
        self.step += 1
        if self.step >= self.steps:
            self.alive = False

    @property
    def pos(self):
        t = self.step / self.steps
        # ease-in-out
        t = t * t * (3 - 2 * t)
        x = self.sx + (self.tx - self.sx) * t
        y = self.sy + (self.ty - self.sy) * t
        return x, y

class Colors:
    BG       = '#0f0f1a'
    PANEL    = '#1a1a2e'
    CARD     = '#16213e'
    EDGE     = '#00e676'
    FOG      = '#448aff'
    CLOUD    = '#e040fb'
    DEVICE   = '#ffd740'
    TEXT     = '#e0e0e0'
    TEXT_DIM = '#9e9e9e'
    ACCENT   = '#00bcd4'
    DANGER   = '#ff5252'
    WARN     = '#ffab40'
    SUCCESS  = '#69f0ae'
    PRI_COLORS = {1: '#78909c', 2: '#4fc3f7', 3: '#ffd740', 4: '#ffab40', 5: '#ff5252'}


class FogEdgeSimulator:
    LAYER_COLORS = {'Edge': Colors.EDGE, 'Fog': Colors.FOG, 'Cloud': Colors.CLOUD}

    def __init__(self, root):
        self.root = root
        self.root.title("⚡ Fog / Edge / Cloud — Data Partitioning Simulator")
        self.root.configure(bg=Colors.BG)
        scr_w = self.root.winfo_screenwidth()
        scr_h = self.root.winfo_screenheight()
        win_w = min(int(scr_w * 0.92), 1500)
        win_h = min(int(scr_h * 0.88), 920)
        x_pos = (scr_w - win_w) // 2
        y_pos = max(0, (scr_h - win_h) // 2 - 20)
        self.root.geometry(f"{win_w}x{win_h}+{x_pos}+{y_pos}")
        self.root.minsize(900, 550)
        self._fs = 'small' if scr_w < 1440 else 'normal'
        self._title_font_size = 18 if self._fs == 'small' else 22
        self._section_font_size = 11 if self._fs == 'small' else 13
        self._body_font_size = 9 if self._fs == 'small' else 10
        self._stat_font_size = 10 if self._fs == 'small' else 12

        self.running = False
        self.speed = 3        
        self.edge_devices = []
        self.edge_layer = EdgeLayer()
        self.fog_layer = FogLayer()
        self.cloud_layer = CloudLayer()
        self.ui_queue = queue.Queue()
        self.update_id = None
        self.animated_dots = []
        self.throughput_history = deque(maxlen=30) 
        self._last_total = 0

        self.stats = {
            'total_packets': 0, 'edge_packets': 0, 'fog_packets': 0, 'cloud_packets': 0,
            'total_data': 0.0, 'edge_data': 0.0, 'fog_data': 0.0, 'cloud_data': 0.0,
        }

        self._build_ui()
        self._create_default_devices()
        self.root.bind('<Escape>', lambda e: self.stop_simulation())
        self.root.bind('<space>', lambda e: self.toggle_simulation())

    def _build_ui(self):
        top = tk.Frame(self.root, bg=Colors.BG)
        top.pack(fill=tk.X, padx=15, pady=(8, 2))
        tk.Label(top, text="⚡ Fog / Edge / Cloud  Data Partitioning Simulator",
                 font=('Segoe UI', self._title_font_size, 'bold'), bg=Colors.BG, fg=Colors.ACCENT).pack(side=tk.LEFT)
        tk.Label(top, text="Space = Play/Pause  |  Esc = Stop",
                 font=('Segoe UI', 9), bg=Colors.BG, fg=Colors.TEXT_DIM).pack(side=tk.RIGHT)

        body = tk.Frame(self.root, bg=Colors.BG)
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        body.columnconfigure(0, weight=0, minsize=220)  
        body.columnconfigure(1, weight=1, minsize=300)   
        body.columnconfigure(2, weight=0, minsize=240)   
        body.rowconfigure(0, weight=1)

        left = tk.Frame(body, bg=Colors.PANEL, bd=0, relief=tk.FLAT)
        left.grid(row=0, column=0, sticky='nsew', padx=(0, 6))
        self._build_left_panel(left)

        center = tk.Frame(body, bg=Colors.PANEL, bd=0)
        center.grid(row=0, column=1, sticky='nsew', padx=(0, 6))
        self._build_center_panel(center)

        right = tk.Frame(body, bg=Colors.PANEL, bd=0)
        right.grid(row=0, column=2, sticky='nsew')
        self._build_right_panel(right)

    def _build_left_panel(self, parent):
        outer_canvas = tk.Canvas(parent, bg=Colors.PANEL, highlightthickness=0)
        vsb = tk.Scrollbar(parent, orient='vertical', command=outer_canvas.yview)
        scroll_frame = tk.Frame(outer_canvas, bg=Colors.PANEL)
        scroll_frame.bind('<Configure>',
                          lambda e: outer_canvas.configure(scrollregion=outer_canvas.bbox('all')))
        outer_canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
        outer_canvas.configure(yscrollcommand=vsb.set)
        outer_canvas.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')
        
        def _on_mousewheel(e):
            outer_canvas.yview_scroll(int(-1 * (e.delta / 120)), 'units')
        outer_canvas.bind_all('<MouseWheel>', _on_mousewheel)
        def _resize_inner(e):
            outer_canvas.itemconfigure(outer_canvas.find_withtag('all')[0], width=e.width)
        outer_canvas.bind('<Configure>', _resize_inner)

        self._section_label(scroll_frame, "📡  Edge Devices")

        list_frame = tk.Frame(scroll_frame, bg=Colors.CARD)
        list_frame.pack(fill=tk.X, padx=8, pady=4)
        lb_height = 6 if self._fs == 'small' else 8
        self.device_listbox = tk.Listbox(
            list_frame, bg=Colors.CARD, fg=Colors.TEXT, font=('Consolas', 9),
            selectmode=tk.SINGLE, height=lb_height, bd=0, highlightthickness=0,
            selectbackground=Colors.ACCENT, selectforeground='#000'
        )
        self.device_listbox.pack(fill=tk.X, padx=4, pady=4)

        ctrl = tk.Frame(scroll_frame, bg=Colors.PANEL)
        ctrl.pack(fill=tk.X, padx=8, pady=4)
        tk.Label(ctrl, text="Type:", bg=Colors.PANEL, fg=Colors.TEXT_DIM,
                 font=('Segoe UI', 9)).pack(anchor='w')
        self.device_type_var = tk.StringVar(value='IoT Sensor')
        combo = ttk.Combobox(ctrl, textvariable=self.device_type_var,
                             values=['IoT Sensor', 'Camera', 'Smart Device', 'Industrial Sensor'],
                             state='readonly', width=18)
        combo.pack(fill=tk.X, pady=3)

        btn_row = tk.Frame(ctrl, bg=Colors.PANEL)
        btn_row.pack(fill=tk.X, pady=3)
        self._btn(btn_row, "➕ Add", Colors.ACCENT, self.add_device).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 3))
        self._btn(btn_row, "➖ Remove", Colors.DANGER, self.remove_device).pack(side=tk.LEFT, expand=True, fill=tk.X)

        self._section_label(scroll_frame, "⚙️  Simulation")

        sim_frame = tk.Frame(scroll_frame, bg=Colors.PANEL)
        sim_frame.pack(fill=tk.X, padx=8, pady=3)
        self.start_btn = self._btn(sim_frame, "▶  Start", Colors.SUCCESS, self.start_simulation)
        self.start_btn.pack(fill=tk.X, pady=2)
        self.stop_btn = self._btn(sim_frame, "⏸  Stop", Colors.WARN, self.stop_simulation)
        self.stop_btn.pack(fill=tk.X, pady=2)
        self.stop_btn.config(state=tk.DISABLED)
        self._btn(sim_frame, "🔄  Reset", '#78909c', self.reset_simulation).pack(fill=tk.X, pady=2)

        self._section_label(scroll_frame, "🏎️  Speed")
        speed_frame = tk.Frame(scroll_frame, bg=Colors.PANEL)
        speed_frame.pack(fill=tk.X, padx=8, pady=3)
        tk.Label(speed_frame, text="Slow", bg=Colors.PANEL, fg=Colors.TEXT_DIM,
                 font=('Segoe UI', 8)).pack(side=tk.LEFT)
        self.speed_var = tk.IntVar(value=3)
        self.speed_slider = tk.Scale(
            speed_frame, from_=1, to=10, orient=tk.HORIZONTAL, variable=self.speed_var,
            bg=Colors.PANEL, fg=Colors.ACCENT, troughcolor=Colors.CARD, highlightthickness=0,
            bd=0, sliderrelief=tk.FLAT, font=('Segoe UI', 8), length=120,
            command=lambda v: setattr(self, 'speed', int(v))
        )
        self.speed_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Label(speed_frame, text="Fast", bg=Colors.PANEL, fg=Colors.TEXT_DIM,
                 font=('Segoe UI', 8)).pack(side=tk.LEFT)

        self._section_label(scroll_frame, "📱  Per-Device Stats")
        dev_stats_frame = tk.Frame(scroll_frame, bg=Colors.CARD)
        dev_stats_frame.pack(fill=tk.X, padx=8, pady=(3, 8))
        cols = ('Device', 'Sent', 'Edge', 'Fog', 'Cloud')
        tree_height = 4 if self._fs == 'small' else 6
        self.device_tree = ttk.Treeview(dev_stats_frame, columns=cols, show='headings', height=tree_height)
        for c in cols:
            self.device_tree.heading(c, text=c)
            self.device_tree.column(c, width=40, anchor='center', minwidth=30)
        self.device_tree.column('Device', width=55, minwidth=45)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background=Colors.CARD, foreground=Colors.TEXT,
                        fieldbackground=Colors.CARD, borderwidth=0, font=('Consolas', 8))
        style.configure("Treeview.Heading", background=Colors.PANEL, foreground=Colors.ACCENT,
                        font=('Segoe UI', 8, 'bold'), borderwidth=0)
        style.map('Treeview', background=[('selected', Colors.ACCENT)])

        self.device_tree.pack(fill=tk.X)

    def _build_center_panel(self, parent):
        self._section_label(parent, "📊  Live Data Flow Visualization")

        self.canvas = tk.Canvas(parent, bg=Colors.BG, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(4, 6))

        self._section_label(parent, "📝  Recent Packets")
        log_outer = tk.Frame(parent, bg=Colors.CARD)
        log_outer.pack(fill=tk.BOTH, padx=10, pady=(0, 10), expand=False)
        sb = tk.Scrollbar(log_outer)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        log_height = 7 if self._fs == 'small' else 10
        self.packet_log = tk.Text(
            log_outer, bg=Colors.CARD, fg=Colors.TEXT, font=('Consolas', 8),
            height=log_height, yscrollcommand=sb.set, wrap=tk.WORD, bd=0, highlightthickness=0
        )
        self.packet_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=4)
        sb.config(command=self.packet_log.yview)
        self.packet_log.tag_config('edge', foreground=Colors.EDGE)
        self.packet_log.tag_config('fog', foreground=Colors.FOG)
        self.packet_log.tag_config('cloud', foreground=Colors.CLOUD)
        self.packet_log.tag_config('dim', foreground=Colors.TEXT_DIM)

    def _build_right_panel(self, parent):
        self._section_label(parent, "📈  Live Statistics")

        stats_frame = tk.Frame(parent, bg=Colors.PANEL)
        stats_frame.pack(fill=tk.X, padx=10, pady=4)
        self.stats_labels = {}
        configs = [
            ('Total Packets', 'total_packets', Colors.TEXT),
            ('Edge Packets',  'edge_packets',  Colors.EDGE),
            ('Fog Packets',   'fog_packets',   Colors.FOG),
            ('Cloud Packets', 'cloud_packets', Colors.CLOUD),
            ('Total Data KB', 'total_data',    Colors.TEXT),
            ('Edge Data KB',  'edge_data',     Colors.EDGE),
            ('Fog Data KB',   'fog_data',      Colors.FOG),
            ('Cloud Data KB', 'cloud_data',    Colors.CLOUD),
        ]
        for label_text, key, color in configs:
            row = tk.Frame(stats_frame, bg=Colors.CARD)
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=label_text, bg=Colors.CARD, fg=Colors.TEXT_DIM,
                     font=('Segoe UI', self._body_font_size), anchor='w').pack(side=tk.LEFT, padx=6, pady=3)
            vl = tk.Label(row, text="0", bg=Colors.CARD, fg=color,
                          font=('Segoe UI', self._stat_font_size, 'bold'), anchor='e')
            vl.pack(side=tk.RIGHT, padx=6, pady=3)
            self.stats_labels[key] = vl

        chart_h = 80 if self._fs == 'small' else 100
        self._section_label(parent, "⏱️  Avg Latency")
        self.latency_canvas = tk.Canvas(parent, bg=Colors.BG, highlightthickness=0, height=chart_h)
        self.latency_canvas.pack(fill=tk.X, padx=8, pady=3)

        self._section_label(parent, "📊  Distribution")
        self.dist_canvas = tk.Canvas(parent, bg=Colors.BG, highlightthickness=0, height=chart_h)
        self.dist_canvas.pack(fill=tk.X, padx=8, pady=3)

        self._section_label(parent, "📶  Throughput")
        self.throughput_canvas = tk.Canvas(parent, bg=Colors.BG, highlightthickness=0, height=chart_h)
        self.throughput_canvas.pack(fill=tk.X, padx=8, pady=(3, 8))

    def _section_label(self, parent, text):
        tk.Label(parent, text=text, font=('Segoe UI', self._section_font_size, 'bold'),
                 bg=parent['bg'], fg=Colors.ACCENT).pack(anchor='w', padx=8, pady=(6, 1))

    def _btn(self, parent, text, color, cmd):
        btn_font_size = 9 if self._fs == 'small' else 10
        b = tk.Button(parent, text=text, command=cmd, bg=color, fg='#000',
                      font=('Segoe UI', btn_font_size, 'bold'), cursor='hand2',
                      relief=tk.FLAT, padx=8, pady=4, activebackground=color)
        return b

    def _create_default_devices(self):
        for dtype, count in [('IoT Sensor', 2), ('Camera', 1), ('Smart Device', 2)]:
            for _ in range(count):
                self._add_device_internal(dtype)
        self._refresh_device_list()

    def _add_device_internal(self, dtype):
        did = f"{dtype[:3].upper()}{len(self.edge_devices)+1:03d}"
        dev = EdgeDevice(did, dtype)
        self.edge_devices.append(dev)
        return dev

    def add_device(self):
        self._add_device_internal(self.device_type_var.get())
        self._refresh_device_list()

    def remove_device(self):
        sel = self.device_listbox.curselection()
        if sel:
            self.edge_devices.pop(sel[0])
            self._refresh_device_list()
        else:
            messagebox.showwarning("No Selection", "Pehle ek device select karein")

    def _refresh_device_list(self):
        self.device_listbox.delete(0, tk.END)
        for d in self.edge_devices:
            self.device_listbox.insert(tk.END, f"{d.emoji} {d.device_id} — {d.device_type}")
        self._refresh_device_tree()

    def _refresh_device_tree(self):
        for item in self.device_tree.get_children():
            self.device_tree.delete(item)
        for d in self.edge_devices:
            self.device_tree.insert('', 'end', values=(
                d.device_id, d.packets_sent, d.edge_count, d.fog_count, d.cloud_count))

    def start_simulation(self):
        if not self.edge_devices:
            messagebox.showwarning("No Devices", "Pehle kam az kam ek device add karein")
            return
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        threading.Thread(target=self._simulation_loop, daemon=True).start()
        self._tick()

    def stop_simulation(self):
        if not self.running:
            return
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        if self.update_id:
            self.root.after_cancel(self.update_id)
            self.update_id = None

    def toggle_simulation(self):
        if self.running:
            self.stop_simulation()
        else:
            self.start_simulation()

    def reset_simulation(self):
        self.stop_simulation()
        self.stats = {k: 0 for k in self.stats}
        self.edge_layer = EdgeLayer()
        self.fog_layer = FogLayer()
        self.cloud_layer = CloudLayer()
        self.animated_dots.clear()
        self.throughput_history.clear()
        self._last_total = 0
        for d in self.edge_devices:
            d.packets_sent = 0
            d.total_data_generated = 0
            d.edge_count = d.fog_count = d.cloud_count = 0
        self.packet_log.delete('1.0', tk.END)
        self._update_stats_labels()
        self._refresh_device_tree()
        self.canvas.delete('all')
        self.latency_canvas.delete('all')
        self.dist_canvas.delete('all')
        self.throughput_canvas.delete('all')
        DataPacket._counter = 0

    def _simulation_loop(self):
        while self.running:
            if not self.edge_devices:
                time.sleep(0.1)
                continue
            dev = random.choice(self.edge_devices)
            pkt = dev.generate_packet()

            if EdgeLayer.should_handle(pkt):
                layer = self.edge_layer
                layer_name = 'edge'
                dev.edge_count += 1
            elif pkt.size > 500:
                layer = self.cloud_layer
                layer_name = 'cloud'
                dev.cloud_count += 1
            else:
                layer = self.fog_layer
                layer_name = 'fog'
                dev.fog_count += 1

            processed = layer.process(pkt)

            self.stats['total_packets'] += 1
            self.stats['total_data'] += pkt.size
            self.stats[f'{layer_name}_packets'] += 1
            self.stats[f'{layer_name}_data'] += pkt.size

            self.ui_queue.put(('log', processed, layer_name, dev.device_id))

            delay = max(0.02, 0.6 / self.speed)
            time.sleep(delay)

    def _tick(self):
        if not self.running:
            self.update_id = None
            return

        try:
            while True:
                msg = self.ui_queue.get_nowait()
                if msg[0] == 'log':
                    _, pkt, layer_name, dev_id = msg
                    self._log_packet(pkt, layer_name)
                    self._spawn_dot(dev_id, layer_name)
        except queue.Empty:
            pass

        self._advance_dots()

        self._draw_canvas()

        self._update_stats_labels()
        self._draw_latency_chart()
        self._draw_distribution()
        self._refresh_device_tree()

        cur = self.stats['total_packets']
        self.throughput_history.append(cur - self._last_total)
        self._last_total = cur
        self._draw_throughput()

        self.update_id = self.root.after(1000, self._tick)

    def _get_layer_target(self, layer_name):
        """Return (x, y) for the target layer node on the canvas."""
        w = self.canvas.winfo_width() or 700
        h = self.canvas.winfo_height() or 420
        if layer_name == 'edge':
            return w * 0.18, h * 0.75
        elif layer_name == 'fog':
            return w * 0.50, h * 0.75
        else:
            return w * 0.82, h * 0.75

    def _get_device_pos(self, dev_id):
        w = self.canvas.winfo_width() or 700
        h = self.canvas.winfo_height() or 420
        if not self.edge_devices:
            return w / 2, h * 0.15
        idx = next((i for i, d in enumerate(self.edge_devices) if d.device_id == dev_id), 0)
        spacing = w / (len(self.edge_devices) + 1)
        return spacing * (idx + 1), h * 0.18

    def _spawn_dot(self, dev_id, layer_name):
        sx, sy = self._get_device_pos(dev_id)
        tx, ty = self._get_layer_target(layer_name)
        color = self.LAYER_COLORS[layer_name.capitalize()]
        self.animated_dots.append(AnimatedDot(sx, sy, tx, ty, color, steps=18))

    def _advance_dots(self):
        for dot in self.animated_dots:
            dot.tick()
        self.animated_dots = [d for d in self.animated_dots if d.alive]

    def _draw_canvas(self):
        c = self.canvas
        c.delete('all')
        w = c.winfo_width() or 700
        h = c.winfo_height() or 420

        if self.edge_devices:
            spacing = w / (len(self.edge_devices) + 1)
            dy = h * 0.18
            for i, dev in enumerate(self.edge_devices):
                dx = spacing * (i + 1)
                r = 18
                self._rounded_rect(c, dx - r - 4, dy - r - 4, dx + r + 4, dy + r + 4,
                                    12, fill=Colors.CARD, outline=Colors.DEVICE, width=2)
                c.create_text(dx, dy - 2, text=dev.emoji, font=('Segoe UI', 14))
                c.create_text(dx, dy + r + 14, text=dev.device_id,
                              font=('Consolas', 8), fill=Colors.TEXT_DIM)

        layers_info = [
            ('Edge', Colors.EDGE, w * 0.18, h * 0.75, self.edge_layer),
            ('Fog',  Colors.FOG,  w * 0.50, h * 0.75, self.fog_layer),
            ('Cloud', Colors.CLOUD, w * 0.82, h * 0.75, self.cloud_layer),
        ]
        node_r = 50
        for name, color, lx, ly, layer_obj in layers_info:
            for gr in range(3, 0, -1):
                alpha_hex = f'{int(40 * gr):02x}'
                glow_color = color 
                c.create_oval(lx - node_r - gr * 4, ly - node_r - gr * 4,
                              lx + node_r + gr * 4, ly + node_r + gr * 4,
                              fill='', outline=color, width=1)
            c.create_oval(lx - node_r, ly - node_r, lx + node_r, ly + node_r,
                          fill=Colors.CARD, outline=color, width=3)
            c.create_text(lx, ly - 14, text=name, font=('Segoe UI', 13, 'bold'), fill=color)
            c.create_text(lx, ly + 6, text=f"{layer_obj.packets_processed} pkts",
                          font=('Consolas', 9), fill=Colors.TEXT_DIM)
            c.create_text(lx, ly + 22, text=f"{layer_obj.avg_latency:.1f}ms",
                          font=('Consolas', 9), fill=Colors.TEXT_DIM)

        if self.edge_devices:
            spacing = w / (len(self.edge_devices) + 1)
            dy = h * 0.18
            for i, dev in enumerate(self.edge_devices):
                dx = spacing * (i + 1)
                counts = [dev.edge_count, dev.fog_count, dev.cloud_count]
                max_idx = counts.index(max(counts)) if any(counts) else 0
                target_x = [w * 0.18, w * 0.50, w * 0.82][max_idx]
                target_y = h * 0.75 - node_r
                line_color = [Colors.EDGE, Colors.FOG, Colors.CLOUD][max_idx]
                c.create_line(dx, dy + 22, target_x, target_y,
                              fill=line_color, width=1, dash=(4, 4), arrow=tk.LAST)

        arrow_y = h * 0.75
        c.create_line(w * 0.18 + node_r + 8, arrow_y, w * 0.50 - node_r - 8, arrow_y,
                      fill=Colors.TEXT_DIM, width=2, arrow=tk.LAST, dash=(6, 4))
        c.create_line(w * 0.50 + node_r + 8, arrow_y, w * 0.82 - node_r - 8, arrow_y,
                      fill=Colors.TEXT_DIM, width=2, arrow=tk.LAST, dash=(6, 4))

        for dot in self.animated_dots:
            x, y = dot.pos
            r = 5
            c.create_oval(x - r, y - r, x + r, y + r, fill=dot.color, outline='')
            if dot.step > 1:
                t2 = max(0, (dot.step - 2)) / dot.steps
                t2 = t2 * t2 * (3 - 2 * t2)
                tx = dot.sx + (dot.tx - dot.sx) * t2
                ty = dot.sy + (dot.ty - dot.sy) * t2
                c.create_oval(tx - 2, ty - 2, tx + 2, ty + 2, fill=dot.color, outline='')

        c.create_text(w * 0.18, h * 0.75 + node_r + 18, text="Low Latency • Local",
                      font=('Segoe UI', 8), fill=Colors.EDGE)
        c.create_text(w * 0.50, h * 0.75 + node_r + 18, text="Aggregation • Regional",
                      font=('Segoe UI', 8), fill=Colors.FOG)
        c.create_text(w * 0.82, h * 0.75 + node_r + 18, text="Heavy Compute • Global",
                      font=('Segoe UI', 8), fill=Colors.CLOUD)

    def _rounded_rect(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1, x2 - radius, y1,
            x2, y1, x2, y1 + radius,
            x2, y2 - radius, x2, y2,
            x2 - radius, y2, x1 + radius, y2,
            x1, y2, x1, y2 - radius,
            x1, y1 + radius, x1, y1,
        ]
        return canvas.create_polygon(points, smooth=True, **kwargs)

    def _log_packet(self, pkt, layer_name):
        ts = pkt.processed_at.strftime("%H:%M:%S")
        tag = layer_name
        self.packet_log.insert(tk.END, f"[{ts}] ", 'dim')
        self.packet_log.insert(tk.END, f"{pkt.processing_layer:5s} ", tag)
        self.packet_log.insert(tk.END,
            f"│ {pkt.device_id} │ {pkt.data_type:18s} │ {pkt.size:>8.1f}KB │ {pkt.processing_time:>7.1f}ms │ Pri:{pkt.priority}\n")
        self.packet_log.see(tk.END)
        if float(self.packet_log.index('end-1c').split('.')[0]) > 200:
            self.packet_log.delete('1.0', '50.0')

    def _update_stats_labels(self):
        for key, lbl in self.stats_labels.items():
            val = self.stats[key]
            if 'data' in key:
                lbl.config(text=f"{val:,.1f}")
            else:
                lbl.config(text=str(val))

    def _draw_latency_chart(self):
        lc = self.latency_canvas
        lc.delete('all')
        cw = lc.winfo_width() or 290
        ch = lc.winfo_height() or 120

        layers = [
            ('Edge',  self.edge_layer.avg_latency,  Colors.EDGE),
            ('Fog',   self.fog_layer.avg_latency,   Colors.FOG),
            ('Cloud', self.cloud_layer.avg_latency, Colors.CLOUD),
        ]
        max_lat = max((l[1] for l in layers), default=1) or 1
        bar_w = 50
        gap = (cw - bar_w * 3) / 4

        for i, (name, lat, color) in enumerate(layers):
            x = gap + i * (bar_w + gap)
            bh = (lat / max_lat) * (ch - 40) if max_lat > 0 else 0
            y_top = ch - 20 - bh
            lc.create_rectangle(x, y_top, x + bar_w, ch - 20, fill=color, outline='')
            lc.create_text(x + bar_w / 2, y_top - 10, text=f"{lat:.1f}",
                           font=('Consolas', 9, 'bold'), fill=color)
            lc.create_text(x + bar_w / 2, ch - 8, text=name,
                           font=('Segoe UI', 9), fill=Colors.TEXT_DIM)

    def _draw_distribution(self):
        dc = self.dist_canvas
        dc.delete('all')
        cw = dc.winfo_width() or 290
        ch = dc.winfo_height() or 130
        total = self.stats['total_packets'] or 1

        layers = [
            ('Edge',  self.stats['edge_packets'],  Colors.EDGE),
            ('Fog',   self.stats['fog_packets'],   Colors.FOG),
            ('Cloud', self.stats['cloud_packets'], Colors.CLOUD),
        ]
        bar_w = 50
        gap = (cw - bar_w * 3) / 4

        for i, (name, cnt, color) in enumerate(layers):
            pct = (cnt / total) * 100
            x = gap + i * (bar_w + gap)
            bh = (pct / 100) * (ch - 45)
            y_top = ch - 22 - bh
            dc.create_rectangle(x, y_top, x + bar_w, ch - 22, fill=color, outline='')
            dc.create_text(x + bar_w / 2, y_top - 10, text=f"{pct:.0f}%",
                           font=('Consolas', 9, 'bold'), fill=color)
            dc.create_text(x + bar_w / 2, ch - 8, text=name,
                           font=('Segoe UI', 9), fill=Colors.TEXT_DIM)

    def _draw_throughput(self):
        tc = self.throughput_canvas
        tc.delete('all')
        cw = tc.winfo_width() or 290
        ch = tc.winfo_height() or 110
        data = list(self.throughput_history)
        if len(data) < 2:
            return

        max_val = max(data) or 1
        pad_x, pad_y = 30, 14
        gw = cw - pad_x * 2
        gh = ch - pad_y * 2

        for i in range(5):
            y = pad_y + gh * i / 4
            tc.create_line(pad_x, y, cw - pad_x, y, fill='#222', dash=(2, 4))
            val = max_val * (1 - i / 4)
            tc.create_text(pad_x - 4, y, text=f"{val:.0f}", anchor='e',
                           font=('Consolas', 7), fill=Colors.TEXT_DIM)

        points = []
        for i, v in enumerate(data):
            x = pad_x + (i / (len(data) - 1)) * gw
            y = pad_y + gh - (v / max_val) * gh
            points.extend([x, y])

        if len(points) >= 4:
            tc.create_line(*points, fill=Colors.ACCENT, width=2, smooth=True)
            fill_pts = [points[0], pad_y + gh] + points + [points[-2], pad_y + gh]
            tc.create_polygon(*fill_pts, fill=Colors.ACCENT, outline='', stipple='gray25')


def main():
    root = tk.Tk()
    app = FogEdgeSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
