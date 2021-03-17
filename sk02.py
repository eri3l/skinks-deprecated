import pandas as pd
import itertools
import numpy as np
import streamlit as st
from itertools import chain
import os
from PIL import Image

st.title("Skinks Search Tool")
#--- 1. Load data
def load_file(filename):
    #df = pd.read_csv(filename)
    # pd.eval() to read columns their corresponding dtype (only for str-list), instead of getting converted by by read_csv()
    df = pd.read_csv(filename, converters={'Trap': eval})
    return df 

df = load_file("skinks_clean05.csv")
# fix dtypes
# TODO: add assertions
df['Sex'] = df['Sex'].astype(str)

#--- 2. Make button lists
def create_button_lists():
    
    cols_to_drop = ['ID', 'Recap', 'Year'] # , 'projected_SVL', 'Toes' ]
    cols = df.drop(cols_to_drop, axis=1) #shouldn't this be a list?
    cols_list = list(cols.columns.values)
    
    col_criteria = []
    
    for col in cols: 
        if col == "Trap":
            col_crit = np.unique([*itertools.chain.from_iterable(df.Trap)])
        elif col == "Sex":
            col_crit = np.unique([*itertools.chain.from_iterable(df.Sex)]) 
        else:
            col_crit = df[col].unique()
        col_criteria.append(col_crit)
        
    criteria_dict = dict(zip(cols_list, col_criteria))
    for  k,v in criteria_dict.items():
        v = v.sort()

    return criteria_dict

criteria_dict = create_button_lists()
        
#--- 3. Get user choice
def get_user_choice(criteria_dict):

    categorical_keys = ['Trap', 'Sex', 'Toes_bool'] #'Easting', 'Northing', 'Sex', 'Capture', 'Missing toes', 'Tail_tipped', 'DNA']
    continuous_keys = ['Weight', 'SVL', 'VTL', 'Regen']
    
    dict_cat = {x:criteria_dict[x] for x in categorical_keys}
    dict_cont = {x:criteria_dict[x] for x in continuous_keys}
    
    
    #------3.1. make st buttons

    st.sidebar.title("Select search criteria")
    #st.sidebar.write("Caution with @trap - top option is an empty string!")
    choice_cat = []
    for k, v in dict_cat.items():
        add_selectbox = st.sidebar.selectbox(k, v)
        choice_cat.append(add_selectbox)
     
    choice_cont = []
    for k, v in dict_cont.items():
        
        v_min, v_max = min(v), max(v)
        v_min,  v_max = float(v_min), float(v_max)  # known bug in Streamlit, github issue #1065
        
        if k == "Weight":
            add_slider = st.sidebar.slider("%s in grams" %k, v_min, v_max,
                                           (v_min, v_max), 0.5)
                                              #(v_max/4, v_max*3/4), 1.0)
        elif k == "SVL":
            # FIXME:
            add_slider = st.sidebar.slider("SVL in mm", 0, 100, 50)                        
        else:
            add_slider = st.sidebar.slider("%s in mm" %k, v_min, v_max,
                                             # (v_max/4, v_max*3/4), 0.5)    # (v_max/4, v_max*3/4) is where to init the slider
                                             (v_min, v_max), 0.5)
        choice_cont.append(add_slider) 

    return choice_cat, choice_cont, dict_cat, dict_cont

choice_cat, choice_cont, dict_cat, dict_cont, = get_user_choice(criteria_dict)
# "You selected **categorical vals**: ", choice_cat
# "You also selected **continuous vals**: ", choice_cont

#--- 4. Search
def search(choice_cat, choice_cont, dict_cat, dict_cont):
    # make choice dict
    choice_values = choice_cat + choice_cont
    
    choice_keys_cat = []
    for k in dict_cat:
        choice_keys_cat.append(k)
        
    choice_keys_cont = []
    for k in dict_cont:
        choice_keys_cont.append(k)
    choice_keys = choice_keys_cat + choice_keys_cont
        
    dict_choice = dict(zip(choice_keys, choice_values))
    
    #--- Search
      
    # FIXME: simple hack for now
     
    # FIXME hack force to list for isin()
    for k,v in dict_choice.items():
        if not type(dict_choice[k]) == (tuple) :
            if dict_choice[k] == "SVL":
                break
            else:
                print("Converting to list -----")
                dict_choice[k] = [dict_choice[k]]
                print(dict_choice[k])
    
    # FIXME:
    dict_choice['SVL'] = dict_choice['SVL'][0]
    #----- SVL search prep
    delta = 10
    current_year = 2021
    df['projected_SVL'] = df['SVL'] + delta*(current_year - df['Year'])
    df.loc[df['projected_SVL']>=70.0, 'projected_SVL'] = 100.0
    
    if dict_choice['SVL'] >= 70:     #FIXME later: it's in a list from above hack
        dict_choice['SVL'] = 100
    
    # ---- TODO: Trap lists
    #st.write(*trap_choice)         # * unpacks a list
    #st.write(list(chain.from_iterable(trap_choice)))    # unpacking nested list
    #df.Trap.apply(lambda x: bool(set(x).intersection(list(chain.from_iterable(trap_choice)))))
    #
    # if single trap selected, set multichoice trap to None

    
    newdf = df.loc[df.Trap.map(set(dict_choice['Trap']).issubset) &
                       #( df['Sex'].isin(dict_choice['Sex']) ) &
                       ( df['Toes_bool'].isin(dict_choice['Toes_bool']) ) &
                       #( (df['Weight'] >= dict_choice['Weight'][0]) & (df['Weight'] <= dict_choice['Weight'][1])) &
                       #( (df['VTL'] >= dict_choice['VTL'][0]) & (df['VTL'] <= dict_choice['VTL'][1]) ) &
                       ((df['projected_SVL'] >= dict_choice['SVL']-5) & (df['projected_SVL'] <= dict_choice['SVL']+5) ) #&
                       #( (df['Regen'] >= dict_choice['Regen'][0]) & (df['Regen'] <= dict_choice['Regen'][1]) )
                       ]

    
    return newdf

newdf = search(choice_cat, choice_cont, dict_cat, dict_cont)

st.markdown("### **RESULTS:**")
st.success("Search complete.")
st.table(newdf)

def display_images(newdf):
    #  
    # for index, row in newdf.iterrows():
    #         st.write(row['ID'])
    #         image = os.path.join("data/images/", row['ID']+".JPG")
    #         st.image(image, caption="This is Skink: "+row['ID']+"\n SVL is: "+str(row['SVL']), use_column_width = True)
    
    options = []
    for index, row in newdf.iterrows():
        options.append(row['ID'])
    
    #temp = st.multiselect("Select skink ID to look up images", options)
    temp = st.selectbox("Select skink ID to look up images", options)
    temp = str(temp)
    st.markdown("---")
    
    # get the df details for the skink ID
    this_skink = df.loc[df['ID'] == temp]
    # st.markdown("<font color=blue>THIS TEXT WILL BE RED</font>", unsafe_allow_html=True)
    st.write("**Details for %s:**" % (temp))
    st.table(this_skink)
    
    imgs = []
    path = 'data/images/Chesterfield/'+str(temp)
    try:
        for f in os.listdir(path):              # 'data/images/Chesterfield/BB01'
            imgs.append(Image.open(os.path.join(path,f)))
    except:
        st.write("Sorry, no images found for: ", temp)
    
    # col1, col2 = st.beta_columns(2)
    # with col1:
    #     st.image([imgs[0], imgs[2]], use_column_width = True)
    # with col2:
    #     st.image([imgs[1], imgs[3]], use_column_width = True)
    st.image(imgs, use_column_width=True)   # width = None

    return imgs

imgs = display_images(newdf)


#if __name__ == "__main__":
#    main()



