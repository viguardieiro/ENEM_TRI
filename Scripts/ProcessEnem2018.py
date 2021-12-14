import pandas as pd

from ProcessEnemDataClass import ProcessEnemData

penem = ProcessEnemData(ano=2018)

# Processa dados de todos
print("[INFO] Processando dados de todos os alunos...")
enem_df = penem.get_data()
print("[INFO] Processamento dos dados de todos os alunos concluído.")

# Processa dados dos concluintes
print("[INFO] Processando dados dos alunos concluintes de 2018...")
concluinte_df = pd.read_csv("../Data/Processed/ENEM2018/Concluintes.csv")

competencias = ['CN', 'CH', 'LC', 'MT']
itens_anulados = {'CN': [],
                     'CH': [],
                     'LC': [],
                     'MT': []}

for comp in competencias:
    penem.process_competence(comp, itens_anulados[comp], enem_df=concluinte_df)
print("[INFO] Processamento dos dados dos alunos concluintes de 2018 concluído.")
print("-------------------------------------------------")

# Processa dados dos concluintes regulares
concluinte_reg_df = pd.read_csv("../Data/Processed/ENEM2018/Concluintes_regular.csv")

competencias = ['CN', 'CH', 'LC', 'MT']
itens_anulados = {'CN': [],
                     'CH': [],
                     'LC': [],
                     'MT': []}

for comp in competencias:
    penem.process_competence(comp, itens_anulados[comp], enem_df=concluinte_reg_df, file_name="Concluintes_regular")
    
#grupo_df = penem.filter_data()