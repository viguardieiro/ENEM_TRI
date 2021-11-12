from ProcessEnemDataClass import ProcessEnemData

penem = ProcessEnemData(ano=2019, competencia='CH', questoes_anuladas=['45'], caderno='Azul', feat_grupo='TP_COR_RACA')
enem_df = penem.get_data()

grupo_df = penem.filter_data()