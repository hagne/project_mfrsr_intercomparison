import pandas as pd
import numpy as np


def chunck_correlation_by_sunelevation(aroAOD_al_new, sfrAOD_al_new, sfr_sunpos_al_new, elevs, weights= 'absolute'):
    df = pd.DataFrame()
    elevs_deg = np.rad2deg(elevs)
    for i in range(len(elevs)-1):
        sfrAOD_al_new_sunpos = sfrAOD_al_new.copy()
        aroAOD_al_new_sunpos = aroAOD_al_new.copy()

        # select data of particular sun elevation
        where = np.logical_and(sfr_sunpos_al_new.data.altitude > elevs[i], sfr_sunpos_al_new.data.altitude <= elevs[i+1])

        sfrAOD_al_new_sunpos.data[~where] = np.nan
        aroAOD_al_new_sunpos.data[~where] = np.nan

        sfrAOD_al_new_sunpos.data.dropna(inplace = True)

        aroAOD_al_new_sunpos.data.dropna(inplace = True)

        # correlate
        empty = False
        try:
            corr = aroAOD_al_new_sunpos.correlate_to(sfrAOD_al_new_sunpos, weights= weights)
        except ValueError as e:
            if str(e) != 'zero-size array to reduction operation maximum which has no identity':
                raise
            else:
                empty = True
        if not empty:
            out = corr.orthogonla_distance_regression
            out = out['output']
            inters, slope = out.beta
            try:
                r = corr.pearson_r[0]
            except ValueError:
                inters, slope, r = (np.nan, np.nan, np.nan)
        else:
            inters, slope, r = (np.nan, np.nan, np.nan)

        # add to output datafram
        dft = pd.DataFrame({'m':slope,
                            'c': inters,
                            'r':r,
                            'no_pts':sfrAOD_al_new_sunpos.data.shape[0],
                            'ang_1': elevs_deg[i],
                            'ang_2': elevs_deg[i+1]},
                           index = [(elevs_deg[i] + elevs_deg[i+1])/2])

        df = df.append(dft)
        df.index.name = 'center_angle'
    return df

def chunk_correlation_by_AOD(aod1, aod2, chuncksize = 1000, weights= 'absolute'):

    df = pd.DataFrame()
    i = 1
    while i:
        #     print(i)
        tst = aod1.copy()
        #     tst.data = tst.data.iloc[tst]
        tst.data = tst.data.sort_values(tst.data.columns[0]).iloc[(i-1) * chuncksize : i * chuncksize, :]
        tst.data.sort_index(inplace = True)

        arotst = aod2.copy()
        arotst.data = arotst.data.loc[tst.data.index,:]

        corr = arotst.correlate_to(tst, weights= weights)
        out = corr.orthogonla_distance_regression['output']
        intersect, slope = out.beta
        df[i] = pd.Series([tst.data.min().min(), tst.data.max().max(), intersect, slope, out.res_var, corr.pearson_r[0], tst.data.shape[0]], index = ['aod_min','aod_max','c','m','var','r','nopt'])

        i += 1
        if tst.data.shape[0] < chuncksize:
            i = False
    df = df.transpose()
    return df

def threshold_correlation_by_AOD(aod1, aod2, chuncksize = 100, threshold = 'low', weights= 'absolute'):

    df = pd.DataFrame()
    i = 1
    while i:
    #     print(i)
        tst = aod1.copy()
    #     tst.data = tst.data.iloc[tst]
        if threshold == 'low':
            tst.data = tst.data.sort_values(tst.data.columns[0]).iloc[(i-1) * chuncksize : , :]
        elif threshold == 'high':
            tst.data = tst.data.sort_values(tst.data.columns[0]).iloc[:aod1.data.shape[0] -(i* chuncksize) , :]
        tst.data.sort_index(inplace = True)

        arotst = aod2.copy()
        arotst.data = arotst.data.loc[tst.data.index,:]


        corr = arotst.correlate_to(tst, weights= weights)
        out = corr.orthogonla_distance_regression['output']
        intersect, slope = out.beta
        df[i] = pd.Series([tst.data.min().min(), tst.data.max().max(), intersect, slope, out.res_var, corr.pearson_r[0], tst.data.shape[0]], index = ['aod_min','aod_max','c','m','var','r','nopt'])

        i += 1
        if tst.data.shape[0] < chuncksize:
            i = False
    df = df.transpose()
    return df

def chunk_wise_autocorr(aod, lag_steps, chuncksize = 1000):
    autocorr_list = []
    df = pd.DataFrame()
    i = 1
    while i:
        tst = aod.copy()
        tst.data = tst.data.sort_values(tst.data.columns[0]).iloc[(i-1) * chuncksize : i * chuncksize, :]
        tst.data.sort_index(inplace = True)

        autocorr = tst.corr_timelag(tst, dt = (lag_steps, 'm'))
        info = {}
        info['autocorr'] = autocorr
        info['aod_min'] = tst.data.min().min()
        info['aod_max'] = tst.data.max().max()
        autocorr_list.append(info)
        i += 1
        if tst.data.shape[0] < chuncksize:
            i = False
    return autocorr_list

