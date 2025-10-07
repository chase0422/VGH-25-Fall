"""
NDI 測試執行器 - 靈活虛擬球版本
"""

import sys, os, types, time as _time, threading, importlib.util
from pathlib import Path

# 匯入虛擬球模擬器
from virtual_spheres import SphereSimulator, SphereConfig, generate_tx_response

# ============= 配置區 =============

# 按鍵排程
KEY_SCHEDULE = {0: 'c', 30: 'c', 60: 'e'}

# 球的配置 - 選擇一種
SPHERE_PRESET = "wave_3"  # 可選: static_3, circle_3, wave_3, mixed

# 或自訂配置（取消註解使用）
# CUSTOM_SPHERES = [
#     SphereConfig((123456, -654321, 111222), "circle_xy", 50000, 0.5, 0.0),
#     SphereConfig((223344, 334455, -445566), "wave_x", 30000, 0.8, 0.0),
#     SphereConfig((-555444, 666333, 777222), "spiral", 40000, 0.6, 1.0),
# ]

# ============= 初始化模擬器 =============

sphere_sim = SphereSimulator()

# 使用預設或自訂
if 'CUSTOM_SPHERES' in locals():
    for config in CUSTOM_SPHERES:
        sphere_sim.add_sphere(config)
    print(f"✓ 使用自訂配置: {len(CUSTOM_SPHERES)} 顆球")
else:
    sphere_sim.add_preset(SPHERE_PRESET)
    print(f"✓ 使用預設: {SPHERE_PRESET}")

# ============= Mock 模組 =============

class _KeyboardMock:
    def __init__(self, schedule):
        self.schedule = dict(schedule)
        self.tick = 0
        self._fired = set()
        self._lock = threading.Lock()
    
    def is_pressed(self, key):
        with self._lock:
            want = self.schedule.get(self.tick)
            if want == key and self.tick not in self._fired:
                self._fired.add(self.tick)
                return True
            return False

keyboard_mock = _KeyboardMock(KEY_SCHEDULE)

def _ticker(mock, period=0.05):
    while True:
        _time.sleep(period)
        with mock._lock:
            mock.tick += 1

threading.Thread(target=_ticker, args=(keyboard_mock,), daemon=True).start()

mod_keyboard = types.ModuleType("keyboard")
mod_keyboard.is_pressed = keyboard_mock.is_pressed

# NDI Mock - 使用虛擬球模擬器
mod_ndicapy = types.ModuleType("ndicapy")
mod_ndicapy.ndiCommand = lambda device, cmd: generate_tx_response(sphere_sim) if str(cmd).startswith("TX:") else "OK"

# Tracker Mock
class NDITracker:
    def __init__(self, settings):
        self.settings = settings
        self._device = types.SimpleNamespace(name="VirtualNDI")
    def start_tracking(self): pass
    def stop_tracking(self): pass
    def close(self): pass

mod_nditracker = types.ModuleType("sksurgerynditracker.nditracker")
mod_nditracker.NDITracker = NDITracker

pkg_sksurgery = types.ModuleType("sksurgerynditracker")
pkg_sksurgery.nditracker = mod_nditracker

# ============= 注入 =============

sys.modules["keyboard"] = mod_keyboard
sys.modules["ndicapy"] = mod_ndicapy
sys.modules["sksurgerynditracker"] = pkg_sksurgery
sys.modules["sksurgerynditracker.nditracker"] = mod_nditracker

print(f"⌨️  按鍵排程: {KEY_SCHEDULE}")

# ============= 尋找目標檔案 =============

def find_target_file():
    here = Path(__file__).resolve().parent
    
    candidates = [
        "NDI_reader_smooth_display.py",
        "NDI_reader_crossplatform.py",
        "NDI transformation reader v241008.py",
    ]
    
    for name in candidates:
        if (here / name).exists():
            return str(here / name)
    
    return None

TARGET_FILE = find_target_file()

if not TARGET_FILE:
    print("❌ 找不到目標檔案")
    sys.exit(1)

print(f"🎯 目標: {Path(TARGET_FILE).name}\n")

# ============= 執行 =============

# 安全終止
def _terminator():
    _time.sleep((max(KEY_SCHEDULE) + 60) * 0.05)
    print("\n⏱ 測試完成")
    os._exit(0)

threading.Thread(target=_terminator, daemon=True).start()

# 執行目標程式
try:
    spec = importlib.util.spec_from_file_location("user_script", TARGET_FILE)
    user_script = importlib.util.module_from_spec(spec)
    sys.modules["user_script"] = user_script
    spec.loader.exec_module(user_script)
except SystemExit:
    pass
except Exception as e:
    print(f"❌ 錯誤: {e}")
