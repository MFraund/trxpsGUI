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
import glob
import pickle

def loadh5data_file(h5path, loadsaved = True, tdcsetting = 'Free', alsbunchtype = 'multi'):
	#%% Loading h5 file to dataframe
	
	barepath, h5ext = os.path.splitext(h5path)
	picklepath = barepath + '_pickle'
	
	if os.path.exists(picklepath) and loadsaved == True:
		
		with open(picklepath, mode='rb') as f:
			vardict = pickle.load(f)
			return vardict['raw2d'], vardict['dfspec']
# 			vardict = json.loads(''.join(f.readlines()))
# 			return vardict['raw2d'], vardict['dfspec']
	
	f = h5py.File(h5path)
	
	df_rawvec = pd.DataFrame()
	
	for colname in f.keys():
		tempdf = pd.DataFrame(np.array(f[colname[:]]).T,
								# dtype = dtype_list[colname],
								columns=[colname[:]])
		df_rawvec = pd.concat([df_rawvec, tempdf], axis=1, copy=False)
		
	del(tempdf)
	
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
	
	if tdcsetting == 'Ext Start':
		df_rawvec = df_rawvec[df_rawvec.t < num_TDC_steps*1.2] # 7.87 us / 27.4 ps = maximum number of steps between laser 
	elif tdcsetting == 'Free':
		pass
	
	
	xOvert = df_rawvec.t.groupby([df_rawvec.x, df_rawvec.t//bin_width]).count()
	#use pandas cut then groupby
	raw2d = xOvert.unstack()
	
	raw2d = raw2d.fillna(0)
	
# 	raw2d = raw2d.reindex(list(range(int(raw2d.index.min()), int(raw2d.index.max())+1)), fill_value=0)
	raw2d = raw2d.reindex(list(range(0, 127+1)), fill_value=0)
# 	raw2d = raw2d.reindex(list(range(0, 128)), fill_value=0)
	
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
	fp = findpeaks(lookahead = 1, interpolate = 5, method='topology', verbose=0)
	results = fp.fit(bunchpattern)
	
	if alsbunchtype == 'multi':
		peak_idxs = results['df'].score.nlargest(24).sort_index()
	elif alsbunchtype  == 'free':
		peak_idxs = results['df'].score.nlargest(12).sort_index()
	# peak_idxs = peak_tup[0]
	
	dfspec = pd.DataFrame()
	
	for peak in range(len(peak_idxs.index)):
		curr_peakidx = peak_idxs.index[peak]
		dfspec[peak] = raw2d.iloc[:, curr_peakidx-1:curr_peakidx+1].sum(axis=1)
		
	
	vardict = {'raw2d':raw2d, 'dfspec':dfspec}
	
	with open(picklepath, mode='wb') as f:
		pickle.dump(vardict, f)
# 		f.write(json.dumps(vardict))
		
	return raw2d, dfspec


def loadh5data_folder(folderpath, tdcsetting = 'Free'):
	filelist = glob.glob(os.path.join(folderpath,'*.h5'))
	numfiles = len(filelist)

	dfspeclist = list()
	raw2dspeclist = list()

	pumpedarray = np.empty([128,numfiles])
	
	psarray = np.empty(numfiles)
	for file in tqdm(range(numfiles)):
		
		filename_noext = os.path.split(filelist[file])[1][:-3]
		psidx = filename_noext.find('ps')
		psval = int(filename_noext[psidx+2:])
		psarray[file] = psval
		
		
		raw2dspec, dfspec = loadh5data_file(filelist[file])
		dfspeclist.append(dfspec)
		raw2dspeclist.append(raw2dspec)
		
		pumpedarray[:,file] = dfspec.iloc[:,2].to_numpy()
		
		
	refspec = 0
	probespec = 2
	interpfac = 200
	
	corr = np.empty(pumpedarray.shape[1])
	for spec in range(pumpedarray.shape[1]):
		resampled_ref = signal.resample(pumpedarray[:,-1], pumpedarray.shape[0]*interpfac, psarray)
		resampled_probe = signal.resample(pumpedarray[:,spec], pumpedarray.shape[0]*interpfac, psarray)
		test = signal.correlate(resampled_ref[0], resampled_probe[0], mode='same')
		maxshift = np.array((len(test)//2 - np.argmin(np.abs(test - test.max())))/interpfac)
		corr[spec] = maxshift
		# np.concatenate([corr, maxshift])

		
	return raw2dspeclist, dfspeclist, psarray, (pumpedarray, corr)