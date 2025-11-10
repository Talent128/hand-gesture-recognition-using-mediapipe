#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据集准备工具
功能：从旧数据集中提取可用数据（Stop、Clockwise、Counter Clockwise）
      为新的7类别数据集做准备
"""

import pandas as pd
import os
import shutil
from datetime import datetime


def backup_old_data():
    """备份旧数据文件"""
    old_csv = 'model/point_history_classifier/point_history.csv'
    
    if not os.path.exists(old_csv):
        print("❌ 找不到旧数据文件！")
        return None
    
    # 创建备份文件名（带时间戳）
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_csv = f'model/point_history_classifier/point_history_backup_{timestamp}.csv'
    
    # 备份
    shutil.copy2(old_csv, backup_csv)
    print(f"✅ 已备份旧数据到: {backup_csv}")
    
    return backup_csv


def extract_usable_data():
    """提取可用的数据（类别0、1、2）"""
    old_csv = 'model/point_history_classifier/point_history.csv'
    new_csv = 'model/point_history_classifier/point_history_new.csv'
    
    if not os.path.exists(old_csv):
        print("❌ 找不到旧数据文件！")
        return
    
    # 读取旧数据（无表头）
    df = pd.read_csv(old_csv, header=None)
    
    print("\n" + "="*70)
    print("旧数据集统计：")
    print("="*70)
    print(f"总样本数: {len(df)}")
    print("\n各类别样本数:")
    old_counts = df[0].value_counts().sort_index()
    for label, count in old_counts.items():
        print(f"  类别 {label}: {count} 个样本")
    
    # 只保留类别 0、1、2 的数据（Stop、Clockwise、Counter Clockwise）
    df_filtered = df[df[0].isin([0, 1, 2])]
    
    print("\n" + "="*70)
    print("提取后的数据统计：")
    print("="*70)
    print(f"总样本数: {len(df_filtered)}")
    print("\n各类别样本数:")
    new_counts = df_filtered[0].value_counts().sort_index()
    for label, count in new_counts.items():
        labels = ['Stop', 'Clockwise', 'Counter Clockwise']
        print(f"  类别 {label} ({labels[label]:20s}): {count} 个样本")
    
    # 保存新数据集
    df_filtered.to_csv(new_csv, header=False, index=False)
    print(f"\n✅ 已保存新数据集到: {new_csv}")
    
    # 显示需要采集的数据量
    print("\n" + "="*70)
    print("接下来需要采集的数据：")
    print("="*70)
    print("  类别 3 (Move Up):     建议采集 500-600 个样本 ⬆️")
    print("  类别 4 (Move Down):   建议采集 500-600 个样本 ⬇️")
    print("  类别 5 (Move Left):   建议采集 500-600 个样本 ⬅️")
    print("  类别 6 (Move Right):  建议采集 500-600 个样本 ➡️")
    print("\n总计需要采集: 2000-2400 个样本")
    
    return new_csv


def replace_with_new_dataset():
    """用新数据集替换旧数据集"""
    old_csv = 'model/point_history_classifier/point_history.csv'
    new_csv = 'model/point_history_classifier/point_history_new.csv'
    
    if not os.path.exists(new_csv):
        print("❌ 找不到新数据集文件！请先运行提取功能。")
        return
    
    # 再次备份
    backup_old_data()
    
    # 替换
    shutil.copy2(new_csv, old_csv)
    print(f"\n✅ 已用新数据集替换旧数据集")
    print(f"   现在可以使用 app.py 采集新的方向数据了！")
    
    # 删除临时文件
    if os.path.exists(new_csv):
        os.remove(new_csv)
        print(f"✅ 已清理临时文件")


def show_menu():
    """显示菜单"""
    print("\n" + "="*70)
    print("              🔧 数据集准备工具")
    print("="*70)
    print("\n请选择操作：")
    print("  1. 备份旧数据集")
    print("  2. 提取可用数据（类别0、1、2）")
    print("  3. 用新数据集替换旧数据集（会先自动备份）")
    print("  4. 完整流程（备份 → 提取 → 替换）")
    print("  5. 仅查看数据统计")
    print("  0. 退出")
    print("="*70)


def show_statistics():
    """显示数据统计"""
    csv_path = 'model/point_history_classifier/point_history.csv'
    
    if not os.path.exists(csv_path):
        print("❌ 找不到数据文件！")
        return
    
    df = pd.read_csv(csv_path, header=None)
    
    print("\n" + "="*70)
    print("当前数据集统计：")
    print("="*70)
    print(f"总样本数: {len(df)}")
    print(f"特征维度: {df.shape[1] - 1}")
    
    print("\n各类别样本数:")
    counts = df[0].value_counts().sort_index()
    
    # 旧的4类别标签
    old_labels = {
        0: 'Stop',
        1: 'Clockwise',
        2: 'Counter Clockwise',
        3: 'Move (混合方向)'
    }
    
    for label, count in counts.items():
        label_name = old_labels.get(label, f'未知类别{label}')
        percentage = (count / len(df)) * 100
        print(f"  类别 {label} ({label_name:25s}): {count:4d} 个样本 ({percentage:5.2f}%)")
    
    if 3 in counts:
        move_count = counts[3]
        print(f"\n⚠️  注意：类别3 (Move) 包含 {move_count} 个混合方向的样本")
        print("   这些数据不能用于训练方向识别模型，建议删除")


def full_process():
    """完整流程"""
    print("\n开始完整数据准备流程...\n")
    
    # 1. 备份
    print("【步骤 1/3】备份旧数据")
    backup_file = backup_old_data()
    if not backup_file:
        return
    
    input("\n按 Enter 继续...")
    
    # 2. 提取
    print("\n【步骤 2/3】提取可用数据")
    new_file = extract_usable_data()
    if not new_file:
        return
    
    print("\n⚠️  警告：下一步将替换旧数据集！")
    confirm = input("确认继续？(输入 yes 继续): ")
    
    if confirm.lower() != 'yes':
        print("❌ 已取消操作")
        return
    
    # 3. 替换
    print("\n【步骤 3/3】替换数据集")
    replace_with_new_dataset()
    
    print("\n" + "="*70)
    print("✅ 数据准备完成！")
    print("="*70)
    print("\n下一步操作：")
    print("1. 运行: python app.py")
    print("2. 按 'h' 键进入轨迹采集模式")
    print("3. 采集新的方向数据：")
    print("   - 按 '3' 采集向上移动数据")
    print("   - 按 '4' 采集向下移动数据")
    print("   - 按 '5' 采集向左移动数据")
    print("   - 按 '6' 采集向右移动数据")
    print("\n4. 使用 python collection_helper.py 查看进度")


def main():
    """主函数"""
    while True:
        show_menu()
        choice = input("\n请输入选项 (0-5): ").strip()
        
        if choice == '0':
            print("\n👋 再见！")
            break
        elif choice == '1':
            backup_old_data()
        elif choice == '2':
            extract_usable_data()
        elif choice == '3':
            replace_with_new_dataset()
        elif choice == '4':
            full_process()
            break  # 完成后退出
        elif choice == '5':
            show_statistics()
        else:
            print("❌ 无效选项，请重新选择")
        
        if choice != '4':
            input("\n按 Enter 继续...")


if __name__ == '__main__':
    main()

