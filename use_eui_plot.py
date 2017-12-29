import pandas as pd, pylab as plt, numpy as np, pdb, os, mpld3

kc_d = pd.read_csv('Revised_2015_Seattle.csv')
kcsec_full = pd.read_csv('~/Downloads/Commercial Building/EXTR_CommBldgSection.csv',encoding='latin1')
city_d = pd.read_csv('2015_Building_Energy_Benchmarking.csv')
lookup_d = pd.read_csv('lookup.csv')


use_d = kc_d.groupby('main_use')[['SiteEnergyUse(kBtu)',
                                'no_parking_use_sum_gfa']].sum().sort_values('SiteEnergyUse(kBtu)',ascending=False)
use_d['count'] = kc_d.groupby('main_use')['main_use'].count()
use_d['mean_eui'] = use_d['SiteEnergyUse(kBtu)']/use_d['no_parking_use_sum_gfa']
use_d = use_d.join(kcsec_full.groupby('main_use')['GrossSqFt'].sum())
use_d = use_d.rename(index=str,columns={'GrossSqFt':'tot_kc_gfa'})
use_d['extrapolated_energy']=use_d['tot_kc_gfa']*use_d['mean_eui']

use_d.to_csv('uses.csv')

fields=['BldgQuality','YrBuilt','EffYr','HeatingSystem','ConstrClass']
xlabels=['Building Quality','Year Built','Year Remodeled','Heating System',
         'Construction Class']

for use in combine.keys():
    s_d = kc_d[kc_d['main_use']==use]
    s_d = s_d[np.isfinite(s_d['site_eui'])]

    dirname = 'plots/'+use
    if not os.path.isdir(dirname): os.mkdir(dirname)
    plt.close('all')
    plt.clf()

    f1,ax1 = plt.subplots()
    f1.subplots_adjust(top=0.97,right=0.99,left=0.08)
    ax1.hist(s_d['site_eui'].values,bins=20)
    ylim = ax1.get_ylim()
    ax1.set_ylim(ylim)
    targ_eui = ashrae_eui[use]
    ax1.plot([targ_eui,targ_eui],ylim,'k--',label='ASHRAE target')
    med_eui = np.median(s_d['site_eui'])
    print(use,med_eui,targ_eui)
    ax1.plot([med_eui,med_eui],ylim,'C0:',label='Median')
    ax1.legend()
    ax1.set_xlabel('Energy Usage Intensity (EUI)')
    ax1.set_ylabel('Number of '+use)
    f1.savefig(dirname+'/eui_hist.png')
    with open(dirname+'/eui_hist.html','w') as outfile:
        outfile.write(mpld3.fig_to_html(f1))

#['Major','Minor','BldgNbr'])['GrossSqFt']
    

    for iF,field in enumerate(fields):
        f,ax = plt.subplots()
        f.subplots_adjust(top=0.97,right=0.97,left=0.1,bottom=0.1)
        
        scatter = ax.scatter(s_d[field].values,s_d['site_eui'].values)
        xlim=ax.get_xlim()
        ylim=ax.get_ylim()
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.plot(xlim,[targ_eui,targ_eui],'k--',label='ASHRAE target')
        ax.plot(xlim,[med_eui,med_eui],'C0:',label='Median')
        ax.legend()
        ax.set_xlabel(xlabels[iF])

        ax.set_ylabel('Energy Usage Intensity (EUI)')
        f.savefig(dirname+'/'+field+'.png')

        tooltip = mpld3.plugins.PointLabelTooltip(scatter,labels=list(s_d['PropertyName'].values))
        mpld3.plugins.connect(f,tooltip)
        with open(dirname+'/'+field+'.html','w') as outfile:
            outfile.write(mpld3.fig_to_html(f))
