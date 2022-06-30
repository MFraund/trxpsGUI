# -*- coding: utf-8 -*-
"""
Created on Sat Apr 16 12:17:20 2022

@author: matth
"""

import os
import time
import sys

import numpy as np
import pandas as pd
import seaborn
from matplotlib import pyplot as plt

import addcopyfighandler
from tqdm import tqdm

import pickle
import h5py


def new_PumpProbeAnalysis(h5path, loadsaved=True, TDCsetting = 'Ext Start'):
	#%% Loading Saved Data
	barepath, h5ext = os.path.splitext(h5path)
	picklepath = barepath + '_pickle'
	
	if os.path.exists(picklepath) and loadsaved == True:
		with open(picklepath, mode='rb') as f:
			vardict = pickle.load(f)
			return vardict['raw2d'], vardict['dfspec']

	#%% Load h5data
	f = h5py.File(h5path)
	
	df_rawvec = pd.DataFrame()
	for colname in f.keys():
		tempdf = pd.DataFrame(np.array(f[colname[:]]).T, columns=[colname[:]])
		df_rawvec = pd.concat([df_rawvec, tempdf], axis=1, copy=False)
	del(tempdf)
	
	Dch_vec = df_rawvec.x
	TDCtime_vec = df_rawvec.t
	
	############ Time Res Empirically
	bunchwidth = 1.9988e5-1.5212e5
	TDC_res_empirical = 328e3/bunchwidth
	
	############ Figuring Time Res
	TDC_res = 27.4 # ps/step
	TDC_res_apparent = 2.74 #ps/step
	
	laser_period = 7877664.0/2 #ps
	# num TDC steps per frame = 7.877664 / 0.0000274 
	
	num_TDC_steps = 7.877664 / (TDC_res_empirical/1e6)
	bin_width = 1e3 # steps/bin
	num_bins = num_TDC_steps / bin_width #
	
	bin_tres_ps = bin_width * TDC_res_empirical # ps/bin???
	
	
	df_rawvec = df_rawvec[df_rawvec.x <=150] # some detector values are 6e5 for some reason
	
	
	TDCtime_vec = TDCtime_vec.to_numpy()
	Dch_vec = Dch_vec.to_numpy()
	
	
	
	TDCtime_vec = TDCtime_vec[Dch_vec <= 128]
	Dch_vec = Dch_vec[Dch_vec <=128]
	
	Dch_vec = Dch_vec[TDCtime_vec < 1e7]
	TDCtime_vec = TDCtime_vec[ TDCtime_vec < 1e7]
# 	print(TDC_res_empirical)
	
# 	return TDCtime_vec
	
	timevec = TDCtime_vec * TDC_res_empirical
	
	Tres = 800
	t_edges = np.arange(0, laser_period, Tres)
	x_edges = np.arange(0, 128)
	PPmap, x_edges, t_edges = np.histogram2d(Dch_vec, timevec, [x_edges, t_edges])
	

	x_cents = x_edges[0:-1] + (x_edges[1] - x_edges[0])/2
	t_cents = t_edges[0:-1] + (t_edges[1] - t_edges[0])/2
	print(x_cents)
	
	import pdb; pdb.set_trace()
	
	return x_edges, x_cents, Tres
	
	if TDCsetting == 'Ext Start':
		df_rawvec = df_rawvec[df_rawvec.t < num_TDC_steps*1.2] # 7.87 us / 27.4 ps = maximum number of steps between laser 
	elif TDCsetting == 'Free':
		pass
	
	return PPmap, x_cents, t_cents, TDCtime_vec
# 	xOvert = df_rawvec.t.groupby([df_rawvec.x, df_rawvec.t//bin_width]).count()
	#use pandas cut then groupby
# 	raw2d = xOvert.unstack()
	
# 	raw2d = raw2d.fillna(0)
	
# 	raw2d = raw2d.reindex(list(range(int(raw2d.index.min()), int(raw2d.index.max())+1)), fill_value=0)
# 	raw2d = raw2d.reindex(list(range(0, 127+1)), fill_value=0)
# 	raw2d = raw2d.reindex(list(range(0, 128)), fill_value=0)


