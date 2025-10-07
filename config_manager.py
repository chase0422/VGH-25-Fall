"""

1007 1123
目前有問題
NDI 虛擬測試環境 - 配置管理器
支援 YAML 配置檔，方便團隊共享測試場景
"""

import yaml
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
    """配置管理器"""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
    
    def save_scenario(self, scenario: TestScenario, filename: str = None):
        """儲存測試場景"""
        if filename is None:
            filename = f"{scenario.name.lower().replace(' ', '_')}.yaml"
        
        filepath = self.config_dir / filename
        
        # 轉換為字典
        data = {
            'name': scenario.name,
            'description': scenario.description,
            'axis_range': scenario.axis_range,
            'spheres': [asdict(s) for s in scenario.spheres],
            'keyboard_schedule': {str(k): v for k, v in scenario.keyboard_schedule.items()}
        }
        
        with open(filepath, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        
        print(f"✓ 配置已儲存: {filepath}")
    
    def load_scenario(self, filename: str) -> TestScenario:
        """載入測試場景"""
        filepath = self.config_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"配置檔不存在: {filepath}")
        
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        
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
        return [f.name for f in self.config_dir.glob("*.yaml")]
    
    def create_preset_scenarios(self):
        """建立預設場景"""
        
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
        self.save_scenario(basic, "basic_test.yaml")
        
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
        self.save_scenario(circular, "circular_motion.yaml")
        
        # 場景 3: 壓力測試
        stress = TestScenario(
            name="Stress Test",
            description="多個球體隨機運動，測試系統極限",
            axis_range=2000,
            spheres=[
                SphereConfigData(f"Sphere {i+1}", 
                               (i*100000, 0, 0), 
                               "random_walk", 
                               150000, 0.8, i*0.5, 1000)
                for i in range(6)
            ],
            keyboard_schedule={i*30: 'c' for i in range(10)}
        )
        stress.keyboard_schedule[300] = 'e'
        self.save_scenario(stress, "stress_test.yaml")
        
        print("\n✓ 已建立 3 個預設場景")


# 使用範例
if __name__ == "__main__":
    manager = ConfigManager()
    
    # 建立預設場景
    manager.create_preset_scenarios()
    
    # 列出所有場景
    print("\n可用場景：")
    for scenario_file in manager.list_scenarios():
        print(f"  - {scenario_file}")
    
    # 載入並顯示場景
    print("\n載入場景示範：")
    scenario = manager.load_scenario("circular_motion.yaml")
    print(f"\n場景: {scenario.name}")
    print(f"描述: {scenario.description}")
    print(f"座標範圍: ±{scenario.axis_range} mm")
    print(f"球體數量: {len(scenario.spheres)}")
    print(f"按鍵事件: {scenario.keyboard_schedule}")