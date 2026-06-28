import os
from .demo import DemoEngine
from .nerfstudio import NerfstudioEngine

ENGINES = {
    "demo": DemoEngine,
    "nerfstudio": NerfstudioEngine,
}

def configured_engine_id():
    if os.getenv("MAKER_SPLAT_REAL_MODE", "0") == "1":
        return os.getenv("MAKER_SPLAT_ENGINE", "nerfstudio")
    return os.getenv("MAKER_SPLAT_ENGINE", "demo")

def get_engine(engine_id=None):
    engine_id = engine_id or configured_engine_id()
    cls = ENGINES.get(engine_id, DemoEngine)
    return cls()

def list_engines():
    out = []
    for key, cls in ENGINES.items():
        engine = cls()
        out.append({
            "id": engine.id,
            "name": engine.name,
            "description": engine.description,
            "preflight": engine.preflight()
        })
    return out
