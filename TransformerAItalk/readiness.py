def real_model_ready(engine):
    return bool(engine and engine._loaded and not engine._demo_mode and engine.model is not None)
