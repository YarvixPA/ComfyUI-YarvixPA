# ComfyUI-YarvixPA — Nodes Index

This repository contains custom ComfyUI nodes by YarvixPA. Below is a compiled list of nodes (discovered via repository code search) with a short description of what each node does and a link to the source file.

NOTE: The code search results used to build this list are limited to 10 results and may be incomplete. For the full, up-to-date list in the repository use the GitHub code search for the `nodes` directory:
https://github.com/YarvixPA/ComfyUI-YarvixPA/search?q=nodes&type=code

---

## Nodes (discovered)

- 🚀 **Batch Images** (BatchImagesNode)  
  - Category: ComfyUI-YarvixPA/Image  
  - Description: Build a batch from a dynamic number of image inputs. Automatically ensures inputs are batched and resizes images as needed so they can be concatenated into one batch tensor.  
  - Source: nodes/Image/batch_images.py — https://github.com/YarvixPA/ComfyUI-YarvixPA/blob/main/nodes/Image/batch_images.py

- Show Any Data Type (ShowAnyDataType)  
  - Category: ComfyUI-YarvixPA/Utils/Show  
  - Description: Display information about any connected data type. Accepts a wildcard input and generates a human-readable description for the frontend (tensor shapes/dtypes, primitive values, JSON-serializable objects, etc.). Useful for debugging or inspecting node outputs.  
  - Source: nodes/Utils/Show/show_any.py — https://github.com/YarvixPA/ComfyUI-YarvixPA/blob/main/nodes/Utils/Show/show_any.py

- Prep Image for Video (Prepimg2Vid)  
  - Category: ComfyUI-YarvixPA/Utils/Video  
  - Description: Prepares an image for video generation by resizing/upscaling, cropping to a chosen aspect ratio and resolution, and applying horizontal/vertical offsets. Returns the prepared image and the width/height chosen. Helpful for generating consistent frames for video pipelines.  
  - Source: nodes/Utils/Video/prepare_img_4_vid.py — https://github.com/YarvixPA/ComfyUI-YarvixPA/blob/main/nodes/Utils/Video/prepare_img_4_vid.py

- 🚀 Frame Calculator (Audio) (FrameCalculatorAudio)  
  - Category: ComfyUI-YarvixPA/Utils/Calculators  
  - Description: Calculates frame count and frame-rate based on an input audio file and a specified FPS. Outputs frame_rate (FLOAT), num_frames (INT), and audio duration as HH:MM:SS (STRING). Also provides formatted text for the UI widget. Useful for syncing visuals to audio.  
  - Source: nodes/Utils/Calculators/frame_calculator_audio.py — https://github.com/YarvixPA/ComfyUI-YarvixPA/blob/main/nodes/Utils/Calculators/frame_calculator_audio.py

- Stitch Images (StitchImages)  
  - Category: ComfyUI-YarvixPA/Image/Stitch  
  - Description: Stitches two images together in a specified direction (right, down, left, up). Options include matching image sizes (resize or pad), adding spacing between images with selectable color, and aligning channels/batches. Returns an unstitch info object (for reversing) plus the stitched image.  
  - Source: nodes/Image/Stitch/stitch_images.py — https://github.com/YarvixPA/ComfyUI-YarvixPA/blob/main/nodes/Image/Stitch/stitch_images.py

- 🚀 Unstitch Images and Mask (UnstitchImagesAndMask)  
  - Category: ComfyUI-YarvixPA/Image/Stitch  
  - Description: Reverse operation for a stitch node. Takes the `UNSTITCH` info plus a stitched IMAGE and MASK and returns either the first or second slice (image and matching mask) based on a selection. Useful for splitting composited images back into parts.  
  - Source: nodes/Image/Stitch/unstitch_images_and_masks.py — https://github.com/YarvixPA/ComfyUI-YarvixPA/blob/main/nodes/Image/Stitch/unstitch_images_and_masks.py

- Remove Background (BiRefNet-based)  
  - Category: ComfyUI-YarvixPA/Image/Remove Background  
  - Description: Remove background from images using BiRefNet family models. Includes logic to vendored-download models into ComfyUI/models, select device, convert between PIL/tensor formats, and run the segmentation model to produce masks and masked images. (Implements model initialization and conversions — see source for model options such as BiRefNet, BiRefNet_lite and dynamic variants.)  
  - Source: nodes/Image/Remove Background/remove_background.py — https://github.com/YarvixPA/ComfyUI-YarvixPA/blob/main/nodes/Image/Remove%20Background/remove_background.py

- Apply Style Model (ApplyStyleModelEnhanced)  
  - Category: ComfyUI-YarvixPA/Flux/Redux  
  - Description: Encodes images with a CLIP Vision encoder and applies a style model to modify conditioning. Supports multiple optional images/strengths and different strength application methods (multiply or attention bias). Outputs modified conditioning for downstream pipelines.  
  - Source: nodes/Flux/Redux/apply_style_model_enhanced.py — https://github.com/YarvixPA/ComfyUI-YarvixPA/blob/main/nodes/Flux/Redux/apply_style_model_enhanced.py

- Inpaint Flux Kontext Conditioning (InpaintFluxKontextConditioning)  
  - Category: ComfyUI-YarvixPA/Flux/Kontext  
  - Description: Adds context-aware inpainting conditioning for Flux pipelines. Encodes pixels into latents via a VAE, prepares masked/noise-masked latents, and extends the positive/negative conditioning sets with concat latents and reference latents for context-aware inpainting. Returns modified positive/negative conditioning and a latent dict.  
  - Source: nodes/Flux/Kontext/inpaint_flux_kontext.py — https://github.com/YarvixPA/ComfyUI-YarvixPA/blob/main/nodes/Flux/Kontext/inpaint_flux_kontext.py

- 🚀 Text Field (TextFieldNode)  
  - Category: ComfyUI-YarvixPA/Utils/Text  
  - Description: A simple multiline text field node that outputs the entered string. Useful for storing prompts, notes, or small pieces of text in a graph.  
  - Source: nodes/Utils/Text/text_field.py — https://github.com/YarvixPA/ComfyUI-YarvixPA/blob/main/nodes/Utils/Text/text_field.py

---

If you want, I can:
- Expand each node entry with its input/output types and default values,
- Add example usage snippets or small screenshots,
- Create/commit this README.md to the repository (I can prepare a commit PR or push if you provide the repo owner/branch instructions).
