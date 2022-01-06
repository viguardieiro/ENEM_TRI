import pandas as pd
from pathlib import Path

features = ['TP_DEPENDENCIA_ADM_ESC', 'TP_ST_CONCLUSAO', 'TP_ENSINO', 'NU_INSCRICAO',
            'CO_MUNICIPIO_RESIDENCIA', 'SG_UF_ESC', 'Q1', 'Q3', 'Q21',
            'TP_PRESENCA_CN',  'TP_PRESENCA_CH',  'TP_PRESENCA_LC',  'TP_PRESENCA_MT',
            'NU_NOTA_CN',      'NU_NOTA_CH',      'NU_NOTA_LC',      'NU_NOTA_MT', 
            'CO_PROVA_CN',     'CO_PROVA_CH',     'CO_PROVA_LC',     'CO_PROVA_MT', 
            'TX_RESPOSTAS_CN', 'TX_RESPOSTAS_CH', 'TX_RESPOSTAS_LC', 'TX_RESPOSTAS_MT',
            'TX_GABARITO_CN',  'TX_GABARITO_CH',  'TX_GABARITO_LC',  'TX_GABARITO_MT']


if Path("../Data/Processed/ENEM2009/All.csv").exists():
    enem_df = pd.read_csv("../Data/Processed/ENEM2009/All.csv")

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
    
    df = enem_df[enem_df['TP_ST_CONCLUSAO']=='2'] # Concluintes em 2009
    df.drop(['TP_ST_CONCLUSAO'], axis=1, inplace=True)
    df.to_csv("../Data/Processed/ENEM2009/Concluintes.csv", index = False)
    print(f"[INFO] {df.shape[0]} participantes concluintes no total.")

    df = enem_df[(enem_df['TP_ST_CONCLUSAO']=='2') & (enem_df['TP_ENSINO']=='1')] # Concluintes regulares em 2009
    df.drop(['TP_ST_CONCLUSAO'], axis=1, inplace=True)
    df.to_csv("../Data/Processed/ENEM2009/Concluintes_regulares.csv", index = False)
    print(f"[INFO] {df.shape[0]} participantes concluintes regulares.")

    df = enem_df[(enem_df['TP_ST_CONCLUSAO']!='2') | (enem_df['TP_ENSINO']!='1')] # Não concluintes em 2009
    df.drop(['TP_ST_CONCLUSAO'], axis=1, inplace=True)
    df.to_csv("../Data/Processed/ENEM2009/NaoConcluintes.csv", index = False)
    print(f"[INFO] {df.shape[0]} participantes não concluintes no total.")
    print('---------------------------')

if Path("../Data/Processed/ENEM2009/All_CH.csv").exists():
    print("[INFO] Tabelas de acerto por questão já existem.")
else:
    print("[INFO] Tabelas de acerto por questão não encontradas.")
    print("[INFO] Gerando tabelas de acerto por questão...")
    questoes_pd = pd.read_csv("../Data/Original/microdados_enem_2009/Dados/ITENS_PROVA_2009.csv",
                            sep=';')

    print("[INFO] Gerando tabelas de acerto por competência...")
    # Para cada competência
    competencias = ['LC', 'CN', 'CH', 'MT']
    #cod_comp = {'CN': '49', 'CH': '53', 'LC': '57', 'MT': '61'}

    for comp in competencias:
        print(f"[INFO] Processando competência {comp}...")
        # Filtra alunos presentes na prova
        df_comp = enem_df[enem_df['TP_PRESENCA_'+comp]==1].copy()
        df_comp = df_comp[['NU_INSCRICAO','CO_PROVA_'+comp, 'TX_RESPOSTAS_'+comp, 'TX_GABARITO_'+comp, 'NU_NOTA_'+comp,
                          'TP_ST_CONCLUSAO', 'TP_ENSINO']]

        cadernos_comp = df_comp[['CO_PROVA_'+comp, 'TX_RESPOSTAS_'+comp]].groupby('CO_PROVA_'+comp).count()
        cadernos_comp = list(cadernos_comp[cadernos_comp['TX_RESPOSTAS_'+comp]>10000].index)

        #if comp=='LC':
        #    cadernos_comp = questoes_pd[questoes_pd['SG_AREA']=='LCT']['CO_PROVA'].unique()
        #else:
        #    cadernos_comp = questoes_pd[questoes_pd['SG_AREA']==comp]['CO_PROVA'].unique()

        df_comp = df_comp[df_comp['CO_PROVA_'+comp].isin(cadernos_comp)]
        # Gera colunas indicando se o candidato acertou ou não a questão
        for i_cad in range(len(cadernos_comp)):
            caderno = int(cadernos_comp[i_cad])
            print(f"[INFO]    Processando caderno {caderno} ({i_cad+1}/{len(cadernos_comp)})...", end='')
            itens_list = questoes_pd[questoes_pd['CO_PROVA']==caderno]['CO_ITEM'].copy().reset_index(drop=True).sort_values()
            for i in range(len(itens_list)):
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

        df = df_comp[(df_comp['TP_ST_CONCLUSAO']==2) & (df_comp['TP_ENSINO']==1)].copy()
        df.drop(['TP_ST_CONCLUSAO', 'TP_ENSINO'], axis=1, inplace=True)
        df.to_csv("../Data/Processed/ENEM2009/Concluintes_regulares_"+comp+".csv", index = False)

        df_comp.drop(['TP_ST_CONCLUSAO', 'TP_ENSINO'], axis=1, inplace=True)
        df_comp.to_csv("../Data/Processed/ENEM2009/All_"+comp+".csv", index = False)

        print(f"[INFO] Processamento da competência {comp} concluído.")

        print(f"[INFO] {df_comp.shape[0]} provas de {comp}.")
        print('[INFO] Nota mínima: ', df_comp['NU_NOTA_'+comp].min())
        print('[INFO] Nota mínima (diferente de zero): ', df_comp[df_comp['NU_NOTA_'+comp]!=0]['NU_NOTA_'+comp].min())
        print('[INFO] Nota máxima: ', df_comp['NU_NOTA_'+comp].max())
        print('---------------------------')
        
if Path("../Data/Processed/ENEM2009/All_grupos.csv").exists():
    print("[INFO] Tabela de grupos já existe.")
    df_grupo = pd.read_csv("../Data/Processed/ENEM2009/All_grupos.csv")
else:
    print("[INFO] Tabela de grupos não encontrada.")
    print("[INFO] Gerando tabela de grupos...")
    
    df_grupo = enem_df[['NU_INSCRICAO','CO_MUNICIPIO_RESIDENCIA', 'SG_UF_ESC', 'Q1','Q3', 'Q21',
                       'TP_DEPENDENCIA_ADM_ESC', 'TP_ENSINO']].copy()
    df_grupo.rename(columns={"Q1": "GENERO", "Q3": "RAÇA", 'Q21': 'RENDA'}, inplace=True)
    df_grupo['REGIAO'] = df_grupo['CO_MUNICIPIO_RESIDENCIA'].apply(str).str[0]
    df_grupo['REGIAO'] = df_grupo['REGIAO'].replace('n', None)
    df_grupo['REGIAO'] = pd.to_numeric(df_grupo['REGIAO'])
    
    df_grupo.to_csv("../Data/Processed/ENEM2009/All_grupos.csv", index = False)
    
    
print("[INFO] Verificando processamento de dados por região...")
if Path("../Data/Processed/ENEM2009/CR_regiaoN_LC.csv").exists():
    print("[INFO] Dados por região já foram processados.")
else:
    print("[INFO] Dados por região não foram encontrados.")
    print("[INFO] Processando dados por região...")

    regiao_map = {1: 'N', 2: 'NE', 3:'SE', 4:'S', 5:'CO'}
    regioes = df_grupo['REGIAO'].unique()
    for reg in regioes:
        nu_regiao = df_grupo[df_grupo['REGIAO']==reg]['NU_INSCRICAO'].tolist()
        print(f"[INFO] Processando região {regiao_map[reg]}...")
        for comp in ['LC', 'CN', 'CH', 'MT']:
            concluintes_df = pd.read_csv("../Data/Processed/ENEM2009/Concluintes_regulares_"+comp+".csv")
            df_regiao = concluintes_df[concluintes_df['NU_INSCRICAO'].isin(nu_regiao)]
            print(f"[INFO]     Comeptência {comp}: {df_regiao.shape[0]} concluintes regulares.")
            df_regiao.to_csv("../Data/Processed/ENEM2009/CR_regiao"+regiao_map[reg]+"_"+comp+".csv", index=False)
        print('---------------------------')
    print("[INFO] Processamento de dados por região concluído.")