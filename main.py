from model import setup_model
from clean_response import parse_json_from_gemini
from calendarAPI import sync_to_calendar
import pathlib
import ast

if not pathlib.Path('schedule.json').exists():
    model_response = setup_model()
    json_str = parse_json_from_gemini(model_response)
    with open("schedule.json", "w+") as f:
        f.write(str(json_str))
else:
    with open("schedule.json", "r") as f:
        json_str = f.read()


print(json_str,"\n\n\n")
events = ast.literal_eval(json_str)
for i in range(len(events)):
    print(events[i],"\n\n")
    sync_to_calendar(events[i])
