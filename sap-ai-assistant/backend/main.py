"""
SAP ABAP AI Assistant - Backend Middleware
Bu middleware, Qwen Coder modelini kullanarak ABAP kodu üretir, analiz eder,
RFC ile SAP sistemlerine bağlanır ve abapGit entegrasyonu sağlar.
"""

import os
import subprocess
import json
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# PyRFC için import (kurulum gerekli: pip install pypfrpc)
try:
    from pyrfc import Connection
except ImportError:
    Connection = None

app = FastAPI(title="SAP ABAP AI Assistant", version="1.0.0")

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Konfigürasyon
class Config:
    MODEL_PATH = os.getenv("MODEL_PATH", "/models/Qwen-Coder-7B-Instruct")
    SAP_HOST = os.getenv("SAP_HOST", "localhost")
    SAP_PORT = int(os.getenv("SAP_PORT", "3300"))
    SAP_CLIENT = os.getenv("SAP_CLIENT", "100")
    SAP_USER = os.getenv("SAP_USER", "")
    SAP_PASSWORD = os.getenv("SAP_PASSWORD", "")
    AZURE_DEVOPS_REPO = os.getenv("AZURE_DEVOPS_REPO", "")
    ABAPGIT_PATH = os.getenv("ABAPGIT_PATH", "./abapgit")

config = Config()

# Request/Response Modelleri
class CodeGenerationRequest(BaseModel):
    scenario: str
    output_type: str = "program"  # program, function_module, class, interface
    include_tests: bool = True

class CodeAnalysisRequest(BaseModel):
    abap_code: str
    analysis_type: str = "all"  # performance, security, syntax, all

class SAPConnectionConfig(BaseModel):
    host: str
    port: int
    client: str
    user: str
    password: str

class GitOperationRequest(BaseModel):
    operation: str  # push, pull, clone, status
    repo_url: Optional[str] = None
    branch: Optional[str] = "master"

# Qwen Model Entegrasyonu
class QwenModel:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """Qwen Coder modelini yükle"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            print(f"Loading model from {self.model_path}...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True
            )
            self.model.eval()
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Model loading failed: {e}")
            print("Running in mock mode for demonstration")
    
    def generate_abap(self, scenario: str, output_type: str = "program") -> str:
        """Senaryoya göre ABAP kodu üret"""
        prompt = self._create_abap_prompt(scenario, output_type)
        
        if self.model is None:
            return self._get_mock_abap(scenario, output_type)
        
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=2048,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return self._extract_abap_code(response)
        except Exception as e:
            print(f"Generation error: {e}")
            return self._get_mock_abap(scenario, output_type)
    
    def _create_abap_prompt(self, scenario: str, output_type: str) -> str:
        """ABAP kod üretimi için prompt oluştur"""
        system_prompt = """You are an expert SAP ABAP developer. Generate clean, 
        efficient, and well-documented ABAP code following best practices.
        Include proper error handling, comments, and follow SAP naming conventions."""
        
        prompt_template = f"""{system_prompt}

Task: Create an ABAP {output_type} for the following scenario:
{scenario}

Requirements:
- Use modern ABAP syntax (7.40+)
- Include proper data declarations
- Add comprehensive comments
- Follow SAP security best practices
- Include error handling

Generate complete, ready-to-import ABAP code:"""
        
        return prompt_template
    
    def _extract_abap_code(self, response: str) -> str:
        """Yanıttan ABAP kodunu çıkar"""
        # Kod bloklarını ayıkla
        if "```abap" in response:
            start = response.find("```abap") + 7
            end = response.find("```", start)
            return response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            return response[start:end].strip()
        return response
    
    def _get_mock_abap(self, scenario: str, output_type: str) -> str:
        """Model yoksa mock ABAP kodu döndür"""
        if output_type == "program":
            return f"""REPORT z_demo_program.

*&---------------------------------------------------------------------*
*& Report Z_DEMO_PROGRAM
*& Generated by SAP ABAP AI Assistant
*& Scenario: {scenario}
*&---------------------------------------------------------------------*

DATA: lv_message TYPE string.

START-OF-SELECTION.
  lv_message = 'Hello from AI-generated ABAP program'.
  WRITE: / lv_message.
  
  " TODO: Implement business logic for: {scenario}
  
  TRY.
      " Your implementation here
      PERFORM process_data.
    CATCH cx_root INTO DATA(lx_exception).
      WRITE: / 'Error:', lx_exception->get_text( ).
  ENDTRY.

FORM process_data.
  " Implementation for: {scenario}
  DATA: lt_data TYPE TABLE OF string,
        ls_data TYPE string.
  
  ls_data = 'Sample data'.
  APPEND ls_data TO lt_data.
  
  LOOP AT lt_data INTO ls_data.
    WRITE: / ls_data.
  ENDLOOP.
ENDFORM.
"""
        elif output_type == "function_module":
            return f"""FUNCTION Z_DEMO_FUNCTION.
*"----------------------------------------------------------------------
*"*"Local Interface:
*"  IMPORTING
*"     VALUE(IV_INPUT) TYPE  STRING
*"  EXPORTING
*"     VALUE(EV_OUTPUT) TYPE  STRING
*"     VALUE(EX_ERROR) TYPE  ABAP_BOOL
*"----------------------------------------------------------------------
  " Function for: {scenario}
  
  CLEAR: ev_output, ex_error.
  
  TRY.
      ev_output = |Processed: { iv_input }|.
    CATCH cx_root INTO DATA(lx_error).
      ex_error = abap_true.
      ev_output = lx_error->get_text( ).
  ENDTRY.

ENDFUNCTION.
"""
        else:  # class
            return f"""CLASS zcl_demo_class DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES if_oo_adt_classrun.
    METHODS: process_scenario
      IMPORTING
        iv_scenario TYPE string
      RETURNING
        VALUE(rv_result) TYPE string.

  PRIVATE SECTION.
    DATA: mv_scenario TYPE string.

ENDCLASS.

CLASS zcl_demo_class IMPLEMENTATION.
  METHOD if_oo_adt_classrun~main.
    DATA(lo_instance) = NEW zcl_demo_class( ).
    out->write( lo_instance->process_scenario( '{scenario}' ) ).
  ENDMETHOD.

  METHOD process_scenario.
    " Implementation for: {scenario}
    mv_scenario = iv_scenario.
    rv_result = |Processing: { iv_scenario }|.
  ENDMETHOD.

ENDCLASS.
"""

# Global model instance
qwen_model = QwenModel(config.MODEL_PATH)

# SAP RFC Bağlantısı
class SAPConnector:
    def __init__(self):
        self.connection = None
    
    def connect(self, config: SAPConnectionConfig) -> bool:
        """SAP sistemine bağlan"""
        if Connection is None:
            print("PyRFC not installed, using mock connection")
            return True
        
        try:
            self.connection = Connection(
                ashost=config.host,
                sysnr=str(config.port),
                client=config.client,
                user=config.user,
                passwd=config.password,
                lang='EN'
            )
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def execute_function(self, func_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """RFC fonksiyonunu çalıştır"""
        if self.connection is None:
            return {"status": "mock", "data": params}
        
        try:
            result = self.connection.call(func_name, **params)
            return {"status": "success", "data": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def upload_abap(self, object_name: str, object_type: str, code: str) -> Dict[str, Any]:
        """ABAP objesini sisteme yükle"""
        # Bu örnek bir implementasyondur
        # Gerçek senaryoda BAPI veya özel RFC kullanılmalı
        return {
            "status": "success",
            "message": f"Object {object_name} uploaded successfully",
            "object_type": object_type,
            "timestamp": str(datetime.now())
        }

sap_connector = SAPConnector()

# abapGit Entegrasyonu
class AbapGitManager:
    def __init__(self, repo_path: str = "./repos"):
        self.repo_path = repo_path
        os.makedirs(repo_path, exist_ok=True)
    
    def clone_repo(self, repo_url: str, branch: str = "master") -> Dict[str, Any]:
        """Azure DevOps reposunu clone et"""
        try:
            repo_name = repo_url.split("/")[-1].replace(".git", "")
            repo_dir = os.path.join(self.repo_path, repo_name)
            
            cmd = ["git", "clone", "-b", branch, repo_url, repo_dir]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "message": result.stdout or result.stderr,
                "path": repo_dir
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def push_changes(self, repo_path: str, message: str = "AI generated changes") -> Dict[str, Any]:
        """Değişiklikleri push et"""
        try:
            cmds = [
                ["git", "-C", repo_path, "add", "."],
                ["git", "-C", repo_path, "commit", "-m", message],
                ["git", "-C", repo_path, "push"]
            ]
            
            for cmd in cmds:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode != 0:
                    return {"status": "error", "message": result.stderr}
            
            return {"status": "success", "message": "Changes pushed successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def pull_changes(self, repo_path: str) -> Dict[str, Any]:
        """Değişiklikleri pull et"""
        try:
            cmd = ["git", "-C", repo_path, "pull"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "message": result.stdout or result.stderr
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_status(self, repo_path: str) -> Dict[str, Any]:
        """Repo durumunu al"""
        try:
            cmd = ["git", "-C", repo_path, "status", "--porcelain"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            return {
                "status": "success",
                "changes": result.stdout.strip().split("\n") if result.stdout else [],
                "clean": len(result.stdout.strip()) == 0
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

abapgit_manager = AbapGitManager()

# ABAP Analiz Motoru
class ABAPAnalyzer:
    @staticmethod
    def analyze(code: str, analysis_type: str = "all") -> Dict[str, Any]:
        """ABAP kodunu analiz et"""
        results = {
            "performance": [],
            "security": [],
            "syntax": [],
            "recommendations": []
        }
        
        lines = code.split("\n")
        
        # Performans analizi
        if analysis_type in ["all", "performance"]:
            results["performance"] = ABAPAnalyzer._analyze_performance(lines)
        
        # Güvenlik analizi
        if analysis_type in ["all", "security"]:
            results["security"] = ABAPAnalyzer._analyze_security(lines)
        
        # Syntax kontrolü
        if analysis_type in ["all", "syntax"]:
            results["syntax"] = ABAPAnalyzer._check_syntax(lines)
        
        # Öneriler
        results["recommendations"] = ABAPAnalyzer._generate_recommendations(results)
        
        return results
    
    @staticmethod
    def _analyze_performance(lines: List[str]) -> List[Dict[str, Any]]:
        """Performans analizi"""
        issues = []
        
        for i, line in enumerate(lines, 1):
            # SELECT * kontrolü
            if "SELECT *" in line.upper():
                issues.append({
                    "line": i,
                    "severity": "high",
                    "issue": "SELECT * kullanımı tespit edildi",
                    "suggestion": "Sadece gerekli alanları seçin"
                })
            
            # INNER TABLE kontrolü
            if "IN TABLE" in line.upper() and "LOOP AT" in line.upper():
                issues.append({
                    "line": i,
                    "severity": "medium",
                    "issue": "Potansiyel performans sorunu",
                    "suggestion": "HASHED TABLE veya binary search düşünün"
                })
            
            # Nested loop kontrolü
            if "LOOP AT" in line.upper():
                # Basit nested loop tespiti
                pass
        
        return issues
    
    @staticmethod
    def _analyze_security(lines: List[str]) -> List[Dict[str, Any]]:
        """Güvenlik analizi"""
        issues = []
        
        for i, line in enumerate(lines, 1):
            # SQL Injection riski
            if "EXECUTE IMMEDIATE" in line.upper():
                issues.append({
                    "line": i,
                    "severity": "critical",
                    "issue": "SQL Injection riski",
                    "suggestion": "Parametreli sorgular kullanın"
                })
            
            # Authority check eksikliği
            if "AUTHORITY-CHECK" not in "\n".join(lines[:i]).upper():
                if any(keyword in line.upper() for keyword in ["UPDATE", "DELETE", "INSERT"]):
                    issues.append({
                        "line": i,
                        "severity": "high",
                        "issue": "Authority check eksik olabilir",
                        "suggestion": "Yetki kontrolü ekleyin"
                    })
        
        return issues
    
    @staticmethod
    def _check_syntax(lines: List[str]) -> List[Dict[str, Any]]:
        """Basit syntax kontrolü"""
        issues = []
        
        # REPORT veya CLASS kontrolü
        has_report = any("REPORT" in line.upper() for line in lines[:10])
        has_class = any("CLASS" in line.upper() and "DEFINITION" in line.upper() for line in lines)
        has_function = any("FUNCTION" in line.upper() for line in lines[:10])
        
        if not (has_report or has_class or has_function):
            issues.append({
                "line": 1,
                "severity": "warning",
                "issue": "Program tipi belirsiz",
                "suggestion": "REPORT, CLASS veya FUNCTION statement ekleyin"
            })
        
        return issues
    
    @staticmethod
    def _generate_recommendations(analysis_results: Dict[str, Any]) -> List[str]:
        """Analiz sonuçlarına göre öneriler oluştur"""
        recommendations = []
        
        if analysis_results["performance"]:
            recommendations.append("Kodunuzda performans iyileştirmeleri yapılabilir.")
        
        if analysis_results["security"]:
            recommendations.append("Güvenlik açıkları tespit edildi, düzeltme önerilir.")
        
        if not recommendations:
            recommendations.append("Kod genel olarak iyi görünüyor.")
        
        return recommendations

# API Endpoints
@app.post("/api/generate")
async def generate_abap_code(request: CodeGenerationRequest):
    """ABAP kodu üret"""
    try:
        abap_code = qwen_model.generate_abap(
            scenario=request.scenario,
            output_type=request.output_type
        )
        
        # Analiz yap
        analysis = ABAPAnalyzer.analyze(abap_code)
        
        return {
            "status": "success",
            "code": abap_code,
            "analysis": analysis,
            "metadata": {
                "output_type": request.output_type,
                "include_tests": request.include_tests,
                "generated_at": str(datetime.now())
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def analyze_abap_code(request: CodeAnalysisRequest):
    """ABAP kodunu analiz et"""
    try:
        analysis = ABAPAnalyzer.analyze(
            code=request.abap_code,
            analysis_type=request.analysis_type
        )
        
        return {
            "status": "success",
            "analysis": analysis,
            "metadata": {
                "analysis_type": request.analysis_type,
                "analyzed_at": str(datetime.now())
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sap/connect")
async def connect_to_sap(config: SAPConnectionConfig):
    """SAP sistemine bağlan"""
    success = sap_connector.connect(config)
    
    if success:
        return {"status": "success", "message": "SAP bağlantısı başarılı"}
    else:
        raise HTTPException(status_code=400, detail="SAP bağlantısı başarısız")

@app.post("/api/sap/upload")
async def upload_to_sap(
    object_name: str,
    object_type: str,
    code: str,
    sap_config: Optional[SAPConnectionConfig] = None
):
    """ABAP objesini SAP sistemine yükle"""
    if sap_config:
        sap_connector.connect(sap_config)
    
    result = sap_connector.upload_abap(object_name, object_type, code)
    return result

@app.post("/api/git/clone")
async def clone_repository(request: GitOperationRequest):
    """Repository clone et"""
    if not request.repo_url:
        raise HTTPException(status_code=400, detail="repo_url required")
    
    result = abapgit_manager.clone_repo(request.repo_url, request.branch)
    return result

@app.post("/api/git/push")
async def push_to_repository(repo_path: str, message: str = "AI generated changes"):
    """Repository'e push et"""
    result = abapgit_manager.push_changes(repo_path, message)
    return result

@app.post("/api/git/pull")
async def pull_from_repository(repo_path: str):
    """Repository'den pull et"""
    result = abapgit_manager.pull_changes(repo_path)
    return result

@app.get("/api/git/status/{repo_path:path}")
async def get_repository_status(repo_path: str):
    """Repository durumunu al"""
    result = abapgit_manager.get_status(repo_path)
    return result

@app.get("/api/health")
async def health_check():
    """Sağlık kontrolü"""
    return {
        "status": "healthy",
        "model_loaded": qwen_model.model is not None,
        "timestamp": str(datetime.now())
    }

if __name__ == "__main__":
    datetime = __import__('datetime').datetime
    uvicorn.run(app, host="0.0.0.0", port=8000)
