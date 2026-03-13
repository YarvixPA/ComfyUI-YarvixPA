import node_helpers


class MultiReferenceLatent:
    """
    Consolidates VAE Encode + ReferenceLatent chaining for multiple
    reference images into a single node.

    For each connected image the node:
      1. VAE-encodes the image into a latent.
      2. Appends `reference_latents` to both positive and negative conditioning.

    The number of image inputs is controlled by the `references` widget
    and dynamically managed by the companion JS extension.
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "positive": ("CONDITIONING", {"tooltip": "Positive conditioning to modify with reference latents."}),
                "negative": ("CONDITIONING", {"tooltip": "Negative conditioning to modify with reference latents."}),
                "vae": ("VAE", {"tooltip": "VAE model used to encode the reference images into latent space."}),
                "references": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 16,
                    "tooltip": "Number of reference image inputs to expose.",
                }),
                "image1": ("IMAGE", {"tooltip": "Reference image 1."}),
            },
        }

    RETURN_TYPES = ("CONDITIONING", "CONDITIONING")
    RETURN_NAMES = ("positive", "negative")
    FUNCTION = "execute"
    CATEGORY = "conditioning"
    DESCRIPTION = (
        "Encodes one or more reference images with a VAE and applies them as "
        "reference latents to both positive and negative conditioning. "
        "Replaces chaining multiple VAE Encode + ReferenceLatent nodes."
    )

    def execute(self, positive, negative, vae, references, **kwargs):
        for i in range(1, references + 1):
            image = kwargs.get(f"image{i}")
            if image is None:
                continue

            # VAE encode the image
            latent = vae.encode(image)

            # Append reference latent to both conditionings
            positive = node_helpers.conditioning_set_values(
                positive, {"reference_latents": [latent]}, append=True
            )
            negative = node_helpers.conditioning_set_values(
                negative, {"reference_latents": [latent]}, append=True
            )

        return (positive, negative)


NODE_CLASS_MAPPINGS = {
    "MultiReferenceLatent": MultiReferenceLatent
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MultiReferenceLatent": "🚀 Multi-ReferenceLatent"
}
