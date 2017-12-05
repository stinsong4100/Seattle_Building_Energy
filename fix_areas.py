import pandas as pd, pdb, numpy as np, os
import urllib.request as urlreq
from bs4 import BeautifulSoup

orig_d = pd.read_csv('Seattle_2015_building.csv')
new_file = 'Revised_2015_Seattle.csv'
istart = 0
if os.path.isfile(new_file):
    try:
        new_tab = pd.read_csv(new_file)
        istart = len(new_tab)
    except:  pass

orig_d = orig_d[:3]

for o_index, orig_row in orig_d[istart:].iterrows():
    taxid = f"{int(orig_row['TaxParcelIdentificationNumber']):010}"
    
    print(orig_row['PropertyName'])
    
    parcel_html = urlreq.urlopen('http://blue.kingcounty.com/Assessor/eRealProperty/Detail.aspx?ParcelNbr='+taxid)
    soup = BeautifulSoup(parcel_html,'html.parser')
    
    table_1 = soup.find('table',{'id':'kingcounty_gov_cphContent_DetailsViewCommBldg'})
    
    multiple_buildings = False
    try:
        # pandas Series created using dict
        series = pd.DataFrame(dict([[td.getText() for td in row.findAll('td')]
                                 for row in table_1.findAll('tr')]))
    except ValueError:
        series = pd.DataFrame(dict([[td.getText() for td in row.findAll('td')]
                                 for row in table_1.findAll('tr')[:16]]))
        multiple_buildings = True

    table_2 = soup.find('table',{'id':'kingcounty_gov_cphContent_GridViewBldgSection'})

    try:
        t2_headers = [th.getText() for th in table_2.find('tr').findAll('th')]
        t2_data = [[td.getText().replace('\n','').replace(',','') for td in row.findAll('td')] 
                   for row in table_2.findAll('tr')[1:]]
        
        # Create data frame
        t2_df = pd.DataFrame(t2_data,columns=t2_headers).set_index('Section Number')
        if multiple_buildings:
            print('MORE THAN ONE BUILDING')
            lr = pd.Series(dict([[td.getText() for td in row.findAll('td')]
                                     for row in table_1.findAll('tr')[-1:]]))
            
        
        # convert 'object' to ints
        t2_df = t2_df.apply(pd.to_numeric,errors='ignore')
        # combine common section uses
        t2_df = t2_df.groupby('Section Use').sum()
        # sort uses by gross square footage
        t2_df = t2_df.sort_values('Gross Sq Ft',ascending=False)

        series = series.append(t2_df.index.values,t2_df['Gross Sq Ft'].values])
    except:  pass
    series.name=taxid

    print(orig_row[[ 'PropertyName',
                     'LargestPropertyUseType',
                     'LargestPropertyUseTypeGFA',
                     'SecondLargestPropertyUseType',
                     'SecondLargestPropertyUseTypeGFA',
                     'ThirdLargestPropertyUseType',
                     'ThirdLargestPropertyUseTypeGFA']])
    print(t2_df['Gross Sq Ft'])
    
    pd.DataFrame(series).T.to_csv(new_file,header=False)

