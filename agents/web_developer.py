"""
JARVIS - Web Developer Agent
Agent for creating websites and web applications with AI
"""

from .base_agent import BaseAgent
from .ai_service import get_ai_service
from typing import Dict, Optional, Any


class WebDeveloperAgent(BaseAgent):
    """Agent for creating websites."""

    def __init__(self):
        super().__init__(
            name="Web Developer",
            description="Creating websites, landing pages, web applications with AI"
        )
        self.capabilities = [
            "Creating HTML/CSS sites",
            "Generating React components",
            "Creating landing pages",
            "Generating JavaScript code",
            "Creating forms and validation",
            "Responsive design",
            "SEO optimization",
            "AI code generation"
        ]
        self.ai_service = get_ai_service()

    def can_handle(self, task: str) -> bool:
        keywords = [
            "site", "landing", "web", "html", "css", "javascript",
            "react", "page", "frontend", "layout", "responsive"
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
            task=task, agent_type="web_developer", context=context
        )

        if result["status"] == "success":
            files = self.ai_service.parse_code_blocks(result["code"])
            return {
                "status": "success", "type": "ai_generated",
                "message": f"AI created web app: {task}", "files": files,
                "tokens_used": result.get("tokens_used", 0),
                "model": result.get("model", "unknown")
            }
        else:
            return self._execute_with_templates(task, context)

    def _execute_with_templates(self, task: str, context: Dict) -> Dict[str, Any]:
        if "landing" in task.lower():
            return self._create_landing(task, context)
        elif "react" in task.lower():
            return self._create_react_component(task, context)
        elif "form" in task.lower():
            return self._create_form(task, context)
        else:
            return self._create_basic_site(task, context)

    def _create_landing(self, task: str, context: Dict) -> Dict[str, Any]:
        html = []
        html.append("<!DOCTYPE html>")
        html.append('<html lang="en">')
        html.append("<head>")
        html.append('    <meta charset="UTF-8">')
        html.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        html.append(f"    <title>{task}</title>")
        html.append('    <link rel="stylesheet" href="style.css">')
        html.append("</head>")
        html.append("<body>")
        html.append("    <header>")
        html.append(f"        <h1>{task}</h1>")
        html.append("    </header>")
        html.append("    <main>")
        html.append("        <p>Site created by JARVIS Web Developer Agent</p>")
        html.append("    </main>")
        html.append('    <script src="script.js"></script>')
        html.append("</body>")
        html.append("</html>")

        css = []
        css.append("/* Styles created by JARVIS Web Developer Agent */")
        css.append("* { margin: 0; padding: 0; box-sizing: border-box; }")
        css.append("body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }")
        css.append("header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; text-align: center; }")
        css.append("main { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }")

        js = []
        js.append("// JavaScript created by JARVIS Web Developer Agent")
        js.append("console.log('JARVIS Web Developer Agent: Site loaded');")
        js.append("document.addEventListener('DOMContentLoaded', () => {")
        js.append("    console.log('DOM ready');")
        js.append("});")

        return {
            "status": "success", "type": "landing",
            "message": f"Creating landing page: {task}",
            "files": {
                "index.html": "\n".join(html),
                "style.css": "\n".join(css),
                "script.js": "\n".join(js)
            }
        }

    def _create_react_component(self, task: str, context: Dict) -> Dict[str, Any]:
        code = []
        code.append("import React from 'react';")
        code.append("")
        code.append("const Component = () => {")
        code.append("    return (")
        code.append('        <div className="component">')
        code.append(f"            <h2>{task}</h2>")
        code.append("            <p>Component created by JARVIS Web Developer Agent</p>")
        code.append("        </div>")
        code.append("    );")
        code.append("};")
        code.append("")
        code.append("export default Component;")

        return {
            "status": "success", "type": "react_component",
            "message": f"Creating React component: {task}",
            "files": {"Component.jsx": "\n".join(code)}
        }

    def _create_form(self, task: str, context: Dict) -> Dict[str, Any]:
        html = []
        html.append("<!DOCTYPE html>")
        html.append('<html lang="en">')
        html.append("<head>")
        html.append('    <meta charset="UTF-8">')
        html.append(f"    <title>{task}</title>")
        html.append("    <style>")
        html.append("        .form-container { max-width: 500px; margin: 2rem auto; padding: 2rem; border: 1px solid #ddd; border-radius: 8px; }")
        html.append("        .form-group { margin-bottom: 1rem; }")
        html.append("        label { display: block; margin-bottom: 0.5rem; font-weight: bold; }")
        html.append("        input, textarea { width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; }")
        html.append("        button { background: #667eea; color: white; padding: 0.75rem 1.5rem; border: none; border-radius: 4px; cursor: pointer; }")
        html.append("    </style>")
        html.append("</head>")
        html.append("<body>")
        html.append('    <div class="form-container">')
        html.append(f"        <h2>{task}</h2>")
        html.append('        <form id="mainForm">')
        html.append('            <div class="form-group">')
        html.append('                <label for="name">Name:</label>')
        html.append('                <input type="text" id="name" name="name" required>')
        html.append("            </div>")
        html.append('            <div class="form-group">')
        html.append('                <label for="email">Email:</label>')
        html.append('                <input type="email" id="email" name="email" required>')
        html.append("            </div>")
        html.append('            <button type="submit">Submit</button>')
        html.append("        </form>")
        html.append("    </div>")
        html.append('    <script src="validation.js"></script>')
        html.append("</body>")
        html.append("</html>")

        js = []
        js.append("// Form validation created by JARVIS Web Developer Agent")
        js.append("document.getElementById('mainForm').addEventListener('submit', (e) => {")
        js.append("    e.preventDefault();")
        js.append("    const name = document.getElementById('name').value;")
        js.append("    const email = document.getElementById('email').value;")
        js.append("    if (!name || !email) { alert('Please fill all fields'); return; }")
        js.append("    alert('Form submitted successfully!');")
        js.append("});")

        return {
            "status": "success", "type": "form",
            "message": f"Creating form: {task}",
            "files": {"form.html": "\n".join(html), "validation.js": "\n".join(js)}
        }

    def _create_basic_site(self, task: str, context: Dict) -> Dict[str, Any]:
        html = []
        html.append("<!DOCTYPE html>")
        html.append('<html lang="en">')
        html.append("<head>")
        html.append('    <meta charset="UTF-8">')
        html.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        html.append(f"    <title>{task}</title>")
        html.append('    <link rel="stylesheet" href="style.css">')
        html.append("</head>")
        html.append("<body>")
        html.append("    <header>")
        html.append(f"        <h1>{task}</h1>")
        html.append("    </header>")
        html.append("    <main>")
        html.append("        <p>Site created by JARVIS Web Developer Agent</p>")
        html.append("    </main>")
        html.append("</body>")
        html.append("</html>")

        css = []
        css.append("/* Styles created by JARVIS Web Developer Agent */")
        css.append("* { margin: 0; padding: 0; box-sizing: border-box; }")
        css.append("body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }")
        css.append("header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; text-align: center; }")

        return {
            "status": "success", "type": "basic_site",
            "message": f"Creating site: {task}",
            "files": {"index.html": "\n".join(html), "style.css": "\n".join(css)}
        }
