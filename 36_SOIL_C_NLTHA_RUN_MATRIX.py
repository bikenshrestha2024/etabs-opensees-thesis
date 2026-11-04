"""36 — generate read-only Soil C 8-pair x M0–M6 x ULS/SLS batch configs.

Example:
python 36_SOIL_C_NLTHA_RUN_MATRIX.py --models-json D:/Thesis/Models/M0_M6_Directories.json --matched-dir D:/Thesis/Records/Matched --output-dir D:/Thesis/RunMatrix
"""
from components.nonlinear_time_history.soil_c_run_matrix import main
if __name__=="__main__":main()
