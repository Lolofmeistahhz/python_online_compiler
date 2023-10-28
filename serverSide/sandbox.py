import subprocess
import os
import uuid
import re
import json
from config import Config
class CodeRunner:
    FILE_DEFAULT_NAME = "runnable.py"
    FILE_DEFAULT_PREVENT = "prevent.py"
    FILE_DEFAULT_UNPREVENT = "unprevent.py"
    SOLUTIONS_DEFAULT_PATH = "files/"
    DEFAULT_TIMEOUT = 5
    INPUT_REGEX = r"input\s{0,1}\("
    SECRET = "C7SNKxm9knQd3r9xyC8qDNTm65wAY8fNhDzF"
    PREVENT_CONTENT = "" # после init не будет пустым
    def __init__(self, config: Config):
        self.DEFAULT_TIMEOUT = config.timeout
        self.update_prevent(config.granted_modules)
    
    def update_prevent(self, modules: list):
        prevent_material_data = ""
        with open("./files/prevent_material.py") as prevent_material:
            prevent_material_data = prevent_material.read()
        
        prevent_material_data = prevent_material_data.replace("granted_modules", str(modules))

        injected_string = "import sys\n"

        self.PREVENT_CONTENT = injected_string + prevent_material_data


    def defend_from_bad_activity(self, output: str):
        # check if the user finds the real input
        if self.SECRET in output :
            return output.replace(self.SECRET, "")
        return output

    def check_for_input(self, code: str):
        match = re.search(self.INPUT_REGEX, code)
        if match:
            return True
        return False
    
    def __run(self, filename: str):
        try:
            result = subprocess.run(["python3", "files/" + filename ], 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                    universal_newlines=True, timeout=self.DEFAULT_TIMEOUT)
            stdout_output = result.stdout
            stderr_output = result.stderr
            return_code = result.returncode
            return (return_code, stdout_output, stderr_output)
        except subprocess.TimeoutExpired:
            return (-1, "", "Timeout excedeed")

    def run_code(self, code: str):
        # if everything is good
        # используем prevent_content из инициализации
        self.add_file(self.PREVENT_CONTENT + "\n" + code)
        # проверка на наличие input() в code
        if self.check_for_input(code):
            return (0, "", "", uuid.uuid4())
        returncode, output, error = self.__run(self.FILE_DEFAULT_NAME)
        return (returncode, output, error, None)
        
    def add_file(self, code: str):
        with open("./files/" + self.FILE_DEFAULT_NAME, "w") as file:
            file.write(code)
        pass
    
    def add_to_file(self, code: str):
        with open("./files/" + self.FILE_DEFAULT_NAME, "a") as file:
            file.write("\n" + code)
    