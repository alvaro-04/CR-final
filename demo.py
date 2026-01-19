import os

# Force CPU-only by hiding GPUs from CUDA runtime. Set this BEFORE importing
# any module that may load CUDA (torch, triton, etc.). If you prefer a
# temporary run you can instead prefix the command with
# `CUDA_VISIBLE_DEVICES="" python demo.py`.
# os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")

from ui import RobotEnvUI

n_objects = 8 
demo = RobotEnvUI(n_objects, visualise_clip=False)

demo.run()