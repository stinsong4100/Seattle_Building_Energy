import bpd_api_python_lib as bpd, numpy as np, pickle

years=np.arange(2015.0,2008.0,-1.0)
fields = ['year_built','site_eui','source_eui','fuel_eui','electric_eui','energy_star_rating']
facility_types = ['Commercial - Other', 'Commercial - Uncategorized', 
       'Education - College or university', 'Education - Other classroom',
       'Education - Preschool or daycare',
       'Food Service - Restaurant or cafeteria',
       'Food Service - Uncategorized', 'Grocery store or food market',
       'Health Care - Inpatient', 'Health Care - Outpatient Uncategorized',
       'Health Care - Uncategorized', 'Industrial', 'Laboratory',
       'Lodging - Dormitory or fraternity/sorority', 'Lodging - Hotel',
       'Lodging - Other', 'Mixed Use - Commercial and Residential',
       'Mixed Use - Predominantly Residential',
       'Multifamily - Uncategorized', 'Nursing Home',
       'Office - Bank or other financial',
       'Office - Medical non diagnostic', 'Office - Uncategorized',
       'Parking Garage', 'Public Assembly - Large Hall',
       'Public Assembly - Library', 'Public Assembly - Other',
       'Public Assembly - Recreation', 'Public Safety - Courthouse',
       'Religious worship', 'Retail - Enclosed mall',
       'Retail - Uncategorized', 'Retail - Vehicle dealership/showroom',
       'Service - Vehicle service/repair shop',
       'Warehouse - Distribution or Shipping center',
       'Warehouse - Non-refrigerated', 'Warehouse - Refrigerated',
       'Warehouse - Self-storage', 'Warehouse - Uncategorized']
                  #'Data Center',
building_classes = ['Commercial','Residential','Unknown']

d = {}
for year in years:
    d[year]={}
    for ft in facility_types:
        d[year][ft]={}
        for field in fields:
            try:
                d[year][ft][field]= \
                    np.array(bpd.scatterplot(filters={'city':['Seattle'],
                                                      'facility_type':[ft],
                                                      'site_year':{'min':year,'max':year+0.999}},
                                             xaxis='floor_area',
                                             yaxis=field)['scatterplot']).transpose()
                try:
                    print("year: %f type: %s field: %s  count: %i"%(year, ft, field,len(d[year][ft][field][0])))
                except IndexError: pass
            except KeyError:  pass

with open('bpd.pck','wb') as f:
    pickle.dump(d,f)
