import django, pandas as pd, pdb, numpy as np

from plots.models import Building, ASHRAE_target, Lookup, Ecotope_target

years=['2015','2016']
for year in years:
    kc_d = pd.read_csv('../Revised_'+year+'_Seattle.csv')

    keep = (np.isfinite(kc_d['SiteEnergyUse(kBtu)']) &
            np.isfinite(kc_d['Electricity(kWh)']) &
            np.isfinite(kc_d['Electricity(kBtu)']) &
            np.isfinite(kc_d['NaturalGas(kBtu)']) &
            np.isfinite(kc_d['SteamUse(kBtu)']) &
            np.isfinite(kc_d['site_eui']) &
            np.isfinite(kc_d['no_parking_gfa']) )
    
    kc_d = kc_d[keep]

    buildings = []
    for bdg in kc_d.iterrows():
        if (bdg[1]['Elevators']=='Yes'): elev=True
        else: elev = False
        building = Building(
            year = int(year),
            Major = int(bdg[1]['Major']),
            Minor = int(bdg[1]['Minor']),
            BldgNbr = int(bdg[1]['BldgNbr']),
            Address = bdg[1]['Address'],
            main_use = bdg[1]['main_use'],
            Number_of_Stories = int(bdg[1]['NbrStories']),
            Construction_Class = int(bdg[1]['ConstrClass']),
            Year_built = int(bdg[1]['YrBuilt']),
            Year_remodeled = int(bdg[1]['EffYr']),
            Heating_System = int(bdg[1]['HeatingSystem']),
            Elevators = elev,
            Tax_PIN = int(bdg[1]['TaxParcelIdentificationNumber']),
            No_parking_gfa = float(bdg[1]['no_parking_gfa']),
            Property_Name = bdg[1]['PropertyName'],
            lat = float(bdg[1]['Latitude']),
            longitude = float(bdg[1]['Longitude']),
            Site_Energy_kbtu = float(bdg[1]['SiteEnergyUse(kBtu)']),
            Electricity_kwh = float(bdg[1]['Electricity(kWh)']),
            Electricity_kbtu = float(bdg[1]['Electricity(kBtu)']),
            Natural_Gas_kbtu = float(bdg[1]['NaturalGas(kBtu)']),
            Steam_kbtu = float(bdg[1]['SteamUse(kBtu)']),
            site_eui = float(bdg[1]['site_eui'])
            )
        buildings.append(building)

    Building.objects.bulk_create(buildings)

ashrae_eui = {'Office':40,'K-12 School':40,'College':65,'Retail':52,
              'Multifamily Housing':30,'Assisted Living':84,'Government':50,
              'Grocery Stores':131,'Hotel':52,'Limited Hotel':52,
              'Theater':23,'Public Assembly':28,'Restaurant':156,
              'Fitness Center':26,'Refrig. Warehouse':69,'NR Warehouse':20,
              'Industrial':50,'Jail':66,'Alternative School':40,
              'Convalescent Hospital':135,'Fire Station':66,'Data Center':400,
              'Hospital':135,'Medical Office':34,'Museum':23,
              'Laboratories':179,'Broadcast Facility':70,'Parking':10}

targets=[]
for use in ashrae_eui.keys():
    target = ASHRAE_target(main_use = use, target = ashrae_eui[use])
    targets.append(target)

ASHRAE_target.objects.bulk_create(targets)

ecotope_eui = {'Office':46.4,'K-12 School':29.3,'College':83.4,'Retail':38.9,
              'Multifamily Housing':20,'Government':46.4,
              'Grocery Stores':115.3,'Hotel':61.4,'Restaurant':233.7,
              'NR Warehouse':24.3,
              'Hospital':123}

targets=[]
for use in ecotope_eui.keys():
    target = Ecotope_target(main_use = use, target = ecotope_eui[use])
    targets.append(target)

Ecotope_target.objects.bulk_create(targets)

Heating_System = {
1 :'Electric',10:'Wall furnace',11:'Package Unit',12:'Warmed and Cooled Air',
13:'Hot & Cooled Water',14:'Heat Pump',15:'Floor Furnace',
16:'Thru-wall Heat PUmp',17:'Complete HVAC',18:'Evaporative Cooling',
19:'Refrigerated Cooling',2 :'Electric Wall',20:'None',
26:'Control Atmos, Cond. Air',27:'Control Atmos., Warm/Cooled',
3 :'Forced Air Unit',4 :'Hot Water',5 :'Hot Water-Radiant',6 :'Space Heaters',
7 :'Steam',8 :'Steam w/o Boiler',9 :'Ventilation'
}

entries=[]
for code in Heating_System.keys():
    entry = Lookup(case='Heating_System',code=code,value=Heating_System[code])
    entries.append(entry)

Building_Quality = {
    2:'Low Cost',3:'Low/Average',4:'Average',5:'Average/Good',6:'Good',
    7:'Good/Excellent',8:'Excellent'
    }
for code in Building_Quality.keys():
    entry = Lookup(case='Building_Quality',code=code,value=Building_Quality[code])
    entries.append(entry)

Construction_Class = {
    1:'Structural Steel',2:'Reinforced Concrete',3:'Masonry',4:'Wood Frame',
    5:'Prefab Steel'
    }
for code in Construction_Class.keys():
    entry = Lookup(case='Construction_Class',code=code,value=Construction_Class[code])
    entries.append(entry)

Shape = {
    1:'Approx Square',2:'Rect or Slight Irreg',3:'Long Rect or Irreg',
    4:'Very Irreg'
    }
for code in Shape.keys():
    entry = Lookup(case='Shape',code=code,value=Shape[code])
    entries.append(entry)

Lookup.objects.bulk_create(entries)
