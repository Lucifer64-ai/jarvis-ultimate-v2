"""
JARVIS - Designer Agent
Agent for UI/UX design, layouts and graphic elements with AI
"""

from .base_agent import BaseAgent
from .ai_service import get_ai_service
from typing import Dict, Optional, Any


class DesignerAgent(BaseAgent):
    """Agent for UI/UX design."""

    def __init__(self):
        super().__init__(
            name="Designer",
            description="UI/UX design, layouts, graphic elements with AI"
        )
        self.capabilities = [
            "Creating UI layouts",
            "Generating CSS styles",
            "Interface design",
            "Creating color schemes",
            "Generating SVG graphics",
            "Responsive design",
            "AI design generation"
        ]
        self.ai_service = get_ai_service()

    def can_handle(self, task: str) -> bool:
        keywords = [
            "design", "layout", "ui", "ux", "interface", "style", "colors",
            "svg", "graphics", "icon", "logo", "appearance", "mockup"
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
            task=task, agent_type="designer", context=context, language="css"
        )

        if result["status"] == "success":
            files = self.ai_service.parse_code_blocks(result["code"])
            return {
                "status": "success", "type": "ai_generated",
                "message": f"AI created design: {task}", "files": files,
                "tokens_used": result.get("tokens_used", 0),
                "model": result.get("model", "unknown")
            }
        else:
            return self._execute_with_templates(task, context)

    def _execute_with_templates(self, task: str, context: Dict) -> Dict[str, Any]:
        if "color" in task.lower() or "palette" in task.lower():
            return self._create_color_scheme(task, context)
        elif "svg" in task.lower() or "icon" in task.lower():
            return self._create_svg(task, context)
        else:
            return self._create_ui_design(task, context)

    def _create_color_scheme(self, task: str, context: Dict) -> Dict[str, Any]:
        css = []
        css.append("/* Color scheme: " + task + " */")
        css.append("/* Created by JARVIS Designer Agent */")
        css.append("")
        css.append(":root {")
        css.append("    --primary-color: #667eea;")
        css.append("    --secondary-color: #764ba2;")
        css.append("    --accent-color: #f093fb;")
        css.append("    --background-color: #f5f7fa;")
        css.append("    --text-color: #333333;")
        css.append("    --text-light: #666666;")
        css.append("    --border-color: #e0e0e0;")
        css.append("    --success-color: #4caf50;")
        css.append("    --warning-color: #ff9800;")
        css.append("    --error-color: #f44336;")
        css.append("}")
        css.append("")
        css.append("body {")
        css.append("    background-color: var(--background-color);")
        css.append("    color: var(--text-color);")
        css.append("}")

        return {
            "status": "success", "type": "color_scheme",
            "message": f"Creating color scheme: {task}",
            "files": {"colors.css": "\n".join(css)}
        }

    def _create_svg(self, task: str, context: Dict) -> Dict[str, Any]:
        svg = []
        svg.append('<?xml version="1.0" encoding="UTF-8"?>')
        svg.append('<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">')
        svg.append(f"    <!-- {task} -->")
        svg.append("    <!-- Created by JARVIS Designer Agent -->")
        svg.append('    <circle cx="32" cy="32" r="30" fill="#667eea" opacity="0.1"/>')
        svg.append('    <path d="M32 16 L40 28 L32 24 L24 28 Z" fill="#667eea"/>')
        svg.append('    <circle cx="32" cy="36" r="8" fill="#764ba2"/>')
        svg.append('</svg>')

        return {
            "status": "success", "type": "svg",
            "message": f"Creating SVG: {task}",
            "files": {"icon.svg": "\n".join(svg)}
        }

    def _create_ui_design(self, task: str, context: Dict) -> Dict[str, Any]:
        css = []
        css.append("/* UI Design: " + task + " */")
        css.append("/* Created by JARVIS Designer Agent */")
        css.append("")
        css.append("* { margin: 0; padding: 0; box-sizing: border-box; }")
        css.append("")
        css.append("body {")
        css.append("    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;")
        css.append("    line-height: 1.6;")
        css.append("    color: #333;")
        css.append("    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);")
        css.append("    min-height: 100vh;")
        css.append("}")
        css.append("")
        css.append(".container { max-width: 1200px; margin: 0 auto; padding: 2rem; }")
        css.append("")
        css.append(".card {")
        css.append("    background: white;")
        css.append("    border-radius: 12px;")
        css.append("    padding: 2rem;")
        css.append("    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);")
        css.append("    margin-bottom: 2rem;")
        css.append("}")
        css.append("")
        css.append(".btn {")
        css.append("    display: inline-block;")
        css.append("    padding: 0.75rem 1.5rem;")
        css.append("    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);")
        css.append("    color: white;")
        css.append("    border-radius: 8px;")
        css.append("    border: none;")
        css.append("    cursor: pointer;")
        css.append("}")

        html = []
        html.append("<!DOCTYPE html>")
        html.append('<html lang="en">')
        html.append("<head>")
        html.append('    <meta charset="UTF-8">')
        html.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        html.append(f"    <title>{task}</title>")
        html.append('    <link rel="stylesheet" href="design.css">')
        html.append("</head>")
        html.append("<body>")
        html.append('    <div class="container">')
        html.append("        <header>")
        html.append(f"            <h1>{task}</h1>")
        html.append("            <p>UI design created by JARVIS Designer Agent</p>")
        html.append("        </header>")
        html.append('        <main class="grid">')
        html.append('            <div class="card">')
        html.append("                <h2>Component 1</h2>")
        html.append("                <p>Description</p>")
        html.append('                <button class="btn">Action</button>')
        html.append("            </div>")
        html.append("        </main>")
        html.append("    </div>")
        html.append("</body>")
        html.append("</html>")

        return {
            "status": "success", "type": "ui_design",
            "message": f"Creating UI design: {task}",
            "files": {"design.css": "\n".join(css), "layout.html": "\n".join(html)}
        }
