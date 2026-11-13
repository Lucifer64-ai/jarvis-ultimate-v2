"""
 °¿¾·на²°½¸µ ¿°µ½¾² JARVIS
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import re


class PatternRecognizer:
    """ °¿¾·на²°½¸µ ¿°µ½¾² ² ¿¾²µ´µ½¸¸ ¿¾»·¾²°µ»."""

    def __init__(self, brain):
        self.brain = brain
        self.patterns_file = Path("data/patterns.json")
        self.patterns_file.parent.mkdir(exist_ok=True)
        self.patterns: Dict = self._load_patterns()
        self.suggestions: List[Dict] = []

    def _load_patterns(self) -> Dict:
        """°³·º° ¿°µ½¾²."""
        if self.patterns_file.exists():
            with open(self.patterns_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "recurring_commands": {},
            "time_based_patterns": {},
            "sequence_patterns": {},
            "learned_automations": []
        }

    def _save_patterns(self):
        """¡¾°ни½¸µ ¿°µ½¾²."""
        with open(self.patterns_file, 'w', encoding='utf-8') as f:
            json.dump(self.patterns, f, ensure_ascii=False, indent=2)

    def analyze_command_history(self, history: List[Dict]) -> List[Dict]:
        """на»из ¸¾¸¸ команд для ²²»µ½¸ ¿°µ½¾²."""
        suggestions = []
        
        # 1. ¾²¾¸µ команд ² ¾´½¾ ²µ¼
        time_patterns = self._detect_time_patterns(history)
        suggestions.extend(time_patterns)
        
        # 2. ¾»µ´¾²°µ»½¾¸ команд
        sequence_patterns = self._detect_sequence_patterns(history)
        suggestions.extend(sequence_patterns)
        
        # 3. §°¾ ¸¿¾»·µ¼µ команд
        frequent_commands = self._detect_frequent_commands(history)
        suggestions.extend(frequent_commands)
        
        self.suggestions = suggestions
        self._save_patterns()
        
        return suggestions

    def _detect_time_patterns(self, history: List[Dict]) -> List[Dict]:
        """±на¶µ½¸µ ²µ¼µ½½ ¿°µ½¾²."""
        suggestions = []
        time_groups = defaultdict(list)
        
        for entry in history:
            try:
                dt = datetime.fromisoformat(entry["timestamp"])
                hour = dt.hour
                minute = dt.minute
                # ¿¿¸µ¼ ¿¾ 15-¼¸½½¼ ¸½µ²°»°¼
                time_slot = f"{hour:02d}:{(minute // 15) * 15:02d}"
                time_groups[time_slot].append(entry["command"])
            except:
                continue
        
        # µ¼ команд, º¾¾µ ¿¾²¾ ² ¾´½¾ ²µ¼
        for time_slot, commands in time_groups.items():
            command_counts = defaultdict(int)
            for cmd in commands:
                command_counts[cmd] += 1
            
            for cmd, count in command_counts.items():
                if count >= 3:  # »¸ команд° ¿¾²¾µ 3+ °·° ² ¾ ²µ¼
                    suggestions.append({
                        "type": "time_pattern",
                        "command": cmd,
                        "time": time_slot,
                        "count": count,
                        "suggestion": f" °¾ ³¾²¾¸µ '{cmd}' ² {time_slot}. ¡¾·´° °²¾¼°¸µº¾µ °¿¸°½¸µ?",
                        "action": "create_schedule"
                    })
        
        return suggestions

    def _detect_sequence_patterns(self, history: List[Dict]) -> List[Dict]:
        """±на¶µ½¸µ ¿¾»µ´¾²°µ»½¾µ¹ команд."""
        suggestions = []
        
        if len(history) < 3:
            return suggestions
        
        # µ¼ ¿¾²¾¸µ ¿¾»µ´¾²°µ»½¾¸ из 2-3 команд
        for seq_length in [2, 3]:
            sequences = defaultdict(int)
            
            for i in range(len(history) - seq_length + 1):
                seq = tuple(entry["command"] for entry in history[i:i+seq_length])
                sequences[seq] += 1
            
            for seq, count in sequences.items():
                if count >= 2:  # »¸ ¿¾»µ´¾²°µ»½¾ ¿¾²¾µ 2+ °·°
                    suggestions.append({
                        "type": "sequence_pattern",
                        "sequence": list(seq),
                        "count": count,
                        "suggestion": f" °¾ ²¿¾»½µµ ¿¾»µ´¾²°µ»½¾: {' ¢ '.join(seq)}. ¡¾·´° ¼°º¾?",
                        "action": "create_macro"
                    })
        
        return suggestions

    def _detect_frequent_commands(self, history: List[Dict]) -> List[Dict]:
        """±на¶µ½¸µ °¾ ¸¿¾»·µ¼ команд."""
        suggestions = []
        command_counts = defaultdict(int)
        
        for entry in history:
            command_counts[entry["command"]] += 1
        
        for cmd, count in command_counts.items():
            if count >= 10:  # »¸ команд° ¸¿¾»·µ 10+ °·
                suggestions.append({
                    "type": "frequent_command",
                    "command": cmd,
                    "count": count,
                    "suggestion": f"¾¼°½´° '{cmd}' ¸¿¾»·µ ¾µ½ °¾ ({count} °·). ¡¾·´° ±¹ °»¸°?",
                    "action": "create_alias"
                })
        
        return suggestions

    def get_suggestions(self) -> List[Dict]:
        """¾»µ½¸µ µº¸ ¿µ´»¾¶µ½¸¹."""
        return self.suggestions

    def accept_suggestion(self, index: int) -> Dict:
        """¸½¸µ ¿µ´»¾¶µ½¸."""
        if index >= len(self.suggestions):
            return {"status": "error", "message": "µ´»¾¶µ½¸µ ни на¹´µ½¾"}
        
        suggestion = self.suggestions[index]
        action = suggestion["action"]
        
        if action == "create_schedule":
            # ¡¾·´°½¸µ °¿¸°½¸
            return {
                "status": "ok",
                "message": f" °¿¸°½¸µ ¾·´°½¾ для команд '{suggestion['command']}' ² {suggestion['time']}",
                "action_taken": "schedule_created"
            }
        
        elif action == "create_macro":
            # ¡¾·´°½¸µ ¼°º¾°
            return {
                "status": "ok",
                "message": f"°º¾ ¾·´°½ для ¿¾»µ´¾²°µ»½¾¸: {' ¢ '.join(suggestion['sequence'])}",
                "action_taken": "macro_created"
            }
        
        elif action == "create_alias":
            # ¡¾·´°½¸µ °»¸°°
            return {
                "status": "ok",
                "message": f"µ´»¾¶¸µ °»¸° для команд '{suggestion['command']}'",
                "action_taken": "alias_pending"
            }
        
        return {"status": "error", "message": "µиз²µ½¾µ ´µ¹²¸µ"}

    def learn_automation(self, trigger: str, action: str) -> Dict:
        """±µ½¸µ ½¾²¾¹ °²¾¼°из°¸¸."""
        automation = {
            "trigger": trigger,
            "action": action,
            "created": datetime.now().isoformat(),
            "usage_count": 0
        }
        
        self.patterns["learned_automations"].append(automation)
        self._save_patterns()
        
        return {
            "status": "ok",
            "message": f"²¾¼°из°¸ ¾±µна: '{trigger}' ¢ '{action}'"
        }

    def get_learned_automations(self) -> List[Dict]:
        """¾»µ½¸µ ¾±µ½½ °²¾¼°из°¸¹."""
        return self.patterns.get("learned_automations", [])
