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

def icc_model(theta, model):
    return model.c+(1-model.c)/(1+pyo.exp(-model.a*(theta-model.b)))

def fit_icc(scores, answers):
    model_it = pyo.ConcreteModel()
    N = len(scores)

    # Model parameters
    model_it.a = pyo.Var(initialize=0.01)
    model_it.b = pyo.Var(initialize=0)
    model_it.c = pyo.Var(within=pyo.NonNegativeReals, bounds=(0,1), initialize=0.2)
    
    # Minimize log loss
    def cost_rule(model):
        
        probs = [icc_model(scores[i], model) for i in range(N)]
        return (-1)*sum([answers[i]*pyo.log(probs[i])+(1-answers[i])*pyo.log(1-probs[i]) for i in range(N)])
    
    model_it.cost = pyo.Objective(rule=cost_rule, sense=pyo.minimize)
    
    opt = pyo.SolverFactory('ipopt')
    opt.solve(model_it) 

    return model_it.a(), model_it.b(), model_it.c(), model_it.cost()

def fit_icc_itens(cn_comp, test):
    icc_par = pd.DataFrame()
    
    for group in cn_comp.keys():
        print(f"Grupo: {group}")
        scores = cn_comp[group]['NU_NOTA_'+test].tolist()
        
        for item in cn_comp[group].columns[2:-1]:
            print(f"  Item: {item}")  
            answers = cn_comp[group][item].tolist()
            try:
                a,b,c,error = fit_icc(scores, answers)

                icc_par.loc[item,'Dscrmn_'+str(group)] = a
                icc_par.loc[item,'Dffclt_'+str(group)] = b
                icc_par.loc[item,'Gussng_'+str(group)] = c
                #icc_par.loc[item,'Error_'+group] = error
            except ValueError:
                print('ValueError')
        
    return icc_par
    
def estimate_all_tests_parameters(ano, item_ing=None, item_esp=None):

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

            icc_par_cn = fit_icc_itens(cn_comp.df_gp, test)

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

        icc_par_cn = fit_icc_itens(lc_comp_ing.df_gp, test)

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

        icc_par_cn = fit_icc_itens(lc_comp_esp.df_gp, test)

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

        icc_par_cn = fit_icc_itens(lc_comp_port.df_gp, test)

        icc_par[feat]['PT'] = icc_par_cn
        
        with open('ICC_par_2019.pickle', 'wb') as handle:
            pickle.dump(icc_par, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    return icc_par