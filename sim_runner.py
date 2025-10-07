"""
NDI 虛擬測試執行器 - 平滑顯示版本
支援跨平台 + 消除閃爍
"""

import sys, os, types, time as _time, threading, importlib.util, platform
from pathlib import Path

# ============= 平滑顯示類別 =============
class SmoothDisplay:
    """平滑畫面更新"""
    
    def __init__(self):
        self.last_lines = []
        self.enabled = True
        
    def clear_and_reset(self):
        """初始化畫面"""
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")
        self.last_lines = []
    
    def update(self, lines):
        """更新畫面（無閃爍）"""
        if not self.enabled:
            return
            
        # 移動到畫面頂部
        sys.stdout.write('\033[H')
        
        # 輸出每一行
        for line in lines:
            sys.stdout.write('\033[K')  # 清除該行
            sys.stdout.write(line + '\n')
        
        # 清除多餘的舊內容
        if len(lines) < len(self.last_lines):
            for _ in range(len(self.last_lines) - len(lines)):
                sys.stdout.write('\033[K\n')
        
        sys.stdout.flush()
        self.last_lines = lines

display = SmoothDisplay()

# ============= 美化輸出 =============
try:
    from rich.console import Console
    console = Console()
    HAS_RICH = True
except ImportError:
    console = None
    HAS_RICH = False

def print_startup_banner():
    """顯示啟動橫幅"""
    lines = [
        "╔" + "═"*58 + "╗",
        "║" + " "*10 + "NDI Polaris 虛擬測試環境" + " "*23 + "║",
        "║" + " "*15 + "平滑顯示版本" + " "*30 + "║",
        "╚" + "═"*58 + "╝",
        "",
        f"作業系統: {platform.system()} {platform.release()}",
        f"Python: {sys.version.split()[0]}",
        "",
    ]
    
    if HAS_RICH:
        for line in lines:
            console.print(line, style="cyan")
    else:
        for line in lines:
            print(line)

# 先清屏
display.clear_and_reset()
print_startup_banner()

# ============= 配置 =============
KEY_SCHEDULE = {0: 'c', 30: 'c', 60: 'e'}
PATCH_TIME_SLEEP = True
UPDATE_RATE = 0.05  # 更新頻率

PREFERRED_FILENAMES = [
    "NDI_reader_smooth_display.py",
    "NDI_reader_crossplatform.py",
    "NDI transformation reader v241008.py",
]

# ============= Mock 模組 =============
class _KeyboardMock:
    def __init__(self, schedule):
        self.schedule = dict(schedule)
        self.tick = 0
        self._fired = set()
        self._lock = threading.Lock()
        self._history = []
    
    def is_pressed(self, key):
        with self._lock:
            want = self.schedule.get(self.tick)
            if want == key and self.tick not in self._fired:
                self._fired.add(self.tick)
                self._history.append((self.tick, key))
                return True
            return False
    
    def get_history(self):
        return self._history.copy()

keyboard_mock = _KeyboardMock(KEY_SCHEDULE)

def _ticker(mock, period=0.05):
    while True:
        _time.sleep(period)
        with mock._lock:
            mock.tick += 1

threading.Thread(target=_ticker, args=(keyboard_mock, UPDATE_RATE), daemon=True).start()

mod_keyboard = types.ModuleType("keyboard")
mod_keyboard.is_pressed = keyboard_mock.is_pressed

# ============= NDI Mock =============
import math
import random

class DynamicCoordinateGenerator:
    """動態座標生成器 - 模擬真實運動"""
    def __init__(self):
        self.start_time = _time.time()
        self.base_coords = [
            (123456, -654321, 111222),
            (223344, 334455, -445566),
            (-555444, 666333, 777222),
        ]
    
    def get_coords(self):
        """獲取當前座標（帶運動效果）"""
        elapsed = _time.time() - self.start_time
        coords = []
        
        for i, (x, y, z) in enumerate(self.base_coords):
            # 添加圓周運動
            angle = elapsed * 0.5 + i * 2.0
            radius = 5000
            
            dx = int(radius * math.cos(angle))
            dy = int(radius * math.sin(angle))
            dz = int(1000 * math.sin(elapsed * 0.3 + i))
            
            # 添加小噪聲
            noise = lambda: random.randint(-100, 100)
            
            coords.extend([
                x + dx + noise(),
                y + dy + noise(),
                z + dz + noise()
            ])
        
        return coords

coord_gen = DynamicCoordinateGenerator()

def _num(n, width=6, sign=True):
    s = f"{abs(int(n)):{width}d}"
    return ("+" if n >= 0 else "-") + s if sign else s

def make_dynamic_tx_string():
    """生成動態座標字串"""
    vals = coord_gen.get_coords()
    chunks = [_num(v, width=6, sign=True) for v in vals]
    return "TXRESP|OK|" + "|".join(chunks) + "|END"

mod_ndicapy = types.ModuleType("ndicapy")
mod_ndicapy.ndiCommand = lambda device, cmd: make_dynamic_tx_string() if str(cmd).startswith("TX:") else "OK"

# ============= Tracker Mock =============
class NDITracker:
    def __init__(self, settings):
        self.settings = settings
        self._device = types.SimpleNamespace(name="VirtualNDI")
        self._started = False
    
    def start_tracking(self):
        self._started = True
    
    def stop_tracking(self):
        self._started = False
    
    def close(self):
        pass

mod_nditracker = types.ModuleType("sksurgerynditracker.nditracker")
mod_nditracker.NDITracker = NDITracker

pkg_sksurgery = types.ModuleType("sksurgerynditracker")
pkg_sksurgery.nditracker = mod_nditracker

# ============= 注入 Mocks =============
sys.modules["keyboard"] = mod_keyboard
sys.modules["ndicapy"] = mod_ndicapy
sys.modules["sksurgerynditracker"] = pkg_sksurgery
sys.modules["sksurgerynditracker.nditracker"] = mod_nditracker

print("✓ Mock 模組已注入")
print(f"⌨️  按鍵排程: {KEY_SCHEDULE}")
print(f"🎬 更新頻率: {1/UPDATE_RATE:.0f} FPS")
print("")

# ============= 時間補丁 =============
if PATCH_TIME_SLEEP:
    _real_sleep = _time.sleep
    def _sleep(dt=0.02):
        keyboard_mock.tick += 1
        _real_sleep(dt)
    _time.sleep = _sleep

# ============= 尋找目標檔案 =============
def find_target_file():
    here = Path(__file__).resolve().parent
    
    for filename in PREFERRED_FILENAMES:
        target = here / filename
        if target.exists():
            return str(target)
    
    candidates = []
    for pattern in ["*NDI*.py", "*ndi*.py"]:
        matches = list(here.glob(pattern))
        candidates.extend(matches)
    
    current_file = Path(__file__).name
    candidates = [
        c for c in candidates 
        if c.name != current_file 
        and not c.name.startswith("test_")
        and not c.name.startswith("sim_")
    ]
    
    if candidates:
        for c in candidates:
            if "smooth" in c.name.lower() or "crossplatform" in c.name.lower():
                return str(c)
        return str(sorted(candidates, key=lambda x: len(x.name))[0])
    
    return None

TARGET_FILE = find_target_file()

if not TARGET_FILE or not os.path.exists(TARGET_FILE):
    print(f"❌ 找不到目標檔案")
    print(f"建議檔名: {', '.join(PREFERRED_FILENAMES)}")
    sys.exit(1)

print(f"🎯 目標檔案: {Path(TARGET_FILE).name}")
print("")

# ============= 安全終止 =============
LAST_TICK = max(KEY_SCHEDULE) if KEY_SCHEDULE else 0

def _terminator():
    _time.sleep((LAST_TICK + 60) * UPDATE_RATE)
    print("\n⏱ 測試完成")
    
    # 檢查輸出
    output_file = Path("Coordinates.txt")
    if output_file.exists():
        print(f"✓ 輸出檔案: {output_file.absolute()}")
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            record_count = sum(1 for line in lines if 'Record' in line)
            print(f"✓ 記錄數量: {record_count}")
    
    os._exit(0)

threading.Thread(target=_terminator, daemon=True).start()

# ============= 執行目標程式 =============
try:
    spec = importlib.util.spec_from_file_location("user_script", TARGET_FILE)
    user_script = importlib.util.module_from_spec(spec)
    sys.modules["user_script"] = user_script
    spec.loader.exec_module(user_script)

except SystemExit:
    pass

except Exception as e:
    print(f"\n❌ 執行錯誤: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\n✓ 測試完成")