import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

regions = ['N', 'NE', 'SE', 'S', 'CO', 'Geral']

def get_df_reg(comp, ano):
    df_reg = {}

    for reg in regions:
        if reg=='Geral':
            df = pd.read_csv("../Data/Processed/ENEM"+ano+"/Concluintes_regulares_"+comp+".csv")
        else:
            df = pd.read_csv("../Data/Processed/ENEM"+ano+"/CR_regiao"+reg+"_"+comp+".csv")

        df_reg[reg] = df
    return df_reg

def print_mean_std(df_reg, comp):
    for reg in ['N', 'NE', 'SE', 'S', 'CO', 'Geral']:
        print(f"{reg} - Média: {df_reg[reg]['NU_NOTA_'+comp].mean():.2f};   Std: {df_reg[reg]['NU_NOTA_'+comp].std():.2f}")
        
def plot_hist_scores(df_reg, comp):
    fig, axs = plt.subplots(2, 3, figsize=(15,8), sharex=True)#, sharey=True)

    fig.suptitle('Histograma de notas - '+comp)

    axs[0,0].hist(df_reg['Geral']['NU_NOTA_'+comp], bins=20, color='gray')
    axs[0,0].set_title("Geral")
    axs[0,1].hist(df_reg['N']['NU_NOTA_'+comp], bins=20, color='tab:blue')
    axs[0,1].set_title("Norte")
    axs[0,2].hist(df_reg['NE']['NU_NOTA_'+comp], bins=20, color='tab:orange')
    axs[0,2].set_title("Nordeste")
    axs[1,0].hist(df_reg['SE']['NU_NOTA_'+comp], bins=20, color='tab:green')
    axs[1,0].set_title("Sudeste")
    axs[1,1].hist(df_reg['S']['NU_NOTA_'+comp], bins=20, color='tab:red')
    axs[1,1].set_title("Sul")
    axs[1,2].hist(df_reg['CO']['NU_NOTA_'+comp], bins=20, color='tab:brown')
    axs[1,2].set_title("Centro-Oeste")

    axs[1,0].set_xlabel('Nota')
    axs[1,1].set_xlabel('Nota')
    axs[1,2].set_xlabel('Nota')

    axs[0,0].set_ylabel('Quantidade')
    axs[1,0].set_ylabel('Quantidade')

    plt.show()
    
def bin_scores(df_reg, comp, questoes_list, nota_min=300, nota_max=760, step=20):

    bins = np.arange(nota_min,nota_max,step)
    
    bin_reg = {}

    for reg in ['N', 'NE', 'SE', 'S', 'CO', 'Geral']:
        df_reg[reg]['Range'+comp] = pd.cut(df_reg[reg]['NU_NOTA_'+comp], bins, right=False)

        bin_r = df_reg[reg][df_reg[reg]['NU_NOTA_'+comp]!=0].groupby('Range'+comp).count()[['NU_INSCRICAO']]
        bin_r = bin_r.rename(columns={'NU_INSCRICAO': 'Total'})
        bin_r = bin_r.join(df_reg[reg][df_reg[reg]['NU_NOTA_'+comp]!=0].groupby('Range'+comp).sum()[questoes_list])

        for q in questoes_list:
            bin_r[q] = bin_r[q]/bin_r['Total']
            
        bin_reg[reg] = bin_r
        
    return bin_reg

def auc_regions(bin_reg, questoes_list):
    auc_reg = pd.DataFrame()
    
    for reg in ['N', 'NE', 'SE', 'S', 'CO', 'Geral']:
        auc_reg[reg] = bin_reg[reg][questoes_list].sum()
        
    return auc_reg

def sort_abs_auc_dif(auc_reg):
    print(auc_reg.diff(axis=1).abs().max(axis=1).sort_values())
    
def plot_item_compar(bin_reg, comp, item):
    bin_item = bin_reg['Geral'][[item]]
    bin_item = bin_item.rename(columns={item: 'Geral'})
    for reg in ['N', 'NE', 'SE', 'S', 'CO']:
        bin_item[reg]  = bin_reg[reg][item]

    bin_item.plot(figsize=(8,6), style=['k--'],
                  title='Proporção de acertos por nota para cada região - '+comp+' '+item,
                  xlabel='Nota', ylabel='Proporção de acertos')
    plt.show()