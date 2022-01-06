from ProcessEnemDataClass import ProcessEnemData

penem = ProcessEnemData(ano=2019)
enem_df = penem.get_data()

competencias = ['CN', 'CH', 'LC', 'MT']
itens_anulados = {'CN': ["45168"],
                     'CH': [],
                     'LC': [],
                     'MT': []}

for comp in competencias:
    penem.process_competence(comp, itens_anulados[comp], enem_df=enem_df, 
                             all_p=True, concluintes=True)

#grupo_df = penem.filter_data()