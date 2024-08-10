# -*- coding: utf-8 -*-
"""
@website: https://k2analytics.co.in
@blog: https://k2analytics.co.in/blog
@email: info@k2analytics.co.in
"""

import pandas as pd
import numpy as np


def woe(df, target,var,bins = 10,fill_na = True):
    df = df.copy()


    if(df[var].dtype.kind in 'biufc'):
        #qtiles = list(np.linspace(0,1,bins+1))[1:]
        #uq_cut_points = list(np.unique(np.quantile(df[var]  , qtiles)))
        #print("for variable  {} uq_cut_points".format(i), len(uq_cut_points))
        
        if len(np.unique(df[var])) < bins:
            df['decile']=df[var] ### Variable Value itself 
        else:                    
            df['decile']=pd.qcut(df[var].rank(), bins, labels=False, duplicates='drop') ### Rank 
        if (fill_na== True):
            df['decile'] = df['decile'].fillna(value="Missing")
        Rank=df.groupby('decile').apply(lambda x: pd.Series([
            np.sum(x[target]),
            np.size(x[target][x[target]==0]),
            ],
            index=(["cnt_resp","cnt_non_resp"])
            )).reset_index()


    else:
        if (fill_na== True):
            df[var] = df[var].fillna(value="Missing")
        Rank=df.groupby(var).apply(lambda x: pd.Series([
            np.sum(x[target]),
            np.size(x[target][x[target]==0]),
            ],
            index=(["cnt_resp","cnt_non_resp"])
            )).reset_index()

    Rank["pct_resp"]=Rank["cnt_resp"]/np.sum(Rank["cnt_resp"])
    Rank["pct_non_resp"]=Rank["cnt_non_resp"]/np.sum(Rank["cnt_non_resp"])

    np.seterr(divide = 'ignore') 
    Rank["WOE"] = np.where(Rank["pct_resp"] != 0, 
        np.log(Rank["pct_resp"] / Rank["pct_non_resp"]),0)
    np.seterr(divide = 'warn') 

    return(Rank)
    


def iv(df, target,bins = 10, fill_na = True, rm_cols =[], woe_table=False):
    df = df.copy()
    
    col_names = df.dtypes.index
    
    col_names = col_names.delete(df.columns.get_loc(target)) 
    
    for i in rm_cols:
        col_names = col_names.delete(df.columns.get_loc(i)) 
    
    woe_dfs = {}
    
    skipped_vars={}
    
    iv_df = pd.DataFrame()
    
    for i in col_names:
        print(f"Variable being processed is {i}")
        missing_perc = (df[i].isna().sum()/df.shape[0])*100
        if(missing_perc >=50):
            missing_dict={i:missing_perc}
            skipped_vars.update(missing_dict)
            pass
        else:
            if(df[i].dtype.kind in 'biufc') :
                #qtiles = list(np.linspace(0,1,bins+1))[1:]
                #uq_cut_points = list(np.unique(np.quantile(df[i]  , qtiles)))
                #print("for variable  {} uq_cut_points".format(i), len(uq_cut_points))
                
                if len(np.unique(df[i])) < bins:
                    df['decile']=df[i] ### Variable Value itself 
                else:                    
                    df['decile']=pd.qcut(df[i].rank(), bins, labels=False, duplicates='drop') ### Rank 
                if (fill_na== True):
                    df['decile'] = df['decile'].fillna(value="Missing")
                Rank=df.groupby('decile').apply(lambda x: pd.Series([
                    np.min(x[i]),
                    np.max(x[i]),
                    np.mean(x[i]),
                    np.sum(x[target]),
                    np.size(x[target][x[target]==0]),
                    ],
                    index=(["Min_Value","Max_Value","Mean_Value","cnt_resp","cnt_non_resp"])
                    )).reset_index()
            else:
                if (fill_na== True):
                    df[i] = df[i].fillna(value="Missing")
                Rank=df.groupby(i).apply(lambda x: pd.Series([
                    np.sum(x[target]),
                    np.size(x[target][x[target]==0]),
                    ],
                    index=(["cnt_resp","cnt_non_resp"])
                    )).reset_index()    
            Rank["pct_resp"]=Rank["cnt_resp"]/np.sum(Rank["cnt_resp"])
            Rank["pct_non_resp"]=Rank["cnt_non_resp"]/np.sum(Rank["cnt_non_resp"])
            Rank["resp_minus_non_resp"] = Rank["pct_resp"] - Rank["pct_non_resp"]
            np.seterr(divide = 'ignore') 
            Rank["WOE"] = np.where(Rank["pct_resp"] != 0, 
                np.log(Rank["pct_resp"] / Rank["pct_non_resp"]),0)
            np.seterr(divide = 'warn') 
            Rank["IV"] = Rank["resp_minus_non_resp"] * Rank["WOE"]
            iv_df_1 = pd.DataFrame({'Var':[i], "IV":[Rank["IV"].sum()]})
            iv_df = pd.concat([iv_df, iv_df_1], ignore_index=True)
            
            del Rank["resp_minus_non_resp"]
            if(df[i].dtype.kind in 'biufc'):
                Rank["Range"] = Rank['Min_Value'].astype('str')+"-"+Rank['Max_Value'].astype('str')
                del Rank["decile"]
                del Rank["Min_Value"]
                del Rank["Max_Value"]
                Rank=Rank[Rank.columns.reindex(['Range' , 'Mean_Value', 'cnt_resp', 
                                                'cnt_non_resp', 'pct_resp', 
                                                'pct_non_resp',
                                                'WOE', 'IV'])[0]]
            woe_dfs[i]=pd.DataFrame(Rank)

    iv_df = iv_df.sort_values('IV', ascending=False).reset_index(drop = True)
    if(woe_table == True):
        return(iv_df,skipped_vars,woe_dfs)
    else:
        return(iv_df,skipped_vars)



