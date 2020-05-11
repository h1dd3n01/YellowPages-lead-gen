import json


class YellowBotPipeline:
    def process_item(self, item, spider):
        with open('leads.json', 'r+') as f:
            file = f.read()
            obj = json.loads(file)
            obj['list'].append(item)
            f.seek(0)
            f.write(json.dumps(obj))
            f.close()
        return item
