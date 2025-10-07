"""
虛擬反光球 3D 可視化 - 使用 Matplotlib (macOS 穩定版)
固定座標軸範圍，優化顯示
"""

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib
import numpy as np
from virtual_spheres import SphereSimulator, SphereConfig
import sys

# 設定中文字體支援（macOS）
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Arial', 'Helvetica']
matplotlib.rcParams['axes.unicode_minus'] = False


class SphereVisualizer:
    """三視圖可視化器 - Matplotlib 版本"""
    
    def __init__(self, simulator: SphereSimulator, fixed_range=1000000):
        self.simulator = simulator
        self.running = False
        self.fixed_range = fixed_range  # 固定顯示範圍 (mm)
        
        # 顏色配置
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F']
        
        # 建立圖表
        self.fig = plt.figure(figsize=(15, 9))
        self.fig.suptitle('Virtual Sphere Visualization - Three Views', 
                         fontsize=18, fontweight='bold', y=0.98)
        
        # 建立子圖
        self.ax_xy = self.fig.add_subplot(2, 2, 1)  # XY 視圖
        self.ax_xz = self.fig.add_subplot(2, 2, 2)  # XZ 視圖
        self.ax_yz = self.fig.add_subplot(2, 2, 3)  # YZ 視圖
        self.ax_info = self.fig.add_subplot(2, 2, 4)  # 資訊面板
        
        # 設置各視圖
        self.setup_axes()
        
        # 儲存圖形物件
        self.scatter_xy = None
        self.scatter_xz = None
        self.scatter_yz = None
        self.texts_xy = []
        self.texts_xz = []
        self.texts_yz = []
        
        # FPS 計數
        self.frame_count = 0
        self.last_time = None
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    def setup_axes(self):
        """設置座標軸 - 固定範圍"""
        # 固定座標範圍
        axis_limit = self.fixed_range
        
        # XY 視圖（俯視）
        self.ax_xy.set_title('XY View (Top)', fontsize=12, fontweight='bold', pad=10)
        self.ax_xy.set_xlabel('X (mm)', fontsize=10)
        self.ax_xy.set_ylabel('Y (mm)', fontsize=10)
        self.ax_xy.set_xlim(-axis_limit, axis_limit)
        self.ax_xy.set_ylim(-axis_limit, axis_limit)
        self.ax_xy.grid(True, alpha=0.3, linestyle='--')
        self.ax_xy.set_aspect('equal')
        self.ax_xy.set_facecolor('#2C3E50')
        self.ax_xy.axhline(y=0, color='white', linewidth=0.5, alpha=0.3)
        self.ax_xy.axvline(x=0, color='white', linewidth=0.5, alpha=0.3)
        
        # XZ 視圖（正視）
        self.ax_xz.set_title('XZ View (Front)', fontsize=12, fontweight='bold', pad=10)
        self.ax_xz.set_xlabel('X (mm)', fontsize=10)
        self.ax_xz.set_ylabel('Z (mm)', fontsize=10)
        self.ax_xz.set_xlim(-axis_limit, axis_limit)
        self.ax_xz.set_ylim(-axis_limit, axis_limit)
        self.ax_xz.grid(True, alpha=0.3, linestyle='--')
        self.ax_xz.set_aspect('equal')
        self.ax_xz.set_facecolor('#2C3E50')
        self.ax_xz.axhline(y=0, color='white', linewidth=0.5, alpha=0.3)
        self.ax_xz.axvline(x=0, color='white', linewidth=0.5, alpha=0.3)
        
        # YZ 視圖（側視）
        self.ax_yz.set_title('YZ View (Side)', fontsize=12, fontweight='bold', pad=10)
        self.ax_yz.set_xlabel('Y (mm)', fontsize=10)
        self.ax_yz.set_ylabel('Z (mm)', fontsize=10)
        self.ax_yz.set_xlim(-axis_limit, axis_limit)
        self.ax_yz.set_ylim(-axis_limit, axis_limit)
        self.ax_yz.grid(True, alpha=0.3, linestyle='--')
        self.ax_yz.set_aspect('equal')
        self.ax_yz.set_facecolor('#2C3E50')
        self.ax_yz.axhline(y=0, color='white', linewidth=0.5, alpha=0.3)
        self.ax_yz.axvline(x=0, color='white', linewidth=0.5, alpha=0.3)
        
        # 資訊面板
        self.ax_info.set_title('Coordinate Information', fontsize=12, fontweight='bold', pad=10)
        self.ax_info.axis('off')
    
    def update(self, frame):
        """更新函數（給動畫用）"""
        if not self.running:
            return []
        
        # 獲取當前位置
        positions = self.simulator.get_all_positions()
        
        if not positions:
            return []
        
        # 清除舊的文字標籤
        for text in self.texts_xy + self.texts_xz + self.texts_yz:
            text.remove()
        self.texts_xy.clear()
        self.texts_xz.clear()
        self.texts_yz.clear()
        
        # 準備數據
        xs, ys, zs = zip(*positions)
        colors = [self.colors[i % len(self.colors)] for i in range(len(positions))]
        
        # XY 視圖
        if self.scatter_xy:
            self.scatter_xy.remove()
        self.scatter_xy = self.ax_xy.scatter(xs, ys, c=colors, s=200, 
                                            edgecolors='white', linewidths=2, zorder=5,
                                            alpha=0.8)
        
        for i, (x, y) in enumerate(zip(xs, ys)):
            text = self.ax_xy.text(x, y, f' #{i+1}', fontsize=10, 
                                  color='white', fontweight='bold',
                                  ha='left', va='center', zorder=6)
            self.texts_xy.append(text)
        
        # XZ 視圖
        if self.scatter_xz:
            self.scatter_xz.remove()
        self.scatter_xz = self.ax_xz.scatter(xs, zs, c=colors, s=200,
                                            edgecolors='white', linewidths=2, zorder=5,
                                            alpha=0.8)
        
        for i, (x, z) in enumerate(zip(xs, zs)):
            text = self.ax_xz.text(x, z, f' #{i+1}', fontsize=10,
                                  color='white', fontweight='bold',
                                  ha='left', va='center', zorder=6)
            self.texts_xz.append(text)
        
        # YZ 視圖
        if self.scatter_yz:
            self.scatter_yz.remove()
        self.scatter_yz = self.ax_yz.scatter(ys, zs, c=colors, s=200,
                                            edgecolors='white', linewidths=2, zorder=5,
                                            alpha=0.8)
        
        for i, (y, z) in enumerate(zip(ys, zs)):
            text = self.ax_yz.text(y, z, f' #{i+1}', fontsize=10,
                                  color='white', fontweight='bold',
                                  ha='left', va='center', zorder=6)
            self.texts_yz.append(text)
        
        # 更新資訊面板
        self.ax_info.clear()
        self.ax_info.axis('off')
        
        info_lines = []
        info_lines.append("=" * 45)
        info_lines.append("  COORDINATE DATA")
        info_lines.append("=" * 45)
        info_lines.append("")
        
        for i, (x, y, z) in enumerate(positions):
            info_lines.append(f"● Sphere {i+1}")
            info_lines.append(f"    X: {x:+10.2f} mm")
            info_lines.append(f"    Y: {y:+10.2f} mm")
            info_lines.append(f"    Z: {z:+10.2f} mm")
            info_lines.append("")
        
        # FPS 計算
        import time
        current_time = time.time()
        if self.last_time is not None:
            fps = 1.0 / (current_time - self.last_time)
            info_lines.append("-" * 45)
            info_lines.append(f"  FPS: {fps:.1f}")
        self.last_time = current_time
        
        info_text = "\n".join(info_lines)
        
        self.ax_info.text(0.05, 0.95, info_text,
                         transform=self.ax_info.transAxes,
                         fontsize=11, verticalalignment='top',
                         fontfamily='monospace',
                         bbox=dict(boxstyle='round', facecolor='#ECF0F1', 
                                  alpha=0.9, edgecolor='#34495E', linewidth=2))
        
        return []
    
    def start(self):
        """開始動畫"""
        self.running = True
        self.anim = FuncAnimation(self.fig, self.update, 
                                 interval=50,  # 20 FPS
                                 blit=False,
                                 cache_frame_data=False)
        plt.show()
    
    def stop(self):
        """停止動畫"""
        self.running = False
        if hasattr(self, 'anim'):
            self.anim.event_source.stop()


def main():
    """主程式"""
    print("\n" + "="*60)
    print("  Virtual Sphere 3D Visualization")
    print("  Matplotlib Version for macOS")
    print("="*60)
    print("\nChoose sphere configuration:")
    print("  1. Static (static_3)")
    print("  2. Circle (circle_3)")
    print("  3. Wave (wave_3)")
    print("  4. Mixed (mixed)")
    print("  5. Custom Spiral")
    
    choice = input("\nSelect (1-5): ").strip()
    
    # 詢問固定範圍
    print("\nAxis range options:")
    print("  1. Standard (±1000 mm)")
    print("  2. Large (±2000 mm)")
    print("  3. Custom")
    
    range_choice = input("Select range (1-3, default=1): ").strip() or "1"
    
    if range_choice == "1":
        fixed_range = 1000000  # ±1000 mm
    elif range_choice == "2":
        fixed_range = 2000000  # ±2000 mm
    elif range_choice == "3":
        try:
            fixed_range = int(input("Enter range in mm: ")) * 1000
        except:
            fixed_range = 1000000
    else:
        fixed_range = 1000000
    
    # 建立模擬器
    sim = SphereSimulator()
    
    configs = {
        "1": "static_3",
        "2": "circle_3",
        "3": "wave_3",
        "4": "mixed"
    }
    
    if choice == "5":
        sim.add_sphere(SphereConfig((0, 0, 0), "spiral", 200000, 0.5, 0.0))
        sim.add_sphere(SphereConfig((300000, 0, 0), "circle_xy", 150000, 0.8, 1.0))
        sim.add_sphere(SphereConfig((0, 300000, 0), "wave_xyz", 180000, 0.6, 2.0))
        print("\n✓ Custom spiral configuration loaded")
    else:
        preset = configs.get(choice, "circle_3")
        sim.add_preset(preset)
        print(f"\n✓ Configuration loaded: {preset}")
    
    print(f"✓ Axis range: ±{fixed_range/1000:.0f} mm")
    print("\n✓ Starting visualization...")
    print("  Animation will start automatically")
    print("  Close window to exit\n")
    
    # 建立並啟動視覺化器
    viz = SphereVisualizer(sim, fixed_range=fixed_range)
    
    try:
        viz.start()
    except KeyboardInterrupt:
        print("\nProgram interrupted")
        viz.stop()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nProgram ended")


if __name__ == "__main__":
    main()
    