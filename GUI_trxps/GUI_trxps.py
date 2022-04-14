# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 04:37:21 2022

@author: matth
"""
import sys
import os
import io
import pdb

from PyQt5 import uic


from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QSizePolicy
from PyQt5.QtWidgets import QFileDialog, QDialog
from PyQt5.QtWidgets import QPushButton, QListWidget, QSpinBox, QTextEdit
from PyQt5.QtWidgets import QLabel, QRadioButton, QGroupBox, QLineEdit
from PyQt5.QtWidgets import QTabWidget, QFrame, QMenu, QCheckBox
# from PyQt5.QtWidgets import QFrame
from PyQt5.QtGui import QIcon, QMouseEvent
from PyQt5.QtCore import pyqtSlot, QTimer, Qt, QEvent, QPoint, QSettings


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends import backend_qt5agg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import addcopyfighandler

import seaborn as sns
import pandas as pd
import numpy as np

import random
import json

from loadh5data import loadh5data_file, loadh5data_folder


class GUI_Window(QMainWindow):
	def __init__(self):
		super(GUI_Window,self).__init__()
		uic.loadUi('form.ui',self)
		self.widget = self.findChild(QWidget, 'centralwidget')
		self.pathlist = []
		self.settings = QSettings('GUI_Window','GUI_Settings')
		self.initUI()
		
	def initUI(self):
		#%% initial placeholders
		self.currfile_name = None
		self.raw2d = pd.DataFrame()
		self.dfspec = pd.DataFrame()
		
		#find widgets in xml file
		#%% addruns box
		#elements
		self.groupBox_addruns = self.findChild(QGroupBox, 'groupBox_addruns')
		self.label_day = self.findChild(QLabel,'label_day')
		self.label_month = self.findChild(QLabel,'label_month')
		self.label_year = self.findChild(QLabel,'label_year')
		self.label_run = self.findChild(QLabel,'label_run')
		self.pushButton_add = self.findChild(QPushButton, 'pushButton_add')
		self.pushButton_browse = self.findChild(QPushButton, 'pushButton_browse')
		self.spinBox_day = self.findChild(QSpinBox, 'spinBox_day')
		self.spinBox_month = self.findChild(QSpinBox, 'spinBox_month')
		self.spinBox_year = self.findChild(QSpinBox, 'spinBox_year')
		self.spinBox_run = self.findChild(QSpinBox, 'spinBox_run')
		self.lineEdit_WorkingDir = self.findChild(QLineEdit, 'lineEdit_WorkingDir')
		self.lineEdit_WorkingDir.setText(self.settings.value('WorkingDir_text',type = str))
		
		self.checkBox_extstart = self.findChild(QCheckBox, 'checkBox_tdctype')
		self.checkBox_alsbunchtype = self.findChild(QCheckBox, 'checkBox_alsbunchtype')
		
		
		
		#signals
		self.pushButton_browse.clicked.connect(self.set_workingdir)
		self.pushButton_add.clicked.connect(self.add_run)
# 		self.pushButton_browse.clicked.connect(self.browse_runs)
		
		#%% loadedruns box
		#elements
		self.groupBox_loadedruns = self.findChild(QGroupBox, 'groupBox_loadedruns')
		self.listWidget_runs = self.findChild(QListWidget, 'listWidget_runs')
		self.pushButton_load = self.findChild(QPushButton, 'pushButton_load')
		self.pushButton_save = self.findChild(QPushButton, 'pushButton_save')
		
		
		#signals
		self.listWidget_runs.itemSelectionChanged.connect(self.list_select)
		
		#%% background box
		#elements
		self.groupBox_background = self.findChild(QGroupBox,'groupBox_background')
		
		#%% normalization box
		#elements
		self.groupBox_normalization = self.findChild(QGroupBox,'groupBox_normalization')
		
		#%% runparams box
		#elements
		self.groupBox_runparams = self.findChild(QGroupBox,'groupBox_runparams')
		self.label_PSval = self.findChild(QLabel,'label_PSval')
		self.label_t0val = self.findChild(QLabel,'label_t0val')
		
		self.spinBox_PSval = self.findChild(QSpinBox,'spinBox_PSval')
		self.spinBox_t0val = self.findChild(QSpinBox,'spinBox_t0val')
		self.spinBox_bunchval = self.findChild(QSpinBox,'spinBox_bunchval')
		
		self.spinBox_PSval.valueChanged.connect(self.change_PSval)
		
# 		self.lineEdit_PSval = self.findChild(QLineEdit,'lineEdit_PSval')
# 		self.lineEdit_t0val = self.findChild(QLineEdit,'lineEdit_t0val')
# 		self.lineEdit_bunchval = self.findChild(QLineEdit, 'lineEdit_bunchval')
		
		#%% Bunch Viewer Tab
		self.tabWidget = self.findChild(QTabWidget, 'tabWidget_main')
		
		self.radioButton_first4 = self.findChild(QRadioButton,'radioButton_first4')
		self.radioButton_first4.setChecked(True) #setting as default
		self.radioButton_pick2 = self.findChild(QRadioButton,'radioButton_pick2')
		self.radioButton_pick2.setEnabled(False)
		
# 		self.frame_2dbunch = self.findChild(QFrame,'frame_2dbunch')
# 		self.frame_intspec = self.findChild(QFrame,'frame_intspec')
# 		self.frame_intspikes = self.findChild(QFrame,'frame_intspikes')
		self.frame_pickedbunch = self.findChild(QFrame,'frame_pickedbunch')
		self.frame_multi_bunchplot = self.findChild(QFrame,'frame_multi_bunchplot')
		
# 		self.fig_frame_2dbunch = PlotCanvas(self.frame_2dbunch)
# 		self.fig_frame_intspec = PlotCanvas(self.frame_intspec)
# 		self.fig_frame_intspikes = PlotCanvas(self.frame_intspikes)
		
		
		#%% Slice Viewer Tab
# 		self.frame_2dspec = self.findChild(QFrame, 'frame_2dspec')
# 		self.frame_tslice = self.findChild(QFrame, 'frame_tslice')
# 		self.frame_eslice = self.findChild(QFrame, 'frame_eslice')
		self.frame_multislice = self.findChild(QFrame, 'frame_multislice')
		self.frame_bigspec = self.findChild(QFrame, 'frame_bigspec')
		
		
		
		#%% Spectral Shifts Tab
		self.frame_specshift = self.findChild(QFrame, 'frame_specshift')
		
		self.init_figcanvas()
		
		
	#%% Slots
	
	def init_figcanvas(self):
		self.fig_frame_multi_bunchplot = MultiPlotCanvas(self.frame_multi_bunchplot)
		self.fig_frame_pickedbunch = PlotCanvas(self.frame_pickedbunch)
		
		self.fig_frame_multislice = MultiPlotCanvas(self.frame_multislice)
		self.fig_frame_bigspec = PlotCanvas(self.frame_bigspec)
		
		self.fig_frame_specshift = PlotCanvas(self.frame_specshift)
		
		
	@pyqtSlot()
	def set_workingdir(self):
		dialog = QFileDialog()
		dialog.setFileMode(QFileDialog.DirectoryOnly)
		dialog.setAcceptMode(QFileDialog.AcceptOpen)
		if dialog.exec_() == QDialog.Accepted:
			path = dialog.selectedFiles()[0]
			self.path = path
			self.lineEdit_WorkingDir.setText(path)
# 		dirname = QFileDialog.getOpenFileName(self, tr("Open Image"), '\D:\Google Drive\Projects\LBL\Beamtimes\ALS')
# 		self.statusBar().showMessage('test button click')
# 		data = [random.random() for i in range(25)]
# 		self.fig_frame_intspec.plot(data = data)
		
	@pyqtSlot()
	def add_run(self):
# 		workingdir = r'D:\Google Drive\Projects\LBL\Beamtimes\ALS 2021 - 9 Nov\Data and Software Dump\Data'
		workingdir = self.lineEdit_WorkingDir.text()
		year = self.spinBox_year.value()
		month = self.spinBox_month.value()
		day = self.spinBox_day.value()
		run = self.spinBox_run.value()
		
		scanfolder = 'PS_Scan_' + str(year) + str(month) + str(day) + '-run' + f'{run:03d}'
		h5file = str(year) + str(month) + str(day) + '-run' + f'{run:03d}' + '.h5'
		scanpath = os.path.join(workingdir, scanfolder)
		h5path = os.path.join(workingdir, h5file)
		
		
		if self.listWidget_runs.findItems(h5file,Qt.MatchExactly) or self.listWidget_runs.findItems(scanfolder, Qt.MatchExactly):
			self.statusBar().showMessage('Duplicate File')
		else:
			try:
				if self.checkBox_extstart.isChecked():
					tdcset = 'Ext Start'
				else:
					tdcset = 'Free'
					
				if self.checkBox_alsbunchtype.isChecked():
					alsset = 'multi'
				else:
					alsset = '2B'
				
				if os.path.isfile(h5path):
						self.raw2d, self.dfspec = loadh5data_file(h5path, tdcsetting=tdcset ,alsbunchtype=alsset)
						self.listWidget_runs.addItem(h5file)
						added_item = self.listWidget_runs.findItems(h5file,Qt.MatchExactly)
						itemrow = self.listWidget_runs.indexFromItem(added_item[0]).row()
						self.pathlist.append(h5path)
						
				elif os.path.isdir(scanpath):
						self.raw2dlist, self.dfspeclist, self.psarray, self.extra = loadh5data_folder(scanpath, tdcsetting=tdcset ,alsbunchtype=alsset)
						self.listWidget_runs.addItem(scanfolder)
						added_item = self.listWidget_runs.findItems(scanfolder,Qt.MatchExactly)
						itemrow = self.listWidget_runs.indexFromItem(added_item[0]).row()
						self.pathlist.append(scanpath)
						
				if itemrow == 0:
					self.list_select(itemrow)
					self.listWidget_runs.setCurrentRow(itemrow)
					
			except:
				self.statusBar().showMessage('Error Loading')
			
			
			
		
	@pyqtSlot()
	def browse_runs(self):
		self.statusBar.showMessage('browsing runs')
		
	@pyqtSlot()
	def change_PSval(self):
		
		self.PSval= np.abs(self.spinBox_PSval.value() - self.psarray).argmin()
		self.spinBox_PSval.setValue(int(self.psarray[self.PSval]))
		if os.path.isdir(self.currpath):
			self.raw2d = self.raw2dlist[self.PSval]
			self.dfspec = self.dfspeclist[self.PSval]
			
		self.update_tab_bunches()
# 		self.raw2d = self.raw2dlist[self.PSval]
# 		self.dfspec = self.dfspeclist[self.PSval]
		
	@pyqtSlot()
	def list_select(self, currrow = None):
		if currrow == None:
			currrow = self.listWidget_runs.currentRow()
		self.currpath = self.pathlist[currrow]
		self.currfile = os.path.split(self.currpath)[1]
		self.currfile_name = os.path.splitext(self.currfile)[0]
		
		if self.checkBox_extstart.isChecked():
			tdcset = 'Ext Start'
		else:
			tdcset = 'Free'
			
		if self.checkBox_alsbunchtype.isChecked():
			alsset = 'multi'
		else:
			alsset = '2B'
		
		if os.path.isfile(self.currpath):
			self.raw2d, self.dfspec = loadh5data_file(self.currpath, tdcsetting=tdcset ,alsbunchtype=alsset)
			self.psarray = np.array([0])
			self.vargout = (np.array([0]), np.array([0]))
			
		elif os.path.isdir(self.currpath):
			self.raw2dlist, self.dfspeclist, self.psarray, self.vargout = loadh5data_folder(self.currpath, tdcsetting=tdcset ,alsbunchtype=alsset)
			# self.PSval
			self.raw2d = self.raw2dlist[2]
			self.dfspec = self.dfspeclist[2]
		self.change_PSval()
		self.update_tab_bunches()
		
	@pyqtSlot()
	def update_tab_bunches(self):
# 		print(self.PSval)
# 		self.init_figcanvas()
		
		#Giving each frame instance access to data
		#This part seems a bit cumbersome, perhaps it can be fixed better than this?
		
		#Bunch Viewer Tab
# 		self.fig_frame_multi_bunchplot.raw2d = self.raw2d
# 		self.fig_frame_multi_bunchplot.dfspec = self.dfspec
# 		self.fig_frame_multi_bunchplot.currfile_name = self.currfile_name
# 		self.fig_frame_pickedbunch.raw2d = self.raw2d
# 		self.fig_frame_pickedbunch.dfspec = self.dfspec
# 		self.fig_frame_pickedbunch.currfile_name = self.currfile_name
		self.fig_frame_pickedbunch.radioButton_first4 = self.radioButton_first4
		
		#Slice Viewer Tab
# 		self.fig_frame_multislice.raw2d = self.raw2d
# 		self.fig_frame_multislice.dfspec = self.dfspec
# 		self.fig_frame_multislice.currfile_name = self.currfile_name
# 		self.fig_frame_bigspec.raw2d = self.raw2d
# 		self.fig_frame_bigspec.dfspec = self.dfspec
# 		self.fig_frame_bigspec.currfile_name = self.currfile_name
		
		#Spectral Shifts Tab
		
		#Plot calls
		self.fig_frame_multi_bunchplot.bigplot(self.fig_frame_multi_bunchplot.axbig)
		self.fig_frame_multi_bunchplot.botplot(self.fig_frame_multi_bunchplot.axbot)
		self.fig_frame_multi_bunchplot.rightplot(self.fig_frame_multi_bunchplot.axright)
		self.fig_frame_pickedbunch.bunchspecplot(self.fig_frame_pickedbunch.axh)
		
		self.fig_frame_multislice.bigplot_slice(self.fig_frame_multislice.axbig)
		self.fig_frame_multislice.botplot_slice(self.fig_frame_multislice.axbot)
		self.fig_frame_multislice.rightplot_slice(self.fig_frame_multislice.axright)
		self.fig_frame_bigspec.bigspecplot(self.fig_frame_bigspec.axh)
		
		self.fig_frame_specshift.specshiftplot(self.fig_frame_specshift.axh)
		
		
	#%% Non Slot Functions
	
	def closeEvent(self, event):
		self.settings.setValue('WorkingDir_text', self.lineEdit_WorkingDir.text())
		print('settings saved')
	#%% Methods
# 	def mousePressEvent(self, event: QMouseEvent):
# 		if event.button() == Qt.RightButton:
# 			self.statusbar.showMessage('right button clicked')
# 	def mouseReleaseEvent(self, QMouseEvent):
# 		self.currclick = [QMouseEvent.x(), QMouseEvent.y()]
# 		print(self.currclick)

			
# 	def contextMenuEvent(self, event):
# 		contextMenu = QMenu(self)
# 		bigplot_action = contextMenu.addAction('Plot Figure Separately')
# 		action = contextMenu.exec_(self.mapToGlobal(event.pos()))
# 		if action == bigplot_action:
# 			print(self.currclick)
# 			print(self.childAt(self.currclick[0], self.currclick[1]).objectName())
# 			pass

# 	def eventFilter(self, obj, event):
# # 		print(event.type())
# 		if event.type() == QEvent.ContextMenu:
# 			self.statusbar.showMessage('eventfilter worked?')
# 			print(event.pos())
# 			print(obj.ChildAt())
# 			return True
# 		return True

#%% Plot class
class PlotCanvas(FigureCanvas):
	
	def __init__(self, frame, dpi=100):
		super().__init__()
		#Basic Properties
		width = frame.width()
		height = frame.height()
		fig = Figure(figsize=(width, height), dpi=dpi)
# 		self.raw2d = gui_window.raw2d
# 		self.dfspec = gui_window.dfspec
# 		self.currfile_name = gui_window.currfile_name
		
		self.canvas = FigureCanvas(fig)
		self.setParent(frame)
		self.setFixedSize(width, height)
		
		
		self.axh = self.figure.add_subplot()
		cid = self.axh.figure.canvas.mpl_connect('button_release_event', self.onrelease)
		
		FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		
	def onrelease(self, event):
		# 3 for right click
		if event.button != 3:
			return
		
		contextMenu = QMenu(self)
		PlotSeparately = contextMenu.addAction('Plot Figure Separately')
		SavePlot = contextMenu.addAction('Save This Plot')
		
		action = contextMenu.exec_(self.mapToGlobal(QPoint(event.x, self.height() - event.y)))
		if action == PlotSeparately:
			tempfig, tempax = plt.subplots()
			self.bunchspecplot(tempax)
			
		elif action == SavePlot:
			pass
		
	def bunchspecplot(self,axh):
		axh.clear()
		
		df = gui.dfspec
		
		if self.radioButton_first4.isChecked():
			for bunch in range(4):
				axh.plot(df.index.values, df.iloc[:,bunch])
			axh.legend(['1','2','3','4'])
			axh.set_xlabel('DLD Channel')
			axh.set_ylabel('Counts')
			
		elif self.radioButton_pick2.isChecked():
			### Uncertain if this is useful anymore, perhaps remove this bit
			#Grab 1st
			axh.plot(df.index.values, df.iloc[:,bunch])
			#Grab 2nd
			
		self.draw()
		
	def bigspecplot(self, axh):
		axh.clear()
		df = gui.dfspec
		axh.plot(df.index.values, df.iloc[:,3])
		axh.set_xlabel('DLD Channel')
		axh.set_ylabel('Counts')
		self.draw()
		
	def specshiftplot(self, axh):
		axh.clear()
		psarray = gui.psarray
		corr = gui.vargout[1]
		axh.scatter(psarray, corr)
		self.draw()
		
class MultiPlotCanvas(FigureCanvas):
	def __init__(self, frame, dpi=100):
		super().__init__()
		# Basic Properties
		width = frame.width()
		height = frame.height()
		fig = Figure(figsize=(width, height), dpi=dpi)
# 		self.raw2d = gui_window.raw2d
# 		self.dfspec = gui_window.dfspec
# 		self.currfile_name = gui_window.currfile_name
		
		self.canvas = FigureCanvas(fig)
		self.setParent(frame)
		self.setFixedSize(width, height)
		
		spec = self.canvas.figure.add_gridspec(nrows = 3, ncols = 3)
		self.axbot = self.figure.add_subplot(spec[2,0:2])
		self.axbig = self.figure.add_subplot(spec[0:2, 0:2], sharex= self.axbot)
		self.axright = self.figure.add_subplot(spec[0:2,2], sharey = self.axbig)
		self.axbig.tick_params('x',labelbottom=False)
		self.axright.tick_params('y',labelleft=False)
		
		self.figure.set_tight_layout(True)
		
		FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		
		cid = self.axbig.figure.canvas.mpl_connect('button_release_event', self.onrelease)
	
	def onrelease(self, event):
		# 3 for right click
		if event.button != 3:
			return
		
		contextMenu = QMenu(self)
		PlotSeparately = contextMenu.addAction('Plot Figure Separately')
		SavePlot = contextMenu.addAction('Save This Plot')
		
		action = contextMenu.exec_(self.mapToGlobal(QPoint(event.x, self.height() - event.y)))
		if action == PlotSeparately:
			tempfig, tempax = plt.subplots()
			
			if gui.tabWidget.currentIndex() == 0:
				if self.axbig.contains(event)[0]:
					self.bigplot(tempax)
				elif self.axbot.contains(event)[0]:
					self.botplot(tempax)
				elif self.axright.contains(event)[0]:
					self.rightplot(tempax)
					
			elif gui.tabWidget.currentIndex() == 1:
				if self.axbig.contains(event)[0]:
					self.bigplot_slice(tempax)
				elif self.axbot.contains(event)[0]:
					self.botplot_slice(tempax)
				elif self.axright.contains(event)[0]:
					self.rightplot_slice(tempax)
			
		elif action == SavePlot:
			if gui.tabWidget.currentIndex() == 0:
				if self.axbig.contains(event)[0] or self.axbot.contains(event)[0] or self.axright.contains(event)[0]:
					self.axbig.figure.savefig('2dBunchPattern_' + gui.currfile_name)
			elif gui.tabWidget.currentIndex() == 1:
				if self.axbig.contains(event)[0] or self.axbot.contains(event)[0] or self.axright.contains(event)[0]:
					self.axbig.figure.savefig('2dSliceView_' + gui.currfile_name)
# 			elif self.axbot.contains(event)[0]:
# 				self.axbot.figure.savefig('IntegratedBunchSpectrum_' + self.currfile_name)
# 				
# 			elif self.axright.contains(event)[0]:
# 				self.axright.figure.savefig('IntegratedTimeSpikes_' + self.currfile_name)
		
		
	def bigplot(self, axh):
		axh.clear()
		df = gui.raw2d.T
		axh.pcolormesh(df.columns, df.index, df.values, shading = 'auto')
		axh.set_ylabel('Time (ns)')
		self.draw()
		
	def botplot(self, axh):
		axh.clear()
		data = gui.raw2d.mean(axis=1)
		axh.plot(data, 'r-')
		axh.set_xlabel('DLD Channel')
		self.draw()
		
	def rightplot(self, axh):
		axh.clear()
		data = gui.raw2d.mean(axis=0)
		axh.plot(data.values, data.index,'r-')
		self.draw()
		
	def bigplot_slice(self,axh):
		axh.clear()
		df = gui.dfspec.T
		axh.pcolormesh(df.columns, df.index, df.values, shading='auto')
		axh.set_ylabel('Bunch')
		self.draw()
		
	def botplot_slice(self, axh):
		axh.clear()
		data = gui.dfspec.iloc[:,:].mean(axis=1)
		axh.plot(data, 'r-')
		axh.set_xlabel('DLD Channel')
		self.draw()
	
	def rightplot_slice(self,axh):
		axh.clear()
		data = gui.dfspec.iloc[:,:].mean(axis=0)
		axh.plot(data.values, data.index,'r-')
		self.draw()
		
	def bigplot_PSslice(self,axh):
		axh.clear()
		df = gui.dfspec.T
		axh.pcolormesh(df.columns, df.index, df.values, shading='auto')
		axh.set_ylabel('Bunch')
		self.draw()
		
	def botplot_PSslice(self, axh):
		axh.clear()
		data = gui.dfspec.iloc[:,:].mean(axis=1)
		axh.plot(data, 'r-')
		axh.set_xlabel('DLD Channel')
		self.draw()
	
	def rightplot_PSslice(self,axh):
		axh.clear()
		data = gui.dfspec.iloc[:,:].mean(axis=0)
		axh.plot(data.values, data.index,'r-')
		self.draw()
		
#%% Run thing idk
if __name__ == '__main__':
	runmain = QApplication(sys.argv)
	
	# Create window
	gui = GUI_Window()
	
	# Install event filter
	gui.installEventFilter(gui)
	
	gui.show()