
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
from matplotlib import colors as mcolor
import scipy as sp
from io import StringIO
import plt_tools

colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

fkt = lambda x, m, c: x * m + c


def refine_data(lan, fit=True):
    date = lan['timedate_raw']
    date = pd.to_datetime(''.join(date.split()[:3]))
    lan['date'] = date

    ###
    data = lan['data_raw']
    databf = StringIO(''.join(data))

    df = pd.read_csv(databf, delim_whitespace=True,
                     names=['time', 'V', 'AMF', 'AOD'],
                     )
    df.index = df.time.apply(lambda x: pd.to_datetime('{:04d}{:02d}{:02d} {:04d}'.format(date.year, date.month, date.day, x)))
    lan['thedata'] = df


    if fit:
        res = sp.stats.linregress(df.AMF, np.log10(df.V))

        new_AMF = np.linspace(-0.5, 6, 10)
        fit_v = fkt(new_AMF, res.slope, res.intercept)
        df_fit = pd.DataFrame({'fitres': 10 ** fit_v}, index=new_AMF)

        lan['fitres'] = df_fit
        lan['slope'] = res.slope
        lan['intercept'] = res.intercept
    return lan


# lan = all_langley_1625[0]


def read_file(fname):
    with open(fname) as rein:
        lines = rein.readlines()

    date = lines.pop(0)

    langleys = []
    while len(lines) > 0:
        wl = int(date.split()[-2])
        out = {}
        data = []
        while 1:
            line = lines.pop(0)
            if 'slope' in line:
                break
            else:
                data.append(line)
        out['data_raw'] = data
        out['timedate_raw'] = date
        out['wavelength'] = wl
        langleys.append(out)
        slope = line

        line = lines.pop(0)
        while len(line.split()) < 4:
            try:
                line = lines.pop(0)
            except IndexError:
                break
        date = line
    return langleys


def process(fname, fit=True):
    langleys = read_file(fname)
    for lan in langleys:
        refine_data(lan, fit=fit)
    tl = type('tl', (), {})
    tl.langleys = langleys
    return tl


def getthebest(lan, no=5):
    langleys = lan.copy()
    max_lan = no
    while len(langleys) > max_lan:
        mean = np.mean([lan['intercept'] for lan in langleys])
        popthis = np.argmax([np.abs(lan['intercept'] - mean) for lan in langleys])
        lan = langleys.pop(popthis)
    return langleys


def plot_wl(langley_sel, steps=2, ax=None, text='wl', vlineat0=True):
    if isinstance(ax, type(None)):
        f, a = plt.subplots()
    else:
        a = ax

    for e, lan in enumerate(langley_sel[::steps]):
        color = colors[e]

        df = lan['thedata']
        df_fitres = lan['fitres']

        a.plot(df.AMF, df.V, color=color, ls='', marker='.')
        g = a.get_lines()[-1]
        g.set_markersize(2)
        #     a.plot(new_AMF, 10**fit_v, color = color)
        df_fitres.plot(ax=a)
        g = a.get_lines()[-1]
        g.set_color(color)
        g.set_linewidth(1)
        a.set_xlim(left=0)
        a.set_yscale('log')
        a.set_ylabel('Voltage (mV)')
        a.set_xlabel('Air mass factor')
    #     break
    a.set_xlim(left=-0.7, right=6.2)
    if vlineat0:
        a.axvline(color='black', linewidth=0.5, linestyle='--')
    leg = a.legend()
    leg.remove()

    if not isinstance(text, type(None)):
        if text == 'wl':
            txt = '{} nm'.format(lan['wavelength'])
        else:
            txt = text

        a.text(0.8, 0.8, txt, transform=a.transAxes)
    return a


def plot_intercept_hist(langs, ax=None, bins=10):
    if isinstance(ax, type(None)):
        f, a = plt.subplots()
    else:
        a = ax
    intersepts = 10 ** np.array([lan['intercept'] for lan in langs])
    out = a.hist(intersepts, bins=bins, orientation='horizontal')
    a.set_yscale('log')
    a.set_xlim(tuple(reversed(a.get_xlim())))
    return a


def plot_langley_gree_ir(langleys):
    f, (aa, ab) = plt.subplots(2, 2,
                               #                          sharey=True,
                               #                          sharex=True,
                               gridspec_kw={'hspace': 0,
                                            'wspace': 0,
                                            'width_ratios': [1, 3]})
    a_500ic, a_500 = aa

    a_1600ic, a_1600 = ab

    langley_sel = [out for out in langleys if 490 < out['wavelength'] < 510]
    plot_intercept_hist(langley_sel, ax=a_500ic, bins=8)
    langley_sel = getthebest(langley_sel, no=10)
    plot_wl(langley_sel, steps=1, ax=a_500, text='500 nm',
            #         vlineat0=False
            )

    langley_sel = [out for out in langleys if 1600 < out['wavelength'] < 1650]
    plot_intercept_hist(langley_sel, ax=a_1600ic, bins=15)
    langley_sel_best = getthebest(langley_sel, no=10)
    plot_wl(langley_sel_best, steps=1, ax=a_1600, text='1625 nm',
            #         vlineat0=False
            )

    # for at in aa:
    #     lable = at.get_ylabel()
    #     at.set_ylabel('')

    # for at in (a_500ic)

    plt_tools.axes.labels.set_shared_label((a_500ic, a_1600ic), 'Voltage (mV)', axis='y')

    a_1600.yaxis.set_major_locator(plt.LogLocator(base=10.0, subs=(1.0,), numdecs=2, numticks=4))

    a_500ic.set_ylim(a_500.get_ylim())
    a_1600ic.set_ylim(a_1600.get_ylim())
    a_500.set_xlim(left=0)
    a_1600.set_xlim(left=0)

    for at in (a_500, a_1600):
        at.spines['left'].set_visible(False)
        at.tick_params(axis='y',  # changes apply to the x-axis
                       which='both',  # both major and minor ticks are affected
                       right=False,  # ticks along the bottom edge are off
                       left=False,  # ticks along the top edge are off
                       labelleft=False
                       )
        at.set_ylabel('')

    for at in (a_500ic, a_1600ic):
        at.spines['right'].set_visible(False)
        at.tick_params(axis='x',  # changes apply to the x-axis
                       which='both',  # both major and minor ticks are affected
                       bottom=False,  # ticks along the bottom edge are off
                       #                     left=False,         # ticks along the top edge are off
                       labelbottom=False
                       )
    return aa, ab

def plot_langleys_superimposed(all_langley_wl, potrange = (350,550)):
    # all_langley_wl = all_langley_1625
    potrange = np.log10(potrange)

    all_langley_wl = all_langley_wl.rename(columns={'data':'thedata'} )

    for e,(i, lan) in enumerate(all_langley_wl.iterrows()):
    #     break
    #
        pot = lan.thedata.V
        # potrange = (350, 550)

        pot = np.log10(pot)


        amf = lan.thedata.AMF
        hist2d, amfint, potint = np.histogram2d(amf, pot, bins = 80, range = ((2,5),potrange))

        if e == 0:
            hist2dall = hist2d.copy()
        else:
            hist2dall += hist2d.copy()
    #     break



    a = plt.subplot()
    pc = a.pcolormesh(amfint[:-1], 10**(potint[:-1]), hist2dall.transpose())
    pc.set_norm(mcolor.LogNorm())
    pc.set_cmap(plt.cm.gnuplot2)

    a.set_yscale('log')
    a.set_title('All Langleys @ {}nm'.format(all_langley_wl.columns.name))
    a.set_ylabel('Voltage (mV)')
    a.set_xlabel('Air mass factor')
    return a

def plot_voltage_hist(list_of_all_langley, nobins = 40, potrange=(150, 1200)):
    hists = []
    for all_langley in list_of_all_langley:
        histall, vedg = get_hist_from_all(all_langley,  potrange=potrange, nobins= nobins)
        histdict = dict(hist = histall, wl = all_langley.columns.name)
        hists.append(histdict)
    #     histall_1600, vedg = get_hist_from_all(all_langley_1625,  potrange=potrange, nobins= nobins)
    #     histall_500, vedg = get_hist_from_all(all_langley_500,  potrange=potrange, nobins = nobins)

    a = plt.subplot()
    alpha = 0.7
    for histdict in hists:
        bars = a.bar(vedg[:-1], histdict['hist'], width = (potrange[1] - potrange[0]) / (nobins-1) , align = 'edge', alpha  = alpha,
                     label = '{}'.format(histdict['wl']))

    # bars = a.bar(vedg[:-1], histall_500, width = (potrange[1] - potrange[0]) / (nobins-1) , align = 'edge', alpha  = alpha, label = '500')
    # bars = a.bar(vedg[:-1], histall_1600, width = (potrange[1] - potrange[0]) / (nobins-1) , align = 'edge', alpha = alpha, label = '1625')
    a.set_yscale('log')
    # a.set_xscale()
    a.set_ylabel('# of measurements')
    a.set_xlabel('Voltage (mV)')
    a.legend(title = 'channel (nm)')
    return a

def has1625channel(path2fold, fname):
    fname = path2fold.joinpath(fname)
    wls = np.unique([out['wavelength'] for out in process(fname, fit=False).langleys])
    return (abs(wls - 1625) < 10).sum()


def fname2dates(fname, idx=0):
    date = fname.split('_')[-1].split('.')[0].split('-')[idx]

    if int(date[:2]) < 50:
        year = '20{}'.format(date[:2])
    else:
        year = '19{}'.format(date[:2])

    date = pd.to_datetime(year) + pd.to_timedelta(int(date[2:]), unit='d')

    return date


def get_all_for_one_wl(files, wl, wltol=30):
    all_langley = []
    for i, row in files.iterrows():
        all_langley += [lang for lang in row.langleys.langleys if (wl - wltol) < lang['wavelength'] < (wl + wltol)]
    df = pd.DataFrame(all_langley)
    df.index = df.date
    df.columns.name = wl
    df.sort_index(inplace=True)
    return df

def some_stats(list_of_all_for_one_wl):
    stlist = []
    for all_langley in list_of_all_for_one_wl:
        all_langley = all_langley.copy()

        minV, maxV = min([lang['thedata'].V.min() for i,lang in all_langley.iterrows()]), max([lang['thedata'].V.max() for i,lang in all_langley.iterrows()])
        stlist.append(pd.DataFrame({'min(V)': minV, 'max(V)': maxV, 'range(V)': maxV - minV},
                           index = [all_langley.columns.name],
                          )
                     )
    df = pd.concat(stlist)
    return df

def get_hist_from_all(all_langley_wl, potrange=(150, 1200), nobins=60):
    all_langley_wl = all_langley_wl.copy()
    all_langley_wl = all_langley_wl.rename(columns={'data': 'thedata'})
    for e, (i, lan) in enumerate(all_langley_wl.iterrows()):
        #     break
        #
        pot = lan.thedata.V
        #     nobins = 80

        #     bins = np.logspace(np.log10(potrange[0]), np.log10(potrange[1]), nobins)
        bins = np.linspace(potrange[0], potrange[1], nobins)
        hist, vedg = np.histogram(pot, bins=bins, range=potrange)

        if e == 0:
            histall = hist
        else:
            histall += hist
    #     break
    return histall, vedg

def mad(x):
    return np.fabs(x - x.mean()).mean()

def plot_intercept(all_langleys, nodays=60):
    f, aa = plt.subplots(2, sharex=True, gridspec_kw=dict(hspace=0,
                                                          height_ratios=[2, 1]))
    at, ab = aa

    ict = 10 ** all_langleys.intercept
    ictm = ict.rolling('{}d'.format(nodays)).median().shift(-nodays / 2, 'd')
    icts = ict.rolling('{}d'.format(nodays)).apply(mad, raw=True).shift(-nodays / 2, 'd')

    #### top
    ict.plot(ax=at, label='Each Langley')

    ictm.plot(ax=at, label='60 day rolling median')
    g = at.get_lines()[-1]
    col = g.get_color()

    at.fill_between(icts.index, ictm - icts, ictm + icts, color=col, alpha=0.3, zorder=100, label='$\pm$mad')

    at.set_ylabel('V$_{0}$ (mV)')
    at.legend()
    #### bottom
    icts.plot(ax=ab, color=colors[2], label='60 day rolling mad')

    ab.set_ylabel('$\sigma$V$_{0}$ (mV)')

    ab.set_xlabel('')
    ab.legend()
    return aa