import pandas as pd
from stac.stac.nonparametric_tests import friedman_test, finner_test

def run_tests(auc_in, verbose=True):
    auc_pvalues = pd.DataFrame()

    if verbose:
        print('Friedman test & Finner test')
        print()

    pvalue_gender, _, pivots_gender = friedman_test(auc_in['M'], auc_in['F'])[1:4]
    pvalue_race, _, pivots_race = friedman_test(auc_in[1], auc_in[2], auc_in[3])[1:4]
    pvalue_income, _, pivots_income = friedman_test(auc_in['alta'], auc_in['média'], auc_in['baixa'])[1:4]

    if verbose:
        print(f"[Friedman Test] Gender - pvalue: {pvalue_gender:.4f}")
        print(f"[Friedman Test] Race - pvalue: {pvalue_race:.4f}")
        print(f"[Friedman Test] Income - pvalue: {pvalue_income:.4f}")

    auc_pvalues = auc_pvalues.append({'Test': 'IN', 'Group': 'Gender', 'p-value': pvalue_gender}, ignore_index = True)
    auc_pvalues = auc_pvalues.append({'Test': 'IN', 'Group': 'Race', 'p-value': pvalue_race}, ignore_index = True)
    auc_pvalues = auc_pvalues.append({'Test': 'IN', 'Group': 'Income', 'p-value': pvalue_income}, ignore_index = True)

    pivots_gender_map = {'M': pivots_gender[0], 'F':  pivots_gender[1]}
    pivots_race_map = {'White': pivots_race[0], 'Black':  pivots_race[1], 'Pardo':  pivots_race[2]}
    pivots_income_map = {'High': pivots_income[0], 'Medium':  pivots_income[1], 'Low':  pivots_income[2]}

    f = finner_test(pivots_gender_map)
    if verbose:
        print(f"[Finner Test] Gender")
        print(f"   {f[0][0]}: {f[2][0]:.3f}")

    f = finner_test(pivots_race_map)
    if verbose:
        print(f"[Finner Test] Race")
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
        print(f"   {f[0][1]}: {f[2][1]:.3f}")
    f = finner_test({'White': pivots_race[0], 'Pardo':  pivots_race[2]})
    if verbose:
        print(f"   {f[0][0]}: {f[2][0]:.3f}")

    f = finner_test(pivots_income_map)
    if verbose:
        print(f"[Finner Test] Income")
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
        print(f"   {f[0][1]}: {f[2][1]:.3f}")
    f = finner_test({'High': pivots_income[0], 'Medium':  pivots_income[1]})
    if verbose:
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
        
    return auc_pvalues

def run_tests_par(icc_par, comp, feat='Race'):
    if feat=='Gender':
        print('Friedman test')
        pvalue_dsc_race, _, pivots_dsc = friedman_test(icc_par['Gender'][comp]['Dscrmn_M'], 
                                                       icc_par['Gender'][comp]['Dscrmn_F'])[1:4]
        pvalue_dff_race, _, pivots_dff = friedman_test(icc_par['Gender'][comp]['Dffclt_M'], 
                                                       icc_par['Gender'][comp]['Dffclt_F'])[1:4]
        pvalue_gus_race, _, pivots_gus = friedman_test(icc_par['Gender'][comp]['Gussng_M'], 
                                                       icc_par['Gender'][comp]['Gussng_F'])[1:4]

        pivots_dsc_gender = {'M': pivots_dsc[0], 'F':  pivots_dsc[1]}
        pivots_dff_gender = {'M': pivots_dff[0], 'F':  pivots_dff[1]}
        pivots_gus_gender = {'M': pivots_gus[0], 'F':  pivots_gus[1]}

        print(f"  p-value discrimination (a): {pvalue_dsc_race:.4f}")
        print(f"  p-value difficulty (b): {pvalue_dff_race:.4f}")
        print(f"  p-value guessing (c): {pvalue_gus_race:.4f}")
        print()
        
        print('Finner test')
        f = finner_test(pivots_dsc_gender)
        print(f"discrimination (a)")
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
        f = finner_test(pivots_dff_gender)
        print(f"difficulty (b)")
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
        f = finner_test(pivots_gus_gender)
        print(f"guessing (c)")
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
    
    if feat=='Race':
        print('Friedman test')
        pvalue_dsc_race, _, pivots_dsc = friedman_test(icc_par['Race'][comp]['Dscrmn_1'], icc_par['Race'][comp]['Dscrmn_2'], 
                                        icc_par['Race'][comp]['Dscrmn_3'])[1:4]
        pvalue_dff_race, _, pivots_dff = friedman_test(icc_par['Race'][comp]['Dffclt_1'], icc_par['Race'][comp]['Dffclt_2'], 
                                        icc_par['Race'][comp]['Dffclt_3'])[1:4]
        pvalue_gus_race, _, pivots_gus = friedman_test(icc_par['Race'][comp]['Gussng_1'],icc_par['Race'][comp]['Gussng_2'], 
                                                  icc_par['Race'][comp]['Gussng_3'])[1:4]
        
        pivots_dsc_race = {'White': pivots_dsc[0], 'Black':  pivots_dsc[1], 'Pardo':  pivots_dsc[2]}
        pivots_dff_race = {'White': pivots_dff[0], 'Black':  pivots_dff[1], 'Pardo':  pivots_dff[2]}
        pivots_gus_race = {'White': pivots_gus[0], 'Black':  pivots_gus[1], 'Pardo':  pivots_gus[2]}
        
        print(f"  p-value discrimination (a): {pvalue_dsc_race:.4f}")
        print(f"  p-value difficulty (b): {pvalue_dff_race:.4f}")
        print(f"  p-value guessing (c): {pvalue_gus_race:.4f}")
        print()
        
        print('Finner test')
        
        f = finner_test(pivots_dsc_race)
        print(f"discrimination (a)")
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
        print(f"   {f[0][1]}: {f[2][1]:.3f}")
        f = finner_test({'White': pivots_dsc[0], 'Pardo':  pivots_dsc[2]})
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
        f = finner_test({'White': pivots_dsc[0], 'Black':  pivots_dsc[1]})
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
        f = finner_test({'Black': pivots_dsc[1], 'Pardo':  pivots_dsc[2]})
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
        
        f = finner_test(pivots_dff_race)
        print(f"difficulty (b)")
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
        print(f"   {f[0][1]}: {f[2][1]:.3f}")
        f = finner_test({'White': pivots_dff[0], 'Pardo':  pivots_dff[2]})
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
        f = finner_test({'White': pivots_dff[0], 'Black':  pivots_dff[1]})
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
        f = finner_test({'Black': pivots_dff[1], 'Pardo':  pivots_dff[2]})
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
        
        f = finner_test(pivots_gus_race)
        print(f"guessing (c)")
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
        print(f"   {f[0][1]}: {f[2][1]:.3f}")
        f = finner_test({'White': pivots_gus[0], 'Pardo':  pivots_gus[2]})
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
        f = finner_test({'White': pivots_gus[0], 'Black':  pivots_gus[1]})
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
        f = finner_test({'Black': pivots_gus[1], 'Pardo':  pivots_gus[2]})
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
        
        
    if feat=='Income':
        print('Friedman test')
        pvalue_dsc_income, _, pivots_dsc = friedman_test(icc_par['Income'][comp]['Dscrmn_alta'], 
                                                         icc_par['Income'][comp]['Dscrmn_média'], 
                                                         icc_par['Income'][comp]['Dscrmn_baixa'])[1:4]
        pvalue_dff_income, _, pivots_dff = friedman_test(icc_par['Income'][comp]['Dffclt_alta'], 
                                                         icc_par['Income'][comp]['Dffclt_média'], 
                                                         icc_par['Income'][comp]['Dffclt_baixa'])[1:4]
        pvalue_gus_income, _, pivots_gus = friedman_test(icc_par['Income'][comp]['Gussng_alta'], 
                                                         icc_par['Income'][comp]['Gussng_média'], 
                                                         icc_par['Income'][comp]['Gussng_baixa'])[1:4]

        pivots_dsc_inc = {'High': pivots_dsc[0], 'Medium':  pivots_dsc[1], 'Low':  pivots_dsc[2]}
        pivots_dff_inc = {'High': pivots_dff[0], 'Medium':  pivots_dff[1], 'Low':  pivots_dff[2]}
        pivots_gus_inc = {'High': pivots_gus[0], 'Medium':  pivots_gus[1], 'Low':  pivots_gus[2]}

        print(f"  p-value discrimination (a): {pvalue_dsc_income:.4f}")
        print(f"  p-value difficulty (b): {pvalue_dff_income:.4f}")
        print(f"  p-value guessing (c): {pvalue_gus_income:.4f}")
        print()
        
        print('Finner test')
        
        f = finner_test(pivots_dsc_inc)
        print(f"discrimination (a)")
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
        print(f"   {f[0][1]}: {f[2][1]:.3f}")
        f = finner_test({'High': pivots_dsc[0], 'Medium':  pivots_dsc[1]})
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
        f = finner_test({'Medium':  pivots_dsc[1], 'Low': pivots_dsc[2]})
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
        
        f = finner_test(pivots_dff_inc)
        print(f"difficulty (b)")
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
        print(f"   {f[0][1]}: {f[2][1]:.3f}")
        f = finner_test({'High': pivots_dff[0], 'Medium':  pivots_dff[1]})
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
        f = finner_test({'Medium':  pivots_dff[1], 'Low': pivots_dff[2]})
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
        
        f = finner_test(pivots_gus_inc)
        print(f"difficulty (b)")
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
        print(f"   {f[0][1]}: {f[2][1]:.3f}")
        f = finner_test({'High': pivots_gus[0], 'Medium':  pivots_gus[1]})
        print(f"   {f[0][0]}: {f[2][0]:.3f}")
        f = finner_test({'Medium':  pivots_gus[1], 'Low': pivots_gus[2]})
        print(f"   {f[0][0]}: {f[2][0]:.3f}")