class FrameCalculatorVideo:
    """
    Calculates number of frames from FPS and duration in seconds.
    Exposes:
      - frame_rate     (FLOAT) — e.g. 29.97, 24.0
      - frame_rate_int (INT)   — rounded, e.g. 30, 24
      - frames_number     (INT)
      - video_duration (STRING, HH:MM:SS)
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "fps": ("FLOAT", {"default": 30.0, "min": 1.0, "max": 480.0, "step": 0.1}),
                "duration_seconds": ("INT", {"default": 0, "min": 0, "step": 1}),
            }
        }

    RETURN_TYPES = ("FLOAT", "INT", "INT", "STRING")
    RETURN_NAMES = ("frame_rate", "frame_rate_int", "frames_number", "video_duration")
    FUNCTION = "execute"
    CATEGORY = "ComfyUI-YarvixPA/Utils/Video"
    DESCRIPTION = "🚀 Calculates the number of frames based on FPS and duration in seconds."
    OUTPUT_NODE = True

    def execute(self, fps=30.0, duration_seconds=0):
        duration_seconds = int(duration_seconds)

        if duration_seconds < 0:
            raise ValueError("duration_seconds must be >= 0.")

        frame_rate = float(fps)
        frame_rate_int = int(round(frame_rate))
        frames_number = int(round(frame_rate * duration_seconds))

        # Convert to HH:MM:SS
        total_seconds = int(duration_seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        video_duration = f"{hours:02}:{minutes:02}:{seconds:02}"

        # Text for the JS widget
        display_text = (
            f"Frame rate: {frame_rate} fps (int: {frame_rate_int})\n"
            f"Number of frames: {frames_number}\n"
            f"Video duration: {video_duration}"
        )

        result = (frame_rate, frame_rate_int, frames_number, video_duration)

        return {
            "ui": { "text": (display_text,) },
            "result": result,
        }


NODE_CLASS_MAPPINGS = {
    "FrameCalculatorVideo": FrameCalculatorVideo
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FrameCalculatorVideo": "🚀 Frame Calculator (Video)"
}
