from libreyolo import SAMPLE_IMAGE

from .service import detect, result_to_dict

result = detect(SAMPLE_IMAGE, save=True)

print(result.boxes.xyxy)
print(result.boxes.conf)
print(result.names[result.boxes.cls[0].item()])
print(getattr(result, "saved_path", None))
print(result_to_dict(result))
