import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
from matplotlib.markers import MarkerStyle
import matplotlib.lines as mlines

plt.rcParams.update({'mathtext.fontset': 'dejavusans'})

def marker_group_gender(auc_fav_ch, cmax=None, auc_std_ch=None):
    x_gender_f = [i+0.5 for i in range(len(auc_fav_ch['Gender'])) if auc_fav_ch.loc[i,'Gender']=='F']
    y_gender_f = [0.5 for i in range(len(x_gender_f))]
    
    x_gender_m = [i+0.5 for i in range(len(auc_fav_ch['Gender'])) if auc_fav_ch.loc[i,'Gender']=='M']
    y_gender_m = [0.5 for i in range(len(x_gender_m))]
    
    if cmax is None:
        return x_gender_f, y_gender_f, x_gender_m, y_gender_m
    else:
        c_gender_f = [auc_std_ch.loc[i,'Gender']/cmax for i in range(len(auc_fav_ch['Gender'])) if auc_fav_ch.loc[i,'Gender']=='F']
        c_gender_m = [auc_std_ch.loc[i,'Gender']/cmax for i in range(len(auc_fav_ch['Gender'])) if auc_fav_ch.loc[i,'Gender']=='M']
        return x_gender_f, y_gender_f, x_gender_m, y_gender_m, c_gender_f, c_gender_m
    
def marker_group_race(auc_fav_ch, cmax=None, auc_std_ch=None):
    x_race_w_ch = [i+0.5 for i in range(len(auc_fav_ch['Race'])) if auc_fav_ch.loc[i,'Race']==1]
    y_race_w_ch = [1.5 for i in range(len(x_race_w_ch))]
    x_race_bl_ch = [i+0.5 for i in range(len(auc_fav_ch['Race'])) if auc_fav_ch.loc[i,'Race']==2]
    y_race_bl_ch = [1.5 for i in range(len(x_race_bl_ch))]
    x_race_br_ch = [i+0.5 for i in range(len(auc_fav_ch['Race'])) if auc_fav_ch.loc[i,'Race']==3]
    y_race_br_ch = [1.5 for i in range(len(x_race_br_ch))]
    
    if cmax is None:
        return x_race_w_ch, y_race_w_ch, x_race_bl_ch, y_race_bl_ch, x_race_br_ch, y_race_br_ch
    else:
        c_race_w_ch = [auc_std_ch.loc[i,'Race']/cmax for i in range(len(auc_fav_ch['Race'])) if auc_fav_ch.loc[i,'Race']==1]
        c_race_bl_ch = [auc_std_ch.loc[i,'Race']/cmax for i in range(len(auc_fav_ch['Race'])) if auc_fav_ch.loc[i,'Race']==2]
        c_race_br_ch = [auc_std_ch.loc[i,'Race']/cmax for i in range(len(auc_fav_ch['Race'])) if auc_fav_ch.loc[i,'Race']==3]
        return x_race_w_ch, y_race_w_ch, x_race_bl_ch, y_race_bl_ch, x_race_br_ch, y_race_br_ch, c_race_w_ch, c_race_bl_ch, c_race_br_ch

def marker_group_income(auc_fav_ch):
    x_income_b_ch = [i+0.5 for i in range(len(auc_fav_ch['Income'])) if auc_fav_ch.loc[i,'Income']=='baixa']
    y_income_b_ch = [2.5 for i in range(len(x_income_b_ch))]
    x_income_m_ch = [i+0.5 for i in range(len(auc_fav_ch['Income'])) if auc_fav_ch.loc[i,'Income']=='média']
    y_income_m_ch = [2.5 for i in range(len(x_income_m_ch))]
    x_income_a_ch = [i+0.5 for i in range(len(auc_fav_ch['Income'])) if auc_fav_ch.loc[i,'Income']=='alta']
    y_income_a_ch = [2.5 for i in range(len(x_income_a_ch))]
    
    return x_income_a_ch, y_income_a_ch, x_income_m_ch, y_income_m_ch, x_income_b_ch, y_income_b_ch
    
def plot_hist(auc_std, auc_fav, ax=None, cmax=0, colors='YlGnBu', yticklabels=True):
    if ax is None:
        fig = plt.figure(figsize=(16,6))
        ax = fig.add_subplot(111, aspect='equal')

        sns.heatmap(auc_std.transpose(), xticklabels=False,
                    linewidths=.5, square=True, 
                    cmap=colors, 
                    cbar_kws={"orientation": "horizontal"}
                   )
    else:
        sns.heatmap(auc_std.transpose(), xticklabels=False, yticklabels=yticklabels,
                    linewidths=.5, square=True, 
                    cmap=colors, vmin=0, vmax=cmax,
                    cbar_kws={"orientation": "horizontal"}, cbar=False,
                    ax=ax
                   )
    if cmax==0:
        x_gender_f, y_gender_f, x_gender_m, y_gender_m = marker_group_gender(auc_fav)
        x_race_w, y_race_w, x_race_bl, y_race_bl, x_race_br, y_race_br = marker_group_race(auc_fav)
        x_income_a, y_income_a, x_income_m, y_income_m, x_income_b, y_income_b = marker_group_income(auc_fav)
        c_gender_f = 'black'
        c_gender_m = 'black'
    else:
        x_gender_f, y_gender_f, x_gender_m, y_gender_m, c_gender_f, c_gender_m = marker_group_gender(auc_fav, cmax=cmax, auc_std_ch=auc_std)
        x_race_w, y_race_w, x_race_bl, y_race_bl, x_race_br, y_race_br, c_race_w, c_race_bl, c_race_br = marker_group_race(auc_fav, cmax=cmax, auc_std_ch=auc_std)
        x_income_a, y_income_a, x_income_m, y_income_m, x_income_b, y_income_b = marker_group_income(auc_fav)
        
        
    ax.scatter(x_gender_f, y_gender_f, marker="$\u2640$", c='white', linewidth=0.8, label='Woman', s=100)
    ax.scatter(x_gender_m, y_gender_m, marker="$\u2642$", c='white', linewidth=0.8, label='Man', s=100)

    ax.scatter(x_race_w, y_race_w, marker='$\mathrm{\mathsf{W}}$', c='white', linewidth=0.8, label='White', s=70)
    ax.scatter(x_race_br, y_race_br, marker='$\mathrm{\mathsf{P}}$', c='white', linewidth=0.8, label='Pardo', s=70)
    ax.scatter(x_race_bl, y_race_bl, marker='$\mathrm{\mathsf{B}}$', c='white', linewidth=0.8, label='Black', s=70)

    ax.scatter(x_income_b, y_income_b, marker=r"$\bigvee$", c='white', linewidth=0.4, label='Low income', s=70)
    ax.scatter(x_income_m, y_income_m, marker='o',facecolors='none', edgecolors='w', linewidth=1.2, 
               label='Medium income', s=50)
    ax.scatter(x_income_a, y_income_a, marker=r"$\bigwedge$", c='white', linewidth=0.4, label='High income', s=70)    
    
def plot_all_hists(auc_std_ch, auc_std_cn, auc_std_mt, auc_std_esp, auc_std_ing, auc_std_pt,
                   auc_fav_ch, auc_fav_cn, auc_fav_mt, auc_fav_esp, auc_fav_ing, auc_fav_pt, colors = 'YlGnBu'):
    cmin = 0
    cmax = max(auc_std_ch.max().max(), auc_std_cn.max().max(), auc_std_mt.max().max(),
           auc_std_esp.max().max(), auc_std_ing.max().max(), auc_std_pt.max().max())
    
    marker_w = mlines.Line2D([], [], marker="$\u2640$", c='black', markersize=10, label='Woman', linestyle='None')
    marker_m = mlines.Line2D([], [], marker="$\u2642$", c='black', markersize=10, label='Man', linestyle='None')

    marker_wh = mlines.Line2D([], [], marker='$\mathrm{\mathsf{W}}$', c='black', label='White', linestyle='None', markersize=8)
    marker_br = mlines.Line2D([], [], marker='$\mathrm{\mathsf{P}}$', c='black', label='Pardo', linestyle='None', markersize=8)
    marker_bl = mlines.Line2D([], [], marker='$\mathrm{\mathsf{B}}$', c='black', label='Black', linestyle='None', markersize=8)

    marker_li = mlines.Line2D([], [], marker=r"$\bigvee$", c='black', label='Low income', linestyle='None',
                             markersize=8)
    marker_mi = mlines.Line2D([], [], marker="o", fillstyle='none', c='black', markeredgewidth=1.7,
                              label='Medium income', linestyle='None', markersize=7)
    marker_hi = mlines.Line2D([], [], marker=r"$\bigwedge$", c='black', label='High income', linestyle='None', 
                              markersize=8)
    
    fig = plt.figure(figsize=(16,5))

    ax1 = plt.subplot2grid((4, 10), (0, 0), colspan=9)
    ax2 = plt.subplot2grid((4, 10), (1, 0), colspan=9)
    ax3 = plt.subplot2grid((4, 10), (2, 0), colspan=9)
    ax4 = plt.subplot2grid((4, 10), (3, 0), colspan=8)
    ax5 = plt.subplot2grid((4, 10), (3, 8))
    ax6 = plt.subplot2grid((4, 10), (3, 9))
    axc = plt.subplot2grid((4, 10), (0, 9), rowspan=3)

    plot_hist(auc_std_ch, auc_fav_ch, colors=colors, cmax=cmax, ax=ax1)
    ax1.set_title("Human Sciences (CH)")

    plot_hist(auc_std_cn, auc_fav_cn, colors=colors, cmax=cmax, ax=ax2)
    ax2.set_title("Natural Sciences (CN)")

    plot_hist(auc_std_mt, auc_fav_mt, colors=colors, cmax=cmax, ax=ax3)
    ax3.set_title("Mathematics (MT)")

    plot_hist(auc_std_pt, auc_fav_pt, colors=colors, cmax=cmax, ax=ax4)
    ax4.set_title("Languages (LC) - Portuguese")

    plot_hist(auc_std_ing, auc_fav_ing, colors=colors, cmax=cmax, ax=ax5, yticklabels=False)
    ax5.set_title("English")

    plot_hist(auc_std_esp, auc_fav_esp, colors=colors, cmax=cmax, ax=ax6, yticklabels=False)
    ax6.set_title("Spanish")

    cmap = mpl.cm.get_cmap(colors)
    norm = mpl.colors.Normalize(vmin=cmin, vmax=cmax)
    cb1 = mpl.colorbar.ColorbarBase(axc, cmap=cmap,
                                    norm=norm)
    cb1.outline.set_visible(False)
    axc.set_title("AUC Discrepancy")

    ax4.legend(loc='upper center', bbox_to_anchor=(0.62, -0.15),
              fancybox=True, shadow=True, ncol=8, handles=[marker_w, marker_m,
                       marker_wh, marker_br, marker_bl,
                       marker_li, marker_mi, marker_hi],
              title='Group with highiest AUC')

    #plt.tight_layout()
    fig.patch.set_facecolor('white')
    plt.savefig('HeatmapAUC2019.png', format='png', dpi=1200)