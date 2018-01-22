import pandas as pd, numpy as np, pylab as plt, pdb, squarify, brewer2mpl, os
from textwrap import fill

use_d = pd.read_csv('uses.csv')

use_d = use_d.rename(index=str,columns={'SiteEnergyUse(kBtu)':'tot_energy'})

ismall = (use_d['tot_energy'] < 2.9e8)
use_d = use_d.append({'main_use':'Other',
              'tot_energy':use_d[ismall]['tot_energy'].sum(),
              'no_parking_gfa':use_d[ismall]['no_parking_gfa'].sum(),
              'count':use_d[ismall]['count'].sum(),
              'mean_eui':use_d[ismall]['mean_eui'].mean(),
              'tot_kc_gfa':use_d[ismall]['tot_kc_gfa'].sum(),
              'extrapolated_energy':use_d[ismall]['extrapolated_energy'].sum()
              },ignore_index=True)

iOther = use_d['main_use']=='Other'
use_d.loc[iOther,'mean_eui']=use_d[iOther]['tot_energy']/use_d[iOther]['no_parking_gfa']
ibig = (use_d['tot_energy'] > 2.9e8)

use_d['en_frac'] = use_d['tot_energy']/use_d['tot_energy'].sum()
en_vals = [f'{val:.1%}' for val in use_d[ibig]['en_frac']]
use_d['gfa_frac'] = use_d['no_parking_gfa']/use_d['no_parking_gfa'].sum()
use_d['count_frac'] = use_d['count']/use_d['count'].sum()

bmap = brewer2mpl.get_map('Paired','Qualitative',12)
colors = bmap.mpl_colors

plt.close('all')
plt.clf()
f,ax = plt.subplots(figsize=(6,6))
f.subplots_adjust(left=0.01,right=0.99,bottom=0.01,top=0.99)
squarify.plot(use_d[ibig]['tot_energy'],
              label=[fill(val,width=12) for val in use_d[ibig]['main_use']],
              ax=ax,value=en_vals,color=colors)
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)

f.savefig('kc_use_tot_energy.png')

f4,ax4 = plt.subplots(1,2,sharey=True,figsize=(8,4))
f4.subplots_adjust(left=0.06,right=0.99,top=0.99,wspace=0,bottom=0.12)
for it,ind in enumerate(use_d[ibig].index):
    if it < 5:
        ax4[0].plot(use_d['no_parking_gfa'][ind]/1e6,
                    use_d['tot_energy'][ind]/1e9,'.',c=colors[ind%12],
                    label=use_d['main_use'][ind],ms=10)
        ax4[1].plot(use_d['count'][ind],use_d['tot_energy'][ind]/1e9,'.',
                    c=colors[ind%12],ms=10)
    else:
        ax4[0].plot(use_d['no_parking_gfa'][ind]/1e6,
                    use_d['tot_energy'][ind]/1e9,'.',c=colors[ind%12])
        ax4[1].plot(use_d['count'][ind],use_d['tot_energy'][ind]/1e9,'.',
                    c=colors[ind%12])



ax4[0].plot([0,25],[0,2.5],label="EUI=100 kBTU/ft$^2$/yr")
ax4[0].plot([0,100],[0,5],label="EUI=50 kBTU/ft$^2$/yr")
ax4[0].set_xlabel('Gross Floor Area [10$^6$ ft$^2$]')
ax4[0].set_ylabel('1 Year Energy Usage [10$^9$ kBTU / yr]')
ax4[0].legend(loc=2,frameon=False)

ax4[1].plot([0,500],[0,5],label="$10^7$ kBTU/building")
ax4[1].set_xlabel('Counts')
ax4[1].set_ylim(0,4.9)
ax4[1].legend()
f4.savefig('kc_count_energy_gfa.png')

use_d = use_d[use_d['main_use']!='Other']
ismall = (use_d['extrapolated_energy'] < 1e9)
use_d = use_d.append({'main_use':'Other',
              'tot_energy':use_d[ismall]['tot_energy'].sum(),
              'no_parking_gfa':use_d[ismall]['no_parking_gfa'].sum(),
              'count':use_d[ismall]['count'].sum(),
              'mean_eui':use_d[ismall]['mean_eui'].mean(),
              'tot_kc_gfa':use_d[ismall]['tot_kc_gfa'].sum(),
              'extrapolated_energy':use_d[ismall]['extrapolated_energy'].sum()
              },ignore_index=True)
ibig = (use_d['extrapolated_energy'] > 1e9)

use_d['extr_en_frac'] = use_d['extrapolated_energy']/use_d['extrapolated_energy'].sum()
extr_en_vals = [f'{val:.1%}' for val in use_d[ibig]['extr_en_frac']]

f2,ax2 = plt.subplots(figsize=(6,6))
f2.subplots_adjust(left=0.01,right=0.99,bottom=0.01,top=0.99)
squarify.plot(use_d[ibig]['extrapolated_energy'],
              label=[fill(val,width=12) for val in use_d[ibig]['main_use']],
              ax=ax2,value=extr_en_vals,color=colors)
ax2.get_xaxis().set_visible(False)
ax2.get_yaxis().set_visible(False)

f2.savefig('kc_extr_energy.png')

f5,ax5 = plt.subplots()
f5.subplots_adjust(left=0.1,right=0.99,top=0.97,wspace=0,bottom=0.12)
for it,ind in enumerate(use_d[ibig].index):
    if it < 5:
        ax5.plot(use_d['tot_kc_gfa'][ind]/1e6,
                    use_d['extrapolated_energy'][ind]/1e9,'.',c=colors[ind%12],
                    label=use_d['main_use'][ind],ms=10)
    else:
        ax5.plot(use_d['tot_kc_gfa'][ind]/1e6,
                    use_d['extrapolated_energy'][ind]/1e9,'.',c=colors[ind%12])



ax5.plot([0,60],[0,6],':',label="EUI=100 kBTU/ft$^2$/yr")
ax5.plot([0,300],[0,15],':',label="EUI=50 kBTU/ft$^2$/yr")
ax5.plot([0,300],[0,12],':',label="EUI=40 kBTU/ft$^2$/yr")
ax5.set_xlabel('Gross Floor Area [10$^6$ ft$^2$]')
ax5.set_ylabel('Annual Energy Usage [10$^9$ kBTU / yr]')
ax5.set_ylim(0,12)
ax5.set_xlim(0,275)
ax5.legend(loc=2,frameon=False)

f5.savefig('kc_extr_energy_gfa.png')
