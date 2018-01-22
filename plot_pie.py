import pandas as pd, numpy as np, pylab as plt, pdb, squarify, brewer2mpl, os

d = pd.read_csv('Seattle_2015_building.csv')

tot_energy = {}
tot_gfa = {}
counts = {}
for key in d['LargestPropertyUseType'].unique():
    if not ((key is np.nan) | (key == 'Parking')):
        tot_energy[key] = d[d['LargestPropertyUseType'] == key]['SiteEnergyUse(kBtu)'].sum()
        tot_gfa[key] = d[d['LargestPropertyUseType'] == key]['PropertyGFABuilding(s)'].sum()
        counts[key] = len(d[d['LargestPropertyUseType'] == key])

for key in d[d['LargestPropertyUseType'] == 'Parking']['SecondLargestPropertyUseType'].unique():
    tot_energy[key] += d[d['SecondLargestPropertyUseType'] == key]['SiteEnergyUse(kBtu)'].sum()
    tot_gfa[key] += d[d['SecondLargestPropertyUseType'] == key]['PropertyGFABuilding(s)'].sum()
    counts[key] += len(d[d['SecondLargestPropertyUseType'] == key])

sum_d = pd.DataFrame.from_dict({'tot_energy':tot_energy,'tot_gfa':tot_gfa,'counts':counts})

bdir = 'buildings'
if not os.path.isdir(bdir): os.mkdir(bdir)
ibig = (sum_d['tot_energy'] > 3e8)

for ft in sum_d[ibig].index:
    ft_buildings = d[d['LargestPropertyUseType']==ft]
    quant = ft_buildings['SiteEUI(kBtu/sf)'].quantile([.25,.5,.75])
    x_eui = (ft_buildings['SiteEUI(kBtu/sf)']<quant[0.25]) | (ft_buildings['SiteEUI(kBtu/sf)']>quant[0.75])
    bf=bdir+'/'+ft.replace(' ','_').replace('/','-')+'.csv'
    ft_buildings[x_eui].sort_values('SiteEUI(kBtu/sf)').to_csv(bf,
                               columns=['PropertyName','SiteEUI(kBtu/sf)'])
    
sum_d = sum_d.rename(index={'Hospital (General Medical & Surgical)':'Hospital',
                            'Non-Refrigerated Warehouse':'NR Warehouse\n',
                            'Other':'Unclassified',
                            'Supermarket/Grocery Store':'Grocery Store\n',
                            'College/University':'College',
                            'Senior Care Community':'Nursing Home',
                            'Other - Entertainment/Public Assembly':'Public Assembly'})

sum_d = sum_d.sort_values('tot_energy',ascending=False)

ismall = (sum_d['tot_energy'] < 3e8)
sum_d.loc['Other']=[sum_d[ismall]['counts'].sum(),
                    sum_d[ismall]['tot_energy'].sum(),
                    sum_d[ismall]['tot_gfa'].sum()]
ibig = (sum_d['tot_energy'] > 3e8)
labels = list(sum_d[ibig].index)
en_values = ['{:.1%}'.format(val) for val in sum_d[ibig]['tot_energy']/sum_d['tot_energy'].sum()]
gfa_values = ['{:.1%}'.format(val) for val in sum_d[ibig]['tot_gfa']/sum_d['tot_gfa'].sum()]
count_values = ['{:.1%}'.format(val) for val in sum_d[ibig]['counts']/sum_d['counts'].sum()]

bmap = brewer2mpl.get_map('Paired','Qualitative',12)
colors = bmap.mpl_colors


plt.close('all')
plt.clf()
f,ax = plt.subplots(figsize=(6,6))
f.subplots_adjust(left=0.01,right=0.99,bottom=0.01,top=0.99)
squarify.plot(sum_d[ibig]['tot_energy'],label=labels,ax=ax,value=en_values,
              color=colors)
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)

f.savefig('pie_tot_energy.png')

f1,ax1 = plt.subplots(figsize=(6,6))
f1.subplots_adjust(left=0.01,right=0.99,bottom=0.01,top=0.99)
squarify.plot(sum_d[ibig]['tot_gfa'],label=labels,ax=ax1,value=gfa_values,
              color=colors)
#ax1.pie(sum_d[ibig]['tot_gfa'],labels=labels,autopct='%1.1f%%',startangle=90)
ax1.get_xaxis().set_visible(False)
ax1.get_yaxis().set_visible(False)

f1.savefig('pie_tot_gfa.png')

f2,ax2 = plt.subplots(figsize=(6,6))
f2.subplots_adjust(left=0.01,right=0.99,bottom=0.01,top=0.99)
#ax2.pie(sum_d[ibig]['counts'],labels=labels,autopct='%1.1f%%',startangle=90)
squarify.plot(sum_d[ibig]['counts'],label=labels,ax=ax2,value=count_values,
              color=colors)
ax2.get_xaxis().set_visible(False)
ax2.get_yaxis().set_visible(False)

f2.savefig('pie_counts.png')

f4,ax4 = plt.subplots(1,2,sharey=True,figsize=(8,4))
f4.subplots_adjust(left=0.06,right=0.99,top=0.99,wspace=0,bottom=0.12)
for it,ind in enumerate(sum_d[ibig].index):
    if it < 5:
        ax4[0].plot(sum_d['tot_gfa'][ind]/1e6,sum_d['tot_energy'][ind]/1e9,'.',
                    label=ind,ms=10)
        ax4[1].plot(sum_d['counts'][ind],sum_d['tot_energy'][ind]/1e9,'.',ms=10)
    else:
        ax4[0].plot(sum_d['tot_gfa'][ind]/1e6,sum_d['tot_energy'][ind]/1e9,'.')
        ax4[1].plot(sum_d['counts'][ind],sum_d['tot_energy'][ind]/1e9,'.')



ax4[0].plot([0,25],[0,2.5],label="EUI=100 kBTU/ft$^2$/yr")
ax4[0].plot([0,100],[0,5],label="EUI=50 kBTU/ft$^2$/yr")
ax4[0].set_xlabel('Gross Floor Area [10$^6$ ft$^2$]')
ax4[0].set_ylabel('1 Year Energy Usage [10$^9$ kBTU / yr]')
ax4[0].legend(loc=2,frameon=False)

ax4[1].plot([0,500],[0,5],label="$10^7$ kBTU/building")
ax4[1].set_xlabel('Counts')
ax4[1].set_ylim(0,4.9)
ax4[1].legend()
f4.savefig('count_energy_gfa.png')
