"""
JARVIS - DevOps Agent
Agent for CI/CD, Docker, deployment automation with AI
"""

from .base_agent import BaseAgent
from .ai_service import get_ai_service
from typing import Dict, Optional, Any


class DevOpsAgent(BaseAgent):
    """Agent for DevOps tasks."""

    def __init__(self):
        super().__init__(
            name="DevOps",
            description="CI/CD, Docker, deployment automation with AI"
        )
        self.capabilities = [
            "Creating Docker files",
            "Generating CI/CD configs",
            "Deployment automation",
            "Creating bash scripts",
            "Server configuration",
            "Monitoring and logging",
            "AI infrastructure generation"
        ]
        self.ai_service = get_ai_service()

    def can_handle(self, task: str) -> bool:
        keywords = [
            "docker", "ci/cd", "deployment", "deploy",
            "automation", "bash", "script", "server", "nginx",
            "github actions", "gitlab ci", "infrastructure"
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
            task=task, agent_type="devops", context=context, language="yaml"
        )

        if result["status"] == "success":
            files = self.ai_service.parse_code_blocks(result["code"])
            return {
                "status": "success", "type": "ai_generated",
                "message": f"AI created DevOps config: {task}", "files": files,
                "tokens_used": result.get("tokens_used", 0),
                "model": result.get("model", "unknown")
            }
        else:
            return self._execute_with_templates(task, context)

    def _execute_with_templates(self, task: str, context: Dict) -> Dict[str, Any]:
        if "docker" in task.lower():
            return self._create_docker(task, context)
        elif "ci" in task.lower() or "cd" in task.lower() or "github actions" in task.lower():
            return self._create_cicd(task, context)
        else:
            return self._create_deployment(task, context)

    def _create_docker(self, task: str, context: Dict) -> Dict[str, Any]:
        dockerfile = []
        dockerfile.append("# Dockerfile for: " + task)
        dockerfile.append("# Created by JARVIS DevOps Agent")
        dockerfile.append("")
        dockerfile.append("FROM python:3.11-slim")
        dockerfile.append("")
        dockerfile.append("WORKDIR /app")
        dockerfile.append("")
        dockerfile.append("# Install dependencies")
        dockerfile.append("COPY requirements.txt .")
        dockerfile.append("RUN pip install --no-cache-dir -r requirements.txt")
        dockerfile.append("")
        dockerfile.append("# Copy code")
        dockerfile.append("COPY . .")
        dockerfile.append("")
        dockerfile.append("# Expose port")
        dockerfile.append("EXPOSE 8000")
        dockerfile.append("")
        dockerfile.append("# Run command")
        dockerfile.append('CMD ["python", "main.py"]')

        compose = []
        compose.append("# Docker Compose for: " + task)
        compose.append("# Created by JARVIS DevOps Agent")
        compose.append("")
        compose.append("version: '3.8'")
        compose.append("")
        compose.append("services:")
        compose.append("  app:")
        compose.append("    build: .")
        compose.append("    ports:")
        compose.append('      - "8000:8000"')
        compose.append("    environment:")
        compose.append("      - ENV=production")
        compose.append("    restart: unless-stopped")

        return {
            "status": "success", "type": "docker",
            "message": f"Creating Docker config: {task}",
            "files": {"Dockerfile": "\n".join(dockerfile), "docker-compose.yml": "\n".join(compose)}
        }

    def _create_cicd(self, task: str, context: Dict) -> Dict[str, Any]:
        workflow = []
        workflow.append("# GitHub Actions CI/CD for: " + task)
        workflow.append("# Created by JARVIS DevOps Agent")
        workflow.append("")
        workflow.append("name: CI/CD Pipeline")
        workflow.append("")
        workflow.append("on:")
        workflow.append("  push:")
        workflow.append("    branches: [ main, develop ]")
        workflow.append("  pull_request:")
        workflow.append("    branches: [ main ]")
        workflow.append("")
        workflow.append("jobs:")
        workflow.append("  test:")
        workflow.append("    runs-on: ubuntu-latest")
        workflow.append("    steps:")
        workflow.append("    - uses: actions/checkout@v3")
        workflow.append("    - name: Set up Python")
        workflow.append("      uses: actions/setup-python@v4")
        workflow.append("      with:")
        workflow.append("        python-version: '3.11'")
        workflow.append("    - name: Install dependencies")
        workflow.append("      run: |")
        workflow.append("        python -m pip install --upgrade pip")
        workflow.append("        pip install -r requirements.txt")
        workflow.append("    - name: Run tests")
        workflow.append("      run: pytest")

        return {
            "status": "success", "type": "cicd",
            "message": f"Creating CI/CD config: {task}",
            "files": {".github/workflows/ci.yml": "\n".join(workflow)}
        }

    def _create_deployment(self, task: str, context: Dict) -> Dict[str, Any]:
        script = []
        script.append("#!/bin/bash")
        script.append("# Deployment script for: " + task)
        script.append("# Created by JARVIS DevOps Agent")
        script.append("")
        script.append("set -e")
        script.append("")
        script.append('echo "Starting deployment: ' + task + '"')
        script.append("")
        script.append("# Update code")
        script.append('echo "Updating code..."')
        script.append("git pull origin main")
        script.append("")
        script.append("# Install dependencies")
        script.append('echo "Installing dependencies..."')
        script.append("pip install -r requirements.txt")
        script.append("")
        script.append("# Restart service")
        script.append('echo "Restarting service..."')
        script.append("systemctl restart jarvis")
        script.append("")
        script.append('echo "Deployment completed!"')

        return {
            "status": "success", "type": "deployment",
            "message": f"Creating deployment script: {task}",
            "files": {"deploy.sh": "\n".join(script)}
        }
