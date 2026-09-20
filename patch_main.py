import sys

with open("main.py", "r") as f:
    content = f.read()

tmb_code = """
import aiohttp

TMB_APP_ID = "22b90d81"
TMB_APP_KEY = "529556e542a70f94952dab25eac1bb7f"

async def fetch_tmb_eta(line: str, stop_code: str):
    url = f"https://api.tmb.cat/v1/ibus/lines/{line}/stops/{stop_code}?app_id={TMB_APP_ID}&app_key={TMB_APP_KEY}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=2.5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    arrivals = data.get("data", {}).get("ibus", [])
                    res = []
                    for arr in arrivals:
                        res.append({
                            "line": arr.get("line"),
                            "destination": arr.get("destination"),
                            "eta": int(arr.get("t-in-min", 0))
                        })
                    return res
    except Exception as e:
        print(f"TMB ETA Error: {e}")
    return []
"""
content = content.replace("async def fetch_fgv_eta(", tmb_code + "\nasync def fetch_fgv_eta(")

get_eta_patch = """        elif type == "metrobus":
            arrivals = await fetch_metrobus_eta(id)
        elif type == "tmb":
            parts = id.split("_")
            if len(parts) == 2:
                arrivals = await fetch_tmb_eta(parts[0], parts[1])"""
content = content.replace('        elif type == "metrobus":\n            arrivals = await fetch_metrobus_eta(id)', get_eta_patch)

get_live_patch = """            elif "tram" in agency_lower: leg_type = "tram"
            elif "tmb" in agency_lower: leg_type = "tmb"
            
            stop_id = leg["from"].get("stopId", "")
            if ":" in stop_id: stop_id = stop_id.split(":")[-1]
            
            if leg_type == "tmb":
                stop_code = leg["from"].get("stopCode", "")
                if not stop_code:
                    parts = stop_id.split(".")
                    if len(parts) >= 2: stop_code = parts[1]
                    else: stop_code = stop_id
                line = leg.get("routeShortName", "")
                stop_id = f"{line}_{stop_code}"
                if not line: return None"""
content = content.replace('            elif "tram" in agency_lower: leg_type = "tram"\n            \n            stop_id = leg["from"].get("stopId", "")\n            if ":" in stop_id: stop_id = stop_id.split(":")[-1]', get_live_patch)


is_rail_patch = """                    agency_lower = leg.get("agency", "").lower()
                    if "metro valencia" in agency_lower or "metrovalencia" in agency_lower or "tram" in agency_lower or ("tmb" in agency_lower and leg["mode"] != "BUS"):
                        is_rail = True
                    else:
                        is_bus = True"""
content = content.replace('                    agency_lower = leg.get("agency", "").lower()\n                    if "metro valencia" in agency_lower or "metrovalencia" in agency_lower or "tram" in agency_lower:\n                        is_rail = True\n                    else:\n                        is_bus = True', is_rail_patch)


leg_type_patch = """                elif "tram" in agency_lower: leg_type = "tram"
                elif "tmb" in agency_lower: leg_type = "tmb"
                
                if leg_mode != "WALK" and leg_type in ["metro", "tram"]:"""
content = content.replace('                elif "tram" in agency_lower: leg_type = "tram"\n                \n                if leg_mode != "WALK" and leg_type in ["metro", "tram"]:', leg_type_patch)

with open("main.py", "w") as f:
    f.write(content)

