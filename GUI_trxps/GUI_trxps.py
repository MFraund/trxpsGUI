# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 04:37:21 2022

@author: matth
"""
import sys
import os
import io

from PyQt5 import uic


from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QSizePolicy
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QPushButton, QListWidget, QSpinBox, QTextEdit
from PyQt5.QtWidgets import QLabel, QRadioButton, QGroupBox, QLineEdit
from PyQt5.QtWidgets import QTabWidget, QFrame, QMenu
# from PyQt5.QtWidgets import QFrame
from PyQt5.QtGui import QIcon, QMouseEvent
from PyQt5.QtCore import pyqtSlot, QTimer, Qt, QEvent, QPoint


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends import backend_qt5agg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import addcopyfighandler

import random

from loadh5data import loadh5data


class GUI_Window(QMainWindow):
	def __init__(self):
		super(GUI_Window,self).__init__()
		uic.loadUi('form.ui',self)
		self.widget = self.findChild(QWidget, 'centralwidget')
		self.pathlist = []
		self.initUI()
		
	def initUI(self):
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
		
		#signals
		self.pushButton_browse.clicked.connect(self.test_click)
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
		self.lineEdit_PSval = self.findChild(QLineEdit,'lineEdit_PSval')
		self.lineEdit_t0val = self.findChild(QLineEdit,'lineEdit_t0val')
		
		#%% Bunch Viewer Tab
		self.frame_2dbunch = self.findChild(QFrame,'frame_2dbunch')
		self.frame_intspec = self.findChild(QFrame,'frame_intspec')
		self.frame_intspikes = self.findChild(QFrame,'frame_intspikes')
		self.frame_pickedbunch = self.findChild(QFrame,'frame_pickedbunch')
		self.frame_multiplot = self.findChild(QFrame,'frame_multiplot')
		self.radioButton_first4 = self.findChild(QRadioButton,'radioButton_first4')
		self.radioButton_pick2 = self.findChild(QRadioButton,'radioButton_pick2')
		
# 		self.fig_frame_2dbunch = PlotCanvas(self.frame_2dbunch)
# 		self.fig_frame_intspec = PlotCanvas(self.frame_intspec)
# 		self.fig_frame_intspikes = PlotCanvas(self.frame_intspikes)
		self.fig_frame_multiplot = PlotCanvas(self.frame_multiplot, multiplot_bool = True)
		self.fig_frame_pickedbunch = PlotCanvas(self.frame_pickedbunch)
		
		
		
		
	#%% Slots
	@pyqtSlot()
	def test_click(self):
		self.statusBar().showMessage('test button click')
# 		data = [random.random() for i in range(25)]
# 		self.fig_frame_intspec.plot(data = data)
		
	@pyqtSlot()
	def add_run(self):
		workingdir = r'D:\Google Drive\Projects\LBL\Beamtimes\ALS 2021 - 9 Nov\Data and Software Dump\Data'
		year = self.spinBox_year.value()
		month = self.spinBox_month.value()
		day = self.spinBox_day.value()
		run = self.spinBox_run.value()
		
		
		h5file = str(year) + str(month) + str(day) + '-run' + f'{run:03d}' + '.h5'
		
		
		h5path = os.path.join(workingdir, h5file)
		
		
		if self.listWidget_runs.findItems(h5file,Qt.MatchExactly):
			self.statusBar().showMessage('Duplicate File')
		else:
			try:
				self.raw2d, self.dfspec = loadh5data(h5path)
				self.listWidget_runs.addItem(h5file)
				added_item = self.listWidget_runs.findItems(h5file,Qt.MatchExactly)
				itemrow = self.listWidget_runs.indexFromItem(added_item[0]).row()
				
				self.pathlist.append(h5path)
				
			except:
				self.statusBar().showMessage('Error Loading')
			
		
	@pyqtSlot()
	def browse_runs(self):
		self.statusBar.showMessage('browsing runs')
		
	@pyqtSlot()
	def list_select(self):
		curritem = self.listWidget_runs.selectedItems()
		currrow = self.listWidget_runs.currentRow()
		self.currpath = self.pathlist[currrow]
		self.currfile = os.path.split(self.currpath)[1]
		self.currfile_name = os.path.splitext(self.currfile)[0]
		
		self.raw2d, self.dfspec = loadh5data(self.currpath)
		self.fig_frame_multiplot.raw2d = self.raw2d
		self.fig_frame_multiplot.dfspec = self.dfspec
		self.fig_frame_multiplot.currfile_name = self.currfile_name
		self.update_tab_bunches()
		
	@pyqtSlot()
	def update_tab_bunches(self):
		
		#need to give each frame instance raw2d and dfspec data
		self.fig_frame_multiplot.bigplot(self.fig_frame_multiplot.axbig)
		self.fig_frame_multiplot.botplot(self.fig_frame_multiplot.axbot)
		self.fig_frame_multiplot.rightplot(self.fig_frame_multiplot.axright)
		
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
	
	def __init__(self, frame, currfile_name = None, multiplot_bool = False, dpi=100):
		super().__init__()
		#Basic Properties
		width = frame.width()
		height = frame.height()
		fig = Figure(figsize=(width, height), dpi=dpi)
		
		self.canvas = FigureCanvas(fig)
		self.setParent(frame)
		self.setFixedSize(width, height)
		
		if multiplot_bool == True:
			
			spec = self.canvas.figure.add_gridspec(nrows = 3, ncols = 3)
			self.axbot = self.figure.add_subplot(spec[2,0:2])
			self.axbig = self.figure.add_subplot(spec[0:2, 0:2], sharex= self.axbot)
			self.axright = self.figure.add_subplot(spec[0:2,2], sharey = self.axbig)
			self.axbig.tick_params('x',labelbottom=False)
			self.axright.tick_params('y',labelleft=False)
			self.figure.set_tight_layout(True)
			
			cid = self.axbig.figure.canvas.mpl_connect('button_release_event', self.onrelease)
			
		else:
			self.axh = self.figure.add_subplot()
			cid = self.axh.figure.canvas.mpl_connect('button_release_event', self.onrelease)
		
		FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		
# 		self.ax = self.figure.gca()
		
		
# class MultiPlotCanvas(FigureCanvas):
# 	def __init__(self, frame, currfile_name = None, dpi=100):
# 		super().__init__()
# 		# Basic Properties
# 		width = frame.width()
# 		height = frame.height()
# 		fig = Figure(figsize=(width, height), dpi=dpi)
# 		
# 		self.canvas = FigureCanvas(fig)
# 		self.setParent(frame)
# 		self.setFixedSize(width, height)
# 		
# 		spec = self.canvas.figure.add_gridspec(nrows = 3, ncols = 3)
# 		self.axbot = self.figure.add_subplot(spec[2,0:2])
# 		self.axbig = self.figure.add_subplot(spec[0:2, 0:2], sharex= self.axbot)
# 		self.axright = self.figure.add_subplot(spec[0:2,2], sharey = self.axbig)
# 		self.axbig.tick_params('x',labelbottom=False)
# 		self.axright.tick_params('y',labelleft=False)
# 		
# 		self.figure.set_tight_layout(True)
# 		
# 		FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
# 		FigureCanvas.updateGeometry(self)
# 		
# 		cid = self.axbig.figure.canvas.mpl_connect('button_release_event', self.onrelease)
	
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
			
			if self.axbig.contains(event)[0]:
				self.bigplot(tempax)
				
			elif self.axbot.contains(event)[0]:
				self.botplot(tempax)
				
			elif self.axright.contains(event)[0]:
				self.rightplot(tempax)
			
		elif action == SavePlot:
			if self.axbig.contains(event)[0]:
				self.axbig.figure.savefig('2dBunchPattern_' + self.currfile_name)
				
			elif self.axbot.contains(event)[0]:
				self.axbot.figure.savefig('IntegratedBunchSpectrum_' + self.currfile_name)
				
			elif self.axright.contains(event)[0]:
				self.axright.figure.savefig('IntegratedTimeSpikes_' + self.currfile_name)
		
		
	def bigplot(self, axh):
		axh.clear()
		df = self.raw2d.T
		axh.pcolormesh(df.columns, df.index, df.values, shading = 'auto')
		axh.set_ylabel('Time (ns)')
		self.draw()
		
	def botplot(self, axh):
# 		ax = self.figure.gca()
		axh.clear()
		data = self.raw2d.mean(axis=1)
		axh.plot(data, 'r-')
		axh.set_xlabel('DLD Channel')
		self.draw()
		
	def rightplot(self, axh):
		axh.clear()
		data = self.raw2d.mean(axis=0)
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