from ProcessEnemDataClass import ProcessEnemData

egb = ProcessEnemData(ano=2019, competencia='CH', questoes_anuladas=['45'], caderno='Azul')
enem_df = egb.get_data()
