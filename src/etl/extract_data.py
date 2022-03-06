
def extract_data_json(json_dict, useful_keys):
    json_dict_output = {}
    for k in useful_keys:
        if type(k) == tuple:
            json_dict_output[f'{k[0]}_{k[1]}'] = json_dict[k[0]][k[1]]
        else:
            json_dict_output[k] = json_dict[k]

    return json_dict_output