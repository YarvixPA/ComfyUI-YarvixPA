class FrameCalculatorAudio:
    """
    Calculates the number of frames based on audio duration and FPS.
    Exposes:
      - frame_rate     (FLOAT) — e.g. 29.97, 24.0
      - frame_rate_int (INT)   — rounded, e.g. 30, 24
      - frames_number     (INT)
      - audio_duration (STRING, HH:MM:SS)
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "fps": ("FLOAT", {"default": 30.0, "min": 1.0, "max": 480.0, "step": 0.1}),
                "audio": ("AUDIO",),
            }
        }

    RETURN_TYPES = ("FLOAT", "INT", "INT", "STRING")
    RETURN_NAMES = ("frame_rate", "frame_rate_int", "frames_number", "audio_duration")
    FUNCTION = "execute"
    CATEGORY = "ComfyUI-YarvixPA/Utils/Calculators"
    DESCRIPTION = "🚀 Calculates the number of frames based on the audio and FPS."
    OUTPUT_NODE = True

    def execute(self, audio, fps=30.0):
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

        frame_rate = float(fps)
        frame_rate_int = int(round(frame_rate))
        frames_number = int(round(frame_rate * duration_seconds))

        # Convert to HH:MM:SS (using floor)
        total_seconds = int(duration_seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        audio_duration = f"{hours:02}:{minutes:02}:{seconds:02}"

        # Text for the JS widget
        display_text = (
            f"Frame rate: {frame_rate} fps (int: {frame_rate_int})\n"
            f"Number of frames: {frames_number}\n"
            f"Audio duration: {audio_duration}"
        )

        result = (frame_rate, frame_rate_int, frames_number, audio_duration)

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
