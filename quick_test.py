#!/usr/bin/env python3
"""
NDI 虛擬測試環境 - 快速測試工具
一鍵測試所有核心功能
"""

import sys
import time
from pathlib import Path


def print_header(title):
    """列印標題"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def test_virtual_spheres():
    """測試 1: 虛擬球體模擬器"""
    print_header("Test 1: Virtual Spheres Simulator")
    
    try:
        from virtual_spheres import SphereSimulator, SphereConfig
        
        # 測試所有運動模式
        modes = ['static', 'circle_xy', 'circle_xz', 'circle_yz', 
                 'figure8_xy', 'spiral', 'random_walk']
        
        print("測試運動模式:")
        for mode in modes:
            sim = SphereSimulator()
            sim.add_sphere(SphereConfig((0, 0, 0), mode, 100000, 0.5, 0))
            pos = sim.get_all_positions()
            print(f"  ✓ {mode:15s} -> {pos[0]}")
        
        print("\n✅ 虛擬球體模擬器測試通過")
        return True
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_manager():
    """測試 2: 配置管理器"""
    print_header("Test 2: Configuration Manager")
    
    try:
        from config_manager_simple import ConfigManager
        
        manager = ConfigManager()
        
        # 建立測試場景
        scenarios = manager.create_preset_scenarios()
        print(f"✓ 已建立 {len(scenarios)} 個預設場景")
        
        # 測試載入
        test_files = ['basic_test.json', 'circular_motion.json']
        for filename in test_files:
            scenario = manager.load_scenario(filename)
            print(f"✓ 載入場景: {scenario.name}")
        
        print("\n✅ 配置管理器測試通過")
        return True
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cli_output():
    """測試 3: 命令行輸出"""
    print_header("Test 3: CLI Output (3 seconds)")
    
    try:
        from virtual_spheres import SphereSimulator
        
        sim = SphereSimulator()
        sim.add_preset('circle_3')
        
        print("座標輸出測試:")
        for i in range(60):  # 3 秒 @ 20 FPS
            positions = sim.get_all_positions()
            print(f"\rTick {i:3d} | ", end="")
            for j, (x, y, z) in enumerate(positions, 1):
                print(f"S{j}:({x:+7d},{y:+7d},{z:+7d}) ", end="")
            sys.stdout.flush()
            time.sleep(0.05)
        
        print("\n\n✅ 命令行輸出測試通過")
        return True
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gui_import():
    """測試 4: GUI 模組導入"""
    print_header("Test 4: GUI Module Import")
    
    try:
        import matplotlib
        print(f"✓ matplotlib {matplotlib.__version__} 已安裝")
        
        # 檢查檔案是否存在
        from pathlib import Path
        if not Path('sphere_visualizer_matplotlib.py').exists():
            print("✗ sphere_visualizer_matplotlib.py 檔案不存在")
            return False
        
        from sphere_visualizer_matplotlib import SphereVisualizer
        print("✓ SphereVisualizer 模組可導入")
        
        print("\n✅ GUI 模組測試通過")
        print("   提示: 執行 python run_from_config.py --gui basic_test.json 啟動 GUI")
        return True
        
    except ImportError as e:
        print(f"\n⚠️  導入失敗: {e}")
        print(f"   請檢查 matplotlib 是否已安裝: pip install matplotlib")
        return False
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_file_structure():
    """測試 5: 檔案結構"""
    print_header("Test 5: File Structure")
    
    required_files = [
        'virtual_spheres.py',
        'config_manager_simple.py',
        'sphere_visualizer_matplotlib.py',
        'run_from_config.py'
    ]
    
    missing = []
    for filename in required_files:
        if Path(filename).exists():
            print(f"✓ {filename}")
        else:
            print(f"✗ {filename} (缺失)")
            missing.append(filename)
    
    # 檢查配置目錄
    if Path('configs').exists():
        configs = list(Path('configs').glob('*.json'))
        print(f"✓ configs/ 目錄 ({len(configs)} 個配置檔)")
    else:
        print("✗ configs/ 目錄不存在")
        missing.append('configs/')
    
    if missing:
        print(f"\n⚠️  缺少 {len(missing)} 個檔案")
        return False
    else:
        print("\n✅ 檔案結構完整")
        return True


def run_all_tests():
    """執行所有測試"""
    print("\n" + "="*60)
    print("  NDI Virtual Test Environment - Quick Test")
    print("="*60)
    
    tests = [
        ("Virtual Spheres", test_virtual_spheres),
        ("Config Manager", test_config_manager),
        ("CLI Output", test_cli_output),
        ("GUI Module", test_gui_import),
        ("File Structure", test_file_structure)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except KeyboardInterrupt:
            print("\n\n⚠️  測試被中斷")
            break
        except Exception as e:
            print(f"\n❌ {name} 測試發生未預期錯誤: {e}")
            results.append((name, False))
    
    # 總結
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status:12s} {name}")
    
    print(f"\n總計: {passed}/{total} 測試通過")
    
    if passed == total:
        print("\n🎉 所有測試通過！系統已就緒")
        print("\n下一步:")
        print("  1. 啟動 GUI:")
        print("     python run_from_config.py --gui circular_motion.json")
        print("\n  2. 互動式選擇:")
        print("     python run_from_config.py")
        print("\n  3. 命令行測試:")
        print("     python run_from_config.py --cli stress_test.json")
    else:
        print(f"\n⚠️  {total - passed} 個測試失敗，請檢查錯誤訊息")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n測試被中斷")
        sys.exit(1)