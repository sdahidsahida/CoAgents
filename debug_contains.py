# debug_contains.py
from framework.tools.tool_manager import ToolManager

tm = ToolManager()

year, month, day, hour, minute = 2002, 2, 2, 2, 2
gender = "男"
location = {"lat": "39n54", "lon": "116e23"}

for tool_type in ["bazi", "ziwei", "astrology"]:
    r = tm.calculate(tool_type, year, month, day, hour, minute, gender, location)
    txt = tm.format_for_prompt(tool_type, r) if r.get("success") else str(r)
    print("\n====", tool_type, "====")
    print("success:", r.get("success"), "err:", r.get("error"))
    print("contains 女命?:", ("女命" in txt))
    print(txt[:800])
