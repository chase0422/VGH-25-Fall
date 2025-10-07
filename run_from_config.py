"""
NDI 虛擬測試環境 - 從配置檔啟動測試/視覺化
支援命令行和 GUI 兩種模式
1007 1126 test fail
"""

import sys
import argparse
from pathlib import Path
from config_manager_simple import ConfigManager, TestScenario
from virtual_spheres import SphereSimulator, SphereConfig


def create_simulator_from_config(scenario: TestScenario) -> SphereSimulator:
    """從配置建立模擬器"""
    sim = SphereSimulator()
    
    for sphere_data in scenario.spheres:
        config = SphereConfig(
            center=tuple(sphere_data.center),
            motion_type=sphere_data.motion_type,
            amplitude=sphere_data.amplitude,
            frequency=sphere_data.frequency,
            phase=sphere_data.phase,
            noise_level=sphere_data.noise_level
        )
        sim.add_sphere(config)
    
    return sim


def run_gui(scenario: TestScenario):
    """啟動 GUI 視覺化"""
    print(f"\n啟動 GUI 視覺化: {scenario.name}")
    print(f"描述: {scenario.description}")
    print(f"座標範圍: ±{scenario.axis_range} mm")
    print(f"球體數量: {len(scenario.spheres)}")
    print("\n正在啟動視窗...")
    
    try:
        # 動態導入避免在命令行模式下載入 matplotlib
        from sphere_visualizer_matplotlib import SphereVisualizer
        
        sim = create_simulator_from_config(scenario)
        viz = SphereVisualizer(sim, fixed_range=scenario.axis_range * 1000)
        viz.start()
        
    except ImportError as e:
        print(f"\n✗ 錯誤: matplotlib 未安裝")
        print(f"  請執行: pip install matplotlib")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_cli(scenario: TestScenario, duration: int = 10):
    """執行命令行測試"""
    print(f"\n執行命令行測試: {scenario.name}")
    print(f"描述: {scenario.description}")
    print(f"測試時長: {duration} 秒")
    print(f"球體數量: {len(scenario.spheres)}")
    print("\n" + "="*60)
    
    sim = create_simulator_from_config(scenario)
    
    import time
    start_time = time.time()
    tick = 0
    
    try:
        while time.time() - start_time < duration:
            # 獲取座標
            positions = sim.get_all_positions()
            
            # 顯示
            print(f"\rTick {tick:4d} | ", end="")
            for i, (x, y, z) in enumerate(positions, 1):
                print(f"S{i}:({x:+8d},{y:+8d},{z:+8d}) ", end="")
            
            tick += 1
            time.sleep(0.05)
        
        print("\n" + "="*60)
        print(f"\n✓ 測試完成")
        
    except KeyboardInterrupt:
        print("\n\n✗ 測試中斷")


def list_scenarios():
    """列出所有可用場景"""
    manager = ConfigManager()
    scenarios = manager.list_scenarios()
    
    if not scenarios:
        print("\n沒有找到任何配置檔")
        print("提示: 執行 python config_manager_simple.py 建立預設場景")
        return []
    
    print("\n可用場景：")
    print("="*60)
    for i, filename in enumerate(scenarios, 1):
        # 載入場景獲取詳細資訊
        try:
            scenario = manager.load_scenario(filename)
            print(f"{i:2d}. {scenario.name}")
            print(f"    檔案: {filename}")
            print(f"    描述: {scenario.description}")
            print(f"    球體: {len(scenario.spheres)} 個")
            print()
        except Exception as e:
            print(f"{i:2d}. {filename} (載入失敗: {e})")
    
    return scenarios


def interactive_mode():
    """互動式模式"""
    print("\n" + "="*60)
    print("  NDI 虛擬測試環境 - 互動式啟動器")
    print("="*60)
    
    scenarios = list_scenarios()
    
    if not scenarios:
        return
    
    print("\n選擇場景編號:", end=" ")
    try:
        choice = int(input().strip())
        if 1 <= choice <= len(scenarios):
            filename = scenarios[choice - 1]
        else:
            print("無效的編號")
            return
    except ValueError:
        print("請輸入數字")
        return
    
    print("\n執行模式：")
    print("  1. GUI 視覺化")
    print("  2. 命令行測試")
    
    mode = input("\n請選擇 (1-2): ").strip()
    
    manager = ConfigManager()
    scenario = manager.load_scenario(filename)
    
    if mode == '1':
        run_gui(scenario)
    elif mode == '2':
        duration = input("\n測試時長（秒，預設 10）: ").strip()
        duration = int(duration) if duration else 10
        run_cli(scenario, duration)
    else:
        print("無效的選項")


def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description='NDI 虛擬測試環境 - 從配置檔啟動',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # 互動式模式
  python run_from_config.py
  
  # 直接啟動 GUI
  python run_from_config.py --gui circular_motion.json
  
  # 執行命令行測試
  python run_from_config.py --cli stress_test.json --duration 30
  
  # 列出所有場景
  python run_from_config.py --list
        """
    )
    
    parser.add_argument(
        '--gui',
        metavar='CONFIG',
        help='啟動 GUI 視覺化'
    )
    
    parser.add_argument(
        '--cli',
        metavar='CONFIG',
        help='執行命令行測試'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=10,
        help='命令行測試時長（秒）'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='列出所有可用場景'
    )
    
    args = parser.parse_args()
    
    # 處理參數
    if args.list:
        list_scenarios()
    elif args.gui:
        manager = ConfigManager()
        scenario = manager.load_scenario(args.gui)
        run_gui(scenario)
    elif args.cli:
        manager = ConfigManager()
        scenario = manager.load_scenario(args.cli)
        run_cli(scenario, args.duration)
    else:
        # 無參數 = 互動模式
        interactive_mode()


if __name__ == "__main__":
    main()