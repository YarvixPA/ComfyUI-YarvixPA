import torch


class GetResolutionImage:
    """
    Displays the resolution (width and height) of an image.
    Outputs:
      - image (IMAGE, passthrough)
      - height (INT)
      - width (INT)

    Also sends formatted text to the frontend so the JS widget
    can display the values inside the node UI.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }

    # Returns: image, height, width
    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("image", "height", "width")
    FUNCTION = "execute"
    CATEGORY = "ComfyUI-YarvixPA/Utils/Image"
    DESCRIPTION = "🚀 Displays the resolution (width and height) of an image."
    OUTPUT_NODE = True

    def execute(self, image):
        # ComfyUI typically handles images as torch tensors:
        #   [B, H, W, C] or [H, W, C], etc.
        if not torch.is_tensor(image):
            raise ValueError("Expected 'image' to be a torch.Tensor.")

        shape = image.shape
        H = 0
        W = 0

        try:
            if len(shape) == 4:
                # [B, H, W, C]
                _, H, W, _ = shape
            elif len(shape) == 3:
                # Could be [H, W, C] or [C, H, W]
                # Heuristic: if first dim looks like channels (1,3,4), use last 2 dims
                if shape[0] in (1, 3, 4):
                    H, W = shape[1], shape[2]
                else:
                    H, W = shape[0], shape[1]
            elif len(shape) >= 2:
                # Fallback: use last two dimensions
                H, W = shape[-2], shape[-1]
            else:
                raise ValueError(f"Unsupported image shape: {tuple(shape)}")

            H = int(H)
            W = int(W)

            display_text = f"Width: {W} px\nHeight: {H} px"

        except Exception as e:
            H = 0
            W = 0
            display_text = f"ERROR getting resolution:\n{e}"
            print(f"[GetImageResolution] {display_text}")

        result = (image, H, W)

        return {
            "ui": {
                "text": (display_text,),
            },
            "result": result,
        }


NODE_CLASS_MAPPINGS = {
    "GetResolutionImage": GetResolutionImage,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GetResolutionImage": "🚀 Get Resolution",
}
