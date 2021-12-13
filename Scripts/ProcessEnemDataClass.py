import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path

class ProcessEnemData():
    def __init__(self, ano=2019, competencia='CH', questoes_anuladas=[], 
                filt_conclusao=True, tipo_conclusao_em=2, # "Estou cursando e concluirei o Ensino Médio em 2019"
                filt_ensino=True, tipo_ensino=1, # Ensino Regular
                feat_grupo = None
                ):

        self.ano = ano
        self.competencia = competencia

        self.filt_conclusao = filt_conclusao
        self.tipo_conclusao_em = tipo_conclusao_em
        self.filt_ensino  =filt_ensino
        self.tipo_ensino = tipo_ensino

        self.questoes_anuladas = questoes_anuladas
        self.questoes_list = ['Questao'+str(i) for i in range(1,46) if i not in self.questoes_anuladas]

        self.features = ['TP_PRESENCA_'+competencia, 'NU_NOTA_'+competencia, 'TX_RESPOSTAS_'+competencia, 
                        'TX_GABARITO_'+competencia, 'CO_PROVA_'+competencia]

        if self.filt_conclusao:
            self.features.append('TP_ST_CONCLUSAO')
        if self.filt_ensino:
            self.features.append('TP_ENSINO')
        if feat_grupo is not None:
            self.features.append(feat_grupo)

        self.feat_grupo = feat_grupo

        self.file_path = "../Data/Processed/ENEM_"+str(self.ano)+"_"+self.competencia
        if feat_grupo is not None:
            self.file_path = self.file_path+"_"+feat_grupo

        self.file_path = self.file_path+".csv"

        self.df = None

    def get_data(self, chunksize = 10 ** 5):
        if Path(self.file_path).exists():
            self.df = pd.read_csv(self.file_path)

        else:
            enem_df = None

            with pd.read_csv("../Data/Original/MICRODADOS_ENEM_"+str(self.ano)+".csv",
                             sep=';', encoding='latin-1', chunksize=chunksize) as reader:
                for chunk in reader:
                    df = chunk[self.features]
                    df = df[df['TP_PRESENCA_'+self.competencia]==1]
                    df.drop(['TP_PRESENCA_'+self.competencia], axis=1, inplace=True)

                    if self.filt_conclusao:
                        df = df[df['TP_ST_CONCLUSAO']==self.tipo_conclusao_em]
                        df.drop(['TP_ST_CONCLUSAO'], axis=1, inplace=True)
                    if self.filt_ensino:
                        df = df[df['TP_ENSINO']==self.tipo_ensino]
                        df.drop(['TP_ENSINO'], axis=1, inplace=True)
                    
                    df.dropna(how='any', inplace=True)

                    if enem_df is None:
                        enem_df = df
                    else:
                        enem_df = enem_df.append(df)


            questoes_pd = pd.read_csv("../Data/Original/microdados_enem"+str(self.ano)+"/Dados/ITENS_PROVA_"+str(self.ano)+".csv",
                    sep=';')

            print("[INFO] Gerando tabela de acerto por competência...")
            print(f"[INFO] Processando cadernos de prova...")
            df_comp = enem_df[['CO_PROVA_'+self.competencia, 
                            'TX_RESPOSTAS_'+self.competencia, 
                            'TX_GABARITO_'+self.competencia, 
                            'NU_NOTA_'+self.competencia]]

            cadernos_comp = questoes_pd[questoes_pd['SG_AREA']==self.competencia]['CO_PROVA'].unique()
            # Gera colunas indicando se o candidato acertou ou não a questão
            for i_cad in range(len(cadernos_comp)):
                caderno = int(cadernos_comp[i_cad])
                print(f"[INFO]    Processando caderno {caderno} ({i_cad+1}/{len(cadernos_comp)})...")
                itens_list = questoes_pd[questoes_pd['CO_PROVA']==caderno]['CO_ITEM'].copy().reset_index(drop=True).sort_values()
                for i in range(45):
                    item_id = str(itens_list.iloc[i])
                    s = "Item "+item_id
                    if s not in df_comp.columns:
                        df_comp.loc[:,s] = 0

                    df_comp.loc[df_comp['CO_PROVA_'+self.competencia]==caderno,s] = df_comp[df_comp['CO_PROVA_'+self.competencia]==caderno]['TX_RESPOSTAS_'+self.competencia].str[i]==df_comp[df_comp['CO_PROVA_'+self.competencia]==caderno]['TX_GABARITO_'+self.competencia].str[i]
                    df_comp.loc[df_comp['CO_PROVA_'+self.competencia]==caderno,s] = df_comp[df_comp['CO_PROVA_'+self.competencia]==caderno][s].astype(int)

                print(f"[INFO]    Processamento do caderno {caderno} concluído.")
            
            # Transforma a coluna de notas em númerico
            df_comp['NU_NOTA_'+self.competencia] = pd.to_numeric(df_comp['NU_NOTA_'+self.competencia])
            df_comp.drop(['CO_PROVA_'+self.competencia,'TX_RESPOSTAS_'+self.competencia, 'TX_GABARITO_'+self.competencia],
                            axis=1, inplace=True)

            df_comp.to_csv("../Data/Processed/ENEM_2009_Concluintes_"+self.competencia+".csv", index = False)

            print(f"[INFO] Processamento da competência {self.competencia} concluído.")

            print(f"[INFO] {df_comp.shape[0]} provas de {self.competencia}.")
            self.df = df_comp

            # for i in range(45):
            #     s = "Questao"+str(i+1)
            #     if i+1 not in self.questoes_anuladas:
            #         enem_df[s] = enem_df['TX_RESPOSTAS_'+self.competencia].str[i]==enem_df['TX_GABARITO_'+self.competencia].str[i]
            #         enem_df[s] = enem_df[s].astype(int)

            # enem_df.drop(['TX_RESPOSTAS_'+self.competencia, 'TX_GABARITO_'+self.competencia],
            #             axis=1, inplace=True)

            # enem_df.to_csv(self.file_path, index = False)
            # enem_df[self.questoes_list].to_csv( "../Data/Processed/ENEM_"+str(self.ano)+"_"+self.competencia+"_only_questions.csv",
            #                                     index = False)

            # self.df = enem_df

        print('[INFO] Nota mínima: ', self.df['NU_NOTA_'+self.competencia].min())
        print('[INFO] Nota mínima (diferente de zero): ', self.df[self.df['NU_NOTA_'+self.competencia]!=0]['NU_NOTA_'+self.competencia].min())
        print('[INFO] Nota máxima: ', self.df['NU_NOTA_'+self.competencia].max())

        return self.df

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

    