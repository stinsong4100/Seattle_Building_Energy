import pandas as pd, pylab as plt, numpy as np

kc_d = pd.read_csv('Revised_2015_Seattle.csv')
kcsec_full = pd.read_csv('~/Downloads/Commercial Building/EXTR_CommBldgSection.csv',encoding='latin1')
city_d = pd.read_csv('2015_Building_Energy_Benchmarking.csv')

iKCSecSchool = (kcsec_full['SectionUse']==365) | \
    (kcsec_full['SectionUse']==366) | \
    (kcsec_full['SectionUse']==484)
school_pins = pd.to_numeric(kcsec_full[iKCSecSchool]['Major'].apply('{0:0>6}'.format)+ \
    kcsec_full[iKCSecSchool]['Minor'].apply('{0:0>4}'.format))

iSchool = np.in1d(kc_d['TaxParcelIdentificationNumber'],school_pins)

s_d = kc_d[iSchool]
s_d = s_d.merge(city_d[['TaxParcelIdentificationNumber','PropertyName',
                  'BuildingType']],on='TaxParcelIdentificationNumber')
s_d = s_d[np.isfinite(s_d['site_eui'])]
s_d = s_d[s_d['site_eui']<100]
sps_d = s_d[s_d['BuildingType'].str.contains('SPS-District')]

plt.close('all')
plt.clf()

f1,ax1 = plt.subplots()
f1.subplots_adjust(top=0.97,right=0.99,left=0.08)
ax1.hist(s_d['site_eui'].values,bins=100,label='All Schools in Seattle')
ax1.hist(sps_d['site_eui'].values,bins=100,label='Seattle Public Schools')
ax1.plot([40,40],[0,7],'k--')
med_eui = np.median(sps_d['site_eui'])
print(med_eui)
ax1.plot([med_eui,med_eui],[0,7],'C1:')
ax1.set_ylim(0,7)
ax1.set_xlabel('Energy Usage Intensity (EUI)')
ax1.set_ylabel('Number of Schools')
ax1.legend()
f1.savefig('school_eui_hist.png')

#['Major','Minor','BldgNbr'])['GrossSqFt']


fields=['BldgQuality','YrBuilt','EffYr','HeatingSystem','ConstrClass']
xlabels=['Building Quality','Year Built','Year Remodeled','Heating System',
         'Construction Class']
for iF,field in enumerate(fields):
    f,ax = plt.subplots()
    f.subplots_adjust(top=0.97,right=0.97,left=0.1,bottom=0.1)

    ax.plot(s_d[field],s_d['site_eui'],'.')
    ax.plot(sps_d[field],sps_d['site_eui'],'.')
    xlim=ax.get_xlim()
    ylim=ax.get_ylim()
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.plot(xlim,[med_eui,med_eui],'k--')
    ax.fill_between(np.array(xlim),60,ylim[1],color='r',alpha=0.1)
    ax.fill_between(np.array(xlim),70,ylim[1],color='r',alpha=0.1)
    ax.fill_between(np.array(xlim),80,ylim[1],color='r',alpha=0.1)
    ax.fill_between(np.array(xlim),90,ylim[1],color='r',alpha=0.1)
    ax.plot(sps_d[field],sps_d['site_eui'],'C1.')
    ax.set_xlabel(xlabels[iF])

    ax.set_ylabel('Energy Usage Intensity (EUI)')
    f.savefig(field+'.png')
