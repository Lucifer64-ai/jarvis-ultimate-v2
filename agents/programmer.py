"""
JARVIS - Programmer Agent
Agent for writing code in various programming languages with AI
"""

from .base_agent import BaseAgent
from .ai_service import get_ai_service
from typing import Dict, Optional, Any


class ProgrammerAgent(BaseAgent):
    """Agent for writing code."""

    def __init__(self):
        super().__init__(
            name="Programmer",
            description="Writing code in Python, JavaScript, C++, Java and other languages with AI"
        )
        self.capabilities = [
            "Writing Python code",
            "Creating JavaScript/TypeScript",
            "Generating C++ code",
            "Creating Java applications",
            "Writing SQL queries",
            "Creating automation scripts",
            "Code refactoring",
            "Performance optimization",
            "AI code generation"
        ]
        self.ai_service = get_ai_service()

    def can_handle(self, task: str) -> bool:
        keywords = [
            "code", "program", "script", "python", "javascript", "c++", "java",
            "function", "class", "algorithm", "write code", "development",
            "programming", "sql", "database"
        ]
        task_lower = task.lower()
        return any(keyword in task_lower for keyword in keywords)

    def execute_task(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        context = context or {}

        if self.ai_service.client:
            return self._execute_with_ai(task, context)
        else:
            return self._execute_with_templates(task, context)

    def _execute_with_ai(self, task: str, context: Dict) -> Dict[str, Any]:
        language = self._detect_language(task)
        result = self.ai_service.generate_code(
            task=task, agent_type="programmer", context=context, language=language
        )

        if result["status"] == "success":
            files = self.ai_service.parse_code_blocks(result["code"])
            return {
                "status": "success", "type": "ai_generated",
                "message": f"AI wrote code: {task}", "files": files,
                "language": language, "tokens_used": result.get("tokens_used", 0),
                "model": result.get("model", "unknown")
            }
        else:
            return self._execute_with_templates(task, context)

    def _execute_with_templates(self, task: str, context: Dict) -> Dict[str, Any]:
        if "python" in task.lower():
            return self._create_python(task, context)
        elif "javascript" in task.lower() or "js" in task.lower():
            return self._create_javascript(task, context)
        elif "sql" in task.lower():
            return self._create_sql(task, context)
        else:
            return self._create_generic_code(task, context)

    def _detect_language(self, task: str) -> str:
        task_lower = task.lower()
        if "python" in task_lower: return "python"
        elif "javascript" in task_lower or "js" in task_lower: return "javascript"
        elif "typescript" in task_lower or "ts" in task_lower: return "typescript"
        elif "c++" in task_lower or "cpp" in task_lower: return "cpp"
        elif "java" in task_lower: return "java"
        elif "sql" in task_lower: return "sql"
        else: return "python"

    def _create_python(self, task: str, context: Dict) -> Dict[str, Any]:
        code = []
        code.append("#!/usr/bin/env python3")
        code.append("# -*- coding: utf-8 -*-")
        code.append(f"# Task: {task}")
        code.append("# Created by JARVIS Programmer Agent")
        code.append("")
        code.append("import sys")
        code.append("from typing import List, Dict, Optional")
        code.append("")
        code.append("")
        code.append("def main():")
        code.append("    print('JARVIS Programmer Agent: Starting program')")
        code.append(f"    print('Task: {task}')")
        code.append("    # Main logic here")
        code.append("    pass")
        code.append("")
        code.append("")
        code.append('if __name__ == "__main__":')
        code.append("    main()")

        return {
            "status": "success", "type": "python_code",
            "message": f"Creating Python code: {task}",
            "files": {"main.py": "\n".join(code)}
        }

    def _create_javascript(self, task: str, context: Dict) -> Dict[str, Any]:
        code = []
        code.append(f"// Task: {task}")
        code.append("// Created by JARVIS Programmer Agent")
        code.append("")
        code.append("class TaskExecutor {")
        code.append("    constructor() {")
        code.append(f'        this.task = "{task}";')
        code.append('        console.log("JARVIS Programmer Agent: Initialized");')
        code.append("    }")
        code.append("    ")
        code.append("    execute() {")
        code.append('        console.log("Executing task: " + this.task);')
        code.append("    }")
        code.append("}")
        code.append("")
        code.append("const executor = new TaskExecutor();")
        code.append("executor.execute();")

        return {
            "status": "success", "type": "javascript_code",
            "message": f"Creating JavaScript code: {task}",
            "files": {"script.js": "\n".join(code)}
        }

    def _create_sql(self, task: str, context: Dict) -> Dict[str, Any]:
        code = []
        code.append(f"-- Task: {task}")
        code.append("-- Created by JARVIS Programmer Agent")
        code.append("")
        code.append("SELECT *")
        code.append("FROM users")
        code.append("WHERE active = true")
        code.append("ORDER BY created_at DESC")
        code.append("LIMIT 100;")

        return {
            "status": "success", "type": "sql_query",
            "message": f"Creating SQL query: {task}",
            "files": {"query.sql": "\n".join(code)}
        }

    def _create_generic_code(self, task: str, context: Dict) -> Dict[str, Any]:
        code = []
        code.append(f"// Task: {task}")
        code.append("// Created by JARVIS Programmer Agent")
        code.append("")
        code.append("function main() {")
        code.append('    console.log("JARVIS Programmer Agent");')
        code.append(f'    console.log("Task: {task}");')
        code.append("}")
        code.append("")
        code.append("main();")

        return {
            "status": "success", "type": "generic_code",
            "message": f"Creating code: {task}",
            "files": {"code.txt": "\n".join(code)}
        }
