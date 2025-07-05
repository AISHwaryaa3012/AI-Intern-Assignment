#!/usr/bin/env python3
import asyncio
import json
import sys
from typing import Any, Dict, List
import random

class EduChain:
    def __init__(self):
        self.mcq_templates = [
            {
                "template": "What is {concept} used for in {topic}?",
                "options": [
                    "A. {opt1}", "B. {opt2}", "C. {opt3}", "D. {opt4}"
                ],
                "answer": "A"
            }
        ]
        
        self.lesson_plan_template = {
            "topic": "{topic}",
            "objectives": [
                "Understand {topic} fundamentals",
                "Apply {topic} in real-world scenarios"
            ],
            "activities": [
                "Lecture: {topic} basics",
                "Hands-on {topic} exercises"
            ]
        }

    def generate_mcqs(self, topic="Python", count=5):
        concepts = ["loops", "functions", "variables", "classes"]
        return {
            "questions": [{
                "question": f"What is {random.choice(concepts)} used for in {topic}?",
                "options": [
                    "A. Code repetition",
                    "B. Data storage", 
                    "C. Both A and B",
                    "D. None"
                ],
                "answer": "A"
            } for _ in range(count)]
        }

    def generate_lesson_plan(self, subject="Math"):
        plan = self.lesson_plan_template.copy()
        plan["topic"] = subject
        plan["objectives"] = [obj.format(topic=subject) for obj in plan["objectives"]]
        plan["activities"] = [act.format(topic=subject) for act in plan["activities"]]
        return plan

class MCPServer:
    def __init__(self):
        self.educhain = EduChain()
        self.tools = [
            {
                "name": "generate_mcqs",
                "description": "Generate multiple choice questions for a given topic",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The topic to generate questions for",
                            "default": "Python"
                        },
                        "count": {
                            "type": "integer",
                            "description": "Number of questions to generate",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 20
                        }
                    }
                }
            },
            {
                "name": "generate_lesson_plan",
                "description": "Generate a lesson plan for a given subject",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "subject": {
                            "type": "string",
                            "description": "The subject to create a lesson plan for",
                            "default": "Math"
                        }
                    }
                }
            }
        ]

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        method = request.get("method")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "python-edu-server",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {"tools": self.tools}
            }
        
        elif method == "tools/call":
            params = request.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "generate_mcqs":
                topic = arguments.get("topic", "Python")
                count = arguments.get("count", 5)
                result = self.educhain.generate_mcqs(topic, count)
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
            
            elif tool_name == "generate_lesson_plan":
                subject = arguments.get("subject", "Math")
                result = self.educhain.generate_lesson_plan(subject)
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32601, "message": f"Unknown method: {method}"}
            }

    async def run(self):
        server = MCPServer()
        
        async def handle_stdin():
            while True:
                try:
                    line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                    if not line:
                        break
                    
                    request = json.loads(line.strip())
                    response = await server.handle_request(request)
                    
                    print(json.dumps(response), flush=True)
                    
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "error": {"code": -32603, "message": str(e)}
                    }
                    if "id" in locals() and "request" in locals():
                        error_response["id"] = request.get("id")
                    print(json.dumps(error_response), flush=True)
        
        await handle_stdin()

if __name__ == "__main__":
    server = MCPServer()
    asyncio.run(server.run())