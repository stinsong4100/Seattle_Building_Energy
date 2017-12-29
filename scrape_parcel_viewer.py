import pandas as pd, pdb, numpy as np, os
from selenium import webdriver

orig_d = pd.read_csv('Seattle_2015_building.csv')
new_file = 'Revised_2015_Seattle.csv'
istart = 0
if os.path.isfile(new_file):
    try:
        new_tab = pd.read_csv(new_file)
        last_taxid = new_tab['TaxParcelIdentificationNumber'].values[-1]
        istart = orig_d.index[orig_d['TaxParcelIdentificationNumber']==last_taxid][0]+1
    except:  pass

#browser = webdriver.PhantomJS()
browser = webdriver.Chrome()

def read_write_one_building(t1_rows):
    # Main pandas DataFrame created using dict
    main_df = pd.DataFrame(dict([[td.text for td in 
                                  row.find_elements_by_tag_name('td')] 
                                 for row in t1_rows[:16]]),index=[taxid])

    #Sometimes, there is no Table 2  (e.g. Mercer Arena/Opera House)
    try:
        t2 = browser.find_element_by_id('kingcounty_gov_cphContent_GridViewBldgSection')

        t2_headers = [th.text for th in t2.find_elements_by_tag_name('tr')[0].find_elements_by_tag_name('th')]
        t2_data = [[td.text.replace('\n','').replace(',','') 
                    for td in row.find_elements_by_tag_name('td')] 
                   for row in t2.find_elements_by_tag_name('tr')[1:]]
        
        # Create data frame
        t2_df = pd.DataFrame(t2_data,columns=t2_headers).set_index('Section Number')
    # convert 'object' to ints
        t2_df = t2_df.apply(pd.to_numeric,errors='ignore')
    # combine common section uses
        t2_df = t2_df.groupby('Section Use').sum()
    # sort uses by gross square footage
        t2_df = t2_df.sort_values('Gross Sq Ft',ascending=False)

        for ift, sub in enumerate(t2_df.index.values):
            main_df['use_'+str(ift+1)],main_df['area_'+str(ift+1)]= \
                [sub,t2_df['Gross Sq Ft'].values[ift]]
    except:  pass

    if not os.path.isfile(new_file): 
        main_df.index.name = 'TaxParcelIdentificationNumber'
        main_df.to_csv(new_file)
    else: main_df.to_csv(new_file,header=False,mode='a')
    print(main_df)

for o_index, orig_row in orig_d[istart:].iterrows():
    taxid = f"{int(orig_row['TaxParcelIdentificationNumber']):010}"
#taxid='0659000475'
    print(orig_row['PropertyName'])

    browser.get('http://blue.kingcounty.com/Assessor/eRealProperty/Detail.aspx?ParcelNbr='+taxid)    
    table_1 = browser.find_element_by_id('kingcounty_gov_cphContent_DetailsViewCommBldg')
    table_1_rows = table_1.find_elements_by_tag_name('tr')
    read_write_one_building(table_1_rows)

# Handle multiple buildings
    if len(table_1_rows)>16: 
        other_links = [a.get_property('href') for a in table_1_rows[-1].find_elements_by_tag_name('a')]
        for link in other_links:
            browser.execute_script(link.replace('javascript:',''))
            table_1 = browser.find_element_by_id('kingcounty_gov_cphContent_DetailsViewCommBldg')
            table_1_rows = table_1.find_elements_by_tag_name('tr')
            read_write_one_building(table_1_rows)
    

    print(orig_row[[ 'PropertyName',
                     'LargestPropertyUseType',
                     'LargestPropertyUseTypeGFA',
                     'SecondLargestPropertyUseType',
                     'SecondLargestPropertyUseTypeGFA',
                     'ThirdLargestPropertyUseType',
                     'ThirdLargestPropertyUseTypeGFA']])


