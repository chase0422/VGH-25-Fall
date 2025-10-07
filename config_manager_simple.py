"""
NDI 虛擬測試環境 - 配置管理器（簡化版，不依賴 YAML）
使用 JSON 格式，Python 內建支援
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class SphereConfigData:
    """球體配置數據"""
    name: str
    center: tuple
    motion_type: str
    amplitude: int
    frequency: float
    phase: float
    noise_level: int = 0


@dataclass
class TestScenario:
    """測試場景"""
    name: str
    description: str
    axis_range: int  # mm
    spheres: List[SphereConfigData]
    keyboard_schedule: Dict[int, str]  # tick -> key


class ConfigManager:
    """配置管理器 - JSON 版本"""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
    
    def save_scenario(self, scenario: TestScenario, filename: str = None):
        """儲存測試場景（JSON 格式）"""
        if filename is None:
            filename = f"{scenario.name.lower().replace(' ', '_')}.json"
        
        filepath = self.config_dir / filename
        
        # 轉換為字典
        data = {
            'name': scenario.name,
            'description': scenario.description,
            'axis_range': scenario.axis_range,
            'spheres': [asdict(s) for s in scenario.spheres],
            'keyboard_schedule': {str(k): v for k, v in scenario.keyboard_schedule.items()}
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 配置已儲存: {filepath}")
        return filepath
    
    def load_scenario(self, filename: str) -> TestScenario:
        """載入測試場景（JSON 格式）"""
        filepath = self.config_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"配置檔不存在: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 重建物件
        spheres = [SphereConfigData(**s) for s in data['spheres']]
        keyboard_schedule = {int(k): v for k, v in data['keyboard_schedule'].items()}
        
        scenario = TestScenario(
            name=data['name'],
            description=data['description'],
            axis_range=data['axis_range'],
            spheres=spheres,
            keyboard_schedule=keyboard_schedule
        )
        
        print(f"✓ 配置已載入: {filepath}")
        return scenario
    
    def list_scenarios(self) -> List[str]:
        """列出所有配置"""
        return [f.name for f in self.config_dir.glob("*.json")]
    
    def create_preset_scenarios(self):
        """建立預設場景"""
        
        scenarios = []
        
        # 場景 1: 基礎測試
        basic = TestScenario(
            name="Basic Test",
            description="三個靜止球體，測試基礎讀取功能",
            axis_range=1000,
            spheres=[
                SphereConfigData("Sphere 1", (0, 0, 0), "static", 0, 0, 0),
                SphereConfigData("Sphere 2", (300000, 0, 0), "static", 0, 0, 0),
                SphereConfigData("Sphere 3", (0, 300000, 0), "static", 0, 0, 0),
            ],
            keyboard_schedule={0: 'c', 30: 'c', 60: 'e'}
        )
        scenarios.append(('basic_test.json', basic))
        
        # 場景 2: 圓周運動
        circular = TestScenario(
            name="Circular Motion",
            description="三個球體做不同平面的圓周運動",
            axis_range=1500,
            spheres=[
                SphereConfigData("XY Circle", (0, 0, 0), "circle_xy", 200000, 0.5, 0.0, 500),
                SphereConfigData("XZ Circle", (0, 0, 0), "circle_xz", 200000, 0.5, 1.57, 500),
                SphereConfigData("YZ Circle", (0, 0, 0), "circle_yz", 200000, 0.5, 3.14, 500),
            ],
            keyboard_schedule={0: 'c', 60: 'c', 120: 'c', 180: 'e'}
        )
        scenarios.append(('circular_motion.json', circular))
        
        # 場景 3: 螺旋運動
        spiral = TestScenario(
            name="Spiral Motion",
            description="三個球體做螺旋運動，測試 3D 追蹤",
            axis_range=2000,
            spheres=[
                SphereConfigData("Spiral 1", (0, 0, 0), "spiral", 200000, 0.5, 0.0, 300),
                SphereConfigData("Spiral 2", (300000, 0, 0), "spiral", 150000, 0.3, 1.57, 300),
                SphereConfigData("Spiral 3", (-300000, 0, 0), "spiral", 180000, 0.4, 3.14, 300),
            ],
            keyboard_schedule={0: 'c', 90: 'c', 180: 'c', 270: 'e'}
        )
        scenarios.append(('spiral_motion.json', spiral))
        
        # 場景 4: 混合運動
        mixed = TestScenario(
            name="Mixed Motion",
            description="混合多種運動模式",
            axis_range=1500,
            spheres=[
                SphereConfigData("Static", (0, 0, 0), "static", 0, 0, 0),
                SphereConfigData("Circle", (400000, 0, 0), "circle_xy", 150000, 0.6, 0, 400),
                SphereConfigData("Spiral", (-400000, 0, 0), "spiral", 180000, 0.4, 0, 400),
            ],
            keyboard_schedule={0: 'c', 60: 'c', 120: 'c', 180: 'e'}
        )
        scenarios.append(('mixed_motion.json', mixed))
        
        # 場景 5: 壓力測試
        stress = TestScenario(
            name="Stress Test",
            description="多個球體隨機運動，測試系統極限",
            axis_range=2000,
            spheres=[
                SphereConfigData(f"Sphere {i+1}", 
                               ((i-2)*200000, 0, 0), 
                               "random_walk", 
                               150000, 0.8, i*0.5, 1000)
                for i in range(5)
            ],
            keyboard_schedule={i*30: 'c' for i in range(10)}
        )
        stress.keyboard_schedule[300] = 'e'
        scenarios.append(('stress_test.json', stress))
        
        # 儲存所有場景
        print(f"\n建立預設場景...")
        print("=" * 60)
        for filename, scenario in scenarios:
            self.save_scenario(scenario, filename)
        
        print(f"\n✓ 已建立 {len(scenarios)} 個預設場景")
        return scenarios
    
    def print_scenario_info(self, scenario: TestScenario):
        """顯示場景資訊"""
        print("\n" + "=" * 60)
        print(f"場景名稱: {scenario.name}")
        print(f"描述: {scenario.description}")
        print(f"座標範圍: ±{scenario.axis_range} mm")
        print(f"球體數量: {len(scenario.spheres)}")
        print("\n球體配置:")
        for i, sphere in enumerate(scenario.spheres, 1):
            print(f"  {i}. {sphere.name}")
            print(f"     位置: {sphere.center}")
            print(f"     運動: {sphere.motion_type}")
            print(f"     振幅: {sphere.amplitude} μm")
            print(f"     頻率: {sphere.frequency} Hz")
        print(f"\n按鍵事件: {len(scenario.keyboard_schedule)} 個")
        for tick, key in sorted(scenario.keyboard_schedule.items()):
            print(f"  Tick {tick:3d}: 按 '{key}'")
        print("=" * 60)


def interactive_menu():
    """互動式選單"""
    manager = ConfigManager()
    
    while True:
        print("\n" + "=" * 60)
        print("  NDI 配置管理器")
        print("=" * 60)
        print("\n選項：")
        print("  1. 建立預設場景")
        print("  2. 列出所有場景")
        print("  3. 查看場景詳情")
        print("  4. 離開")
        
        choice = input("\n請選擇 (1-4): ").strip()
        
        if choice == '1':
            manager.create_preset_scenarios()
            
        elif choice == '2':
            scenarios = manager.list_scenarios()
            if scenarios:
                print("\n可用場景：")
                for i, name in enumerate(scenarios, 1):
                    print(f"  {i}. {name}")
            else:
                print("\n沒有找到任何場景配置檔")
                print("提示: 選擇選項 1 建立預設場景")
                
        elif choice == '3':
            scenarios = manager.list_scenarios()
            if not scenarios:
                print("\n沒有找到任何場景配置檔")
                continue
            
            print("\n可用場景：")
            for i, name in enumerate(scenarios, 1):
                print(f"  {i}. {name}")
            
            try:
                idx = int(input("\n選擇場景編號: ")) - 1
                if 0 <= idx < len(scenarios):
                    scenario = manager.load_scenario(scenarios[idx])
                    manager.print_scenario_info(scenario)
                else:
                    print("無效的編號")
            except ValueError:
                print("請輸入數字")
                
        elif choice == '4':
            print("\n再見！")
            break
        
        else:
            print("\n無效的選項")


# 使用範例
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        # 自動模式：直接建立預設場景
        manager = ConfigManager()
        manager.create_preset_scenarios()
        
        print("\n列出所有場景：")
        for i, scenario_file in enumerate(manager.list_scenarios(), 1):
            print(f"  {i}. {scenario_file}")
        
        # 示範載入場景
        print("\n載入場景示範：")
        scenario = manager.load_scenario("circular_motion.json")
        manager.print_scenario_info(scenario)
    else:
        # 互動模式
        interactive_menu()