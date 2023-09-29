import json
import os


def get_list_json_files():
    file_list = os.listdir(os.getcwd())
    json_files = [
        file
        for file in file_list
        if file.endswith(".json")
    ]
    return json_files


def get_data_from_parameters_file(file_name):
    with open(f"{file_name}.json", "r") as parameters:
        data = json.load(parameters)
    return data
