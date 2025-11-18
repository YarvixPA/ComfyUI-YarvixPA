import torch


class FrameCalculatorAudio:
    """
    Calculates the number of frames based on audio duration and FPS.
    Exposes:
      - frame_rate (FLOAT)
      - num_frames (INT)
      - audio_duration (STRING, HH:MM:SS)

    Also sends a formatted text to the frontend so the JS widget
    can display all three values inside the node UI.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "fps": ("FLOAT", {"default": 30.0, "min": 1.0, "max": 480.0, "step": 0.1},),
                "audio": ("AUDIO",),
            }
        }

    # Returns 3 values: frame_rate, num_frames and audio_duration
    RETURN_TYPES = ("FLOAT", "INT", "STRING")
    RETURN_NAMES = ("frame_rate", "num_frames", "audio_duration")
    FUNCTION = "execute"
    CATEGORY = "ComfyUI-YarvixPA/Utils/Calculators"
    DESCRIPTION = "🚀 Calculates the number of frames based on the audio and FPS."
    OUTPUT_NODE = True  # Ensures the node runs even if nothing is connected

    def execute(self, audio, fps=30.0):
        fps = float(fps)

        if not isinstance(audio, dict):
            raise ValueError(
                "Invalid 'audio' input: expected a dictionary with 'waveform' and 'sample_rate'."
            )
        if "waveform" not in audio or "sample_rate" not in audio:
            raise ValueError("'audio' must contain 'waveform' and 'sample_rate'.")

        waveform = audio["waveform"]
        sample_rate = int(audio["sample_rate"])

        if sample_rate <= 0:
            raise ValueError("Audio sample_rate must be greater than 0.")

        # waveform: [batch, channels, samples]
        num_samples = int(waveform.shape[-1])
        duration_seconds = num_samples / float(sample_rate)

        frame_rate = fps
        num_frames = int(round(frame_rate * duration_seconds))

        # Conversion to HH:MM:SS (using floor instead of round)
        total_seconds = int(duration_seconds)  # truncated
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        audio_duration = f"{hours:02}:{minutes:02}:{seconds:02}"

        # Text that will be shown in the JS widget
        display_text = (
            f"Frame rate: {frame_rate:.2f} fps\n"
            f"Number of frames: {num_frames}\n"
            f"Audio duration: {audio_duration}"
        )

        # Normal outputs for other nodes
        result = (frame_rate, num_frames, audio_duration)

        # "ui" is passed to the frontend and becomes `message.text`
        return {
            "ui": {
                "text": (display_text,),
            },
            "result": result,
        }


NODE_CLASS_MAPPINGS = {
    "FrameCalculatorAudio": FrameCalculatorAudio,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FrameCalculatorAudio": "🚀 Frame Calculator (Audio)",
}
