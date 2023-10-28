import json

class Config:
    timeout: int
    input_process_timeout: int
    granted_modules: list

    def __init__(self):
        with open("./config.json") as file:
            data = json.load(file)
            self.timeout = data["timeout"]
            self.granted_modules = data["modules"]
            self.input_process_timeout = data["input_process_timeout"]
    def test(self):
        print(self.timeout, self.input_process_timeout, self.granted_modules)
        print(self.granted_modules)
