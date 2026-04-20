from src.robot_persona.src import RobotPersona
from src.stt.src import STT
import sounddevice as sd
from dotenv import load_dotenv
import os
import subprocess

def pickle_to_movement(path, env_name="unisim"):

    """
    
    Implement function that opens the robot pickle file
    and converts it into robot movement

    Input:
    path: str (directory to movement pickle file)

    """
    # YOUR CODE HERE
    process = f"""python {path}"""
    print(process)
    #subprocess.run(process.split())

if __name__ == "__main__":

    # Input Variables
    persona = "a Helpful Assistant"
    movement_directory = os.path.join('src', 'movements')

    # .env file (if not exist)
    if not os.path.isfile(".env"):
        env_vars ={
            "HF_TOKEN": "your-hf-token-here"
        }
        with open(".env", "w") as f:
                for key, value in env_vars.items():
                    # Ensure the key is uppercase (standard convention) 
                    # and write the pair to the file
                    f.write(f"{key.upper()}={value}\n")
        
        raise FileNotFoundError('Add HF Token')


    # Models
    load_dotenv()
    HF_TOKEN = os.getenv('HF_TOKEN') # Or use your own huggingface API Key
    persona = RobotPersona(persona, movement_directory)
    stt = STT()
    stream = sd.InputStream(samplerate=stt.SAMPLERATE, 
                        channels=1, 
                        callback=stt.audio_callback)

    with stream:
        stt.process_audio(persona.forward, pickle_to_movement)
