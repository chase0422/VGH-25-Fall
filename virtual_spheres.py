"""
虛擬反光球模擬器 - 靈活配置版
"""

import math
import random
import time
from dataclasses import dataclass
from typing import List, Tuple, Callable


@dataclass
class SphereConfig:
    """單顆球的配置"""
    center: Tuple[float, float, float]  # 中心座標 (x, y, z)
    motion_type: str = "static"          # 運動類型
    amplitude: float = 5000              # 振幅
    frequency: float = 0.5               # 頻率
    phase: float = 0.0                   # 相位
    noise: float = 100                   # 噪聲大小


class VirtualSphere:
    """虛擬反光球"""
    
    def __init__(self, config: SphereConfig):
        self.config = config
        self.start_time = time.time()
    
    def get_position(self) -> Tuple[int, int, int]:
        """獲取當前位置"""
        t = time.time() - self.start_time
        x, y, z = self.config.center
        
        # 根據運動類型計算偏移
        if self.config.motion_type == "static":
            dx, dy, dz = 0, 0, 0
        
        elif self.config.motion_type == "circle_xy":
            # XY平面圓周運動
            angle = t * self.config.frequency + self.config.phase
            dx = self.config.amplitude * math.cos(angle)
            dy = self.config.amplitude * math.sin(angle)
            dz = 0
        
        elif self.config.motion_type == "circle_xz":
            # XZ平面圓周運動
            angle = t * self.config.frequency + self.config.phase
            dx = self.config.amplitude * math.cos(angle)
            dy = 0
            dz = self.config.amplitude * math.sin(angle)
        
        elif self.config.motion_type == "wave_x":
            # X軸正弦波動
            dx = self.config.amplitude * math.sin(t * self.config.frequency + self.config.phase)
            dy, dz = 0, 0
        
        elif self.config.motion_type == "wave_xyz":
            # 三軸波動
            dx = self.config.amplitude * math.sin(t * self.config.frequency + self.config.phase)
            dy = self.config.amplitude * math.sin(t * self.config.frequency * 1.3 + self.config.phase)
            dz = self.config.amplitude * math.sin(t * self.config.frequency * 0.7 + self.config.phase)
        
        elif self.config.motion_type == "spiral":
            # 螺旋運動
            angle = t * self.config.frequency + self.config.phase
            r = self.config.amplitude * (1 + 0.1 * t)
            dx = r * math.cos(angle)
            dy = r * math.sin(angle)
            dz = self.config.amplitude * 0.5 * math.sin(t * 0.5)
        
        elif self.config.motion_type == "random_walk":
            # 隨機遊走
            dx = random.uniform(-self.config.amplitude, self.config.amplitude)
            dy = random.uniform(-self.config.amplitude, self.config.amplitude)
            dz = random.uniform(-self.config.amplitude * 0.3, self.config.amplitude * 0.3)
        
        else:
            dx, dy, dz = 0, 0, 0
        
        # 添加噪聲
        noise = lambda: random.uniform(-self.config.noise, self.config.noise)
        
        return (
            int(x + dx + noise()),
            int(y + dy + noise()),
            int(z + dz + noise())
        )


class SphereSimulator:
    """反光球模擬器"""
    
    def __init__(self):
        self.spheres: List[VirtualSphere] = []
    
    def add_sphere(self, config: SphereConfig):
        """添加一顆球"""
        self.spheres.append(VirtualSphere(config))
    
    def add_preset(self, preset_name: str):
        """添加預設配置"""
        if preset_name == "static_3":
            # 3顆靜止球
            self.add_sphere(SphereConfig((123456, -654321, 111222), "static"))
            self.add_sphere(SphereConfig((223344, 334455, -445566), "static"))
            self.add_sphere(SphereConfig((-555444, 666333, 777222), "static"))
        
        elif preset_name == "circle_3":
            # 3顆圓周運動球（不同相位）
            for i in range(3):
                self.add_sphere(SphereConfig(
                    center=(100000 * i, 0, 0),
                    motion_type="circle_xy",
                    amplitude=50000,
                    frequency=0.5,
                    phase=i * 2.0
                ))
        
        elif preset_name == "wave_3":
            # 3顆波動球
            centers = [(123456, -654321, 111222), (223344, 334455, -445566), (-555444, 666333, 777222)]
            for i, center in enumerate(centers):
                self.add_sphere(SphereConfig(
                    center=center,
                    motion_type="wave_xyz",
                    amplitude=30000,
                    frequency=0.3 + i * 0.1,
                    noise=50
                ))
        
        elif preset_name == "mixed":
            # 混合運動
            self.add_sphere(SphereConfig((123456, -654321, 111222), "circle_xy", 40000, 0.5))
            self.add_sphere(SphereConfig((223344, 334455, -445566), "wave_x", 30000, 0.8))
            self.add_sphere(SphereConfig((-555444, 666333, 777222), "static"))
    
    def get_all_positions(self) -> List[Tuple[int, int, int]]:
        """獲取所有球的位置"""
        return [sphere.get_position() for sphere in self.spheres]
    
    def clear(self):
        """清除所有球"""
        self.spheres.clear()


# ============= 工具函數 =============

def format_coord(n: int, width: int = 6, sign: bool = True) -> str:
    """格式化座標為 NDI 格式"""
    s = f"{abs(n):{width}d}"
    return ("+" if n >= 0 else "-") + s if sign else s


def generate_tx_response(simulator: SphereSimulator) -> str:
    """生成 TX:0008 格式的回應"""
    positions = simulator.get_all_positions()
    
    coords = []
    for x, y, z in positions:
        coords.extend([x, y, z])
    
    chunks = [format_coord(c) for c in coords]
    return "TXRESP|OK|" + "|".join(chunks) + "|END"


# ============= 快速測試 =============

if __name__ == "__main__":
    print("虛擬反光球模擬器測試\n")
    
    # 建立模擬器
    sim = SphereSimulator()
    
    # 測試不同預設
    presets = ["static_3", "circle_3", "wave_3", "mixed"]
    
    for preset in presets:
        print(f"【 測試: {preset} 】")
        sim.clear()
        sim.add_preset(preset)
        
        # 顯示 5 幀
        for frame in range(5):
            tx_response = generate_tx_response(sim)
            positions = sim.get_all_positions()
            
            print(f"Frame {frame}:")
            for i, (x, y, z) in enumerate(positions, 1):
                print(f"  Sphere {i}: ({x:+8d}, {y:+8d}, {z:+8d})")
            
            time.sleep(0.2)
        
        print()
    
    # 自訂配置範例
    print("【 自訂配置 】")
    sim.clear()
    sim.add_sphere(SphereConfig(
        center=(0, 0, 0),
        motion_type="spiral",
        amplitude=50000,
        frequency=0.8,
        noise=200
    ))
    
    for frame in range(5):
        pos = sim.get_all_positions()[0]
        print(f"Frame {frame}: {pos}")
        time.sleep(0.2)
