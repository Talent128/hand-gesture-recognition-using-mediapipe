#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
==========================================
配置管理模块
==========================================
功能：管理手势与快捷键映射配置
"""

import json
import os


class ConfigManager:
    """配置管理类"""
    
    DEFAULT_CONFIG = {
        'ppt': {
            'gestures': {
                'Thumbs Down': 'next_slide',
                'Thumbs Up': 'prev_slide',
                'Open': 'first_slide',
                'Close': 'last_slide',
                'Move Up': 'scroll_up',
                'Move Down': 'scroll_down'
            },
            'keyboard_shortcuts': {
                'next_slide': 'ArrowRight',
                'prev_slide': 'ArrowLeft',
                'first_slide': 'Home',
                'last_slide': 'End',
                'scroll_up': 'PageUp',
                'scroll_down': 'PageDown'
            }
        },
        'video': {
            'gestures': {
                'Open': 'play',
                'Close': 'pause',
                'OK': 'restart',
                'Peace': 'fullscreen',
                'Quiet Coyote': 'exit_fullscreen',
                'Thumbs Up': 'volume_up',
                'Thumbs Down': 'volume_down',
                'Move Left': 'seek_backward',
                'Move Right': 'seek_forward',
                'Clockwise': 'speed_up',
                'Counter Clockwise': 'speed_down'
            },
            'keyboard_shortcuts': {
                'play': 'Space',
                'pause': 'Space',
                'restart': 'r',
                'fullscreen': 'f',
                'exit_fullscreen': 'Escape',
                'volume_up': 'ArrowUp',
                'volume_down': 'ArrowDown',
                'seek_backward': 'ArrowLeft',
                'seek_forward': 'ArrowRight',
                'speed_up': '>',
                'speed_down': '<'
            }
        }
    }
    
    def __init__(self, config_file=None):
        """初始化配置管理器"""
        if config_file is None:
            # 使用绝对路径，确保无论从哪里启动都能找到配置文件
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, '../..'))
            config_file = os.path.join(project_root, 'gesture_control_app', 'config', 'gesture_mapping.json')
        self.config_file = config_file
        print(f"[ConfigManager] 配置文件路径: {self.config_file}")
        print(f"[ConfigManager] 配置文件是否存在: {os.path.exists(self.config_file)}")
        self.config = self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    print(f"[ConfigManager] 成功加载配置文件")
                    print(f"[ConfigManager] Video手势数量: {len(config.get('video', {}).get('gestures', {}))}")
                    print(f"[ConfigManager] Video快捷键数量: {len(config.get('video', {}).get('keyboard_shortcuts', {}))}")
                    if 'Quiet Coyote' in config.get('video', {}).get('gestures', {}):
                        print(f"[ConfigManager] ✅ Quiet Coyote 存在于配置中")
                    else:
                        print(f"[ConfigManager] ❌ Quiet Coyote 不存在于配置中")
                    if 'exit_fullscreen' in config.get('video', {}).get('keyboard_shortcuts', {}):
                        print(f"[ConfigManager] ✅ exit_fullscreen 存在于配置中")
                    else:
                        print(f"[ConfigManager] ❌ exit_fullscreen 不存在于配置中")
                    return config
            except Exception as e:
                print(f"[ConfigManager] 加载配置文件失败: {e}, 使用默认配置")
                return self.DEFAULT_CONFIG.copy()
        else:
            # 创建默认配置文件
            print(f"[ConfigManager] 配置文件不存在，创建默认配置文件")
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
    
    def _save_config(self, config):
        """保存配置文件"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def get_config(self, module=None):
        """
        获取配置
        
        Args:
            module: 模块名称 ('ppt' 或 'video')，None则返回全部配置
        
        Returns:
            配置字典
        """
        if module:
            return self.config.get(module, {})
        return self.config
    
    def update_config(self, module, config_data):
        """
        更新配置
        
        Args:
            module: 模块名称 ('ppt' 或 'video')
            config_data: 新的配置数据
        
        Returns:
            bool: 是否成功
        """
        try:
            if module in self.config:
                self.config[module].update(config_data)
            else:
                self.config[module] = config_data
            
            self._save_config(self.config)
            return True
        except Exception as e:
            print(f"更新配置失败: {e}")
            return False
    
    def reset_config(self, module=None):
        """
        重置配置为默认值
        
        Args:
            module: 模块名称，None则重置全部配置
        
        Returns:
            bool: 是否成功
        """
        try:
            if module:
                self.config[module] = self.DEFAULT_CONFIG[module].copy()
            else:
                self.config = self.DEFAULT_CONFIG.copy()
            
            self._save_config(self.config)
            return True
        except Exception as e:
            print(f"重置配置失败: {e}")
            return False
    
    def get_action_for_gesture(self, module, gesture_name):
        """
        获取手势对应的操作
        
        Args:
            module: 模块名称 ('ppt' 或 'video')
            gesture_name: 手势名称
        
        Returns:
            str: 操作名称
        """
        gestures = self.config.get(module, {}).get('gestures', {})
        return gestures.get(gesture_name, None)
    
    def get_keyboard_shortcut(self, module, action):
        """
        获取操作对应的键盘快捷键
        
        Args:
            module: 模块名称 ('ppt' 或 'video')
            action: 操作名称
        
        Returns:
            str: 快捷键
        """
        shortcuts = self.config.get(module, {}).get('keyboard_shortcuts', {})
        return shortcuts.get(action, None)

