import pandas as pd
from pathlib import Path

features = ['TP_DEPENDENCIA_ADM_ESC', 'TP_ST_CONCLUSAO', 'TP_ENSINO',
            'TP_PRESENCA_CN',  'TP_PRESENCA_CH',  'TP_PRESENCA_LC',  'TP_PRESENCA_MT',
            'NU_NOTA_CN',      'NU_NOTA_CH',      'NU_NOTA_LC',      'NU_NOTA_MT', 
            'CO_PROVA_CN',     'CO_PROVA_CH',     'CO_PROVA_LC',     'CO_PROVA_MT', 
            'TX_RESPOSTAS_CN', 'TX_RESPOSTAS_CH', 'TX_RESPOSTAS_LC', 'TX_RESPOSTAS_MT',
            'TX_GABARITO_CN',  'TX_GABARITO_CH',  'TX_GABARITO_LC',  'TX_GABARITO_MT']


if Path("../Data/Processed/ENEM2009/Concluintes.csv").exists():
    enem_df = pd.read_csv("../Data/Processed/ENEM2009/Concluintes.csv")

else:
    chunksize = 10 ** 5
    enem_df = None

    with pd.read_csv("../Data/Original/microdados_enem_2009/Dados/MICRODADOS_ENEM_2009.csv",
                        sep=';', encoding='latin-1', chunksize=chunksize, 
                        error_bad_lines=False, index_col=False, dtype='unicode') as reader:
        for chunk in reader:
            df = chunk[features]

            if enem_df is None:
                enem_df = df
            else:
                enem_df = enem_df.append(df)

    enem_df.to_csv("../Data/Processed/ENEM2009/All.csv", index = False)
    print(f"[INFO] {enem_df.shape[0]} participantes no total.")

    df = enem_df[(enem_df['TP_ST_CONCLUSAO']=='2') & (enem_df['TP_ENSINO']=='1')] # Concluientes em 2009
    df.drop(['TP_ST_CONCLUSAO'], axis=1, inplace=True)
    df.to_csv("../Data/Processed/ENEM2009/Concluintes.csv", index = False)
    print(f"[INFO] {df.shape[0]} participantes concluintes no total.")

    df = enem_df[(enem_df['TP_ST_CONCLUSAO']!='2') | (enem_df['TP_ENSINO']!='1')] # Não concluientes em 2009
    df.drop(['TP_ST_CONCLUSAO'], axis=1, inplace=True)
    df.to_csv("../Data/Processed/ENEM2009/NaoConcluintes.csv", index = False)
    print(f"[INFO] {df.shape[0]} participantes não concluintes no total.")
    print('---------------------------')


questoes_pd = pd.read_csv("../Data/Original/microdados_enem_2009/Dados/ITENS_PROVA_2009.csv",
                        sep=';')

print("[INFO] Gerando tabelas de acerto por competência...")
# Para cada competência
competencias = ['CN', 'CH', 'LC', 'MT']
#cod_comp = {'CN': '49', 'CH': '53', 'LC': '57', 'MT': '61'}

for comp in competencias:
    print(f"[INFO] Processando competência {comp}...")
    # Filtra alunos presentes na prova
    df_comp = enem_df[enem_df['TP_PRESENCA_'+comp]==1].copy()
    df_comp = df_comp[['CO_PROVA_'+comp, 'TX_RESPOSTAS_'+comp, 'TX_GABARITO_'+comp, 'NU_NOTA_'+comp]]

    cadernos_comp = questoes_pd[questoes_pd['SG_AREA']==comp]['CO_PROVA'].unique()
    # Gera colunas indicando se o candidato acertou ou não a questão
    for i_cad in range(len(cadernos_comp)):
        caderno = int(cadernos_comp[i_cad])
        print(f"[INFO]    Processando caderno {caderno} ({i_cad+1}/{len(cadernos_comp)})...", end='')
        itens_list = questoes_pd[questoes_pd['CO_PROVA']==caderno]['CO_ITEM'].copy().reset_index(drop=True).sort_values()
        for i in range(45):
            item_id = str(itens_list.iloc[i])
            s = "Item "+item_id
            if s not in df_comp.columns:
                df_comp.loc[:,s] = 0

            df_comp.loc[df_comp['CO_PROVA_'+comp]==caderno,s] = df_comp[df_comp['CO_PROVA_'+comp]==caderno]['TX_RESPOSTAS_'+comp].str[i]==df_comp[df_comp['CO_PROVA_'+comp]==caderno]['TX_GABARITO_'+comp].str[i]
            df_comp.loc[df_comp['CO_PROVA_'+comp]==caderno,s] = df_comp[df_comp['CO_PROVA_'+comp]==caderno][s].astype(int)

        print(f"Concluído.")
    
    # Transforma a coluna de notas em númerico
    df_comp['NU_NOTA_'+comp] = pd.to_numeric(df_comp['NU_NOTA_'+comp])
    df_comp.drop(['CO_PROVA_'+comp,'TX_RESPOSTAS_'+comp, 'TX_GABARITO_'+comp], axis=1, inplace=True)

    df_comp.to_csv("../Data/Processed/ENEM2009/Concluintes_"+comp+".csv", index = False)

    print(f"[INFO] Processamento da competência {comp} concluído.")

    print(f"[INFO] {df_comp.shape[0]} provas de {comp}.")
    print('[INFO] Nota mínima: ', df_comp['NU_NOTA_'+comp].min())
    print('[INFO] Nota mínima (diferente de zero): ', df_comp[df_comp['NU_NOTA_'+comp]!=0]['NU_NOTA_'+comp].min())
    print('[INFO] Nota máxima: ', df_comp['NU_NOTA_'+comp].max())
    print('---------------------------')