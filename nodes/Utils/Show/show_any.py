import json
from typing import Any
import torch


class ShowAnyDataType:
    """
    Node to display information about any incoming data type.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # "*" (wildcard) accepts any data type
                "ANY": (
                    "*",
                    {
                        "forceInput": True,
                        "placeholder": "Connect INT, FLOAT, STRING or any data type",
                    },
                ),
            },
            "hidden": {
                # Hidden inputs to store information in PNG info
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    @classmethod
    def VALIDATE_INPUTS(cls, input_types):
        """
        Skip strict backend validation for the wildcard input.
        """
        return True

    # Node properties
    CATEGORY = "ComfyUI-YarvixPA/Utils/Show"
    OUTPUT_NODE = True  # Ensures the node is executed
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "execute"
    DESCRIPTION = "🚀 Displays information about any connected data type."

    def execute(self, ANY: Any, unique_id: str, extra_pnginfo=None):
        """
        Inspect the input data and build a human-readable description string
        that will be shown in the UI.
        """
        # Unpack if it is a single-element list
        value_to_display = (
            ANY[0] if isinstance(ANY, list) and len(ANY) == 1 else ANY
        )

        display_value = ""

        try:
            # Torch tensors (IMAGE, MASK, etc.)
            if isinstance(value_to_display, torch.Tensor):
                display_value = (
                    f"Type: {type(value_to_display).__name__} (Tensor)\n"
                    f"Shape: {value_to_display.shape}\n"
                    f"Dtype: {value_to_display.dtype}"
                )
                if value_to_display.numel() > 0:
                    example_value = value_to_display.flatten().cpu().item()
                    display_value += (
                        f"\n(Example value (CPU): {example_value:.4f}...)"
                    )

            # Latent dict with 'samples' key
            elif isinstance(value_to_display, dict) and "samples" in value_to_display:
                samples_shape = value_to_display["samples"].shape
                display_value = (
                    "Type: LATENT (Dict)\n"
                    f"Shape Samples: {samples_shape}"
                )

            # Primitive types
            elif isinstance(value_to_display, (int, float, str, bool)):
                display_value = (
                    f"Type: {type(value_to_display).__name__.upper()}\n"
                    f"Value: {value_to_display}"
                )

            # Generic conversion
            else:
                try:
                    display_value = json.dumps(value_to_display, indent=2)
                except Exception:
                    display_value = (
                        f"Type: {type(value_to_display).__name__}\n"
                        f"String representation: {str(value_to_display)[:500]}"
                    )

        except Exception as e:
            display_value = f"Error while describing the data. Error: {e}"

        # Return value for the UI: the 'text' key will be mapped
        # to message.text on the frontend.
        return {"ui": {"text": (display_value,)}}


NODE_CLASS_MAPPINGS = {
    "ShowAnyDataType": ShowAnyDataType,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ShowAnyDataType": "🚀 Show Any",
}
