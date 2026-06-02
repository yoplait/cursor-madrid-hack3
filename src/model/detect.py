from libreyolo import LibreYOLO, SAMPLE_IMAGE

# One factory, any architecture. Auto-detects family, size, and classes.
model = LibreYOLO("LibreYOLO9t.pt")

# Accepts file paths, URLs, PIL, NumPy, tensors, or raw bytes.
result = model(SAMPLE_IMAGE, save=True)

print(result.boxes.xyxy)        # (N, 4) tensor of bounding boxes
print(result.boxes.conf)        # (N,) confidence scores
print(result.names[result.boxes.cls[0].item()])  # class name of the first detection
print(getattr(result, "saved_path", None))  # where the annotated image was saved
