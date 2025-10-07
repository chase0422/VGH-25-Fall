import random
import math
import time

class SphereTrajectory:
    """模擬反光球的運動軌跡"""
    def __init__(self, center, radius=50, speed=0.1):
        self.center = center  # (x, y, z)
        self.radius = radius
        self.speed = speed
        self.phase = random.uniform(0, 2 * math.pi)
    
    def get_position(self, t):
        """根據時間 t 計算當前位置（圓周運動）"""
        angle = self.phase + t * self.speed
        x = self.center[0] + self.radius * math.cos(angle)
        y = self.center[1] + self.radius * math.sin(angle)
        z = self.center[2] + random.uniform(-5, 5)  # 輕微 Z 軸抖動
        return (x, y, z)

def _num(n, width=6, sign=True):
    """格式化數字為固定寬度字串"""
    s = f"{abs(int(n)):{width}d}"
    return ("+" if n >= 0 else "-") + s if sign else s

def make_fake_tx_string(tick=0, num_spheres=3, add_noise=True):
    """
    產生擬真的 TX:0008 回應字串
    
    參數:
        tick: 當前時間刻度
        num_spheres: 反光球數量 (1-20)
        add_noise: 是否添加測量噪聲
    """
    trajectories = [
        SphereTrajectory(center=(123456, -654321, 111222)),
        SphereTrajectory(center=(223344, 334455, -445566)),
        SphereTrajectory(center=(-555444, 666333, 777222)),
    ]
    
    vals = []
    for i, traj in enumerate(trajectories[:num_spheres]):
        x, y, z = traj.get_position(tick * 0.05)  # 50ms per tick
        
        # 添加測量噪聲
        if add_noise:
            noise = lambda: random.uniform(-10, 10)
            x += noise()
            y += noise()
            z += noise()
        
        vals.extend([int(x), int(y), int(z)])
    
    chunks = [_num(v, width=6, sign=True) for v in vals]
    return "TXRESP|OK|" + "|".join(chunks) + "|END"

def make_tx_with_status(tick=0, out_of_volume=False):
    """
    產生包含狀態資訊的 TX 回應
    
    根據 API 文件 p.162-174，TX 指令可以返回多種狀態
    """
    base_response = make_fake_tx_string(tick)
    
    if out_of_volume:
        # 模擬球體移出測量範圍
        base_response = base_response.replace("OK", "OOV")
    
    return base_response

# 測試函數
if __name__ == "__main__":
    print("=== 測試座標生成 ===")
    for t in [0, 10, 20, 30]:
        print(f"\nTick {t}:")
        print(make_fake_tx_string(tick=t))
    
    print("\n=== 測試 OOV 情況 ===")
    print(make_tx_with_status(tick=0, out_of_volume=True))
