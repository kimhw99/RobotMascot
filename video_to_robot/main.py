import subprocess
import shutil
import os
from pathlib import Path

# --- Configuration ---
BASE_DIR = Path.cwd()
PROMPT_HMR_DIR = BASE_DIR / "PromptHMR"
GMR_DIR = BASE_DIR / "GMR"
OUTPUT_DIR = BASE_DIR / "output"

def run_command(command, cwd=None):
    """Utility to run shell commands and handle errors."""
    print(f"Executing: {' '.join(command)}")
    subprocess.run(command, cwd=cwd, check=True)

def main(INPUT_VIDEO):
    # 1. Setup paths
    input_video_path = BASE_DIR / "input" / INPUT_VIDEO
    output_video_dir = OUTPUT_DIR / INPUT_VIDEO
    
    # Create output directory
    output_video_dir.mkdir(parents=True, exist_ok=True)

    # 2. Run PromptHMR (Video to SMPL-X)
    # Copy input to PromptHMR
    shutil.copy(input_video_path, PROMPT_HMR_DIR / INPUT_VIDEO)
    
    run_command([
        "conda", "run", "-n", "phmr_pt2.4", 
        "python", "scripts/run_pipeline.py", 
        "--input_video", INPUT_VIDEO, 
        "--output_folder", "smplx"
    ], cwd=PROMPT_HMR_DIR)

    # 3. Move Assets to GMR (Conversion)
    run_command([
        "python", "convert_smpl_to_smplx_npz.py", 
        "--input-dir", str(PROMPT_HMR_DIR / "smplx"), 
        "--output-dir", str(GMR_DIR / "smplx_npz")
    ], cwd=BASE_DIR)

    # 4. Run GMR
    run_command([
        "conda", "run", "-n", "gmr", 
        "python", "scripts/smplx_to_robot.py", 
        "--smplx_file", "smplx_npz/subject-1.npz", 
        "--robot", "unitree_g1", 
        "--save_path", f"results/{INPUT_VIDEO}/result.pkl", 
        "--record_video", "--rate_limit"
    ], cwd=GMR_DIR)

    # 5. Move Results & Clean Up
    print("Organizing output files...")
    
    # Move GMR results to output folder
    gmr_results_src = GMR_DIR / "results" / INPUT_VIDEO
    if gmr_results_src.exists():
        # Using shutil.copytree + rm or move depending on OS permissions
        shutil.copytree(str(gmr_results_src), os.path.join(str(OUTPUT_DIR), INPUT_VIDEO), dirs_exist_ok=True)

    gmr_smplx_src = GMR_DIR / "smplx_npz"
    if gmr_smplx_src.exists():
        # Using shutil.copytree + rm or move depending on OS permissions
        shutil.copytree(str(gmr_smplx_src), os.path.join(str(OUTPUT_DIR), INPUT_VIDEO, 'smplx_npz'), dirs_exist_ok=True)
        shutil.rmtree(gmr_smplx_src, ignore_errors=True)

    # Move SMPLX data to output/video_name/
    smplx_src = PROMPT_HMR_DIR / "smplx"
    if smplx_src.exists():
        shutil.copytree(str(smplx_src), os.path.join(str(output_video_dir), 'smplx'), dirs_exist_ok=True)
        shutil.rmtree(smplx_src, ignore_errors=True)

    # Remove temporary video in PromptHMR
    temp_video = PROMPT_HMR_DIR / INPUT_VIDEO
    if temp_video.exists():
        temp_video.unlink()

    print(f"Pipeline complete. Results available in: {OUTPUT_DIR}")

if __name__ == "__main__":
    INPUT_VIDEO = "talk.mp4"
    main(INPUT_VIDEO)
