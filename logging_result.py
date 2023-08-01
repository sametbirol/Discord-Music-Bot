import os
from error_logger import log_error,log_info
from dotenv import load_dotenv
load_dotenv()
TOP_LIMIT = int(os.getenv("TOP_LIMIT"))
BOTTOM_LIMIT = int(os.getenv("BOTTOM_LIMIT"))


def filter_info(result):
    collectiveList = []
    try:
        for entry in result["entries"]:
            lowest_kpbs_format = filter_formats(entry)
            if lowest_kpbs_format != False:
                log_info(lowest_kpbs_format)
                collectiveList.append(lowest_kpbs_format)
    except Exception as e:
        log_error(e)
    return collectiveList


def filter_formats(entry):
    available_formats = []
    filtered_formats = []
    try: 
        for element in entry:
            available_formats.append(element)
            
    except Exception as e:
        log_error(e)
    try:
        filtered_formats = [
            {
                "source": fmt["url"],
                "title": entry["title"],
                "abr": fmt["abr"],
                "description" : entry["description"],
                "thumbnail" : entry["thumbnail"],
                "duration_string" : entry["duration_string"],
                "webpage_url" : entry["webpage_url"],
            }
            for fmt in entry["formats"]
            if fmt.get("abr", 0)
            and BOTTOM_LIMIT <= int(fmt["abr"]) <= TOP_LIMIT
            and fmt["acodec"] != "none"
            and fmt["vcodec"] == "none"
        ]
        log_info(available_formats)
        log_info({'thumbnail' : entry["thumbnail"]})
        log_info({'webpage_url' : entry["webpage_url"]})
        log_info({'fulltitle' : entry["fulltitle"]})
        log_info({'duration_string' : entry["duration_string"]})
        log_info({'original_url' : entry["original_url"]})
        if filtered_formats:
            return sorted(filtered_formats, key=lambda x: x["abr"],reverse=True)[0]
        else:
            return False
    except Exception as e:
        log_error(e)
        return False
