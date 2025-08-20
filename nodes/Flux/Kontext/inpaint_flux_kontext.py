import torch
import torch.nn.functional as F
import node_helpers


def conditioning_set_values(cond, vals={}):
    result = []
    for entry in cond:
        key, data = entry[0], dict(entry[1])
        for k, v in vals.items():
            data[k] = v
        result.append([key, data])
    return result


class InpaintFluxKontextConditioning:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "positive": ("CONDITIONING",),
                "negative": ("CONDITIONING",),
                "vae": ("VAE",),
                "pixels": ("IMAGE",),
                "mask": ("MASK",),
                "noise_mask": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "Add a noise mask to the latent so sampling will only happen within the mask.",
                    },
                ),
            }
        }

    RETURN_TYPES = ("CONDITIONING", "CONDITIONING", "LATENT")
    RETURN_NAMES = ("positive", "negative", "latent")
    FUNCTION = "encode"
    CATEGORY = "ComfyUI-YarvixPA/Flux/Kontext"
    DESCRIPTION = "Adds context-aware inpainting conditioning for Flux pipelines."

    def _encode_latent(self, vae, pixels):
        encoded = vae.encode(pixels[:, :, :, :3])
        return {"samples": encoded}

    def encode(self, positive, negative, pixels, vae, mask, noise_mask):
        # ajustar dimensiones a múltiplos de 8
        new_h, new_w = (pixels.shape[1] // 8) * 8, (pixels.shape[2] // 8) * 8
        mask = F.interpolate(
            mask.reshape((-1, 1, mask.shape[-2], mask.shape[-1])),
            size=(pixels.shape[1], pixels.shape[2]),
            mode="bilinear",
        )

        original, working = pixels, pixels.clone()
        if working.shape[1] != new_h or working.shape[2] != new_w:
            h_off, w_off = (working.shape[1] % 8) // 2, (working.shape[2] % 8) // 2
            working = working[:, h_off : new_h + h_off, w_off : new_w + w_off, :]
            mask = mask[:, :, h_off : new_h + h_off, w_off : new_w + w_off]

        # aplicar máscara sobre píxeles
        blend = (1.0 - mask.round()).squeeze(1)
        working[:, :, :, :3] = (working[:, :, :, :3] - 0.5) * blend.unsqueeze(-1) + 0.5

        concat_latent = vae.encode(working)
        orig_latent = vae.encode(original)

        latent_dict = {"samples": orig_latent}
        if noise_mask:
            latent_dict["noise_mask"] = mask

        # codificación auxiliar de referencia
        reference_latent = self._encode_latent(vae, original)

        conditioned = []
        for current in [positive, negative]:
            base = conditioning_set_values(
                current, {"concat_latent_image": concat_latent, "concat_mask": mask}
            )
            extended = node_helpers.conditioning_set_values(
                base,
                {"reference_latents": [reference_latent["samples"]]},
                append=True,
            )
            conditioned.append(extended)

        return (conditioned[0], conditioned[1], latent_dict)


NODE_CLASS_MAPPINGS = {
    "InpaintFluxKontextConditioning": InpaintFluxKontextConditioning
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "InpaintFluxKontextConditioning": "🚀 Inpaint Flux Kontext"
}
