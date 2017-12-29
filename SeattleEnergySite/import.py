import django, pandas as pd, pdb, numpy as np

from plots.models import Building, ASHRAE_target

kc_d = pd.read_csv('../Revised_2015_Seattle.csv')

keep = (np.isfinite(kc_d['SiteEnergyUse(kBtu)']) &
        np.isfinite(kc_d['Electricity(kWh)']) &
        np.isfinite(kc_d['Electricity(kBtu)']) &
        np.isfinite(kc_d['NaturalGas(kBtu)']) &
        np.isfinite(kc_d['SteamUse(kBtu)']) &
        np.isfinite(kc_d['site_eui']) &
        np.isfinite(kc_d['no_parking_use_sum_gfa']) )

kc_d = kc_d[keep]

for bdg in kc_d.iterrows():
    if (bdg[1]['Elevators']=='Yes'): elev=True
    else: elev = False
    building = Building(
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
        No_parking_gfa = float(bdg[1]['no_parking_use_sum_gfa']),
        Property_Name = bdg[1]['PropertyName'],
        Site_Energy_kbtu = float(bdg[1]['SiteEnergyUse(kBtu)']),
        Electricity_kwh = float(bdg[1]['Electricity(kWh)']),
        Electricity_kbtu = float(bdg[1]['Electricity(kBtu)']),
        Natural_Gas_kbtu = float(bdg[1]['NaturalGas(kBtu)']),
        Steam_kbtu = float(bdg[1]['SteamUse(kBtu)']),
        site_eui = float(bdg[1]['site_eui'])
        )
    building.save()

ashrae_eui = {'Office':40,'K-12 School':40,'College':65,'Retail':52,
           'Apartments':30,'Assisted Living':84,'Government':50,
           'Grocery Stores':131,'Hotel':52,'Limited Hotel':52,
           'Theater':23,'Public Assembly':28,'Restaurant':156,
           'Fitness Center':26,'Refrig. Warehouse':69,'Non-Ref Warehouse':20,
           'Industrial':50,'Jail':66,'Alternative School':40,
           'Convalescent Hospital':135,'Fire Station':66,
           'Hospital':135,'Medical Office':34,'Museum':23,
           'Laboratories':179,'Broadcast Facility':70}

for use in ashrae_eui.keys():
    target = ASHRAE_target(main_use = use, target = ashrae_eui[use])
    target.save()
