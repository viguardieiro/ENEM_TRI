from ProcessEnemDataClass import ProcessEnemData

penem = ProcessEnemData(ano=2019)
enem_df = penem.get_data()

concluinte_df = enem_df[(enem_df['TP_ST_CONCLUSAO']==2) & (enem_df['TP_ENSINO']==1)]

competencias = ['CN', 'CH', 'LC', 'MT']
itens_anulados = {'CN': [],
                     'CH': [],
                     'LC': [],
                     'MT': []}

for comp in competencias:
    penem.process_competence(comp, itens_anulados[comp], enem_df=concluinte_df)

#grupo_df = penem.filter_data()