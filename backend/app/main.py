
import os
import sys 


# Add domain/src and project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../domain/src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


from fastapi import FastAPI
from backend.app.api.v1 import router as v1_router

app = FastAPI(title="Cognitive Digital Twin API")

app.include_router(v1_router)


