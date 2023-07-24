import os
from dotenv import load_dotenv
load_dotenv()
TOP_LIMIT = int(os.getenv("TOP_LIMIT"))
BOTTOM_LIMIT = int(os.getenv("BOTTOM_LIMIT"))


def log_music_search_result(server_name, search_query, result):
    filename = f"{server_name}_log.txt"
    collectiveList = []
    with open(filename, "a", encoding="utf-8") as file:
        file.write(f"Search Query: {search_query}\n")
        for entry in result["entries"]:
            filtered = filter_formats(entry)
            # print("filtered data", filtered)
            sorted_data = sorted(filtered, key=lambda x: x['abr'])
            # print("aorted data", sorted_data)
            collectiveList.append(sorted_data[0])
            # file.write(f'{sorted_data[0]} \n')
            # file.write(f'{sorted_data} \n')
            allfiltered_sorted = sorted(filter_formats(entry), key=lambda x: x['abr'])
            allfiltered_sorted = sorted(filter_formats(entry), key=lambda x: x['abr'])
            file.write(f'{allfiltered_sorted} \n')
    return collectiveList


def filter_formats(entry):
    
    filtered_formats = [{'source': fmt['url'], 'title': entry['title'], 'abr' : fmt['abr']} for fmt in entry['formats'] if fmt.get('abr', 0) and BOTTOM_LIMIT <= fmt['abr'] <= TOP_LIMIT and fmt['acodec'] != 'none' and fmt['vcodec'] == 'none']
    return filtered_formats
    
