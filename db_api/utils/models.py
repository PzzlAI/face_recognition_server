from pydantic import BaseModel
from typing import Optional

class admin_credentials(BaseModel):
    username: str
    password: str
    company_code: Optional[str] = None
    employee_code: Optional[str] = None
    # serial_de_dispositivo: str
    # objectID: str

class admin_schema(admin_credentials):
    nombre_completo: str

class admin_credentials_return(BaseModel):
    access: bool
    status: str
    name: Optional[str] = None
    # company_code: Optional[str] = None
    # employee_code: Optional[str] = None

class collaborator_schema(BaseModel):
    company_code: str
    employee_code: str
    nombre_completo: str
    # serial_de_dispositivo: Optional[str] = None

class company_code_model(BaseModel):
    company_code: str

class employee_code_model(company_code_model):
    employee_code: str

class collaborator_return_model(BaseModel):
    employee_code: str
    nombre_completo: str







