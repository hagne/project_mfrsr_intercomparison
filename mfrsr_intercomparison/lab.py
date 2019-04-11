import pandas as pd


def chunk_correlation_by_AOD(aod1, aod2, chuncksize = 1000):

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

        corr = arotst.correlate_to(tst)
        out = corr.orthogonla_distance_regression['output']
        intersect, slope = out.beta
        df[i] = pd.Series([tst.data.min().min(), tst.data.max().max(), intersect, slope, out.res_var, corr.pearson_r[0], tst.data.shape[0]], index = ['aod_min','aod_max','c','m','var','r','nopt'])

        i += 1
        if tst.data.shape[0] < chuncksize:
            i = False
    df = df.transpose()
    return df

def threshold_correlation_by_AOD(aod1, aod2, chuncksize = 100, threshold = 'low'):

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


        corr = arotst.correlate_to(tst)
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
    #     print(i)
        tst = aod.copy()
    #     tst.data = tst.data.iloc[tst]
        tst.data = tst.data.sort_values(tst.data.columns[0]).iloc[(i-1) * chuncksize : i * chuncksize, :]
        tst.data.sort_index(inplace = True)

#         arotst = aod2.copy()
#         arotst.data = arotst.data.loc[tst.data.index,:]

        autocorr = tst.corr_timelag(tst, dt = (lag_steps, 'm'))
#         corr = arotst.correlate_to(tst)
#         out = corr.orthogonla_distance_regression['output']
#         intersect, slope = out.beta
#         df[i] = pd.Series([tst.data.min().min(), tst.data.max()max(), intersect, slope, out.res_var, corr.pearson_r[0], tst.data.shape[0]], index = ['aod_min','aod_max','c','m','var','r','nopt'])
        info = {}
        info['autocorr'] = autocorr
        info['aod_min'] = tst.data.min().min()
        info['aod_max'] = tst.data.max().max()
        autocorr_list.append(info)
        i += 1
        if tst.data.shape[0] < chuncksize:
            i = False
    return autocorr_list