from ProcessEnemDataClass import ProcessEnemData
#import pandas as pd

penem = ProcessEnemData(ano=2019)
enem_df = penem.get_data()

competencias = ['CN', 'CH', 'LC', 'MT']
itens_anulados = {'CN': ["45168"],
                     'CH': [],
                     'LC': [],
                     'MT': []}

for comp in competencias:
    penem.process_competence(comp, itens_anulados[comp], all_p=True, concluintes=True)
    
df_grupo = penem.get_group_features()

#penem.process_region_competence()

#penem.process_group_competence(gp_feat='REGIAO', gp_name='regiao', 
#                               gp_map={1: 'N', 2: 'NE', 3:'SE', 4:'S', 5:'CO'})

#penem.process_group_competence(gp_feat='TP_COR_RACA', gp_name='raca', 
#                               gp_map={0:'ND', 1: 'Branca', 2: 'Preta', 3:'Parda', 4:'Amarela', 5:'Indigena'})

#penem.process_group_competence(gp_feat='TP_SEXO', gp_name='sexo', 
#                               gp_map={'M':'Masculino', 'F': 'Feminino'})

#gp_map_renda = {}
#for let in 'ABCDEFGHIJKLMNOPQ':
#    gp_map_renda[let] = let.lower()
#penem.process_group_competence(gp_feat='RENDA', gp_name='renda', 
#                               gp_map=gp_map_renda)

#penem.process_classe_renda()
