
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import math

def fix_scientific_notation_text(text):  
    split_text = text.split('E')
    if len(split_text) > 1:
        mantissa = float(split_text[0])
        exponent = float(split_text[1])
        return(mantissa*math.pow(10, exponent))
    else:
        return(float(split_text[0]))

def extract_steady_state_df(file):
    lines = []
    with open(file, 'r') as f:
        for line in f:
            lines.append(line)
    state_text_start = "The steady states shown below are both consistent with the mass"
    state_text_end = "Eigenvalues for Steady State No. 1"

    state_text_start_index = [i for i, item in enumerate(lines) if re.search(state_text_start, item)][0]
    state_text_end_index = [i for i, item in enumerate(lines) if re.search(state_text_end, item)][0]
    steady_state_lines = lines[(state_text_start_index+6):(state_text_end_index - 2)]
    new_lines = []
    for line in steady_state_lines:
        new_line = line.split('\t')
        species = new_line[1].strip()
        steady_state_1 = new_line[0].strip()
        steady_state_2 = new_line[2]

        steady_state_1 = fix_scientific_notation_text(steady_state_1)
        steady_state_2 = re.sub(r'\\', '', steady_state_2).strip()
        steady_state_2 = fix_scientific_notation_text(steady_state_2)
        
        new_line = [species, steady_state_1, steady_state_2]
        new_lines.append(new_line)
    df = pd.DataFrame(new_lines, columns = ['species', 'steady_state_1', 'steady_state_2'])
    df['species'] = df['species'].str.replace('*', 'a')
    return(df)
    


def parse_rate_line(line):
    split_line_1 = line.split('>')
    left_text = split_line_1[0]
    product_text = split_line_1[1]
    product_text = re.sub('\\n', '', product_text)
    product_text = re.sub(r'\\', '', product_text)
    
    split_line_2 = re.split(r'-+', left_text, maxsplit=1)
    reactants_text = split_line_2[0].strip()
    
    rate_text = split_line_2[1]
    rate_text = re.sub(r'\-+$', '', rate_text)
    rate_text_split = rate_text.split('E')
    if len(rate_text_split)>1:
        mantissa = float(rate_text_split[0])
        exponent = float(rate_text_split[1])
        rate = mantissa*math.pow(10, exponent)
    else:
        rate = float(rate_text_split[0])
    return([reactants_text, product_text, rate])

def format_species_names(df):
    df['reactants'] = df['reactants'].str.replace('*', 'a')
    df['reactants'] = df['reactants'].str.replace('0', 'empty')
    df['products'] = df['products'].str.replace('*', 'a')
    df['products'] = df['products'].str.replace('0', 'empty')

    df['reactants'] = df['reactants'].str.split('+')
    df['reactants'] = df['reactants'].apply(lambda x: [txt.strip() for txt in x])
    df['reactants'] = [sorted(x) for x in df['reactants']]
    df['products'] = df['products'].str.split('+')
    df['products'] = [sorted(x) for x in df['products']]
    df['products'] = df['products'].apply(lambda x: [txt.strip() for txt in x])
    df['products'] = [sorted(x) for x in df['products']]

    df['reactant_text'] = df['reactants'].apply(lambda x: '+'.join(x))
    df['product_text'] = df['products'].apply(lambda x: '+'.join(x))
    
    return(df)

def extract_rate_df(file):
    assert 'higher_deficiency' in file
    lines = []
    with open(file, 'r') as f:
        for line in f:
            lines.append(line)
    rates_text_start = 'The following mass action system gives rise to multiple steady states:'
    rates_text_end = 'The steady states shown below are both consistent with the mass'
    rates_text_start_index = [i for i, item in enumerate(lines) if re.search(rates_text_start, item)][0]
    rates_text_end_index = [i for i, item in enumerate(lines) if re.search(rates_text_end, item)][0]
    rate_lines = lines[(rates_text_start_index+3):(rates_text_end_index - 2)]
    parsed_rate_lines = [parse_rate_line(x) for x in rate_lines]
    print(file)
    df = pd.DataFrame(parsed_rate_lines, columns = ['reactants', 'products', 'rate'])
    df = format_species_names(df)
    return(df)


def extract_rate_df2(file):
    df = pd.read_csv(file)
    # df['reactants'] = df['reactants'].str.replace('*', 'a')
    df['reactants'] = [re.split('=>', x)[0] for x in df['reaction']]
    df['reactants'] = ['empty' if x=='' else x for x in df['reactants']]
    df['products'] = [re.split('=>', x)[1] for x in df['reaction']]
    df['products'] = ['empty' if x=='' else x for x in df['products']]

    df['reactants'] = df['reactants'].str.split('+')
    df['reactants'] = [sorted(x) for x in df['reactants']]
    df['products'] = df['products'].str.split('+')
    df['products'] = [sorted(x) for x in df['products']]
    df['reactant_text'] = df['reactants'].apply(lambda x: '+'.join(x))
    df['product_text'] = df['products'].apply(lambda x: '+'.join(x))
    df['ss_rate'] = df['rate']
    df = df[['reactants', 'products', 'ss_rate']]
    return(df)

# # file = 'crntoolbox_results_aug_15\legewi_wild_higher_deficiency.rtf'
# # ss_df = extract_steady_state_df(file)
# # print(ss_df)

# # rdf = extract_rate_df(file)
# # print(rdf)