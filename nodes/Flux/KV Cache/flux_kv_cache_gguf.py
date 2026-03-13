# Flux KV Cache node optimized for GGUF models with partial loading/offloading
import torch
import logging


class GGUF_KV_Attn_Input:
    """
    KV Cache attention patch for GGUF models.

    Differences from the original KV_Attn_Input:
    - Stores cached K/V tensors on CPU by default so they survive GPU
      memory pressure and model offloading cycles
    - cleanup() is a no-op: the cache persists across offload/reload within
      a generation. A new cache object is created per generation.
    - Uses a hash of reference token info to detect when references change,
      only then does it invalidate the cache
    """
    def __init__(self, cache_device="cpu"):
        self.cache = {}
        self.cache_device = torch.device(cache_device)
        self._ref_hash = None
        self.set_cache = False
        self._logged_build = False

    def __call__(self, q, k, v, extra_options, **kwargs):
        reference_image_num_tokens = extra_options.get("reference_image_num_tokens", [])
        if len(reference_image_num_tokens) == 0:
            return {}

        ref_toks = sum(reference_image_num_tokens)
        ref_hash = (ref_toks, tuple(reference_image_num_tokens))

        # If reference images changed (added/removed), invalidate cache
        if ref_hash != self._ref_hash:
            is_rebuild = len(self.cache) > 0
            self.cache = {}
            self._ref_hash = ref_hash
            self._logged_build = False
            if is_rebuild:
                logging.info("Flux KV Cache (GGUF): Cache rebuilt")

        cache_key = "{}_{}".format(extra_options["block_type"], extra_options["block_index"])

        if cache_key in self.cache:
            kk, vv = self.cache[cache_key]
            # Move cached tensors from CPU to the compute device
            kk = kk.to(device=k.device, dtype=k.dtype)
            vv = vv.to(device=v.device, dtype=v.dtype)
            self.set_cache = False
            return {"q": q, "k": torch.cat((k, kk), dim=2), "v": torch.cat((v, vv), dim=2)}

        # First pass (step 0): cache reference K/V on the chosen device (CPU by default)
        self.cache[cache_key] = (
            k[:, :, -ref_toks:].detach().to(self.cache_device),
            v[:, :, -ref_toks:].detach().to(self.cache_device),
        )
        self.set_cache = True
        if not self._logged_build:
            logging.info("Flux KV Cache (GGUF): Cache built")
            self._logged_build = True
        return {"q": q, "k": k, "v": v}

    def cleanup(self):
        # Intentionally do NOT clear the cache.
        # GGUF models get offloaded/reloaded frequently (e.g. for VAE),
        # which triggers cleanup(). Clearing here would destroy the cache
        # between denoising steps. The cache is naturally replaced when
        # a new GGUF_KV_Attn_Input instance is created per generation.
        pass


class FluxKVCacheGGUF:
    """
    Flux KV Cache node optimized for GGUF models.

    Connects between Unet Loader (GGUF) and the sampler.
    Enables KV Cache for reference images on Flux family models,
    with persistence across model offload/reload cycles within a generation.

    Workflow: Unet Loader (GGUF) -> [MODEL] -> Flux KV Cache (GGUF) -> [MODEL] -> KSampler
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("MODEL",),
            },
            "optional": {
                "cache_on_cpu": ("BOOLEAN", {"default": True, "tooltip": "Store KV cache on CPU (survives VRAM pressure) or GPU (faster but may be lost during offloading)"}),
            }
        }

    RETURN_TYPES = ("MODEL",)
    FUNCTION = "execute"
    CATEGORY = "bootleg"
    TITLE = "🚀 Flux KV Cache (GGUF)"
    DESCRIPTION = "Enables KV Cache optimization for reference images on Flux family models loaded via GGUF. The cache persists across model offload/reload cycles, preventing the performance degradation seen with the standard Flux KV Cache node on GGUF models."

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Force ComfyUI to re-execute this node on every prompt.
        # Without this, ComfyUI caches the node output and reuses
        # the same GGUF_KV_Attn_Input across prompts, causing stale
        # K/V when reference images change.
        return float("nan")

    @classmethod
    def execute(cls, model, cache_on_cpu=True):
        m = model.clone()
        cache_device = "cpu" if cache_on_cpu else "cuda"
        input_patch_obj = GGUF_KV_Attn_Input(cache_device=cache_device)

        def model_input_patch(inputs):
            if len(input_patch_obj.cache) > 0:
                ref_image_tokens = sum(inputs["transformer_options"].get("reference_image_num_tokens", []))
                if ref_image_tokens > 0:
                    img = inputs["img"]
                    inputs["img"] = img[:, :-ref_image_tokens]
            return inputs

        m.set_model_attn1_patch(input_patch_obj)
        m.set_model_post_input_patch(model_input_patch)
        if hasattr(model.model.diffusion_model, "params"):
            m.add_object_patch("diffusion_model.params.default_ref_method", "index_timestep_zero")
        else:
            m.add_object_patch("diffusion_model.default_ref_method", "index_timestep_zero")

        cache_label = "CPU" if cache_on_cpu else "GPU"
        logging.info(f"Flux KV Cache (GGUF): Applied on {cache_label}")
        return (m,)


NODE_CLASS_MAPPINGS = {
    "FluxKVCacheGGUF": FluxKVCacheGGUF,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FluxKVCacheGGUF": "🚀 Flux KV Cache (GGUF)",
}
