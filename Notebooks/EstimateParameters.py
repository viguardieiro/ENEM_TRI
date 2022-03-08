import pyomo.environ as pyo
import math
import numpy as np
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

def icc(theta, a, b, c):
    return c+(1-c)/(1+math.exp(-a*(theta-b)))

def icc_model(theta, model):
    return model.c+(1-model.c)/(1+pyo.exp(-model.a*(theta-model.b)))

def fit_icc(notas, prop):
    model_it1 = pyo.ConcreteModel()

    # Model parameters
    model_it1.a = pyo.Var(initialize=0.01)
    model_it1.b = pyo.Var(initialize=0)
    model_it1.c = pyo.Var(within=pyo.NonNegativeReals, bounds=(0,1), initialize=0.2)

    # Minimize squared error
    def cost_rule(model):
        return sum([(icc_model(notas[i], model)-prop[i])**2 for i in range(len(notas))])
    model_it1.cost = pyo.Objective(rule=cost_rule, sense=pyo.minimize)

    opt = pyo.SolverFactory('ipopt')
    opt.solve(model_it1) 

    return model_it1.a(), model_it1.b(), model_it1.c(), model_it1.cost()

def fit_icc_itens(bin_comp, nota_min=350, nota_max=750, step=15):
    icc_par = pd.DataFrame()
    
    for group in bin_comp.keys():
        prop_group = bin_comp[group].copy()
        prop_group['Media'] = [i+step/2 for i in np.arange(nota_min, nota_max-step, step)]
        prop_group.dropna(how='any', inplace=True)
        prop_group.reset_index(drop=True, inplace=True)
        notas = prop_group['Media'].tolist()
        
        for item in prop_group.columns[1:-1]:
            prop = prop_group[item].tolist()
            a,b,c,error = fit_icc(notas, prop)
            
            icc_par.loc[item,'Dscrmn_'+str(group)] = a
            icc_par.loc[item,'Dffclt_'+str(group)] = b
            icc_par.loc[item,'Gussng_'+str(group)] = c
            #icc_par.loc[item,'Error_'+group] = error
            
    return icc_par
    
def estimate_all_tests_parameters(ano, item_ing, item_esp):

    icc_par = {'Gender': {},
              'Race': {},
              'Income': {}}

    for feat in ['Gender','Race','Income']:
        for test in ['CH', 'CN', 'MT']:
            cn_comp = GroupComparator(comp=test, ano=ano, 
                                      gp_feat = feat_map[feat]['gp_feat'], 
                                      gp_name = feat_map[feat]['gp_name'], 
                                      gp_map = feat_map[feat]['gp_map'],
                                      gps = feat_map[feat]['gps']
                                     )
            df_gp = cn_comp.get_df_gp()
            nota_mean = df_gp['Geral']['NU_NOTA_'+test].mean()
            nota_std = df_gp['Geral']['NU_NOTA_'+test].std()

            for group in df_gp.keys():
                cn_comp.df_gp[group]['NU_NOTA_'+test] = (df_gp[group]['NU_NOTA_'+test]-nota_mean)/nota_std

            bin_cn = cn_comp.bin_scores(nota_min=-2.5, nota_max=4.5, step=0.5)
            icc_par_cn = fit_icc_itens(bin_cn, nota_min=-2.5, nota_max=4.5, step=0.5)

            icc_par[feat][test] = icc_par_cn


        test = 'LC'
        # Languages
        ch_comp = GroupComparator(comp='LC', ano=ano, 
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

        nota_mean = df_gp_pt['Geral']['NU_NOTA_'+test].mean()
        nota_std = df_gp_pt['Geral']['NU_NOTA_'+test].std()

        # English
        lc_comp_ing = GroupComparator(comp='LC', ano=ano,
                                      gp_feat = feat_map[feat]['gp_feat'], 
                                      gp_name = feat_map[feat]['gp_name'], 
                                      gp_map = feat_map[feat]['gp_map'],
                                      gps = feat_map[feat]['gps'])
        lc_comp_ing.df_gp = df_gp_ing
        for group in df_gp_ing.keys():
            lc_comp_ing.df_gp[group]['NU_NOTA_'+test] = (df_gp_ing[group]['NU_NOTA_'+test]-nota_mean)/nota_std

        bin_cn = lc_comp_ing.bin_scores(nota_min=-2.5, nota_max=4.5, step=0.5)
        icc_par_cn = fit_icc_itens(bin_cn, nota_min=-2.5, nota_max=4.5, step=0.5)

        icc_par[feat]['EN'] = icc_par_cn

        # Spanish
        lc_comp_esp = GroupComparator(comp='LC', ano=ano,
                                      gp_feat = feat_map[feat]['gp_feat'], 
                                      gp_name = feat_map[feat]['gp_name'], 
                                      gp_map = feat_map[feat]['gp_map'],
                                      gps = feat_map[feat]['gps'])
        lc_comp_esp.df_gp = df_gp_esp
        for group in df_gp_esp.keys():
            lc_comp_esp.df_gp[group]['NU_NOTA_'+test] = (df_gp_esp[group]['NU_NOTA_'+test]-nota_mean)/nota_std

        bin_cn = lc_comp_esp.bin_scores(nota_min=-2.5, nota_max=4.5, step=0.5)
        icc_par_cn = fit_icc_itens(bin_cn, nota_min=-2.5, nota_max=4.5, step=0.5)

        icc_par[feat]['SP'] = icc_par_cn

        # Portguese
        lc_comp_port = GroupComparator(comp='LC', ano=ano,
                                      gp_feat = feat_map[feat]['gp_feat'], 
                                      gp_name = feat_map[feat]['gp_name'], 
                                      gp_map = feat_map[feat]['gp_map'],
                                      gps = feat_map[feat]['gps'])
        lc_comp_port.df_gp = df_gp_pt
        for group in df_gp_pt.keys():
            lc_comp_port.df_gp[group]['NU_NOTA_'+test] = (df_gp_pt[group]['NU_NOTA_'+test]-nota_mean)/nota_std

        bin_cn = lc_comp_port.bin_scores(nota_min=-2.5, nota_max=4.5, step=0.5)
        icc_par_cn = fit_icc_itens(bin_cn, nota_min=-2.5, nota_max=4.5, step=0.5)

        icc_par[feat]['PT'] = icc_par_cn
        
    return icc_par