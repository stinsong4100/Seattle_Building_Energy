import bpd_api_python_lib as bpd, numpy as np, pickle, pylab as plt, os
import pandas as pd, pdb
from textwrap import wrap

sea_d = pd.read_csv('Seattle_2015_building.csv')

with open('bpd_tables.pck','rb') as f: d=pickle.load(f)

ashrae_eui = pd.read_csv('ashrae_eui.csv',header=None,index_col=0).T

plotlist = {'Office - Uncategorized':'Office',
            'Multifamily - Uncategorized':'Multifamily Housing',
            'Health Care - Inpatient':'Hospital',
            'Lodging - Hotel':'Hotel',
            'Office - Medical non diagnostic':'Medical Office',
            'Retail - Uncategorized':'Retail Store',
            'Education - Other classroom':'K-12 School',
            'Nursing Home':'Nursing Home',
            'Education - College or university':'College/University',
            'Grocery store or food market':'Grocery Store',
            'Public Assembly - Recreation':'Performing Arts'}

sea_dict = {'Office - Uncategorized':'Office',
            'Multifamily - Uncategorized':'Multifamily Housing',
            'Health Care - Inpatient':'Hospital (General Medical & Surgical)',
                        'Lodging - Hotel':'Hotel',
            'Office - Medical non diagnostic':'Medical Office',
            'Retail - Uncategorized':'Retail Store',
            'Education - Other classroom':'K-12 School',
            'Nursing Home':'Senior Care Community',
            'Education - College or university':'College/University',
            'Grocery store or food market':'Supermarket/Grocery Store',
            'Public Assembly - Recreation':'Performing Arts'}

plt.close('all')
plt.clf()
f,ax=plt.subplots(4,3,sharex=True,figsize=[9,9])
f.subplots_adjust(top=0.96,bottom=0.05,hspace=0.2,left=0.08,right=0.99)

regs = ['sea','z4c','nat']
col=['C2','C3','C4']
labs=['Zone 4C','Nation']


for ift,ft in enumerate(plotlist):
    ix = int(ift/3)
    iy = ift % 3

    ax[ix,iy].set_title('\n'.join(wrap(plotlist[ft],25)))

    for ir,rg in enumerate(regs[1:3]):
        ax[ix,iy].fill_between(d[rg][ft]['years'],
                               d[rg][ft]['25s'],d[rg][ft]['75s'],
                               color=col[ir],alpha=0.2,label=labs[ir])

    if len(d['sea'][ft]['50s']) > 1:
        ax[ix,iy].plot(d['sea'][ft]['years'],d['sea'][ft]['50s'])
        yerr = [np.array(d['sea'][ft]['75s']) - np.array(d['sea'][ft]['50s']),
                np.array(d['sea'][ft]['50s']) - np.array(d['sea'][ft]['25s'])]
        ax[ix,iy].errorbar(d['sea'][ft]['years'],d['sea'][ft]['50s'],yerr=yerr,color='C0')
    else:
        ax[ix,iy].plot(d['sea'][ft]['years'],d['sea'][ft]['50s'],'o')
        yerr = [np.array(d['sea'][ft]['75s']) - np.array(d['sea'][ft]['50s']),
                np.array(d['sea'][ft]['50s']) - np.array(d['sea'][ft]['25s'])]
        #pdb.set_trace()
        ax[ix,iy].errorbar(d['sea'][ft]['years'],d['sea'][ft]['50s'],yerr=yerr,color='C0')

    sea_quant = sea_d[sea_d['LargestPropertyUseType']==sea_dict[ft]]['SiteEUI(kBtu/sf)'].quantile([.25,.5,.75])
    ax[ix,iy].plot(2015.2,sea_quant[0.5],c='m')
    sea_yerr = [np.array([sea_quant[0.75]-sea_quant[0.5]]),np.array([sea_quant[0.5]-sea_quant[0.25]])]
    ax[ix,iy].errorbar(2015.2,sea_quant[0.5],yerr=sea_yerr,color='m')
    
    ax[ix,iy].plot([2008,2015],[ashrae_eui[ft][1],ashrae_eui[ft][1]],color='C5')
    ax[ix,iy].text(0.8,0.1,str(d['sea'][ft]['counts'][0]),color='C0',
                   transform=ax[ix,iy].transAxes)
    ax[ix,iy].text(0.8,0.8,str(d['nat'][ft]['counts'][0]),color='C3',
                   transform=ax[ix,iy].transAxes)
    ax[ix,iy].text(0.1,0.1,str(ashrae_eui[ft][1]),color='C5',
                   transform=ax[ix,iy].transAxes)
    ylims=ax[ix,iy].get_ylim()
    ax[ix,iy].set_ylim(0,ylims[1])

ax[2,2].legend(loc=2)
f.text(0.5,0.01,'Years',ha='center')
f.text(0.01,0.5,'Energy Usage Intensity (EUI) [kBTU / ft$^2$ / yr]',va='center',rotation='vertical')

f.savefig('Seattle_Median_EUIs.png')
