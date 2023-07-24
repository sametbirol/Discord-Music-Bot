import os
from error_logger import log_error
from dotenv import load_dotenv
load_dotenv()
TOP_LIMIT = int(os.getenv("TOP_LIMIT"))
BOTTOM_LIMIT = int(os.getenv("BOTTOM_LIMIT"))


def log_music_search_result(server_name, search_query, result):
    filename = f"{server_name}_log.txt"
    collectiveList = []
    with open(filename, "a", encoding="utf-8") as file:
        file.write(f"Search Query: {search_query}\n")
        try:
            for entry in result["entries"]:
                lowest_kpbs_format = filter_formats(entry)
                if lowest_kpbs_format != False:
                    collectiveList.append(lowest_kpbs_format)
                    file.write(f'{lowest_kpbs_format} \n')
        except Exception as e:
            log_error(e)
    return collectiveList


def filter_formats(entry):
    copy_top_limit = TOP_LIMIT
    filtered_formats = []
    try:
        while not filtered_formats and copy_top_limit < 256:
            filtered_formats = [
                {
                    "source": fmt["url"],
                    "title": entry["title"],
                    "abr": fmt["abr"],
                }
                for fmt in entry["formats"]
                if fmt.get("abr", 0)
                and BOTTOM_LIMIT <= fmt["abr"] <= copy_top_limit
                and fmt["acodec"] != "none"
                and fmt["vcodec"] == "none"
            ]
            copy_top_limit += 16

        if filtered_formats:
            return sorted(filtered_formats, key=lambda x: x["abr"])[0]
        else:
            return False
    except Exception as e:
        log_error(e)
        return False
