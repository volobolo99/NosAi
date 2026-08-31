import logging

logger = logging.getLogger("ControlPlane")

MODE_WEIGHTS = {
    "FAST": {"speed": 1.0, "safety": 0.7, "objective": 0.6},
    "SMART": {"speed": 0.8, "safety": 1.0, "objective": 1.0},
    "DEEP": {"speed": 0.5, "safety": 1.2, "objective": 1.2},
    "LOW_RES": {"speed": 1.1, "safety": 0.8, "objective": 0.7},
}

class GuardAiControlPlane:
    def __init__(self, vision_engine=None, mission_solver=None):
        self.vision = vision_engine
        self.solver = mission_solver
        self.mode = "SMART"

    def handle_mode_switch(self, new_mode: str):
        mode = new_mode.upper()
        if mode not in MODE_WEIGHTS:
            raise ValueError(f"Unsupported MissionSolverMode: {new_mode}")
        self.mode = mode
        if self.solver is not None and hasattr(self.solver, "update_utility_weights_by_profile"):
            self.solver.update_utility_weights_by_profile(mode)
        logger.info("Mission Utility Score (U_m) reconfigured: %s", mode)

    async def handle_manual_recheck(self, frame_id, label, x_min, y_min, x_max, y_max):
        if not 0 <= x_min <= x_max <= 1 or not 0 <= y_min <= y_max <= 1:
            raise ValueError("BoundingBox coordinates must be normalized to [0,1]")
        logger.info("Manual Recheck frame=%s label=%s", frame_id, label)
        if self.vision is None:
            return None
        method = getattr(self.vision, "execute_focused_inference_rt_detr", None)
        if method is None:
            raise RuntimeError("TensorRT focused-inference adapter is not configured")
        verified = await method(frame_id, label, x_min, y_min, x_max, y_max)
        return verified
