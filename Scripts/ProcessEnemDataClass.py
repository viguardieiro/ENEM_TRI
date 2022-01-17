import pandas as pd
import numpy as np
from tqdm import tqdm

import matplotlib.pyplot as plt

from pathlib import Path

class ProcessEnemData():
    def __init__(self, ano=2019):

        self.ano = ano

        self.original_file_path = "../Data/Original/microdados_enem_"+str(self.ano)+"/DADOS/MICRODADOS_ENEM_"+str(self.ano)+".csv"
        self.clean_file_path = "../Data/Processed/ENEM"+str(self.ano)+"/All.csv"

        self.df = None
        self.df_grupo = None
        self.base_path = "../Data/Processed/ENEM"+str(self.ano)+"/CR_data/"

    def get_data(self, chunksize = 10 ** 5):
        print(f"[INFO] Processando dados do ENEM {self.ano}...")
        
        print("[INFO] Checando se os dados já foram processados...")
        if Path(self.clean_file_path).exists():
            print("[INFO] Arquivo de dados encontrado.")
            self.df = pd.read_csv(self.clean_file_path)

        else:
            print("[INFO] Arquivo de dados não encontrado.")
            print("[INFO] Processando dados...")
            features = ['NU_INSCRICAO', 'TP_DEPENDENCIA_ADM_ESC', 'TP_ST_CONCLUSAO', 'TP_ENSINO',
                        'CO_MUNICIPIO_RESIDENCIA', 'SG_UF_ESC', 'TP_SEXO', 'Q006', 'TP_COR_RACA',
                        'TP_PRESENCA_CN',  'TP_PRESENCA_CH',  'TP_PRESENCA_LC',  'TP_PRESENCA_MT',
                        'NU_NOTA_CN',      'NU_NOTA_CH',      'NU_NOTA_LC',      'NU_NOTA_MT', 
                        'CO_PROVA_CN',     'CO_PROVA_CH',     'CO_PROVA_LC',     'CO_PROVA_MT', 
                        'TX_RESPOSTAS_CN', 'TX_RESPOSTAS_CH', 'TX_RESPOSTAS_LC', 'TX_RESPOSTAS_MT',
                        'TX_GABARITO_CN',  'TX_GABARITO_CH',  'TX_GABARITO_LC',  'TX_GABARITO_MT',
                        'TP_LINGUA']
            
            enem_df = None

            with pd.read_csv(self.original_file_path,
                        sep=';', encoding='latin-1', chunksize=chunksize, 
                        index_col=False, dtype='unicode') as reader:
                for chunk in reader:
                    df = chunk[features]

                    if enem_df is None:
                        enem_df = df
                    else:
                        enem_df = enem_df.append(df)
                    
            print("[INFO] Processamento de dados concluído.")
            
            print("[INFO] Salvando dados processados...", end='')
            enem_df.to_csv(self.clean_file_path, index = False)
            print("Concluído.")
            
            print(f"[INFO] {enem_df.shape[0]} participantes no total.")
            
            df = enem_df[enem_df['TP_ST_CONCLUSAO']=='2'].copy() # Concluintes no ano
            df.drop(['TP_ST_CONCLUSAO'], axis=1, inplace=True)
            df.to_csv("../Data/Processed/ENEM"+str(self.ano)+"/Concluintes.csv", index = False)
            print(f"[INFO] {df.shape[0]} participantes concluintes no total.")
            
            df = enem_df[(enem_df['TP_ST_CONCLUSAO']=='2') & (enem_df['TP_ENSINO']=='1')].copy() # Concluintes regulares no ano
            df.drop(['TP_ST_CONCLUSAO'], axis=1, inplace=True)
            df.to_csv("../Data/Processed/ENEM"+str(self.ano)+"/Concluintes_regular.csv", index = False)
            print(f"[INFO] {df.shape[0]} participantes concluintes regulares.")

            df = enem_df[(enem_df['TP_ST_CONCLUSAO']!='2') | (enem_df['TP_ENSINO']!='1')].copy() # Não concluintes no ano
            df.drop(['TP_ST_CONCLUSAO'], axis=1, inplace=True)
            df.to_csv("../Data/Processed/ENEM"+str(self.ano)+"/NaoConcluintes.csv", index = False)
            print(f"[INFO] {df.shape[0]} participantes não concluintes no total.")
            print('-------------------------------------------------------------')
            
            self.df = enem_df
           
        return self.df
    
    def process_competence(self, comp, itens_anulados, all_p=True, concluintes=True):
        Path(self.base_path).mkdir(parents=True, exist_ok=True)
        if Path("../Data/Processed/ENEM"+str(self.ano)+"/All_"+comp+".csv").exists():
            print("[INFO] Tabelas de acerto por questão para "+comp+" já existem.")
        else:
            enem_df = pd.read_csv("../Data/Processed/ENEM"+str(self.ano)+"/All.csv")
            
            questoes_pd = pd.read_csv("../Data/Original/microdados_enem_"+str(self.ano)+"/DADOS/ITENS_PROVA_"+str(self.ano)+".csv",
                        sep=';')

            print(f"[INFO] Gerando tabelas de acerto para {comp}...")

            # Filtra alunos presentes na prova
            df_comp = enem_df[enem_df['TP_PRESENCA_'+comp]==1].copy()

            if comp=='LC':
                df_comp = df_comp[['NU_INSCRICAO','CO_PROVA_'+comp, 'TX_RESPOSTAS_'+comp, 'TX_GABARITO_'+comp, 'NU_NOTA_'+comp,
                              'TP_ST_CONCLUSAO', 'TP_ENSINO', 'TP_LINGUA']]
            else:
                df_comp = df_comp[['NU_INSCRICAO','CO_PROVA_'+comp, 'TX_RESPOSTAS_'+comp, 'TX_GABARITO_'+comp, 'NU_NOTA_'+comp,
                                  'TP_ST_CONCLUSAO', 'TP_ENSINO']]
            

            cadernos_comp = df_comp[['CO_PROVA_'+comp, 'TX_RESPOSTAS_'+comp]].groupby('CO_PROVA_'+comp).count()
            cadernos_comp = list(cadernos_comp[cadernos_comp['TX_RESPOSTAS_'+comp]>10000].index)

            df_comp = df_comp[df_comp['CO_PROVA_'+comp].isin(cadernos_comp)]
            # Gera colunas indicando se o candidato acertou ou não a questão
            for i_cad in range(len(cadernos_comp)):
                caderno = int(cadernos_comp[i_cad])
                print(f"[INFO]    Processando caderno {caderno} ({i_cad+1}/{len(cadernos_comp)})...", end='')
                itens_list = questoes_pd[questoes_pd['CO_PROVA']==caderno]['CO_ITEM'].copy().reset_index(drop=True)
                
                for i in range(len(itens_list)):
                    item_id = str(itens_list.iloc[i])
                    if item_id not in itens_anulados:
                        s = "Item "+item_id
                        if s not in df_comp.columns:
                            df_comp[s] = 0

                        df_comp.loc[df_comp['CO_PROVA_'+comp]==caderno,s] = df_comp[df_comp['CO_PROVA_'+comp]==caderno]['TX_RESPOSTAS_'+comp].str[i]==df_comp[df_comp['CO_PROVA_'+comp]==caderno]['TX_GABARITO_'+comp].str[i]
                        df_comp.loc[df_comp['CO_PROVA_'+comp]==caderno,s] = df_comp[df_comp['CO_PROVA_'+comp]==caderno][s].astype(int)
                        if comp=='LC':
                            df_comp.loc[((df_comp['CO_PROVA_'+comp]==caderno) & (df_comp['TX_GABARITO_'+comp].str[i]=='9'))
                                        ,s] = None
                
                print(f"Concluído.")

            df_comp.dropna(axis=0, how='any', inplace=True)
            # Transforma a coluna de notas em númerico
            df_comp['NU_NOTA_'+comp] = pd.to_numeric(df_comp['NU_NOTA_'+comp])
            df_comp.drop(['CO_PROVA_'+comp,'TX_RESPOSTAS_'+comp, 'TX_GABARITO_'+comp], axis=1, inplace=True)

            if concluintes:
                df = df_comp[(df_comp['TP_ST_CONCLUSAO']==2) & (df_comp['TP_ENSINO']==1)].copy()
                df.drop(['TP_ST_CONCLUSAO', 'TP_ENSINO'], axis=1, inplace=True)
                df.to_csv(self.base_path+"CR_"+comp+".csv", index = False)

            if all_p:
                df_comp.drop(['TP_ST_CONCLUSAO', 'TP_ENSINO'], axis=1, inplace=True)
                df_comp.to_csv("../Data/Processed/ENEM"+str(self.ano)+"/All_"+comp+".csv", index = False)

            print(f"[INFO] Processamento da competência {comp} concluído.")

            print(f"[INFO] {df_comp.shape[0]} provas de {comp}.")
            print('[INFO] Nota mínima: ', df_comp['NU_NOTA_'+comp].min())
            print('[INFO] Nota mínima (diferente de zero): ', df_comp[df_comp['NU_NOTA_'+comp]!=0]['NU_NOTA_'+comp].min())
            print('[INFO] Nota máxima: ', df_comp['NU_NOTA_'+comp].max())
            print('------------------------------------------------------')

            return df_comp

    def get_group_features(self, group_features=['NU_INSCRICAO','CO_MUNICIPIO_RESIDENCIA', 'SG_UF_ESC', 
                                            'TP_SEXO','TP_COR_RACA','Q006','TP_DEPENDENCIA_ADM_ESC', 'TP_ENSINO'],
                          gp_map_classe = {'E': ['A','B','C','D'],
                                           'D': ['E','F','G'],
                                           'C': ['H','I','J','K','L','M','N'],
                                           'B': ['O','P'],
                                           'A': ['Q']}):
        
        print("[INFO] Verificando processamento da tabela de grupos...")
        if Path("../Data/Processed/ENEM"+str(self.ano)+"/All_grupos.csv").exists():
            print("[INFO]    Tabela de grupos já existe.")
            df_grupo = pd.read_csv("../Data/Processed/ENEM"+str(self.ano)+"/All_grupos.csv")
        else:
            print("[INFO]    Tabela de grupos não encontrada.")
            print("[INFO]    Gerando tabela de grupos...")
            
            enem_df = pd.read_csv("../Data/Processed/ENEM"+str(self.ano)+"/All.csv")
            
            df_grupo = enem_df[group_features].copy()
            df_grupo.rename(columns={'Q006': 'RENDA'}, inplace=True)
            df_grupo['REGIAO'] = df_grupo['CO_MUNICIPIO_RESIDENCIA'].apply(str).str[0]
            df_grupo['REGIAO'] = df_grupo['REGIAO'].replace('n', None)
            df_grupo['REGIAO'] = pd.to_numeric(df_grupo['REGIAO'])
            
            df_grupo['CLASSE'] = 0
            for classe in gp_map_classe.keys():
                for renda in gp_map_classe[classe]:
                    df_grupo.loc[df_grupo['RENDA']==renda,'CLASSE'] = classe

            df_grupo.to_csv("../Data/Processed/ENEM"+str(self.ano)+"/All_grupos.csv", index = False)
            print("[INFO]    Processamento da tabela de grupos concluído.")
            
        self.df_grupo = df_grupo
        print('------------------------------------------------------')
        return df_grupo
            
    def process_group_competence(self, gp_feat='TP_COR_RACA', gp_name='raca', 
                                gp_map={0:'ND', 1: 'Branca', 2: 'Preta', 3:'Parda', 4:'Amarela', 5:'Indigena'}):
        print("[INFO] Verificando processamento de dados por "+gp_name+"...")
        Path(self.base_path+gp_name).mkdir(parents=True, exist_ok=True)
        if Path(self.base_path+gp_name+"/"+gp_name+"_"+gp_map[list(gp_map.keys())[0]]+"_LC.csv").exists():
            print("[INFO]    Dados por "+gp_name+" já foram processados.")
        else:
            print("[INFO]    Dados por "+gp_name+" não foram encontrados.")
            print("[INFO]    Processando dados por "+gp_name+"...")

            for g in gp_map.keys():
                nu_grupo = self.df_grupo[self.df_grupo[gp_feat]==g]['NU_INSCRICAO'].tolist()
                print(f"[INFO] Processando {gp_name} {gp_map[g]}...")
                for comp in ['LC', 'CN', 'CH', 'MT']:
                    concluintes_df = pd.read_csv(self.base_path+"CR_"+comp+".csv")
                    df_g = concluintes_df[concluintes_df['NU_INSCRICAO'].isin(nu_grupo)]
                    print(f"[INFO]     Comeptência {comp}: {df_g.shape[0]} concluintes regulares.")
                    df_g.to_csv(self.base_path+gp_name+"/"+gp_name+"_"+gp_map[g]+"_"+comp+".csv", index=False)
                print('---')
            print("[INFO]    Processamento de dados por "+gp_name+" concluído.")
        print('------------------------------------------------------')
        
    def process_classe_renda(self, gp_map_classe = {'E': ['a','b','c','d'],
                                                     'D': ['e','f','g'],
                                                     'C': ['h','i','j','k','l','m','n'],
                                                     'B': ['o','p'],
                                                     'A': ['q']}):
        Path(self.base_path+"classe").mkdir(parents=True, exist_ok=True)
        print("[INFO] Verificando processamento de dados por classe...")
        if Path(self.base_path+"classe/classe_A_LC.csv").exists():
            print("[INFO]    Dados por classe já foram processados.")
        else:
            print("[INFO]    Dados por classe não foram encontrados.")
            print("[INFO]    Processando dados por classe...")

            for classe in gp_map_classe.keys():
                print(f"[INFO] Processando classe {classe}...")
                for comp in ['LC', 'CN', 'CH', 'MT']:
                    classe_df = pd.DataFrame()
                    for renda in gp_map_classe[classe]:
                        renda_df = pd.read_csv(self.base_path+"/renda/renda_"+renda+"_"+comp+".csv")
                        classe_df = classe_df.append(renda_df)
                    print(f"[INFO]     Comeptência {comp}: {classe_df.shape[0]} concluintes regulares.")
                    classe_df['CLASSE'] = classe
                    classe_df.to_csv(self.base_path+"classe/classe_"+classe+"_"+comp+".csv", 
                                     index=False)
                print('---')
            print("[INFO]    Processamento de dados por classe concluído.")
        print('------------------------------------------------------')
        
    def filter_data(self, grupos=None):
        if grupos is None:
            grupos = self.df[self.feat_grupo].unique()

        grupo_df = {}

        for grupo in grupos:
            df_grupo = self.df[self.df[self.feat_grupo]==grupo]
            df_grupo = df_grupo.drop(self.feat_grupo, axis=1)
            grupo_df[grupo] = df_grupo

            print(f"[INFO] Grupo {grupo}: {df_grupo.shape[0]} provas")
            df_grupo.to_csv("../Data/Processed/ENEM_"+str(self.ano)+"_"+self.competencia+"_"+self.feat_grupo+"_"+str(grupo)+".csv",
                            index = False)

        return grupo_df

    def bin_data(self, nota_min=300, nota_max=750, step=20):
        bins = np.arange(nota_min,nota_max,step)

        self.df['RangeCH'] = pd.cut(self.df['NU_NOTA_'+self.competencia], bins, right=False)

        self.bin_df = self.df[self.df['NU_NOTA_'+self.competencia]!=0].groupby('RangeCH').count()[['TP_COR_RACA']]
        self.bin_df = self.bin_df.rename(columns={'TP_COR_RACA': 'Total'})
        self.bin_df = self.bin_df.join(self.df[self.df['NU_NOTA_'+self.competencia]!=0].groupby('RangeCH').sum()[self.questoes_list])

        for q in self.questoes_list:
            self.bin_df[q] = self.bin_df[q]/self.bin_df['Total']

        return self.bin_df

    def plot_cci(self, questoes=None, legenda=False, subplots=False, figsize=(8, 6)):
        if questoes is None:
            questoes = self.questoes_list

        ax = self.bin_df[questoes].plot(title='Proporção de acertos por proeficiência', legend=legenda, subplots=subplots,
                                    figsize=figsize)
        ax.set_xlabel("Proeficiência")
        ax.set_ylabel("Proporção de acertos")
        
        plt.show()

        return ax

    