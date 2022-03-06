from src.etl.extract_data import extract_data_json
import json
import os
import zipfile

#Set up current dir
os.chdir('/Users/u1079317/Desktop/Personal/MSc_Exeter/Intro_DS/CW2/data/')

# #Unzip top level zip file
# with zipfile.ZipFile(file_path) as top_zip:
#     top_zip.extractall()

useful_keys = ['coordinates',
               'created_at',
               'id',
               'lang',
               'place',
               'text',
               'timestamp_ms']

useful_keys += [('user',v) for v in [ 'name', 'screen_name', 'id']]

list_dict = []

cwd = os.getcwd()

for f in sorted(os.listdir())[:5]:
    with zipfile.ZipFile(os.path.join(cwd, f)) as tmp_zip:
        with tmp_zip.open(tmp_zip.namelist()[0]) as tmp_json:
            for line in tmp_json.readlines():
                line_dict = json.loads(line)
                list_dict.append(extract_data_json(line_dict, useful_keys))


print(len(list_dict))