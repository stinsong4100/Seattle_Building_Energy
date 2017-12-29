#
# Building data obtained from King County Assessors Office
# http://info.kingcounty.gov/assessor/DataDownload/default.aspx
# All buildings included in Commercial Building file
# Used sqlite3 to join city and county tables
# sqlite> .mode csv
# sqlite> .import EXTR_CommBldg.csv kc
# sqlite> .import EXTR_CommBldgSection.csv kcsec
# sqlite> .import '/Users/stinson/Dropbox/SBC/Seattle Building Energy/Seattle_Building_Energy/Seattle_2015_building.csv' c
# sqlite> .headers on
# sqlite> .output kccommsection.csv
# sqlite> select * from kcsec join c on 
# kcsec.Major||kcsec.Minor = substr('0000'||c.TaxParcelIdentificationNumber,-10,10);
# sqlite> .quit
#
# Note: substr adds 0 padding to match maximum possible buildings
#
# and likewise for kc
#
# sqlite> .output kccomm.csv
# sqlite> select kc.*,c.TaxParcelIdentificationNumber from kc join c on 
#  kc.Major||kc.Minor = substr('0000'||c.TaxParcelIdentificationNumber,-10,10);
# sqlite> .quit
#
# This leaves some duplicates, you can kc_d.drop_duplicates() and resave csv
#

import pandas as pd, pdb, numpy as np, os, pylab as plt

kc_full = pd.read_csv('~/Downloads/Commercial Building/EXTR_CommBldg.csv',
                      encoding='latin1')
kcsec_full = pd.read_csv('~/Downloads/Commercial Building/EXTR_CommBldgSection.csv',encoding='latin1')
#.set_index(['Major','Minor','BldgNbr','SectionUse'])
#city_d = pd.read_csv('Seattle_2015_building.csv')
city_d = pd.read_csv('2015_Building_Energy_Benchmarking.csv')
city_d['c_use_sum_gfa'] = city_d['LargestPropertyUseTypeGFA'] + city_d['SecondLargestPropertyUseTypeGFA'] + city_d['ThirdLargestPropertyUseTypeGFA']
lookup_d = pd.read_csv('lookup.csv')

kc_full['TaxParcelIdentificationNumber'] = pd.to_numeric(\
    kc_full['Major'].apply('{0:0>6}'.format)+ \
    kc_full['Minor'].apply('{0:0>4}'.format))

# sum total square feet in section table, concat to main table
kc_gfa = kcsec_full.groupby(['Major','Minor','BldgNbr'])['GrossSqFt'].sum()
kc_gfa.name = 'use_sum_gfa'
kc_full = pd.concat([kc_full.set_index(['Major','Minor','BldgNbr']),kc_gfa],
                 axis=1)

# same thing, but with no parking
np_kc_gfa = kcsec_full[(kcsec_full['SectionUse']!=345) & 
                    (kcsec_full['SectionUse']!=388) &
                    (kcsec_full['SectionUse']!=70) &
                    (kcsec_full['SectionUse']!=850) &
                    (kcsec_full['SectionUse']!=851)].groupby(['Major','Minor','BldgNbr'])['GrossSqFt'].sum()
np_kc_gfa.name = 'no_parking_use_sum_gfa'
kc_full = pd.concat([kc_full,np_kc_gfa],axis=1)

kc_d = pd.merge(kc_full.reset_index(),city_d[[
            'PropertyName','TaxParcelIdentificationNumber',
            'PropertyGFATotal','c_use_sum_gfa','SiteEnergyUse(kBtu)',
            'SiteEnergyUseWN(kBtu)', 'SteamUse(kBtu)','Electricity(kWh)', 
            'Electricity(kBtu)','NaturalGas(therms)', 'NaturalGas(kBtu)',
            'OtherFuelUse(kBtu)','BuildingType']],
                left_on=['TaxParcelIdentificationNumber'],#'BldgGrossSqFt'],
                right_on=['TaxParcelIdentificationNumber'],#'PropertyGFATotal'],
                how='inner')

kc_d['keep']=True
icopy = kc_d.duplicated('TaxParcelIdentificationNumber',keep=False)
kc_d.loc[icopy,'keep']=False
repeat_pins = np.unique(kc_d[icopy]['TaxParcelIdentificationNumber'])
for pin in repeat_pins:
    buildings = kc_d[kc_d['TaxParcelIdentificationNumber']==pin]
    kc_gfas = np.sort(np.unique(buildings['BldgGrossSqFt']))[::-1]
    city_gfas = np.sort(np.unique(buildings['PropertyGFATotal']))[::-1]
    for ic,cgfa in enumerate(city_gfas):
        try:
            kc_d.loc[(kc_d['PropertyGFATotal']==cgfa)&(kc_d['BldgGrossSqFt']==kc_gfas[ic]),'keep']=True
            print('Keeping: ',pin,cgfa,kc_gfas[ic])
        except IndexError: pass  # more city values than county values


kc_d=kc_d[kc_d['keep']]

iLowArea = kc_d['no_parking_use_sum_gfa']<kc_d['PropertyGFATotal']/10
kc_d.loc[iLowArea,'no_parking_use_sum_gfa']=kc_d.loc[iLowArea,'PropertyGFATotal']


# What is missing?
temp_a = np.setxor1d(kc_d['TaxParcelIdentificationNumber'],city_d['TaxParcelIdentificationNumber'])
missing_pins = np.int64(temp_a[np.isfinite(temp_a)])

kc_condos = pd.read_csv('/Users/stinson/Downloads/Condo Complex and Units/EXTR_CondoComplex.csv')
kc_condos['TaxParcelIdentificationNumber'] = pd.to_numeric(\
    kc_condos['Major'].apply('{0:0>6}'.format)+'0000')

condo_bools = np.in1d(missing_pins,kc_condos['TaxParcelIdentificationNumber'])
# !!! XXX  Condos NEED to be taken care of later XXX
condo_pins = missing_pins[condo_bools]
print('# of city Condo PINS in KC data: ',len(np.unique(condo_pins)))
# Weird stuff in here, typically no building data, revert it to city values
missing_pins = missing_pins[~condo_bools]
print('# of city PINS missing from KC data: ',len(np.unique(missing_pins)))

# Search for missing items
# Turned off for now because it is limited number of weird cases
if False:
    iOldPIN = np.in1d(city_d['TaxParcelIdentificationNumber'],missing_pins)
    locs = city_d[iOldPIN]['Location']
    old_pins = city_d[iOldPIN]['TaxParcelIdentificationNumber'].values
    
    print("FAILED LIST:")
    addresses = locs.str.split('\n').str[0].str.split(' ')
#kc_full = kc_full.drop(np.where(kc_full['Address'].str.contains('NaN'))[0])
    for iMissing,(address,old_pin) in enumerate(zip(addresses,old_pins)):
        iMatch = kc_full['Address'].str.contains(r'\s*'.join(address))
        try:
            if (kc_full[iMatch]['EffYr'].values[0]<2015):
                pin = kc_full[iMatch][['Major','Minor']].values[0]
                taxpin = f'{pin[0]:06}'+f'{pin[1]:04}'
                kc_d[kc_d['TaxParcelIdentificationNumber']==old_pin]['TaxParcelIdentificationNumber'] = taxpin
        except:
            print(iMissing,address,old_pin)

# Double check City's SiteEnergy column
ce = (city_d[['SteamUse(kBtu)','Electricity(kBtu)','NaturalGas(kBtu)',
          'OtherFuelUse(kBtu)']].sum(axis=1)-city_d['SiteEnergyUse(kBtu)'])
ce = ce[np.isfinite(ce)]
print('Max Energy difference between total and sum: ',np.max(ce),' kBtu')

# Plots
plt.close('all')
plt.clf()

f1,ax1 = plt.subplots()
f1.subplots_adjust()
ax1.hist(ce,bins=100,range=[0,2e3],log=True)
f1.savefig('d_energy_city.png')


kc_d['site_eui'] = kc_d['SiteEnergyUse(kBtu)'] / kc_d['no_parking_use_sum_gfa']

combine = {'Office':[304,344,381,810,820,840,845,847],
           'K-12 School':[358,365,366,484],
           'College':[368,377],
           'Retail':[303,318,319,353,410,412,413,414,455,534,830,846,848,860],
           'Apartments':[300,321,338,352,348,459,551],
           'Assisted Living':[330,424,451,589,710],
           'Government':[327,491],
           'Grocery Stores':[340,446,458],
           'Hotel':[594,841],
           'Limited Hotel':[332,343,595,842,853],
           'Theater':[302,379,380],
           'Public Assembly':[173,306,308,311,309,323,324,337,426,482,
                              486,514,573,574],
           'Restaurant':[314,350],
           'Fitness Center':[416,418,483,485],
           'Refrig. Warehouse':[447],
           'Non-Ref Warehouse':[326,386,387,406,407,525,534,703],
           'Industrial':[392,453,470,471,487,494,495,527,528],
           'Jail':[335,489],'Alternative School':[156],
           'Convalescent Hospital':[313],'Fire Station':[322],
           'Hospital':[331],'Medical Office':[341],'Museum':[481],
           'Laboratories':[496],'Broadcast Facility':[498]}

for name,use_list in combine.items():
    kc_d.loc[np.in1d(kc_d['PredominantUse'],use_list),'main_use']=name
    kcsec_full.loc[np.in1d(kcsec_full['SectionUse'],use_list),'main_use']=name

kc_d.to_csv('Revised_2015_Seattle.csv')

# Make some plots    
f,ax = plt.subplots()
f.subplots_adjust()

# Buildings sorted by KC GFA values and then lines of the other sq. ft measures
kc_area_sort = kc_d.sort_values('BldgGrossSqFt')
ax.plot(kc_area_sort['c_use_sum_gfa'].values,label='City Sum of Use GFA')
ax.plot(kc_area_sort['PropertyGFATotal'].values,label='City Reported Total')
ax.semilogy(kc_area_sort['no_parking_use_sum_gfa'].values,label='KC No Parking Areas')
ax.semilogy(kc_area_sort['use_sum_gfa'].values,label='KC Sum of Use Areas')
ax.plot(kc_area_sort['BldgGrossSqFt'].values,label='KC Reported Total')
ax.set_xlabel('Building')
ax.set_xlim(800,3980)
ax.set_ylabel('Building Gross Floor Area [ft$^2$]')
ax.legend()

f.savefig('KC_area_compare.png')

# 4 scatter plots comparing the various GFA measures
f2,ax2 = plt.subplots(2,2,sharex=True,sharey=True)
f2.subplots_adjust(hspace=0,wspace=0,right=0.99,top=0.95)

for ix in np.arange(2):
    for iy in np.arange(2): 
        ax2[ix,iy].plot([1e4,3e6],[1e4,3e6],'k')

ax2[0,0].loglog(kc_d['BldgGrossSqFt'].values,kc_d['use_sum_gfa'].values,'.',
                label='Sum of Use Areas')
ax2[1,0].plot(kc_d['BldgGrossSqFt'].values,
              kc_d['no_parking_use_sum_gfa'].values,
              '.',label='Parking subtracted')
ax2[1,1].plot(kc_d['BldgGrossSqFt'].values,
              kc_d['PropertyGFATotal'].values,'.',
              label='Reported Total')
ax2[0,1].plot(kc_d['BldgGrossSqFt'].values,kc_d['c_use_sum_gfa'].values,'.',
              label='Sum of Use GFA')

for ix in np.arange(2):
    for iy in np.arange(2): 
        ax2[ix,iy].legend()

ax2[0,0].set_ylim(1e4,3e6)
ax2[0,0].set_xlim(1e4,3e6)
ax2[0,0].set_ylabel('Floor Area')
ax2[0,0].set_title('King County Data')
ax2[0,1].set_title('City Data')
ax2[1,0].set_xlabel('Building Gross Floor Area [ft$^2$]')

f2.savefig('Area_compare.png')

