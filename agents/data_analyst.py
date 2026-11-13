"""
JARVIS - Data Analyst Agent
Agent for data analysis, statistics, visualization with AI
"""

from .base_agent import BaseAgent
from .ai_service import get_ai_service
from typing import Dict, Optional, Any


class DataAnalystAgent(BaseAgent):
    """Agent for data analysis."""

    def __init__(self):
        super().__init__(
            name="Data Analyst",
            description="Data analysis, statistics, visualization, database work with AI"
        )
        self.capabilities = [
            "CSV/Excel file analysis",
            "Statistical analysis",
            "Creating charts and visualizations",
            "Database work",
            "Data processing (pandas)",
            "Machine learning (basic)",
            "Data cleaning and preparation",
            "AI analytical code generation"
        ]
        self.ai_service = get_ai_service()

    def can_handle(self, task: str) -> bool:
        keywords = [
            "data", "analysis", "statistics", "chart", "visualization",
            "csv", "excel", "pandas", "numpy", "database", "sql",
            "data processing", "report"
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
        result = self.ai_service.generate_code(
            task=task, agent_type="data_analyst", context=context, language="python"
        )

        if result["status"] == "success":
            files = self.ai_service.parse_code_blocks(result["code"])
            return {
                "status": "success", "type": "ai_generated",
                "message": f"AI created analysis code: {task}", "files": files,
                "tokens_used": result.get("tokens_used", 0),
                "model": result.get("model", "unknown")
            }
        else:
            return self._execute_with_templates(task, context)

    def _execute_with_templates(self, task: str, context: Dict) -> Dict[str, Any]:
        if "chart" in task.lower() or "visualization" in task.lower():
            return self._create_visualization(task, context)
        elif "report" in task.lower():
            return self._create_report(task, context)
        else:
            return self._analyze_data(task, context)

    def _create_visualization(self, task: str, context: Dict) -> Dict[str, Any]:
        code = []
        code.append("#!/usr/bin/env python3")
        code.append("# -*- coding: utf-8 -*-")
        code.append(f"# Task: {task}")
        code.append("# Created by JARVIS Data Analyst Agent")
        code.append("")
        code.append("import pandas as pd")
        code.append("import matplotlib.pyplot as plt")
        code.append("import seaborn as sns")
        code.append("")
        code.append("")
        code.append("def create_visualization():")
        code.append("    data = {")
        code.append("        'category': ['A', 'B', 'C', 'D'],")
        code.append("        'values': [10, 25, 15, 30]")
        code.append("    }")
        code.append("    df = pd.DataFrame(data)")
        code.append("    plt.figure(figsize=(10, 6))")
        code.append("    sns.barplot(data=df, x='category', y='values')")
        code.append(f"    plt.title('{task}')")
        code.append("    plt.xlabel('Category')")
        code.append("    plt.ylabel('Value')")
        code.append("    plt.tight_layout()")
        code.append("    plt.savefig('chart.png', dpi=300)")
        code.append("    plt.show()")
        code.append('    print("Visualization saved to chart.png")')
        code.append("")
        code.append("")
        code.append('if __name__ == "__main__":')
        code.append("    create_visualization()")

        return {
            "status": "success", "type": "visualization",
            "message": f"Creating visualization: {task}",
            "files": {"visualization.py": "\n".join(code)}
        }

    def _create_report(self, task: str, context: Dict) -> Dict[str, Any]:
        code = []
        code.append("#!/usr/bin/env python3")
        code.append("# -*- coding: utf-8 -*-")
        code.append(f"# Task: {task}")
        code.append("# Created by JARVIS Data Analyst Agent")
        code.append("")
        code.append("import pandas as pd")
        code.append("from datetime import datetime")
        code.append("")
        code.append("")
        code.append("def generate_report():")
        code.append('    print("JARVIS Data Analyst Agent: Generating report")')
        code.append(f'    print("Task: {task}")')
        code.append('    print("Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))')
        code.append("    ")
        code.append("    data = {")
        code.append("        'metric': ['Sales', 'Clients', 'Conversion'],")
        code.append("        'value': [1000, 150, 15.5]")
        code.append("    }")
        code.append("    df = pd.DataFrame(data)")
        code.append("    report_file = 'report.csv'")
        code.append("    df.to_csv(report_file, index=False, encoding='utf-8')")
        code.append('    print("Report saved to", report_file)')
        code.append("    print(df.to_string(index=False))")
        code.append("")
        code.append("")
        code.append('if __name__ == "__main__":')
        code.append("    generate_report()")

        return {
            "status": "success", "type": "report",
            "message": f"Creating report: {task}",
            "files": {"report.py": "\n".join(code)}
        }

    def _analyze_data(self, task: str, context: Dict) -> Dict[str, Any]:
        code = []
        code.append("#!/usr/bin/env python3")
        code.append("# -*- coding: utf-8 -*-")
        code.append(f"# Task: {task}")
        code.append("# Created by JARVIS Data Analyst Agent")
        code.append("")
        code.append("import pandas as pd")
        code.append("import numpy as np")
        code.append("")
        code.append("")
        code.append("def analyze_data():")
        code.append('    print("JARVIS Data Analyst Agent: Data analysis")')
        code.append(f'    print("Task: {task}")')
        code.append("    data = np.random.randn(100, 3)")
        code.append("    df = pd.DataFrame(data, columns=['A', 'B', 'C'])")
        code.append('    print("\\n=== Statistics ===")')
        code.append("    print(df.describe())")
        code.append('    print("\\n=== Correlation ===")')
        code.append("    print(df.corr())")
        code.append("    df.to_csv('analysis_results.csv', index=False)")
        code.append('    print("Results saved to analysis_results.csv")')
        code.append("")
        code.append("")
        code.append('if __name__ == "__main__":')
        code.append("    analyze_data()")

        return {
            "status": "success", "type": "analysis",
            "message": f"Analyzing data: {task}",
            "files": {"analysis.py": "\n".join(code)}
        }
