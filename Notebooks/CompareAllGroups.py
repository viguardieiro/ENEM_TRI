import pandas as pd
from CompareGroupsFunctions import *

feat_map = {'Gender': {'gp_feat':'TP_SEXO',
                       'gp_map':{'M':'Masculino', 'F': 'Feminino'},
                       'gp_name':'sexo',
                       'gps':None
                      },
            'Race':   {'gp_feat':'TP_COR_RACA',
                       'gp_name':'raca',
                       'gp_map':{0:'ND', 1: 'Branca', 2: 'Preta', 3:'Parda', 4:'Amarela', 5:'Indigena'},
                       'gps':[1, 2, 3]
                      },
            'Income': {'gp_feat':'CLASSE', 
                       'gp_name':'classe', 
                       'gp_map':{'alta': '2+ MW',
                                  'média': '1/2-2 MW',
                                  'baixa': '0-1/2 MW'
                                  },
                       'gps':None
                      }
           }

def all_groups_std_df(comp, ano, item_ing=None, item_esp=None):
    if comp!='LC':
        auc_std_ch = pd.DataFrame()
        auc_fav_ch = pd.DataFrame()
        auc_ch_all = None

        for feat in ['Gender','Race','Income']:
            ch_comp = GroupComparator(comp=comp, ano=ano, 
                                          gp_feat = feat_map[feat]['gp_feat'], 
                                          gp_name = feat_map[feat]['gp_name'], 
                                          gp_map = feat_map[feat]['gp_map'],
                                          gps = feat_map[feat]['gps']
                                         )
            df_gp = ch_comp.get_df_gp()
            bin_ch = ch_comp.bin_scores(step=10)
            auc_ch = ch_comp.auc_groups()
            auc_std_ch[feat] = ch_comp.auc_std()    
            auc_fav_ch[feat] = ch_comp.favored_group()
            
            if auc_ch_all is None:
                auc_ch_all = auc_ch[auc_ch.columns[:-1]].copy()
            else:
                auc_ch_all = auc_ch_all.join(auc_ch[auc_ch.columns[:-1]])

        auc_std_ch = auc_std_ch.sort_index().reset_index(drop=True)
        auc_fav_ch = auc_fav_ch.sort_index().reset_index(drop=True)
        
        return auc_std_ch, auc_fav_ch, auc_ch_all
    else:
        auc_std_pt = pd.DataFrame()
        auc_std_in = pd.DataFrame()
        auc_std_es = pd.DataFrame()
        
        auc_fav_pt = pd.DataFrame()
        auc_fav_in = pd.DataFrame()
        auc_fav_es = pd.DataFrame()
        
        auc_pt_all = None
        auc_in_all = None
        auc_es_all = None
        
        for feat in ['Gender','Race','Income']:
            ch_comp = GroupComparator(comp=comp, ano=ano, 
                                          gp_feat = feat_map[feat]['gp_feat'], 
                                          gp_name = feat_map[feat]['gp_name'], 
                                          gp_map = feat_map[feat]['gp_map'],
                                          gps = feat_map[feat]['gps']
                                         )
            df_gp = ch_comp.get_df_gp()
            bin_ch = ch_comp.bin_scores
            
            df_gp_ing = {}
            df_gp_esp = {}
            df_gp_pt = {}

            for g in df_gp.keys():
                df_gp_ing[g] = df_gp[g][df_gp[g]['TP_LINGUA']==0][['NU_INSCRICAO','NU_NOTA_LC']].copy()
                df_gp_esp[g] = df_gp[g][df_gp[g]['TP_LINGUA']==1][['NU_INSCRICAO','NU_NOTA_LC']].copy()
                df_gp_pt[g] = df_gp[g][['NU_INSCRICAO','NU_NOTA_LC']].copy()

                for col in df_gp[list(df_gp.keys())[0]].columns:
                    if col in item_ing:
                        df_gp_ing[g][col] = df_gp[g][df_gp[g]['TP_LINGUA']==0][col]
                    elif col in item_esp:
                        df_gp_esp[g][col] = df_gp[g][df_gp[g]['TP_LINGUA']==1][col]
                    elif col!='NU_INSCRICAO' and col!='NU_NOTA_LC' and col!='TP_LINGUA':
                        df_gp_pt[g][col] = df_gp[g][col]

            # English
            lc_comp_ing = GroupComparator(comp=comp, ano=ano,
                                          gp_feat = feat_map[feat]['gp_feat'], 
                                          gp_name = feat_map[feat]['gp_name'], 
                                          gp_map = feat_map[feat]['gp_map'],
                                          gps = feat_map[feat]['gps'])
            lc_comp_ing.df_gp = df_gp_ing
            bin_ch = lc_comp_ing.bin_scores(step=10)
            auc_ch = lc_comp_ing.auc_groups()
            auc_std_in[feat] = lc_comp_ing.auc_std()  
            auc_fav_in[feat] = lc_comp_ing.favored_group()
            
            if auc_in_all is None:
                auc_in_all = auc_ch[auc_ch.columns[:-1]].copy()
            else:
                auc_in_all = auc_in_all.join(auc_ch[auc_ch.columns[:-1]])
            
            # Spanish
            lc_comp_esp = GroupComparator(comp=comp, ano=ano,
                                          gp_feat = feat_map[feat]['gp_feat'], 
                                          gp_name = feat_map[feat]['gp_name'], 
                                          gp_map = feat_map[feat]['gp_map'],
                                          gps = feat_map[feat]['gps'])
            lc_comp_esp.df_gp = df_gp_esp
            bin_ch = lc_comp_esp.bin_scores(step=10)
            auc_ch = lc_comp_esp.auc_groups()
            auc_std_es[feat] = lc_comp_esp.auc_std()  
            auc_fav_es[feat] = lc_comp_esp.favored_group()
            
            if auc_es_all is None:
                auc_es_all = auc_ch[auc_ch.columns[:-1]].copy()
            else:
                auc_es_all = auc_es_all.join(auc_ch[auc_ch.columns[:-1]])
            
            # Portuguese
            lc_comp_port = GroupComparator(comp=comp, ano=ano,
                                          gp_feat = feat_map[feat]['gp_feat'], 
                                          gp_name = feat_map[feat]['gp_name'], 
                                          gp_map = feat_map[feat]['gp_map'],
                                          gps = feat_map[feat]['gps'])
            lc_comp_port.df_gp = df_gp_pt
            bin_ch = lc_comp_port.bin_scores(step=10)
            auc_ch = lc_comp_port.auc_groups()
            auc_std_pt[feat] = lc_comp_port.auc_std()  
            auc_fav_pt[feat] = lc_comp_port.favored_group()
            
            if auc_pt_all is None:
                auc_pt_all = auc_ch[auc_ch.columns[:-1]].copy()
            else:
                auc_pt_all = auc_pt_all.join(auc_ch[auc_ch.columns[:-1]])
            
        auc_std_pt = auc_std_pt.sort_index().reset_index(drop=True)
        auc_std_in = auc_std_in.sort_index().reset_index(drop=True)
        auc_std_es = auc_std_es.sort_index().reset_index(drop=True)
            
        auc_fav_pt = auc_fav_pt.sort_index().reset_index(drop=True)
        auc_fav_in = auc_fav_in.sort_index().reset_index(drop=True)
        auc_fav_es = auc_fav_es.sort_index().reset_index(drop=True)
            
        return auc_std_pt, auc_std_in, auc_std_es, auc_fav_pt, auc_fav_in, auc_fav_es, auc_pt_all, auc_in_all, auc_es_all