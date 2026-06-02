from libreyolo import LibreYOLO, SAMPLE_IMAGE

# RF-DETR is the transformer flagship. The "-seg" suffix tells the factory
# to load the segmentation head. Same call shape as detection.
model = LibreYOLO("LibreRFDETRs-seg.pt")

# save=True draws boxes plus translucent mask overlays on top of the image.
result = model(SAMPLE_IMAGE, save=True)

# Boxes still work the same as in detection
print(result.boxes.xyxy)            # (N, 4) bounding boxes
print(result.boxes.cls)             # (N,) class IDs

# Masks are the new bit
print(result.masks.data.shape)      # (N, H, W) binary masks at image resolution
print(result.masks.xy[0].shape)     # polygon contour for the first instance
print(getattr(result, "saved_path", None))  # annotated output path
