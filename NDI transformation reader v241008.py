"""
NDI Transformation Reader - 平滑顯示版本
消除畫面閃爍，優化更新率
"""

from sksurgerynditracker.nditracker import NDITracker
import ndicapy
import time
import os
import platform
import keyboard
from pathlib import Path
import sys

# ============= 平滑顯示工具 =============

class SmoothDisplay:
    """平滑畫面更新，避免閃爍"""
    
    def __init__(self):
        self.last_lines = []
        
    def clear_and_reset(self):
        """初始化畫面"""
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")
        self.last_lines = []
    
    def update(self, lines):
        """更新畫面內容，不閃爍"""
        # 移動游標到開始位置
        sys.stdout.write('\033[H')  # Move cursor to home
        
        # 輸出新內容
        for line in lines:
            # 清除該行到行尾，避免殘留字元
            sys.stdout.write('\033[K')
            sys.stdout.write(line + '\n')
        
        # 如果新內容比舊內容少，清除剩餘行
        if len(lines) < len(self.last_lines):
            for _ in range(len(self.last_lines) - len(lines)):
                sys.stdout.write('\033[K\n')
        
        sys.stdout.flush()
        self.last_lines = lines


# ============= 跨平台配置 =============

def get_default_rom_path():
    """根據作業系統取得預設 ROM 路徑"""
    system = platform.system()
    home = Path.home()
    
    if system == "Windows":
        default_path = home / "Desktop" / "NDI" / "Probe14_091224.rom"
    elif system == "Darwin":  # Mac
        default_path = home / "Desktop" / "NDI" / "Probe14_091224.rom"
    else:  # Linux
        default_path = home / "ndi" / "Probe14_091224.rom"
    
    return str(default_path)


# ============= 程式配置 =============

NUM_DIGIT = 6
NUM_DIMEN = 3
BUTTON_REC = "c"
BUTTON_EXPORT = "e"
UPDATE_RATE = 0.05  # 更新頻率（秒）

ROM_FILE_PATH = get_default_rom_path()

SETTINGS = {
    "tracker type": "polaris",
    "romfiles": [ROM_FILE_PATH],
}

# 建立平滑顯示器
display = SmoothDisplay()

# ============= 核心函數 =============

class Sphere:
    """球體類別"""
    def __init__(self, pos_list):
        self.x = pos_list[0]
        self.y = pos_list[1]
        self.z = pos_list[2]


def TX0008_pos_str_to_list(str_input, len_digit):
    """解析 TX:0008 座標字串"""
    list_position = []
    while len(str_input) > 0:
        if str_input[0] in "+-":
            str_coord = str_input[:len_digit + 1]
            str_coord_point = str_coord[:5] + "." + str_coord[5:]
            list_position.append(str_coord_point)
            str_input = str_input[len_digit + 1:]
        else:
            str_input = str_input[1:]
    
    return list_position


def format_sphere_display(sphere_list, picked_count):
    """格式化球體顯示內容"""
    lines = []
    
    # 標題
    lines.append("╔" + "═"*58 + "╗")
    lines.append("║" + " "*15 + "NDI Transformation Reader" + " "*18 + "║")
    lines.append("╚" + "═"*58 + "╝")
    lines.append("")
    
    # 操作說明
    lines.append(f"操作: 按 '{BUTTON_REC}' 記錄座標 | 按 '{BUTTON_EXPORT}' 匯出並結束")
    lines.append(f"已記錄: {picked_count} 筆座標")
    lines.append("─"*60)
    lines.append("")
    
    # 當前座標
    lines.append("【 當前座標 】")
    for idx, sphere in enumerate(sphere_list, 1):
        lines.append(f"  Sphere {idx}:")
        lines.append(f"    X: {sphere.x:>12s}  Y: {sphere.y:>12s}  Z: {sphere.z:>12s}")
    
    lines.append("")
    lines.append("─"*60)
    
    return lines


# ============= 主程式 =============

try:
    # 初始化顯示
    display.clear_and_reset()
    
    # 顯示啟動資訊
    startup_lines = [
        "╔" + "═"*58 + "╗",
        "║" + " "*15 + "NDI Transformation Reader" + " "*18 + "║",
        "║" + " "*10 + "平滑顯示版本 - 消除閃爍" + " "*20 + "║",
        "╚" + "═"*58 + "╝",
        "",
        f"作業系統: {platform.system()}",
        f"ROM 路徑: {ROM_FILE_PATH}",
        "",
        "正在初始化 NDI Tracker...",
    ]
    display.update(startup_lines)
    
    # 初始化 Tracker
    TRACKER = NDITracker(SETTINGS)
    TRACKER.start_tracking()
    
    time.sleep(0.5)
    
    # 開始追蹤
    picked_coord = []
    last_update_time = time.time()
    
    while True:
        current_time = time.time()
        
        # 控制更新頻率
        if current_time - last_update_time < UPDATE_RATE:
            time.sleep(0.01)
            continue
        
        last_update_time = current_time
        
        # 讀取座標
        TX0008_pos_str = ndicapy.ndiCommand(TRACKER._device, 'TX:0008')
        pos_list = TX0008_pos_str_to_list(TX0008_pos_str, NUM_DIGIT)
        
        # 驗證座標數量
        if len(pos_list) % NUM_DIMEN != 0:
            continue
        
        # 建立球體物件
        list_sphere = []
        while len(pos_list) > 0:
            list_sphere.append(Sphere(pos_list[:NUM_DIMEN]))
            pos_list = pos_list[NUM_DIMEN:]
        
        # 處理按鍵
        is_BUTTON_REC_pressed = keyboard.is_pressed(BUTTON_REC)
        is_BUTTON_EXPORT_pressed = keyboard.is_pressed(BUTTON_EXPORT)
        
        if is_BUTTON_REC_pressed:
            picked_coord.append(list_sphere)
            time.sleep(0.2)  # 防止重複按鍵
        
        elif is_BUTTON_EXPORT_pressed:
            # 匯出檔案
            output_file = Path("Coordinates.txt")
            
            with open(output_file, "w", encoding="utf-8") as file:
                file.write("NDI Coordinates Export\n")
                file.write("=" * 50 + "\n")
                file.write(f"Total Records: {len(picked_coord)}\n")
                file.write("=" * 50 + "\n")
                
                for record_idx, record in enumerate(picked_coord, 1):
                    file.write(f"\n【 Record {record_idx} 】\n")
                    for sphere_idx, sphere in enumerate(record, 1):
                        file.write(f"\nSphere {sphere_idx}\n")
                        file.write(f"  X: {sphere.x}\n")
                        file.write(f"  Y: {sphere.y}\n")
                        file.write(f"  Z: {sphere.z}\n")
            
            # 顯示完成訊息
            final_lines = [
                "",
                "╔" + "═"*58 + "╗",
                "║" + " "*20 + "匯出完成！" + " "*27 + "║",
                "╚" + "═"*58 + "╝",
                "",
                f"✓ 座標已匯出至: {output_file.absolute()}",
                f"✓ 總共記錄: {len(picked_coord)} 筆",
                "",
            ]
            display.update(final_lines)
            time.sleep(2)
            break
        
        # 更新顯示（平滑更新，不閃爍）
        display_lines = format_sphere_display(list_sphere, len(picked_coord))
        display.update(display_lines)
    
    TRACKER.stop_tracking()
    TRACKER.close()
    print("\n程式已正常結束")

except KeyboardInterrupt:
    print("\n\n程式被使用者中斷")
    if 'TRACKER' in locals():
        TRACKER.stop_tracking()
        TRACKER.close()

except Exception as e:
    print(f"\n錯誤: {e}")
    import traceback
    traceback.print_exc()
    if 'TRACKER' in locals():
        TRACKER.stop_tracking()
        TRACKER.close()