class FrameCalculatorVideo:
    """
    Calculates number of frames from FPS and duration in seconds.
    Exposes:
      - frame_rate (FLOAT)
      - num_frames (INT)
      - video_duration (STRING, HH:MM:SS)

    Also sends a formatted text to the frontend so the JS widget
    can display all three values inside the node UI.
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

    RETURN_TYPES = ("FLOAT", "INT", "STRING")
    RETURN_NAMES = ("frame_rate", "num_frames", "video_duration")
    FUNCTION = "execute"
    CATEGORY = "ComfyUI-YarvixPA/Utils/Video"
    DESCRIPTION = "🚀 Calculates the number of frames based on FPS and duration in seconds."
    OUTPUT_NODE = True  # Always runs

    def execute(self, fps=30.0, duration_seconds=0):
        fps = float(fps)
        duration_seconds = int(duration_seconds)

        if duration_seconds < 0:
            raise ValueError("duration_seconds must be >= 0.")

        frame_rate = fps
        num_frames = int(round(frame_rate * duration_seconds))

        # Convert to HH:MM:SS
        total_seconds = int(duration_seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        video_duration = f"{hours:02}:{minutes:02}:{seconds:02}"

        # Text for the JS widget
        display_text = (
            f"Frame rate: {frame_rate:.2f} fps\n"
            f"Number of frames: {num_frames}\n"
            f"Video duration: {video_duration}"
        )

        # Outputs for other nodes
        result = (frame_rate, num_frames, video_duration)

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
