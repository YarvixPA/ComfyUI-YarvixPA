import torch
import comfy.utils


class ContainsAnyDict(dict):
    """Accept any optional input name and treat it as IMAGE."""

    def __init__(self, value):
        super().__init__()
        self._value = value  # e.g. ("IMAGE",)

    def __missing__(self, key):
        return self._value

    def __contains__(self, key):
        return True


class BatchImagesNode:
    """Dynamic image batch builder. Inputs are created in JS."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image1": ("IMAGE",),
            },
            "optional": ContainsAnyDict(("IMAGE",)),  # unlimited imageX inputs
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("IMAGE",)
    FUNCTION = "batch"
    CATEGORY = "ComfyUI-YarvixPA/Image"
    DESCRIPTION = "Build a batch from a dynamic number of image inputs."

    @staticmethod
    def _ensure_batch(img):
        if img.ndim == 3:
            return img.unsqueeze(0)
        return img

    @staticmethod
    def _resize_if_needed(img, h, w):
        if img.shape[1] != h or img.shape[2] != w:
            img = comfy.utils.common_upscale(
                img.movedim(-1, 1),  # [B,C,H,W]
                w,
                h,
                "bilinear",
                "center",
            ).movedim(1, -1)        # [B,H,W,C]
        return img

    def batch(self, image1, **kwargs):
        image1 = self._ensure_batch(image1)
        h, w = image1.shape[1], image1.shape[2]

        images = [image1]

        # Add all dynamic images
        for img in kwargs.values():
            if img is None:
                continue
            img = self._ensure_batch(img)
            img = self._resize_if_needed(img, h, w)
            images.append(img)

        # Merge
        if len(images) == 1:
            out = images[0]
        else:
            out = torch.cat(images, dim=0)

        return (out,)


NODE_CLASS_MAPPINGS = {
    "BatchImagesNode": BatchImagesNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BatchImagesNode": "🚀 Batch Images",
}
