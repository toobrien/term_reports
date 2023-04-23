from v2.cot_v2_api  import API_ROOT, REPORT_STR
from requests       import get


if __name__ == "__main__":

    fd = open("./raw_recs.py", "w")

    file_txt = "from enum import IntEnum\n\n\n"

    for rt in REPORT_STR.values():

        res = get(f"{API_ROOT}/{rt}/index")
        res = res.json()

        for code, desc in res.items():

            res     = get(f"{API_ROOT}/{rt}/{code}")
            res     = res.json()
            keys    = list(res.keys())

            enum_def = f"class {rt}_raw(IntEnum):\n\n"

            for i in range(len(keys)):

                field_name =    keys[i].lower()         \
                                .replace("-", "_")      \
                                .replace(" ", "_")      \
                                .replace("(", "")       \
                                .replace(")", "")       \
                                .replace("=", "")       \
                                .replace("%", "pct")    \
                                .strip()

                enum_def += f"\t{field_name:40s} = {i}\n"

            file_txt += f"{enum_def}\n\n"

            break
    
    fd.write(file_txt)
