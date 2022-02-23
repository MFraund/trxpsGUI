# -*- coding: utf-8 -*-
"""
Created on Thu Jan 20 01:19:24 2022

@author: matth
"""

#%% Imports
import h5py
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from tqdm import tqdm
from scipy import signal
import os
from findpeaks import findpeaks

def loadh5data(h5path):
	#%% Loading h5 file to dataframe
	
	
	f = h5py.File(h5path)
	
	df_rawvec = pd.DataFrame()
	# dtype_list = 
	
	for colname in f.keys():
# 	    print(colname)
	    tempdf = pd.DataFrame(np.array(f[colname[:]]).T,
	                          # dtype = dtype_list[colname],
	                          columns=[colname[:]])
	    df_rawvec = pd.concat([df_rawvec, tempdf], axis=1, copy=False)
		
	del(tempdf)
	
# 	print(df_rawvec)
	############ Time Res Empirically
	bunchwidth = 1.9988e5-1.5212e5
	TDC_res_empirical = 328e3/bunchwidth
	
	############ Figuring Time Res
	TDC_res = 27.4 # ps/step
	TDC_res_apparent = 2.74 #ps/step
	
	# laser period = 7.878 us
	# num TDC steps per frame = 7.877664 / 0.0000274 
	
	num_TDC_steps = 7.877664 / (TDC_res_empirical/1e6)
	bin_width = 1e3 # steps/bin
	num_bins = num_TDC_steps / bin_width #
	
	bin_tres_ps = bin_width * TDC_res_empirical # ps/bin???
	
	
	
	#dropping bad rows
	# df_rawvec.dropna(inplace=True, thresh = 3)
	df_rawvec = df_rawvec[df_rawvec.x <=150] # some detector values are 6e5 for some reason
	df_rawvec = df_rawvec[df_rawvec.t < num_TDC_steps*1.2] # 7.87 us / 27.4 ps = maximum number of steps between laser 
	
	
	xOvert = df_rawvec.t.groupby([df_rawvec.x, df_rawvec.t//bin_width]).count()
	#use pandas cut then groupby
	raw2d = xOvert.unstack()
	raw2d = raw2d.fillna(0)
	raw2d = raw2d.reindex(list(range(int(raw2d.index.min()), int(raw2d.index.max())+1)), fill_value=0)
	
	counts2d = raw2d.values
	
	
	raw2d.columns = raw2d.columns * bin_tres_ps/1000
	x_det_ch = raw2d.index.values
	t_ps = raw2d.columns.values*1000
	# t_ps = t_binned_steps #still not right yet
	
	# avg_spec = raw2d.mean(axis=1) # old definition
	bunchpattern = raw2d.mean(axis=0)
	bunchpattern.index = bunchpattern.index * bin_tres_ps/1000 
	
	# wut = signal.find_peaks(bunchpattern, distance = 250/(bin_tres_ps/1000) )
	# peak_tup = signal.find_peaks(bunchpattern, prominence = 2)
	fp = findpeaks(lookahead = 1, interpolate = 5, method='topology')
	results = fp.fit(bunchpattern)
	peak_idxs = results['df'].score.nlargest(24).sort_index()
	# peak_idxs = peak_tup[0]
	
	dfspec = pd.DataFrame()
	
	for peak in range(len(peak_idxs.index)):
	    curr_peakidx = peak_idxs.index[peak]
	    dfspec[peak] = raw2d.iloc[:, curr_peakidx-1:curr_peakidx+1].sum(axis=1)
		
	avg_spec = dfspec.mean(axis=1)
	int_spec = dfspec.sum(axis=1)
	
	return raw2d, dfspec