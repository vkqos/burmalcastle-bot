import subprocess
import time
import sys
import os
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import urllib.request

# Функции сетапа
def install_python_if_needed():
    print("Проверка наличия Python...")
    try:
        subprocess.run(["python", "--version"], check=True, capture_output=True)
        print("Python уже установлен")
        return True
    except:
        print("Python не найден. Скачиваю Python 3.12...")
        python_installer = "python_installer.exe"
        urllib.request.urlretrieve("https://www.python.org/ftp/python/3.12.0/python-3.12.0.exe", python_installer)
        subprocess.run([python_installer, "/quiet", "InstallAllUsers=1", "PrependPath=1"])
        time.sleep(30)
        os.remove(python_installer)
        return True

def install_libraries():
    print("Устанавливаю библиотеки...")
    libraries = ["pyautogui", "pygetwindow", "pillow", "pyscreeze"]
    for lib in libraries:
        print(f"Устанавливаю {lib}...")
        subprocess.run([sys.executable, "-m", "pip", "install", lib])

def find_dnplayer_path():
    print("Поиск dnplayer.exe...")
    for root, dirs, files in os.walk("C:\\"):
        try:
            if "dnplayer.exe" in files:
                path = os.path.join(root, "dnplayer.exe")
                print(f"Найдено: {path}")
                return path
        except:
            continue
    return None

# Основное приложение
class ModernBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hustle Castle Bot")
        self.root.geometry("500x800")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f0f0f")
        
        self.colors = {
            "bg": "#0f0f0f",
            "card": "#1e1e1e",
            "accent": "#6c63ff",
            "accent_hover": "#5a52d5",
            "success": "#00b894",
            "warning": "#fdcb6e",
            "danger": "#ff7675",
            "text": "#ffffff",
            "text_secondary": "#b2bec3"
        }
        
        self.running = False
        self.paused = False
        self.mode = "arena"
        self.arena_round = 0
        
        self.arena_file = "arena_coords.json"
        self.dnplayer_file = "dnplayer_coords.json"
        self.cathedral_file = "cathedral_coords.json"
        self.dungeon_file = "dungeon_coords.json"
        self.bay_file = "bay_coords.json"
        
        self.arena_coords = self.load_json(self.arena_file)
        self.dnplayer_coords = self.load_json(self.dnplayer_file)
        self.cathedral_coords = self.load_json(self.cathedral_file)
        self.dungeon_coords = self.load_json(self.dungeon_file)
        self.bay_coords = self.load_json(self.bay_file)
        
        self.setup_ui()
        
    def setup_ui(self):
        title_frame = tk.Frame(self.root, bg=self.colors["bg"], height=60)
        title_frame.pack(fill="x", pady=(20, 10))
        
        title = tk.Label(title_frame, text="HUSTLE CASTLE BOT", font=("Segoe UI", 18, "bold"), 
                        bg=self.colors["bg"], fg=self.colors["accent"])
        title.pack()
        
        subtitle = tk.Label(title_frame, text="Автоматический фарминг", font=("Segoe UI", 10), 
                          bg=self.colors["bg"], fg=self.colors["text_secondary"])
        subtitle.pack()
        
        self.create_mode_card()
        self.create_control_card()
        self.create_status_card()
        self.create_ldplayer_card()
        
        self.coords_notebook = ttk.Notebook(self.root)
        self.coords_notebook.pack(fill="x", padx=20, pady=10)
        
        style = ttk.Style()
        style.configure("TNotebook", background=self.colors["card"], borderwidth=0)
        style.configure("TNotebook.Tab", background=self.colors["bg"], foreground=self.colors["text"], padding=[15, 5])
        style.map("TNotebook.Tab", background=[("selected", self.colors["accent"])])
        
        self.create_arena_tab()
        self.create_cathedral_tab()
        self.create_dungeon_tab()
        self.create_bay_tab()
    
    def create_mode_card(self):
        card = tk.Frame(self.root, bg=self.colors["card"], relief="flat", bd=0)
        card.pack(fill="x", padx=20, pady=10)
        
        tk.Label(card, text="🎮 РЕЖИМ", font=("Segoe UI", 10, "bold"), 
                bg=self.colors["card"], fg=self.colors["text_secondary"]).pack(anchor="w", padx=15, pady=(10, 5))
        
        modes_frame = tk.Frame(card, bg=self.colors["card"])
        modes_frame.pack(pady=10, padx=15)
        
        self.mode_var = tk.StringVar(value="arena")
        modes = [("⚔ Арена", "arena"), ("⛪ Собор", "cathedral"), ("🏰 Подземелье", "dungeon"), ("⚓ Бухта", "bay")]
        
        self.mode_buttons = []
        for i, (text, value) in enumerate(modes):
            btn = tk.Button(modes_frame, text=text, font=("Segoe UI", 10), 
                          bg=self.colors["accent"] if value == "arena" else self.colors["bg"],
                          fg=self.colors["text"], relief="flat", bd=0, padx=15, pady=8,
                          command=lambda v=value: self.select_mode(v))
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
            self.mode_buttons.append(btn)
        
        modes_frame.grid_columnconfigure(0, weight=1)
        modes_frame.grid_columnconfigure(1, weight=1)
    
    def select_mode(self, mode):
        self.mode = mode
        self.mode_var.set(mode)
        for btn in self.mode_buttons:
            btn.config(bg=self.colors["bg"])
        for btn in self.mode_buttons:
            if mode in btn.cget("text").lower():
                btn.config(bg=self.colors["accent"])
                break
    
    def create_control_card(self):
        card = tk.Frame(self.root, bg=self.colors["card"], relief="flat", bd=0)
        card.pack(fill="x", padx=20, pady=10)
        
        tk.Label(card, text="🎮 УПРАВЛЕНИЕ", font=("Segoe UI", 10, "bold"), 
                bg=self.colors["card"], fg=self.colors["text_secondary"]).pack(anchor="w", padx=15, pady=(10, 5))
        
        controls = tk.Frame(card, bg=self.colors["card"])
        controls.pack(pady=10, padx=15)
        
        self.start_btn = self.create_button(controls, "▶ СТАРТ", self.start_bot, self.colors["success"])
        self.start_btn.pack(side="left", expand=True, fill="x", padx=5)
        
        self.pause_btn = self.create_button(controls, "⏸ ПАУЗА", self.pause_bot, self.colors["warning"], disabled=True)
        self.pause_btn.pack(side="left", expand=True, fill="x", padx=5)
        
        self.stop_btn = self.create_button(controls, "⏹ СТОП", self.stop_bot, self.colors["danger"], disabled=True)
        self.stop_btn.pack(side="left", expand=True, fill="x", padx=5)
    
    def create_button(self, parent, text, command, color, disabled=False):
        btn = tk.Button(parent, text=text, font=("Segoe UI", 10, "bold"),
                       bg=color, fg="white", relief="flat", bd=0,
                       padx=15, pady=8, cursor="hand2",
                       activebackground=self.colors["accent_hover"],
                       activeforeground="white", command=command)
        if disabled:
            btn.config(state="disabled", bg=self.colors["text_secondary"])
        return btn
    
    def create_status_card(self):
        card = tk.Frame(self.root, bg=self.colors["card"], relief="flat", bd=0)
        card.pack(fill="x", padx=20, pady=10)
        
        tk.Label(card, text="📊 СТАТУС", font=("Segoe UI", 10, "bold"), 
                bg=self.colors["card"], fg=self.colors["text_secondary"]).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.status_frame = tk.Frame(card, bg=self.colors["card"], height=60)
        self.status_frame.pack(fill="x", padx=15, pady=10)
        
        self.status_icon = tk.Label(self.status_frame, text="⭕", font=("Segoe UI", 14),
                                   bg=self.colors["card"], fg=self.colors["danger"])
        self.status_icon.pack(side="left", padx=(0, 10))
        
        self.status_label = tk.Label(self.status_frame, text="Остановлен", font=("Segoe UI", 11),
                                    bg=self.colors["card"], fg=self.colors["text_secondary"])
        self.status_label.pack(side="left")
        
        self.progress_label = tk.Label(card, text="", font=("Segoe UI", 9),
                                      bg=self.colors["card"], fg=self.colors["accent"])
        self.progress_label.pack(pady=(0, 10))
    
    def create_ldplayer_card(self):
        card = tk.Frame(self.root, bg=self.colors["card"], relief="flat", bd=0)
        card.pack(fill="x", padx=20, pady=10)
        
        tk.Label(card, text="📱 LDPLAYER", font=("Segoe UI", 10, "bold"), 
                bg=self.colors["card"], fg=self.colors["text_secondary"]).pack(anchor="w", padx=15, pady=(10, 5))
        
        coords = self.dnplayer_coords.get("hustle_castle", {"x": 0, "y": 0})
        coord_text = f"({coords['x']}, {coords['y']})" if coords['x'] != 0 else "не установлены"
        
        self.dnplayer_label = tk.Label(card, text=f"📍 Координаты игры: {coord_text}", 
                                      font=("Segoe UI", 9), bg=self.colors["card"], fg=self.colors["text_secondary"])
        self.dnplayer_label.pack(anchor="w", padx=15, pady=(0, 5))
        
        btn_frame = tk.Frame(card, bg=self.colors["card"])
        btn_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        set_coord_btn = tk.Button(btn_frame, text="🎯 Установить координаты игры", font=("Segoe UI", 9),
                                 bg=self.colors["bg"], fg=self.colors["text"], relief="flat", bd=0,
                                 padx=10, pady=5, cursor="hand2", command=self.set_dnplayer_coordinate)
        set_coord_btn.pack(side="left", padx=(0, 5))
        
        launch_btn = tk.Button(btn_frame, text="🚀 Запустить игру", font=("Segoe UI", 9),
                              bg=self.colors["bg"], fg=self.colors["text"], relief="flat", bd=0,
                              padx=10, pady=5, cursor="hand2", command=self.launch_game)
        launch_btn.pack(side="left")
    
    def create_arena_tab(self):
        tab = tk.Frame(self.coords_notebook, bg=self.colors["card"])
        self.coords_notebook.add(tab, text="⚔ Арена")
        
        canvas = tk.Canvas(tab, bg=self.colors["card"], highlightthickness=0)
        scrollbar = tk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=self.colors["card"])
        
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Label(scrollable, text="ОСНОВНЫЕ КНОПКИ", font=("Segoe UI", 10, "bold"),
                bg=self.colors["card"], fg=self.colors["accent"]).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.arena_btns = {}
        arena_buttons = [("Вход на арену", "entry"), ("Участвовать", "participate"), 
                        ("Подтвердить", "confirm"), ("Бой", "fight"), ("Забрать награду", "reward"), ("Домой", "home")]
        
        for text, key in arena_buttons:
            frame = tk.Frame(scrollable, bg=self.colors["card"])
            frame.pack(fill="x", padx=15, pady=5)
            
            coords = self.arena_coords.get(key, {"x": 0, "y": 0})
            status = "✅" if coords['x'] != 0 else "❌"
            
            label = tk.Label(frame, text=f"{status} {text}:", font=("Segoe UI", 10),
                            bg=self.colors["card"], fg=self.colors["text"], width=15, anchor="w")
            label.pack(side="left")
            
            coord_label = tk.Label(frame, text=f"({coords['x']}, {coords['y']})" if coords['x'] != 0 else "не выбрано",
                                  font=("Segoe UI", 9), bg=self.colors["card"], fg=self.colors["text_secondary"])
            coord_label.pack(side="left", padx=10)
            
            set_btn = tk.Button(frame, text="Установить", font=("Segoe UI", 9),
                               bg=self.colors["bg"], fg=self.colors["accent"], relief="flat", bd=0,
                               cursor="hand2", command=lambda k=key, cl=coord_label, lb=label: self.set_arena_coord(k, cl, lb))
            set_btn.pack(side="right")
            
            self.arena_btns[key] = {"label": coord_label, "status": label}
        
        tk.Label(scrollable, text="ПРОТИВНИКИ (от 10 до 5)", font=("Segoe UI", 10, "bold"),
                bg=self.colors["card"], fg=self.colors["accent"]).pack(anchor="w", padx=15, pady=(15, 5))
        
        opponents_frame = tk.Frame(scrollable, bg=self.colors["card"])
        opponents_frame.pack(pady=10, padx=15)
        
        self.opponent_btns = {}
        
        for i in range(5, 11):
            coords = self.arena_coords.get(f"opponent_{i}", {"x": 0, "y": 0})
            status = "✅" if coords['x'] != 0 else "❌"
            
            btn = tk.Button(opponents_frame, text=f"{status} {i}", font=("Segoe UI", 9),
                           bg=self.colors["bg"], fg=self.colors["text"], relief="flat", bd=0,
                           width=5, cursor="hand2",
                           command=lambda num=i: self.set_opponent_coord(num))
            btn.grid(row=(i-5)//3, column=(i-5)%3, padx=3, pady=3)
            self.opponent_btns[i] = btn
        
        save_btn = tk.Button(scrollable, text="💾 СОХРАНИТЬ ВСЕ НАСТРОЙКИ АРЕНЫ", font=("Segoe UI", 10),
                            bg=self.colors["accent"], fg="white", relief="flat", bd=0,
                            padx=15, pady=8, cursor="hand2", command=self.save_arena_coords)
        save_btn.pack(pady=(15, 20))
    
    def create_cathedral_tab(self):
        tab = tk.Frame(self.coords_notebook, bg=self.colors["card"])
        self.coords_notebook.add(tab, text="⛪ Собор")
        self.create_simple_tab(tab, self.cathedral_coords, "cathedral", self.cathedral_file)
    
    def create_dungeon_tab(self):
        tab = tk.Frame(self.coords_notebook, bg=self.colors["card"])
        self.coords_notebook.add(tab, text="🏰 Подземелье")
        self.create_simple_tab(tab, self.dungeon_coords, "dungeon", self.dungeon_file)
    
    def create_bay_tab(self):
        tab = tk.Frame(self.coords_notebook, bg=self.colors["card"])
        self.coords_notebook.add(tab, text="⚓ Бухта")
        self.create_simple_tab(tab, self.bay_coords, "bay", self.bay_file)
    
    def create_simple_tab(self, tab, coords_dict, mode_name, save_file):
        frame = tk.Frame(tab, bg=self.colors["card"])
        frame.pack(expand=True, fill="both")
        
        tk.Label(frame, text=f"НАСТРОЙКА {mode_name.upper()}", font=("Segoe UI", 12, "bold"),
                bg=self.colors["card"], fg=self.colors["accent"]).pack(pady=20)
        
        info_frame = tk.Frame(frame, bg=self.colors["card"])
        info_frame.pack(pady=20)
        
        coords = coords_dict.get("entry", {"x": 0, "y": 0})
        status = "✅" if coords['x'] != 0 else "❌"
        
        tk.Label(info_frame, text=f"{status} Кнопка входа:", font=("Segoe UI", 11),
                bg=self.colors["card"], fg=self.colors["text"]).pack()
        
        coord_label = tk.Label(info_frame, text=f"({coords['x']}, {coords['y']})" if coords['x'] != 0 else "не выбрано",
                              font=("Segoe UI", 10), bg=self.colors["card"], fg=self.colors["text_secondary"])
        coord_label.pack(pady=5)
        
        set_btn = tk.Button(info_frame, text="Установить координаты", font=("Segoe UI", 10),
                           bg=self.colors["accent"], fg="white", relief="flat", bd=0,
                           padx=15, pady=8, cursor="hand2",
                           command=lambda: self.set_simple_coord(mode_name, save_file, coord_label))
        set_btn.pack(pady=10)
    
    def set_simple_coord(self, mode_name, save_file, label):
        self.current_simple_mode = mode_name
        self.current_simple_file = save_file
        self.current_simple_label = label
        self.update_status(f"Наведись на кнопку '{mode_name}' и нажми Enter", "waiting")
        self.root.bind('<Return>', self.on_simple_coord_set)
    
    def on_simple_coord_set(self, event):
        pos = pyautogui.position()
        coords = self.load_json(self.current_simple_file)
        coords["entry"] = {"x": pos.x, "y": pos.y}
        self.save_json(self.current_simple_file, coords)
        
        if self.current_simple_mode == "cathedral":
            self.cathedral_coords = coords
        elif self.current_simple_mode == "dungeon":
            self.dungeon_coords = coords
        elif self.current_simple_mode == "bay":
            self.bay_coords = coords
        
        self.current_simple_label.config(text=f"({pos.x}, {pos.y})")
        self.update_status(f"Координаты для {self.current_simple_mode} сохранены!", "success")
        self.root.unbind('<Return>')
    
    def set_arena_coord(self, key, label, status_label):
        self.current_key = key
        self.current_label = label
        self.current_status_label = status_label
        self.update_status(f"Наведись на кнопку '{key}' и нажми Enter", "waiting")
        self.root.bind('<Return>', self.on_arena_coord_set)
    
    def on_arena_coord_set(self, event):
        pos = pyautogui.position()
        self.arena_coords[self.current_key] = {"x": pos.x, "y": pos.y}
        self.current_label.config(text=f"({pos.x}, {pos.y})")
        self.current_status_label.config(text=f"✅ {self.current_status_label.cget('text')[2:]}")
        self.update_status(f"Координаты для '{self.current_key}' сохранены!", "success")
        self.root.unbind('<Return>')
    
    def set_opponent_coord(self, num):
        self.current_opponent = num
        self.update_status(f"Наведись на противника {num} и нажми Enter", "waiting")
        self.root.bind('<Return>', self.on_opponent_coord_set)
    
    def on_opponent_coord_set(self, event):
        pos = pyautogui.position()
        self.arena_coords[f"opponent_{self.current_opponent}"] = {"x": pos.x, "y": pos.y}
        self.opponent_btns[self.current_opponent].config(text=f"✅ {self.current_opponent}")
        self.update_status(f"Координаты противника {self.current_opponent} сохранены!", "success")
        self.root.unbind('<Return>')
    
    def set_dnplayer_coordinate(self):
        self.update_status("Наведись на иконку Hustle Castle в LDPlayer и нажми Enter", "waiting")
        self.root.bind('<Return>', self.on_dnplayer_coord_set)
    
    def on_dnplayer_coord_set(self, event):
        pos = pyautogui.position()
        self.dnplayer_coords["hustle_castle"] = {"x": pos.x, "y": pos.y}
        self.save_json(self.dnplayer_file, self.dnplayer_coords)
        self.dnplayer_label.config(text=f"📍 Координаты игры: ({pos.x}, {pos.y})")
        self.update_status(f"Координаты сохранены! ({pos.x}, {pos.y})", "success")
        self.root.unbind('<Return>')
    
    def save_arena_coords(self):
        self.save_json(self.arena_file, self.arena_coords)
        self.update_status("Настройки арены сохранены!", "success")
    
    def load_json(self, filename):
        if os.path.exists(filename):
            with open(filename, "r") as f:
                return json.load(f)
        return {}
    
    def save_json(self, filename, data):
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
    
    def launch_game(self):
        dnplayer_path = find_dnplayer_path()
        if not dnplayer_path:
            self.update_status("Ошибка: не найден dnplayer.exe!", "error")
            return
        
        import pyautogui
        import pygetwindow as gw
        
        subprocess.Popen([dnplayer_path])
        self.update_status("Запускаю LDPlayer...", "waiting")
        
        def wait_and_click():
            time.sleep(25)
            for win in gw.getAllWindows():
                if "ldplayer" in win.title.lower():
                    win.activate()
                    break
            time.sleep(2)
            pyautogui.hotkey('f11')
            time.sleep(3)
            coords = self.dnplayer_coords.get("hustle_castle", {"x": 0, "y": 0})
            if coords['x'] != 0:
                pyautogui.doubleClick(coords['x'], coords['y'])
                self.update_status("Hustle Castle запущен!", "success")
            else:
                self.update_status("Координаты не установлены!", "error")
        
        threading.Thread(target=wait_and_click, daemon=True).start()
    
    def update_status(self, message, status_type="info"):
        icons = {"info": "ℹ️", "success": "✅", "error": "❌", "waiting": "⏳", "working": "🔄"}
        colors = {"info": self.colors["text_secondary"], "success": self.colors["success"],
                 "error": self.colors["danger"], "waiting": self.colors["warning"], "working": self.colors["accent"]}
        
        self.status_icon.config(text=icons.get(status_type, "⭕"))
        self.status_label.config(text=message, fg=colors.get(status_type, self.colors["text_secondary"]))
        self.root.update()
    
    def start_bot(self):
        self.running = True
        self.paused = False
        self.arena_round = 0
        self.start_btn.config(state="disabled", bg=self.colors["text_secondary"])
        self.pause_btn.config(state="normal", bg=self.colors["warning"])
        self.stop_btn.config(state="normal", bg=self.colors["danger"])
        self.update_status("Бот запущен", "working")
        self.bot_thread = threading.Thread(target=self.run_bot)
        self.bot_thread.start()
    
    def pause_bot(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_btn.config(text="▶ ПРОДОЛЖИТЬ", bg=self.colors["success"])
            self.update_status("На паузе", "waiting")
        else:
            self.pause_btn.config(text="⏸ ПАУЗА", bg=self.colors["warning"])
            self.update_status("Работает", "working")
    
    def stop_bot(self):
        self.running = False
        self.paused = False
        self.start_btn.config(state="normal", bg=self.colors["success"])
        self.pause_btn.config(state="disabled", bg=self.colors["text_secondary"], text="⏸ ПАУЗА")
        self.stop_btn.config(state="disabled", bg=self.colors["text_secondary"])
        self.update_status("Остановлен", "info")
        self.progress_label.config(text="")
    
    def run_bot(self):
        while self.running:
            while self.paused and self.running:
                time.sleep(0.5)
            if not self.running:
                break
            
            if self.mode == "arena":
                self.do_arena()
            else:
                self.do_simple_mode()
            
            if self.running and not self.paused:
                self.arena_round += 1
                self.update_status(f"Арена завершена! Раунд {self.arena_round}", "success")
                self.progress_label.config(text=f"✅ Раунд {self.arena_round} завершен")
                time.sleep(3)
    
    def do_simple_mode(self):
        import pyautogui
        coords_map = {
            "cathedral": self.cathedral_coords,
            "dungeon": self.dungeon_coords,
            "bay": self.bay_coords
        }
        coords = coords_map.get(self.mode, {})
        if coords.get("entry", {}).get("x", 0) != 0:
            self.update_status(f"Захожу в {self.mode}...", "working")
            pyautogui.click(coords["entry"]["x"], coords["entry"]["y"])
            time.sleep(3)
            self.update_status(f"Готово!", "success")
        else:
            self.update_status(f"Координаты для {self.mode} не настроены!", "error")
            self.stop_bot()
    
    def do_arena(self):
        import pyautogui
        coords = self.arena_coords
        needed = ["entry", "participate", "confirm", "fight", "reward", "home"]
        for key in needed:
            if key not in coords or coords[key]['x'] == 0:
                self.update_status(f"Ошибка: не настроена кнопка {key}", "error")
                self.stop_bot()
                return
        
        if self.arena_round == 0:
            self.update_status("Захожу на арену...", "working")
            pyautogui.click(coords["entry"]["x"], coords["entry"]["y"])
            time.sleep(2)
        
        self.update_status("Нажимаю 'Участвовать'...", "working")
        pyautogui.click(coords["participate"]["x"], coords["participate"]["y"])
        time.sleep(2)
        
        self.update_status("Нажимаю 'Подтвердить'...", "working")
        pyautogui.click(coords["confirm"]["x"], coords["confirm"]["y"])
        time.sleep(2)
        
        self.update_status("Ожидаю 60 секунд после подтверждения...", "waiting")
        for i in range(60):
            if not self.running or self.paused:
                return
            self.progress_label.config(text=f"⏳ Ожидание перед боями: {60-i} сек")
            time.sleep(1)
        
        for i in range(10, 4, -1):
            if not self.running or self.paused:
                return
            opp_key = f"opponent_{i}"
            if opp_key in coords and coords[opp_key]['x'] != 0:
                self.update_status(f"Выбираю противника {i}...", "working")
                pyautogui.click(coords[opp_key]["x"], coords[opp_key]["y"])
                time.sleep(1.5)
                
                self.update_status(f"Нажимаю 'Бой'...", "working")
                pyautogui.click(coords["fight"]["x"], coords["fight"]["y"])
                time.sleep(1.5)
                
                self.update_status(f"Ожидаю 3 секунды...", "waiting")
                time.sleep(3)
                
                self.update_status(f"Нажимаю 'Домой'...", "working")
                pyautogui.click(coords["home"]["x"], coords["home"]["y"])
                time.sleep(2)
                
                for j in range(120):
                    if not self.running or self.paused:
                        return
                    self.progress_label.config(text=f"⚔ Бой {i}/10 • Ожидание: {120-j} сек")
                    time.sleep(1)
                
                if i > 5:
                    self.update_status(f"Возвращаюсь на арену...", "working")
                    pyautogui.click(coords["entry"]["x"], coords["entry"]["y"])
                    time.sleep(2)
        
        self.update_status("Нажимаю 'Забрать награду'...", "working")
        pyautogui.click(coords["reward"]["x"], coords["reward"]["y"])
        time.sleep(2)
        
        self.update_status("Нажимаю 'Домой'...", "working")
        pyautogui.click(coords["home"]["x"], coords["home"]["y"])
        time.sleep(2)

def main():
    # Сетап
    install_python_if_needed()
    install_libraries()
    
    # Запуск приложения
    root = tk.Tk()
    app = ModernBotApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
