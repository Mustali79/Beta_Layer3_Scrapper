import requests
import pandas as pd
import logging
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)


def get_description(item):

    description = ""
    if "missionDoc" not in item:
        return description
    for firstContent in item['missionDoc']['content']:
        for secondContent in firstContent.get("content", []):
            description += secondContent.get("text", "")
        description += "\n"
    return description

url = "https://beta.layer3.xyz/api/trpc/task.getTasks"

next_cursor = "null"
res = []

page = 1
while True:

    if next_cursor == "null":
        querystring = {"input":"{\"json\":{\"taskType\":[\"BOUNTY\",\"QUEST\"],\"onlyUnavailable\":null,\"onlyClaimed\":null,\"onlyInProgressQuests\":null,\"includeFeatured\":false,\"includeClaimed\":false,\"includeExpired\":false,\"cursor\":null},\"meta\":{\"values\":{\"onlyUnavailable\":[\"undefined\"],\"onlyClaimed\":[\"undefined\"],\"onlyInProgressQuests\":[\"undefined\"],\"cursor\":[\"undefined\"]}}}"}
    else:
        querystring = {"input":"{\"json\":{\"taskType\":[\"BOUNTY\",\"QUEST\"],\"onlyUnavailable\":null,\"onlyClaimed\":null,\"onlyInProgressQuests\":null,\"includeFeatured\":false,\"includeClaimed\":false,\"includeExpired\":false,\"cursor\":" + str(next_cursor) + "},\"meta\":{\"values\":{\"onlyUnavailable\":[\"undefined\"],\"onlyClaimed\":[\"undefined\"],\"onlyInProgressQuests\":[\"undefined\"],\"cursor\":" + str(next_cursor) + "}}}"}

    payload = ""
    logging.info(f"Getting jobs for {page} page")
    response = requests.request("GET", url, data=payload, params=querystring)

    data = response.json()
    items = data['result']['data']['json']['items']
    for item in items:
        res.append(item)
        if item['numberOfSubTasks'] > 0:
    
            slug = item['namespace']
            new_url = 'https://beta.layer3.xyz/api/trpc/config.globalAnnouncement,quest.childTasksFromQuestSlug?batch=1&input={"0":{"json":null,"meta":{"values":["undefined"]}},"1":{"json":{"slug":"' + slug + '"}}}'
            
            content = requests.get(new_url)
            new_data = content.json()
            new_bounties = [x["ChildTask"] for x in new_data[1]['result']['data']['json']]
            for bounty in new_bounties:
                bounty["parent_id"] = item["id"]
            res += new_bounties
            
    descriptions = [get_description(item) for item in res]
    df = pd.json_normalize(res)
    df = df[["id", "title", "xp", "numberOfSubTasks", "Dao.name", "parent_id"]]
    df.columns = ["id", "title", "xp", "number of sub-bounties", "Dao name", "parent_id"]
    df["description"] = descriptions
    df.to_csv('beta_layer_results.csv', index=False)

    next_cursor = data['result']['data']['json']['nextCursor']
    if next_cursor == None:
        break
    page += 1

logging.info(f"Found {len(df)} total bounties")
    


