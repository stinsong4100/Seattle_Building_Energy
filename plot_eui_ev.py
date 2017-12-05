import bpd_api_python_lib as bpd, numpy as np, pickle, pylab as plt, os
from textwrap import wrap

years=np.arange(2015.0,2008.0,-1.0)
zone4 = ['4A Mixed - Humid (Baltimore-MD)',
         '4B Mixed - Dry (Albuquerque-NM)',
         '4C Mixed - Marine (Salem-OR)']
zone4c = ['4C Mixed - Marine (Salem-OR)']

regions = [['city','Seattle'],['climate',zone4c],['climate',zone4],['']]
regs = ['sea','z4c','z4','nat']
if os.path.isfile('bpd_tables.pck'):
    with open('bpd_tables.pck','rb') as f: d=pickle.load(f)
else:
    d = {}
    for year in years:
        for ireg, reg in enumerate(regions):
            try:
                if reg[0] is '':
                    raw = bpd.table(filters={'site_year':{'min':year,'max':year+0.999}},
                                    group_by=['facility_type'],
                                    analyze_by="site_eui")['table']
                else: 
                    raw = bpd.table(filters={reg[0]:[reg[1]],
                                             'site_year':{'min':year,'max':year+0.999}},
                                    group_by=['facility_type'],
                                    analyze_by="site_eui")['table']
            except: pass

            if regs[ireg] not in d.keys(): d[regs[ireg]]={}
            for rec in raw:
                if rec['count'] > 0:
                    rv = rec['group'][0]['value']
                    print(year, regs[ireg], rv, rec['count'])
                    if rv not in d[regs[ireg]].keys(): d[regs[ireg]][rv]={}
                    if 'years' not in d[regs[ireg]][rv].keys(): 
                        d[regs[ireg]][rv]['years']=[]
                        d[regs[ireg]][rv]['means']=[]
                        d[regs[ireg]][rv]['0s']=[]
                        d[regs[ireg]][rv]['100s']=[]
                        d[regs[ireg]][rv]['25s']=[]
                        d[regs[ireg]][rv]['50s']=[]
                        d[regs[ireg]][rv]['75s']=[]
                        d[regs[ireg]][rv]['stdevs']=[]
                        d[regs[ireg]][rv]['counts']=[]
                    d[regs[ireg]][rv]['years'].append(year)
                    d[regs[ireg]][rv]['counts'].append(rec['count'])
                    d[regs[ireg]][rv]['means'].append(rec['mean'])
                    d[regs[ireg]][rv]['0s'].append(rec['percentile_0'])
                    d[regs[ireg]][rv]['100s'].append(rec['percentile_100'])
                    d[regs[ireg]][rv]['25s'].append(rec['percentile_25'])
                    d[regs[ireg]][rv]['50s'].append(rec['percentile_50'])
                    d[regs[ireg]][rv]['75s'].append(rec['percentile_75'])
                    d[regs[ireg]][rv]['stdevs'].append(rec['standard_deviation'])
                    
    with open('bpd_tables.pck','wb') as f:
        pickle.dump(d,f)

ashrae_eui = {'Commercial - Other':40,
 'Commercial - Uncategorized':40,
 'Commercial - Unknown':40,
 'Education - College or university':65,
 'Education - Other classroom':40,
 'Food Service - Restaurant or cafeteria':156,
 'Food Service - Uncategorized':85,
 'Grocery store or food market':131,
 'Health Care - Inpatient':135,
 'Lodging - Dormitory or fraternity/sorority':54,
 'Lodging - Hotel':52,
 'Mixed Use - Commercial and Residential':30,
 'Mixed Use - Predominantly Residential':30,
 'Multifamily - Uncategorized':30,
 'Nursing Home':84,
 'Office - Administrative or Professional':40,
 'Office - Medical non diagnostic':34,
 'Office - Uncategorized':40,
 'Parking Garage':10,
 'Public Assembly - Library':61,
 'Public Assembly - Other':28,
 'Public Assembly - Recreation':26,
 'Religious worship':23,
 'Retail - Uncategorized':30,
 'Service - Post office or postal center':43,
 'Warehouse - Distribution or Shipping center':22,
 'Warehouse - Non-refrigerated':11,
 'Warehouse - Refrigerated':69,
 'Warehouse - Self-storage':15,
 'Warehouse - Uncategorized':20,
 '5+ Unit Building':43}
                        
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

    for ir,rg in enumerate(regs[1:4]):
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

    
    ax[ix,iy].plot([2008,2015],[ashrae_eui[ft],ashrae_eui[ft]],color='C5')
    ax[ix,iy].text(0.8,0.1,str(d['sea'][ft]['counts'][0]),color='C0',
                   transform=ax[ix,iy].transAxes)
    ax[ix,iy].text(0.8,0.8,str(d['nat'][ft]['counts'][0]),color='C3',
                   transform=ax[ix,iy].transAxes)
    ax[ix,iy].text(0.1,0.1,str(ashrae_eui[ft]),color='C5',
                   transform=ax[ix,iy].transAxes)
    ylims=ax[ix,iy].get_ylim()
    ax[ix,iy].set_ylim(0,ylims[1])

ax[2,2].legend(loc=2)
f.text(0.5,0.01,'Years',ha='center')
f.text(0.01,0.5,'Energy Usage Intensity (EUI) [kBTU / ft$^2$ / yr]',va='center',rotation='vertical')

f.savefig('Seattle_Median_EUIs.png')
