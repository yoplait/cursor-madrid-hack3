Fix the LibreYOLO model loading error.



Current error:

LibreYOLO() missing 1 required positional argument: 'model\_path'



The application must not call LibreYOLO() without arguments.



Add a required or default CLI argument:



\--model



Default value:

LibreYOLOXs.pt



Then initialize the model like this:



from libreyolo import LibreYOLO



model = LibreYOLO(args.model)



The README must show PowerShell examples using:



python .\\analyze\_video.py `

&#x20; --video ".\\videos\\Fortnite\_20260124123317.mp4" `

&#x20; --model "LibreYOLOXs.pt" `

&#x20; --classes person car weapon `

&#x20; --confidence 0.45 `

&#x20; --sample-rate 5 `

&#x20; --viewer `

&#x20; --save-annotated-video



Also improve the error message when the model cannot be loaded. It should say:

"Failed to load LibreYOLO model. Please provide a valid model path using --model."



Do not silently fall back to LibreYOLO() with no model.

