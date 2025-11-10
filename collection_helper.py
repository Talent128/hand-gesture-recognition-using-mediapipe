#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据采集进度查看工具
用于查看手势训练数据的采集进度
"""

import pandas as pd
import os
import sys


def check_collection_progress():
    """检查数据采集进度"""
    csv_path = 'model/point_history_classifier/point_history.csv'
    label_path = 'model/point_history_classifier/point_history_classifier_label.csv'
    
    # 检查数据文件是否存在
    if not os.path.exists(csv_path):
        print("❌ 数据文件不存在！")
        print(f"   路径: {csv_path}")
        return
    
    # 检查标签文件是否存在
    if not os.path.exists(label_path):
        print("❌ 标签文件不存在！")
        print(f"   路径: {label_path}")
        return
    
    try:
        # 读取标签文件
        with open(label_path, 'r', encoding='utf-8-sig') as f:
            labels = [line.strip() for line in f if line.strip()]
        
        if not labels:
            print("❌ 标签文件为空！")
            return
        
        # 读取CSV文件（无表头）
        df = pd.read_csv(csv_path, header=None)
        counts = df[0].value_counts().sort_index()
        
        print("\n" + "="*70)
        print("              🎯 动态手势数据采集统计")
        print("="*70)
        
        total_collected = 0
        
        # 显示每个类别的样本数
        for i in range(len(labels)):
            current = counts.get(i, 0)
            total_collected += current
            
            # 状态图标（根据样本数显示）
            if current >= 500:
                status = "✅"
            elif current >= 100:
                status = "🔄"
            elif current > 0:
                status = "📝"
            else:
                status = "⏳"
            
            # 打印类别信息
            print(f"{status} 类别 {i} ({labels[i]:25s}): {current:5d} 个样本")
        
        print("="*70)
        print(f"📊 总样本数: {total_collected} 个")
        print(f"📋 类别数量: {len(labels)} 个")
        print("="*70)
        
        # 数据平衡性检查
        if len(counts) > 0:
            min_count = counts.min()
            max_count = counts.max()
            balance_ratio = min_count / max_count if max_count > 0 else 0
            
            print(f"\n数据分布:")
            print(f"  • 最少样本类别: {min_count} 个")
            print(f"  • 最多样本类别: {max_count} 个")
            print(f"  • 平衡比例: {balance_ratio:.2%}")
            
            if balance_ratio < 0.5:
                print("  ⚠️  建议: 数据不平衡，建议补充样本较少的类别")
            else:
                print("  ✅ 数据分布较为均衡")
        
        
    except Exception as e:
        print(f"❌ 读取文件时出错: {e}")
        import traceback
        traceback.print_exc()
        return


def check_static_gesture_progress():
    """检查静态手势数据采集进度"""
    csv_path = 'model/keypoint_classifier/keypoint.csv'
    label_path = 'model/keypoint_classifier/keypoint_classifier_label.csv'
    
    # 检查数据文件是否存在
    if not os.path.exists(csv_path):
        print("❌ 静态手势数据文件不存在！")
        print(f"   路径: {csv_path}")
        return
    
    # 检查标签文件是否存在
    if not os.path.exists(label_path):
        print("❌ 标签文件不存在！")
        print(f"   路径: {label_path}")
        return
    
    try:
        # 读取标签文件
        with open(label_path, 'r', encoding='utf-8-sig') as f:
            labels = [line.strip() for line in f if line.strip()]
        
        if not labels:
            print("❌ 标签文件为空！")
            return
        
        # 读取CSV文件
        df = pd.read_csv(csv_path, header=None)
        counts = df[0].value_counts().sort_index()
        
        print("\n" + "="*70)
        print("              ✋ 静态手势数据采集统计")
        print("="*70)
        
        total_collected = 0
        
        # 显示每个类别的样本数
        for i in range(len(labels)):
            current = counts.get(i, 0)
            total_collected += current
            
            # 状态图标（根据样本数显示）
            if current >= 500:
                status = "✅"
            elif current >= 100:
                status = "🔄"
            elif current > 0:
                status = "📝"
            else:
                status = "⏳"
            
            # 打印类别信息
            print(f"{status} 类别 {i} ({labels[i]:25s}): {current:5d} 个样本")
        
        print("="*70)
        print(f"📊 总样本数: {total_collected} 个")
        print(f"📋 类别数量: {len(labels)} 个")
        print("="*70)
        
        # 数据平衡性检查
        if len(counts) > 0:
            min_count = counts.min()
            max_count = counts.max()
            balance_ratio = min_count / max_count if max_count > 0 else 0
            
            print(f"\n数据分布:")
            print(f"  • 最少样本类别: {min_count} 个")
            print(f"  • 最多样本类别: {max_count} 个")
            print(f"  • 平衡比例: {balance_ratio:.2%}")
            
            if balance_ratio < 0.5:
                print("  ⚠️  建议: 数据不平衡，建议补充样本较少的类别")
            else:
                print("  ✅ 数据分布较为均衡")
        
    except Exception as e:
        print(f"❌ 读取文件时出错: {e}")
        import traceback
        traceback.print_exc()


def show_data_distribution():
    """显示数据分布统计"""
    csv_path = 'model/point_history_classifier/point_history.csv'
    label_path = 'model/point_history_classifier/point_history_classifier_label.csv'
    
    if not os.path.exists(csv_path):
        print("❌ 数据文件不存在！")
        return
    
    if not os.path.exists(label_path):
        print("❌ 标签文件不存在！")
        return
    
    try:
        # 读取标签文件
        with open(label_path, 'r', encoding='utf-8-sig') as f:
            labels = [line.strip() for line in f if line.strip()]
        
        df = pd.read_csv(csv_path, header=None)
        
        print("\n" + "="*70)
        print("              📈 数据分布详细统计")
        print("="*70)
        
        print(f"\n总样本数: {len(df)}")
        print(f"特征维度: {df.shape[1] - 1}")  # 减去标签列
        print(f"类别数量: {len(labels)}")
        
        print("\n各类别样本分布:")
        counts = df[0].value_counts().sort_index()
        for label_id, count in counts.items():
            percentage = (count / len(df)) * 100
            label_name = labels[label_id] if label_id < len(labels) else f"未知类别{label_id}"
            print(f"  类别 {label_id} ({label_name:20s}): {count:4d} 个样本 ({percentage:5.2f}%)")
        
        # 数据平衡性检查
        if len(counts) > 0:
            min_count = counts.min()
            max_count = counts.max()
            balance_ratio = min_count / max_count if max_count > 0 else 0
            
            print(f"\n数据平衡性:")
            print(f"  最少样本类别: {min_count} 个")
            print(f"  最多样本类别: {max_count} 个")
            print(f"  平衡比例: {balance_ratio:.2%}")
            
            if balance_ratio < 0.5:
                print("  ⚠️  警告: 数据不平衡，建议补充样本较少的类别")
            else:
                print("  ✅ 数据分布较为均衡")
        
        print("="*70)
        
    except Exception as e:
        print(f"❌ 分析数据时出错: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    print("\n" + "="*70)
    print("           手势识别数据采集辅助工具")
    print("="*70)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'static':
            check_static_gesture_progress()
        elif command == 'dynamic':
            check_collection_progress()
        elif command == 'stats':
            show_data_distribution()
        else:
            print(f"❌ 未知命令: {command}")
            print_usage()
    else:
        # 默认显示动态手势进度
        check_collection_progress()
        print("\n" + "-"*70)
        check_static_gesture_progress()


def print_usage():
    """打印使用说明"""
    print("\n使用方法:")
    print("  python collection_helper.py           # 查看所有数据采集进度")
    print("  python collection_helper.py dynamic   # 仅查看动态手势进度")
    print("  python collection_helper.py static    # 仅查看静态手势进度")
    print("  python collection_helper.py stats     # 查看详细统计信息")


if __name__ == '__main__':
    main()

