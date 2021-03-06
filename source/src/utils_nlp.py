import torch
import pandas as pd
from os import walk
import numpy as np
import json

def xo_merge_files(path_in, path_out, extension):
    # initiate a empty string
    final_text = ""
    # get all the files with extension js, the walk function gives a tuple
    for (dirpath, dirname, filenames) in walk(path_in):
        for file in filenames:
            # the / is important :D
            my_path = dirpath + "/" + file
            if my_path.endswith('.' + extension):
                with open(my_path) as file:
                    # read the whole file
                    final_text += file.read()
    with open(path_out, "w") as f:
        f.write(final_text)


def xo_read_file(path):
    try:
        with open(path, "r") as f:
            return f.read()
    except:
        print("file doesn't exist")


def xo_read_lines(path):
    lines = []
    with open(path, "r", encoding="utf8") as f:
        for line in f:
            lines.append(line.strip())
    return lines


def xo_write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

def xo_write_json(path, dataframe):
    dataframe.to_json(path, force_ascii=False,orient="records")

def xo_write_json_fromlist(path, ls):
    with open(path, 'w', encoding='utf-8') as outfile:
        json.dump(ls, outfile, ensure_ascii=False)

def xo_count_words(s):
    return len(s.split())


def xo_replace_with_mask(sent, index, word):
    sent = sent.split()
    sent[index] = "<mask>"
    masked_sent = " ".join(sent).replace("' ", "'").replace(" ,", ",").replace(" .", ".").replace("$$ ", "")
    return masked_sent


def xo_prob_options(obj_camembert, options):
    answers = [(x[2].strip(), x[1]) for x in obj_camembert if x[2].strip() in options]
    # different number of answers
    if len(answers) == 0:
        return (0, 0, 0, 0)
    elif len(answers) == 1:
        return (answers[0][0], answers[0][1], 0, 0)
    else:
        return (answers[0][0], answers[0][1], answers[1][0], answers[1][1])


def xo_load_data():
    pd_good = pd.read_csv("wino_for_bert_changed.csv", sep=";")
    pd_good = pd_good.iloc[:, 1:]
    col_names = list(pd_good.columns)
    pd_good = pd.read_csv("wino_for_bert_changed.csv", sep=";", names=col_names, header=None)
    # pd_good = pd_good.iloc[:, 1:]
    pd_good["response1"] = 0
    pd_good["prob1"] = 0
    pd_good["response2"] = 0
    pd_good["prob2"] = 0
    pd_good = pd_good.iloc[1:, :]
    return pd_good


def xo_load_cam(model):
    camembert = torch.hub.load('pytorch/fairseq', model)
    camembert.eval()
    return camembert


def xo_produce_answers(model, pd_good):
    for i, row in pd_good.iterrows():
        masked_line = row.masked
        options = row.options.split()
        answers = model.fill_mask(masked_line, topk=100)
        pd_good.loc[i, ["response1"]], pd_good.loc[i, ["prob1"]], pd_good.loc[i, ["response2"]], pd_good.loc[
            i, ["prob2"]] = xo_prob_options(answers, options)
    return pd_good

def xo_test_single_sent(model, sent):
    ans = model.fill_mask(sent, topk=20)
    for a in ans:
        print(a)


def xo_computer_score(pd_good):
    counter_correct = 0
    counter_noresponse = 0
    counter_badresponse = 0
    for i, row in pd_good.iterrows():
        if row.answer == row.response1:
            counter_correct += 1
        elif row.response1 == 0:
            counter_noresponse += 1
        else:
            counter_badresponse += 1
    counter_total = counter_correct + counter_badresponse + counter_noresponse
    print("correct:", round(counter_correct, 2))
    print("no response:", round(counter_noresponse, 2))
    print("bad_response:", round(counter_badresponse, 2))
    print("total_responses", round(counter_total, 2))
    print("exactitude", round((counter_correct / counter_total) * 100, 2))
    print("qualite", round((counter_correct / (counter_total - counter_noresponse)) * 100, 2))
    print("reussite", round(((counter_correct + counter_noresponse / 2) / counter_total) * 100, 2))

def xo_cleanfrwac_alt(fpath):
    fr_pmi_ancien = pd.read_csv(fpath)
    # delete second and 3rd rows and reset index
    fr_pmi_ancien.drop([0, 1], inplace=True)
    fr_pmi_ancien.reset_index(drop=True, inplace=True)
    # col names lowercase and rename second column nb_npropre and keep names simple
    fr_pmi_ancien.rename(str.lower, axis='columns', inplace=True)
    fr_pmi_ancien.rename(columns={'np': 'nb_npropre', 'r0 lm': 'r0', 'r1 lm': 'r1', 'item': 'schema'}, inplace=True)
    # keep 8 first columns
    fr_pmi_ancien.drop(fr_pmi_ancien.columns[8:], axis=1, inplace=True)
    fr_pmi_ancien.dropna(how='all', inplace=True)
    fr_pmi_ancien['type'].replace(np.nan, "alt", inplace=True)
    fr_pmi_ancien['type'].replace("std", "alt", inplace=True)
    # reorder columns
    fr_pmi_ancien = fr_pmi_ancien[["schema", "type", "nb_npropre", "r0", "r1", "question","special","alternate"]]
    fr_pmi_ancien_alt = fr_pmi_ancien[fr_pmi_ancien["type"] == "alt"]
    # clean a non existence row
    fr_pmi_ancien_alt.drop([131], inplace=True)
    return fr_pmi_ancien_alt

def xo_read_json(path):
    with open(path) as f:
        data = json.load(f)
    return data