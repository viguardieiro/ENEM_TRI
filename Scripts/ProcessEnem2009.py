import pandas as pd
from pathlib import Path

features = ['TP_DEPENDENCIA_ADM_ESC', 'TP_ST_CONCLUSAO',
            'TP_PRESENCA_CN', 'TP_PRESENCA_CH', 'TP_PRESENCA_LC', 'TP_PRESENCA_MT',
            'NU_NOTA_CN',     'NU_NOTA_CH',     'NU_NOTA_LC',     'NU_NOTA_MT', 
            'CO_PROVA_CN', 'CO_PROVA_CH', 'CO_PROVA_LC', 'CO_PROVA_MT', 
            'TX_RESPOSTAS_CN', 'TX_RESPOSTAS_CH', 'TX_RESPOSTAS_LC', 'TX_RESPOSTAS_MT',
            'TX_GABARITO_CN', 'TX_GABARITO_CH', 'TX_GABARITO_LC', 'TX_GABARITO_MT']


if Path("../Data/Processed/ENEM_2009_All.csv").exists():
    enem_df = pd.read_csv("../Data/Processed/ENEM_2009_All.csv")

else:
    chunksize = 10 ** 5
    enem_df = None

    with pd.read_csv("../Data/Original/MICRODADOS_ENEM_2009.csv",
                        sep=';', encoding='latin-1', chunksize=chunksize, 
                        error_bad_lines=False, index_col=False, dtype='unicode') as reader:
        for chunk in reader:
            df = chunk[features]

            df = df[df['TP_ST_CONCLUSAO']=='2'] # Concluientes em 2009
            df = df[df['TP_DEPENDENCIA_ADM_ESC']!='4'] # Escolas públicas
            df.drop(['TP_ST_CONCLUSAO', 'TP_DEPENDENCIA_ADM_ESC'], axis=1, inplace=True)

            if enem_df is None:
                enem_df = df
            else:
                enem_df = enem_df.append(df)

    enem_df.to_csv("../Data/Processed/ENEM_2009_All.csv", index = False)
    print(f"[INFO] {enem_df.shape[0]} participantes no total.")
    print('---------------------------')


# Para cada competência
competencias = ['CN', 'CH', 'LC', 'MT']
cod_comp = {'CN': '49', 'CH': '53', 'LC': '57', 'MT': '61'}

for comp in competencias:
    # Filtra alunos presentes na prova
    df_comp = enem_df[enem_df['TP_PRESENCA_'+comp]=='1']
    # Filtra os alunos que fizeram o mesmo caderno de prova
    df_comp = df_comp[df_comp['CO_PROVA_'+comp]==cod_comp[comp]]

    feat_comp = ['NU_NOTA_'+comp, 'TX_RESPOSTAS_'+comp, 'TX_GABARITO_'+comp]
    df_comp = df_comp[feat_comp]
    
    # Transforma a coluna de notas em númerico
    df_comp['NU_NOTA_'+comp] = pd.to_numeric(df_comp['NU_NOTA_'+comp])

    # Gera colunas indicando se o candidato acertou ou não a questão
    for i in range(45):
        s = "Questao"+str(i+1)
        df_comp[s] = df_comp['TX_RESPOSTAS_'+comp].str[i]==df_comp['TX_GABARITO_'+comp].str[i]
        df_comp[s] = df_comp[s].astype(int)
    df_comp.drop(['TX_RESPOSTAS_'+comp, 'TX_GABARITO_'+comp], axis=1, inplace=True)

    df_comp.to_csv("../Data/Processed/ENEM_2009_"+comp+"_caderno_"+cod_comp[comp]+".csv", index = False)

    print(f"[INFO] {df_comp.shape[0]} provas de {comp}.")
    print('[INFO] Nota mínima: ', df_comp['NU_NOTA_'+comp].min())
    print('[INFO] Nota mínima (diferente de zero): ', df_comp[df_comp['NU_NOTA_'+comp]!=0]['NU_NOTA_'+comp].min())
    print('[INFO] Nota máxima: ', df_comp['NU_NOTA_'+comp].max())
    print('---------------------------')