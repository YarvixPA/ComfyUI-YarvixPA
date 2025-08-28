import torch

class FrameCalculatorAudio:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO", ),
                "fps": ("FLOAT", {"default": 30.0, "min": 1.0, "max": 480.0, "step": 0.1}),
            }
        }

    # Now returns 3 values: frame_rate, num_frames and audio_duration
    RETURN_TYPES = ("FLOAT", "INT", "STRING")
    RETURN_NAMES = ("frame_rate", "num_frames", "audio_duration")
    FUNCTION = "execute"
    CATEGORY = "ComfyUI-YarvixPA/Utils/Calculators"
    DESCRIPTION = "🚀 Calculates the number of frames based on the audio and FPS."

    def execute(self, audio, fps=30.0):
        fps = float(fps)

        if not isinstance(audio, dict):
            raise ValueError("Invalid 'audio' input: expected a dictionary with 'waveform' and 'sample_rate'.")
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

        return (frame_rate, num_frames, audio_duration)

NODE_CLASS_MAPPINGS = {
    "FrameCalculatorAudio": AudioFrameCalculator,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FrameCalculatorAudio": "🚀 Frame Calculator (Audio)",
}
