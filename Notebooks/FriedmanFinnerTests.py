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