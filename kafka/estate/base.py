CREATED = "created"

class StorageEvent:
    def __init__(self, path, format="html", _type=CREATED):
        self.path = path
        self.type = _type
        self.format = format
    def to_dict(self):
        return {
            "path": self.path,
            "type": self.type,
            "format": self.format
        }
    def to_json(self):
        import json
        return json.dumps(self.to_dict())