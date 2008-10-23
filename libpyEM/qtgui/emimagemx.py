#!/usr/bin/env python

#
# Author: Steven Ludtke (sludtke@bcm.edu)
# Copyright (c) 2000-2006 Baylor College of Medicine
#
# This software is issued under a joint BSD/GNU license. You may use the
# source code in this file under either license. However, note that the
# complete EMAN2 and SPARX software packages have some GPL dependencies,
# so you are responsible for compliance with the licenses of these packages
# if you opt to use BSD licensing. The warranty disclaimer below holds
# in either instance.
#
# This complete copyright notice must be included in any revised version of the
# source code. Additional authorship citations may be added, but existing
# author citations must be preserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston MA 02111-1307 USA
#
#

from PyQt4 import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore import Qt
from OpenGL import GL,GLU,GLUT
from OpenGL.GL import *
from OpenGL.GLU import *
from valslider import ValSlider
from math import *
from EMAN2 import *
import EMAN2
import sys
import numpy
from emimageutil import ImgHistogram,EMEventRerouter,EMParentWin
from weakref import WeakKeyDictionary
from pickle import dumps,loads
from PyQt4.QtGui import QImage
from PyQt4.QtCore import QTimer

from emglobjects import EMOpenGLFlagsAndTools
from emapplication import EMStandAloneApplication, EMQtWidgetModule, EMGUIModule

GLUT.glutInit(sys.argv)

class EMImageMXWidget(QtOpenGL.QGLWidget,EMEventRerouter):
	"""
	"""
	def __init__(self, em_mx_module,parent=None):
		#self.initflag = True
		self.mmode = "drag"

		fmt=QtOpenGL.QGLFormat()
		fmt.setDoubleBuffer(True)
		fmt.setSampleBuffers(True)
		QtOpenGL.QGLWidget.__init__(self,fmt, parent)
		EMEventRerouter.__init__(self,em_mx_module)
		
		self.imagefilename = None
		
		#self.resize(480,480)
		
	def get_target(self):
		return self.target
	
	def set_data(self,data):
		self.target.set_data(data)
	
	def set_file_name(self,name):
		#print "set image file name",name
		self.imagefilename = name
		
	def get_image_file_name(self):
		return self.imagefilename
	
	def initializeGL(self):
		glClearColor(0,0,0,0)
		
		glEnable(GL_LIGHTING)
		glEnable(GL_LIGHT0)
		#glEnable(GL_DEPTH_TEST)
		#print "Initializing"
		glLightfv(GL_LIGHT0, GL_AMBIENT, [0.9, 0.9, 0.9, 1.0])
		glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
		glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
		glLightfv(GL_LIGHT0, GL_POSITION, [0.5,0.7,11.,0.])

		glEnable(GL_CULL_FACE)
		glCullFace(GL_BACK)
	def paintGL(self):
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		
		if ( self.target == None ): return
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		#context = OpenGL.contextdata.getContext(None)
		#print "Matrix context is", context
		self.target.render()

	
	def resizeGL(self, width, height):
		if width <= 0 or height <= 0: return None
		GL.glViewport(0,0,width,height)
	
		GL.glMatrixMode(GL.GL_PROJECTION)
		GL.glLoadIdentity()
		GL.glOrtho(0.0,width,0.0,height,-50,50)
		GL.glMatrixMode(GL.GL_MODELVIEW)
		GL.glLoadIdentity()
		
		try: self.target.resize_event(width,height)
		except: pass
	def set_mouse_mode(self,mode):
		self.mmode = mode
		self.target.set_mouse_mode(mode)
	
	def get_frame_buffer(self):
		# THIS WILL FAIL ON WINDOWS APPARENTLY, because Windows requires a temporary context - but the True flag is stopping the creation of a temporary context
		# (because display lists are involved)
		return self.renderPixmap(0,0,True)



class EMMXCoreMouseEvents:
	'''
	A base class for objects that handle mouse events in the EMImageMXModule
	'''
	def __init__(self,mediator):
		'''
		Stores only a reference to the mediator
		'''
		if not isinstance(mediator,EMMXCoreMouseEventsMediator):
			print "error, the mediator should be a EMMXCoreMouseEventsMediator"
			return
		self.mediator = mediator
		
	def mouse_up(self,event):
		'''
		Inheriting classes to potentially define this function
		'''
		pass

	def mouse_down(self,event):
		'''
		Inheriting classes to potentially define this function
		'''
		pass
		
	def mouse_drag(self,event):
		'''
		Inheriting classes to potentially define this function
		'''
		pass
	
	def mouse_move(self,event):
		'''
		Inheriting classes to potentially define this function
		'''
		pass

	def mouse_wheel(self,event):
		'''
		Inheriting classes to potentially define this function
		'''
		pass

class EMMXCoreMouseEventsMediator:
	def __init__(self,target):
		if not isinstance(target,EMImageMXModule):
			print "error, the target should be a EMImageMXModule"
			return
		
		self.target = target
		
	def scr_to_img(self,vec):
		return self.target.scr_to_img(vec)
	
	def get_parent(self):
		return self.target.get_parent()

	def get_box_image(self,idx):
		return self.target.get_box_image(idx)
	
	def pop_box_image(self,idx,event=None,redraw=False):
		self.target.pop_box_image(idx,event,redraw)
	
	def get_density_max(self):
		return self.target.get_density_max()
	
	def get_density_min(self):
		return self.target.get_density_min()
	
	def emit(self,*args,**kargs):
		self.target.emit(*args,**kargs)

	def set_selected(self,selected,update_gl=True):
		self.target.set_selected(selected,update_gl)
		
	def force_display_update(self):
		self.target.force_display_update() 
		
	def get_scale(self):
		return self.target.get_scale()

class EMMXDelMouseEvents(EMMXCoreMouseEvents):
	def __init__(self,mediator):
		EMMXCoreMouseEvents.__init__(self,mediator)
		
	def mouse_up(self,event):
		if event.button()==Qt.LeftButton:
			lc=self.mediator.scr_to_img((event.x(),event.y()))
			if lc != None:
				self.mediator.pop_box_image(lc[0],event,True)
				self.mediator.force_display_update()


class EMMXDragMouseEvents(EMMXCoreMouseEvents):
	def __init__(self,mediator):
		EMMXCoreMouseEvents.__init__(self,mediator)
	
	def mouse_down(self,event):
		if event.button()==Qt.LeftButton:
			lc= self.mediator.scr_to_img((event.x(),event.y()))
			if lc == None: 
				print "strange lc error"
				return
			box_image = self.mediator.get_box_image(lc[0])
			xs=int(box_image.get_xsize())
			ys=int(box_image.get_ysize())
			drag = QtGui.QDrag(self.mediator.get_parent())
			mime_data = QtCore.QMimeData()
			
			mime_data.setData("application/x-eman", dumps(box_image))
			
			EMAN2.GUIbeingdragged= box_image	# This deals with within-application dragging between windows
			mime_data.setText( str(lc[0])+"\n")
			di=QImage(box_image.render_amp8(0,0,xs,ys,xs*4,1.0,0,255,self.mediator.get_density_min(),self.mediator.get_density_max(),1.0,14),xs,ys,QImage.Format_RGB32)
			mime_data.setImageData(QtCore.QVariant(di))
			drag.setMimeData(mime_data)
	
			# This (mini image drag) looks cool, but seems to cause crashing sometimes in the pixmap creation process  :^(
			#di=QImage(self.data[lc[0]].render_amp8(0,0,xs,ys,xs*4,1.0,0,255,self.minden,self.maxden,14),xs,ys,QImage.Format_RGB32)
			#if xs>64 : pm=QtGui.QPixmap.fromImage(di).scaledToWidth(64)
			#else: pm=QtGui.QPixmap.fromImage(di)
			#drag.setPixmap(pm)
			#drag.setHotSpot(QtCore.QPoint(12,12))
					
			dropAction = drag.start()
		
class EMMAppMouseEvents(EMMXCoreMouseEvents):
	def __init__(self,mediator):
		EMMXCoreMouseEvents.__init__(self,mediator)
	
	def mouse_down(self,event):
		if event.button()==Qt.LeftButton:
			lc=self.mediator.scr_to_img((event.x(),event.y()))
			if lc:
				self.mediator.emit(QtCore.SIGNAL("mx_image_selected"),event,lc)
				self.mediator.set_selected([lc[0]],True)
			
	def mouse_move(self,event):
		if event.buttons()&Qt.LeftButton:
			self.mediator.emit(QtCore.SIGNAL("mx_mousedrag"),event,self.mediator.get_scale())
	
	def mouse_up(self,event):
		if event.button()==Qt.LeftButton:
			lc=self.mediator.scr_to_img((event.x(),event.y()))
		
			if  not event.modifiers()&Qt.ShiftModifier:
				self.mediator.emit(QtCore.SIGNAL("mx_mouseup"),event,lc)
			else:
				if lc != None:
					self.mediator.pop_box_image(lc[0],event,True)
					self.mediator.force_display_update()
					
	
	def mousePressEvent(self, event):
		lc=self.scr_to_img((event.x(),event.y()))
#		print lc
		if event.button()==Qt.MidButton or (event.button()==Qt.LeftButton and event.modifiers()&Qt.ControlModifier):
			self.show_inspector(1)
		elif event.button()==Qt.RightButton or (event.button()==Qt.LeftButton and event.modifiers()&Qt.AltModifier):
			app =  QtGui.QApplication.instance()
			try:
				app.setOverrideCursor(Qt.ClosedHandCursor)
			except: # if we're using a version of qt older than 4.2 than we have to use this...
				app.setOverrideCursor(Qt.SizeAllCursor)
				
			self.mousedrag=(event.x(),event.y())

class EMImageMXModule(EMGUIModule):
	
	def load_font_renderer(self):
		try:
			self.font_render_mode = EMGUIModule.FTGL
			self.font_renderer = get_3d_font_renderer()
			self.font_renderer.set_face_size(16)
			self.font_renderer.set_font_mode(FTGLFontMode.TEXTURE)
		except:
			self.font_render_mode = EMGUIModule.GLUT
	
	def get_qt_widget(self):
		if self.qt_context_parent == None:	
			
			self.gl_context_parent = EMImageMXWidget(self)
			self.qt_context_parent = EMParentWin(self.gl_context_parent)
			self.gl_widget = self.gl_context_parent
			#self.optimally_resize()
			self.qt_context_parent.setAcceptDrops(True)
		
		return self.qt_context_parent
	
	def get_gl_widget(self,qt_context_parent,gl_context_parent):
		from emfloatingwidgets import EM2DGLView, EM2DGLWindow
		self.init_size_flag = False
		if self.gl_widget == None:
			
			self.gl_context_parent = gl_context_parent
			self.qt_context_parent = qt_context_parent
			
			gl_view = EM2DGLView(self,image=None)
			self.gl_widget = EM2DGLWindow(self,gl_view)
			self.gl_widget.target_translations_allowed(True)
			self.update_window_title(self.filename)
		return self.gl_widget
	
	def get_desktop_hint(self):
		return self.desktop_hint
	allim=WeakKeyDictionary()
	def __init__(self, data=None,application=None):
		self.desktop_hint = "image"
		self.init_size_flag = True
		self.data=None
		EMGUIModule.__init__(self,application,ensure_gl_context=True)
		EMImageMXModule.allim[self] = 0
		self.filename = ''
		self.datasize=(1,1)
		self.scale=1.0
		self.minden=0
		self.maxden=1.0
		self.invert=0
		self.fft=None
		self.mindeng=0
		self.maxdeng=1.0
		self.gamma=1.0
		self.origin=(0,0)
		self.mx_cols=8
		self.nshow=-1
		self.mousedrag=None
		self.nimg=0
		self.changec={}
		self.mmode="drag"
		self.selected=[]
		self.hist = []
		self.targetorigin=None
		self.targetspeed=20.0
		self.mag = 1.1				# magnification factor
		self.invmag = 1.0/self.mag	# inverse magnification factor
		self.glflags = EMOpenGLFlagsAndTools() 	# supplies power of two texturing flags
		self.tex_names = [] 		# tex_names stores texture handles which are no longer used, and must be deleted
		self.suppress_inspector = False 	# Suppresses showing the inspector - switched on in emfloatingwidgets
		self.image_file_name = None
		
		self.coords={}
		self.nshown=0
		self.valstodisp=["Img #"]
		
		self.inspector=None
		
		self.font_size = 0
		self.load_font_renderer()
		if data:
			self.set_data(data,False)
			
		self.text_bbs = {} # bounding box cache - key is a string, entry is a list of 6 values defining a 
		
		self.use_display_list = True # whether or not a display list should be used to render the main view - if on, this will save on time if the view is unchanged
		self.main_display_list = 0	# if using display lists, the stores the display list
		self.display_states = [] # if using display lists, this stores the states that are checked, and if different, will cause regeneration of the display list
		self.draw_background = False # if true  will paint the background behind the images black using a polygon - useful in 3D contexts, ie i the emimagemxrotary
		
		
		self.img_num_offset = 0		# used by emimagemxrotary for display correct image numbers
		self.max_idx = 99999999		# used by emimagemxrotary for display correct image numbers
	
		self.__init_mouse_handlers()
		
		self.reroute_delete_target = None

	
	def width(self):
		if self.gl_widget != None:
			return self.gl_widget.width()
		else:
			return 0
	
	def using_ftgl(self):
		return self.font_render_mode == EMGUIModule.FTGL
	
	def get_font_size(self):
		return self.font_renderer.get_face_size()
		
	def set_font_size(self,value):
		self.font_renderer.set_face_size(value)
		self.force_display_update() # only for redoing the fonts, this could be made more efficient :(
		self.updateGL()
		
	def height(self):
		if self.gl_widget != None:
			return self.gl_widget.height()
		else:
			return 0
	
	def __init_mouse_handlers(self):
		
		self.mouse_events_mediator = EMMXCoreMouseEventsMediator(self)
		self.mouse_event_handlers = {}
		self.mouse_event_handlers["app"] = EMMAppMouseEvents(self.mouse_events_mediator)
		self.mouse_event_handlers["del"] = EMMXDelMouseEvents(self.mouse_events_mediator)
		self.mouse_event_handlers["drag"] = EMMXDragMouseEvents(self.mouse_events_mediator)
		self.mouse_event_handler = self.mouse_event_handlers[self.mmode]
	
	def set_file_name(self,name):
		#print "set image file name",name
		self.image_file_name = name
	
	def get_inspector(self):
		if not self.inspector : 
			self.inspector=EMImageInspectorMX(self)
			self.inspector_update()
		return self.inspector
	
	def inspector_update(self):
		#FIXME
		pass
		#print "do inspector update"
		
	
	def set_reroute_delete_target(self,target):
		self.reroute_delete_target = target
	
	def get_scale(self):
		return self.scale
	
	def pop_box_image(self,idx,event=None,update_gl=False):
		if self.reroute_delete_target  == None:
			d = self.data.pop(idx)
			self.display_states = []
			if event != None: self.emit(QtCore.SIGNAL("mx_boxdeleted"),event,[idx],False)
			if update_gl:
				self.display_states = [] 
				self.updateGL()
			return d
		else:
			self.reroute_delete_target.pop_box_image(idx)
			if event != None: self.emit(QtCore.SIGNAL("mx_boxdeleted"),event,[idx],False)

	def get_box_image(self,idx):
		return self.data[idx]

	def emit(self,*args,**kargs):
		qt_widget = self.application.get_qt_emitter(self)
		qt_widget.emit(*args,**kargs)
	
	def __del__(self):
		if self.main_display_list != 0:
			glDeleteLists(self.main_display_list,1)
			self.main_display_list = 0
	
		if ( len(self.tex_names) > 0 ):	
			glDeleteTextures(self.tex_names)
			self.tex_names = []
	
	def get_cols(self):
		return self.mx_cols
	
	def force_display_update(self):
		''' If display lists are being used this will force a regeneration'''
		self.display_states = []
	
	def set_img_num_offset(self,n):
		self.img_num_offset = n
		self.force_display_update() # empty display lists causes an automatic regeneration of the display list
	
	def get_img_num_offset(self):
		return self.img_num_offset
	
	def set_draw_background(self,bool):
		self.draw_background = bool
		self.force_display_update()# empty display lists causes an automatic regeneration of the display list
		
	def set_use_display_list(self,bool):
		self.use_display_list = bool
		
	def set_max_idx(self,n):
		self.force_display_update()# empty display lists causes an automatic regeneration of the display list
		self.max_idx = n
		
	def set_min_max_gamma(self,minden,maxden,gamma,update_gl=True):
		self.minden= minden
		self.maxden= maxden
		self.gamma = gamma
		if update_gl: self.updateGL()
		
	def get_hist(self): return self.hist
	
	def get_image(self,idx):
		return self.data[idx]
	
	def get_image_file_name(self):
		''' warning - could return none in some circumstances'''
		try: return self.gl_widget.get_image_file_name()
		except: return None
	
	def __del__(self):
		if ( len(self.tex_names) > 0 ):	glDeleteTextures(self.tex_names)
	
	def optimally_resize(self):
		if isinstance(self.gl_context_parent,EMImageMXWidget):
			self.qt_context_parent.resize(*self.get_parent_suggested_size())
		else:
			self.gl_widget.resize(*self.get_parent_suggested_size())
		
	
	def get_parent_suggested_size(self):
		if self.data != None and isinstance(self.data[0],EMData): 
			if len(self.data)<self.mx_cols :
				w=len(self.data)*(self.data[0].get_xsize()+2)
				hfac = 1
			else : 
				w=self.mx_cols*(self.data[0].get_xsize()+2)
				hfac = len(self.data)/self.mx_cols+1
			hfac *= self.data[0].get_ysize()
			if hfac > 512: hfac = 512
			if w > 512: w = 512
			return (int(w)+12,int(hfac)+12) # the 12 is related to the EMParentWin... hack...
		else: return (512+12,512+12)
	
	def update_window_title(self,filename):
		if isinstance(self.gl_context_parent,EMImageMXWidget):
			self.qt_context_parent.setWindowTitle(remove_directories_from_name(filename))
		else:
			if self.gl_widget != None:
				self.gl_widget.setWindowTitle(remove_directories_from_name(filename))
	
	def set_data(self,data,filename='',update_gl=True):
		
		if data == None or not isinstance(data,list) or len(data)==0:
			self.data = [] 
			return
		if not isinstance(data[0],EMData):
			print "strange error in set_data"
			return

		self.filename = filename
		self.update_window_title(self.filename)
		self.data=data
		
		self.force_display_update()
		self.nimg=len(data)
		
		self.minden=data[0].get_attr("mean")
		self.maxden=1
		self.mindeng=self.minden
		self.maxdeng=1
		
		for i in data:
			if i == None: continue
			if i.get_zsize()!=1 :
				self.data=None
				if update_gl: self.updateGL()
				return
			mean=i.get_attr("mean")
			sigma=i.get_attr("sigma")
			m0=i.get_attr("minimum")
			m1=i.get_attr("maximum")
			if sigma == 0: continue

			self.minden=min(self.minden,max(m0,mean-3.0*sigma))
			self.maxden=max(self.maxden,min(m1,mean+3.0*sigma))
			self.mindeng=min(self.mindeng,max(m0,mean-5.0*sigma))
			self.maxdeng=max(self.maxdeng,min(m1,mean+5.0*sigma))

		self.max_idx = len(data)

		if self.font_render_mode == EMGUIModule.FTGL:
			self.font_size = data[0].get_xsize()/6
			self.font_renderer.set_face_size(self.font_size)
		for i,d in enumerate(data):
			try:
				d.set_attr("original_number",i)
			except:pass

		#if update_gl: self.updateGL()

	def updateGL(self):
		try: self.gl_widget.updateGL()
		except: pass
		
	def set_den_range(self,x0,x1,update_gl=True):
		"""Set the range of densities to be mapped to the 0-255 pixel value range"""
		self.minden=x0
		self.maxden=x1
		if update_gl: self.updateGL()
	
	def get_density_min(self):
		return self.minden
	
	def get_density_max(self):
		return self.maxden
	
	def get_gamma(self):
		return self.gamma
	
	def set_origin(self,x,y,update_gl=True):
		"""Set the display origin within the image"""
		self.origin=(x,y)
		self.targetorigin=None
		if update_gl: self.updateGL()
		
	def set_scale(self,newscale,adjust=True,update_gl=True):
		"""Adjusts the scale of the display. Tries to maintain the center of the image at the center"""
		
		if self.targetorigin : 
			self.origin=self.targetorigin
			self.targetorigin=None
			
		if self.data and len(self.data)>0 and (self.data[0].get_ysize()*newscale>self.gl_widget.height() or self.data[0].get_xsize()*newscale>self.gl_widget.width()):
			newscale=min(float(self.gl_widget.height())/self.data[0].get_ysize(),float(self.gl_widget.width())/self.data[0].get_xsize())
			if self.inspector: self.inspector.scale.setValue(newscale)
			
			
#		yo=self.height()-self.origin[1]-1
		yo=self.origin[1]
#		self.origin=(newscale/self.scale*(self.width()/2+self.origin[0])-self.width()/2,newscale/self.scale*(self.height()/2+yo)-self.height()/2)
#		self.origin=(newscale/self.scale*(self.width()/2+self.origin[0])-self.width()/2,newscale/self.scale*(yo-self.height()/2)+self.height()/2)
		if adjust:
			self.origin=(newscale/self.scale*(self.gl_widget.width()/2+self.origin[0])-self.gl_widget.width()/2,newscale/self.scale*(self.gl_widget.height()/2+self.origin[1])-self.gl_widget.height()/2)
#		print self.origin,newscale/self.scale,yo,self.height()/2+yo
		
		self.scale=newscale
		if update_gl: self.updateGL()
		
	def set_density_min(self,val,update_gl=True):
		self.minden=val
		if update_gl: self.updateGL()
		
	def set_density_max(self,val,update_gl=True):
		self.maxden=val
		if update_gl: self.updateGL()

	def get_mmode(self):
		return self.mmode
	
	def set_mouse_mode(self,mode):
		self.mmode = mode
		meh  = self.mouse_event_handler
		try:
			self.mouse_event_handler = self.mouse_event_handlers[self.mmode]
		except:
			print "unknown mode:",mode
			self.mouse_event_handler = meh # just keep the old one
		
	def set_gamma(self,val,update_gl=True):
		self.gamma=val
		if update_gl:self.updateGL()
	
	def set_mx_cols(self,val,update_gl=True):
		if self.mx_cols==val: return
		if val<1 : val=1
		
		self.mx_cols=val
		if update_gl: self.updateGL()
		try:
			if self.inspector.nrow.value!=val :
				self.inspector.nrow.setValue(val)
		except: pass
		
	def set_n_show(self,val,update_gl=True):
		self.nshow=val
		if update_gl: self.updateGL()

	def set_invert(self,val,update_gl=True):
		if val: self.invert=1
		else : self.invert=0
		if update_gl: self.updateGL()

	def timeout(self):
		"""Called a few times each second when idle for things like automatic scrolling"""
		if self.targetorigin :
			vec=(self.targetorigin[0]-self.origin[0],self.targetorigin[1]-self.origin[1])
			h=hypot(vec[0],vec[1])
			if h<=self.targetspeed :
				self.origin=self.targetorigin
				self.targetorigin=None
			else :
				vec=(vec[0]/h,vec[1]/h)
				self.origin=(self.origin[0]+vec[0]*self.targetspeed,self.origin[1]+vec[1]*self.targetspeed)
			#self.updateGL()
	
	def get_max_matrix_ranges(self):
		return get_matrix_ranges(0,0)
	
	def get_matrix_ranges(self,x,y):
		n=len(self.data)
		w=int(min(self.data[0].get_xsize()*self.scale,self.gl_widget.width()))
		h=int(min(self.data[0].get_ysize()*self.scale,self.gl_widget.height()))
		
		yoff = 0
		if y < 0:
			ybelow = floor(-y/(h+2))
			yoff = ybelow*(h+2)+y
			visiblerows = int(ceil(float(self.gl_widget.height()-yoff)/(h+2)))
		else: visiblerows = int(ceil(float(self.gl_widget.height()-y)/(h+2)))
				
		maxrow = int(ceil(float(n)/self.mx_cols))
		ystart =-y/(h+2)
		if ystart < 0: ystart = 0
		elif ystart > 0:
			ystart = int(ystart)
			visiblerows = visiblerows + ystart
		if visiblerows > maxrow: visiblerows = maxrow

		xoff = 0
		if x < 0:
			xbelow = floor(-x/(w+2))
			xoff = xbelow*(w+2)+x
			visiblecols =  int(ceil(float(self.gl_widget.width()-xoff)/(w+2)))
		else: visiblecols =  int(ceil(float(self.gl_widget.width()-x)/(w+2)))

		xstart =-x/(w+2)
		if xstart < 0:
			xstart = 0
		else:
			xstart = int(xstart)
			visiblecols = visiblecols + xstart
		if visiblecols > self.mx_cols:
			visiblecols = self.mx_cols
	
		return [int(xstart),int(visiblecols),int(ystart),int(visiblerows)]
	
	def display_state_changed(self):
		display_states = []
		display_states.append(self.gl_widget.width())
		display_states.append(self.gl_widget.height())
		display_states.append(self.origin[0])
		display_states.append(self.origin[1])
		display_states.append(self.scale)
		display_states.append(self.invert)
		display_states.append(self.minden)
		display_states.append(self.maxden)
		display_states.append(self.gamma)
		display_states.append(self.mx_cols)
		display_states.append(self.draw_background)
		display_states.append(self.img_num_offset)
		if len(self.display_states) == 0:
			self.display_states = display_states
			return True
		else:
			for i in range(len(display_states)):
				
				if display_states[i] != self.display_states[i]:
					self.display_states = display_states
					return True
		
		return False
			
	
	def set_font_render_resolution(self):
		if self.font_render_mode != EMGUIModule.FTGL:
			print "error, can't call set_font_render_resolution if the mode isn't FTGL"
			
		#self.font_renderer.set_face_size(int(self.gl_widget.height()*0.015))
		#print "scale is",self.scale
	
	def __draw_backdrop(self):
		light = glIsEnabled(GL_LIGHTING)
		glDisable(GL_LIGHTING)
	
		glColor(.9,.9,.9)
		glBegin(GL_QUADS)
		glVertex(0,0,-1)
		glColor(.9,.9,.9)
		glVertex(self.gl_widget.width(),0,-1)
		glColor(.9,.9,.9)
		glVertex(self.gl_widget.width(),self.gl_widget.height(),-1)
		glColor(.9,.9,.9)
		glVertex(0,self.gl_widget.height(),-1)
		glEnd()
		if light: glEnable(GL_LIGHTING)
	
	
	def render(self):
		if not self.data : return
		if self.font_render_mode == EMGUIModule.FTGL: self.set_font_render_resolution()
		self.image_change_count = self.data[0].get_changecount() # this is important when the user has more than one display instance of the same image, for instance in e2.py if 
		render = False
		if self.use_display_list:
			
			if self.display_state_changed():
				if self.main_display_list != 0:
					glDeleteLists(self.main_display_list,1)
					self.main_display_list = 0

			if self.main_display_list == 0:
				self.main_display_list = glGenLists(1)
				glNewList(self.main_display_list,GL_COMPILE)
				render = True
		else: render = True
		
		if render: 
			if self.draw_background:
				self.__draw_backdrop()
				
			glMaterial(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,(.2,.2,.8,1.0))
			glMaterial(GL_FRONT,GL_SPECULAR,(.2,.2,.8,1.0))
			glMaterial(GL_FRONT,GL_SHININESS,100.0)
		
			#for i in self.data:
				#self.changec[i]=i.get_attr("changecount")
			
			if not self.invert : pixden=(0,255)
			else: pixden=(255,0)
			
			n=len(self.data)
			self.hist=numpy.zeros(256)
			#if len(self.coords)>n : self.coords=self.coords[:n] # dont know what this does? Had to comment out, changing from a list to a dictionary
			glColor(0.5,1.0,0.5)
			glLineWidth(2)
			try:
				# we render the 16x16 corner of the image and decide if it's light or dark to decide the best way to 
				# contrast the text labels...
				a=self.data[0].render_amp8(0,0,16,16,16,self.scale,pixden[0],pixden[1],self.minden,self.maxden,self.gamma,4)
				ims=[ord(pv) for pv in a]
				if sum(ims)>32768 : txtcol=(0.0,0.0,0.0)
				else : txtcol=(1,1,1.0)
			except: txtcol=(1.0,1.0,1.0)
	
			if ( len(self.tex_names) > 0 ):	glDeleteTextures(self.tex_names)
			self.tex_names = []
	
			self.nshown=0
			
			x,y=-self.origin[0],-self.origin[1]
			w=int(min(self.data[0].get_xsize()*self.scale,self.gl_widget.width()))
			h=int(min(self.data[0].get_ysize()*self.scale,self.gl_widget.height()))
			
			[xstart,visiblecols,ystart,visiblerows] = self.get_matrix_ranges(x,y)
				
			#print "rows",visiblerows-ystart,"cols",visiblecols-xstart
			#print "yoffset",yoff,"xoffset",xoff
			#print (visiblerows-ystart)*(h+2)+yoff,self.gl_widget.height(),"height",(visiblecols-xstart)*(w+2)+xoff,self.gl_widget.width()		
			invscale=1.0/self.scale
			self.coords = {}
			for row in range(ystart,visiblerows):
				for col in range(xstart,visiblecols):
					i = (row)*self.mx_cols+col
					try:
						if self.data[i] == None: continue
					except: continue
					#print i,n
					if i >= n : break
					tx = int((w+2)*(col) + x)
					ty = int((h+2)*(row) + y)
					tw = w
					th = h
					rx = 0	#render x
					ry = 0	#render y
					#print "Prior",i,':',row,col,tx,ty,tw,th,y,x
					drawlabel = True
					if (tx+tw) > self.gl_widget.width():
						tw = int(self.gl_widget.width()-tx)
					elif tx<0:
						drawlabel=False
						rx = int(ceil(-tx*invscale))
						tw=int(w+tx)
						tx = 0
						
	
					#print h,row,y
					#print "Prior",i,':',row,col,tx,ty,tw,th,'offsets',yoffset,xoffset
					if (ty+th) > self.gl_widget.height():
						#print "ty + th was greater than",self.gl_widget.height()
						th = int(self.gl_widget.height()-ty)
					elif ty<0:
						drawlabel = False
						ry = int(ceil(-ty*invscale))
						th=int(h+ty)
						ty = 0
						
					#print i,':',row,col,tx,ty,tw,th,'offsets',yoffset,xoffset
					if th < 0 or tw < 0:
						#weird += 1
						#print "weirdness"
						#print col,row,
						continue
					
					try:
						exc = self.data[i].get_attr("excluded")
						if exc == True:
							light = glIsEnabled(GL_LIGHTING)
							glEnable(GL_LIGHTING)
							width = tw/2.0
							height = th/2.0
							glPushMatrix()
							glTranslatef(tx+width,ty+height,0)
							glScale(width,height,1.0)
							self.__render_excluded_square()
							glPopMatrix()
							if not light: glEnable(GL_LIGHTING)
						else: raise
					except: 
							pass
					#i = (row+yoffset)*self.mx_cols+col+xoffset
					#print i,':',row,col,tx,ty,tw,th
					shown = True
					#print rx,ry,tw,th,self.gl_widget.width(),self.gl_widget.height(),self.origin
					if not self.glflags.npt_textures_unsupported():
						a=self.data[i].render_amp8(rx,ry,tw,th,(tw-1)/4*4+4,self.scale,pixden[0],pixden[1],self.minden,self.maxden,self.gamma,2)
						self.texture(a,tx,ty,tw,th)
					else:
						a=self.data[i].render_amp8(rx,ry,tw,th,(tw-1)/4*4+4,self.scale,pixden[0],pixden[1],self.minden,self.maxden,self.gamma,6)
						glRasterPos(tx,ty)
						glDrawPixels(tw,th,GL_LUMINANCE,GL_UNSIGNED_BYTE,a)
							
					
					hist2=numpy.fromstring(a[-1024:],'i')
					self.hist+=hist2
					# render labels		
					if drawlabel:
						self.__draw_mx_text(tx,ty,txtcol,i)
						
					self.coords[i]=(tx,ty,tw,th)
					
					if shown : self.nshown+=1
			
			for i in self.selected:
				try:
					data = self.coords[i]	
					glColor(0.5,0.5,1.0)
					glBegin(GL_LINE_LOOP)
					glVertex(data[0],data[1])
					glVertex(data[0]+data[2],data[1])
					glVertex(data[0]+data[2],data[1]+data[3])
					glVertex(data[0],data[1]+data[3])
					glEnd()
				except:
					# this means the box isn't visible!
					pass
			# If the user is lost, help him find himself again...
			if self.nshown==0 : 
				try: self.targetorigin=(0,self.coords[self.selected[0]][1]-self.gl_widget.height()/2+self.data[0].get_ysize()*self.scale/2)
				except: self.targetorigin=(0,0)
				self.targetspeed=100.0
			
			if self.inspector : self.inspector.set_hist(self.hist,self.minden,self.maxden)
		else:
			try:
				glCallList(self.main_display_list)
			except: pass
		
		if self.use_display_list and render :
			glEndList()
			glCallList(self.main_display_list)
	
	def __render_excluded_square(self):
		glBegin(GL_QUADS)
		glColor(0,0,0)
		glNormal(-.1,.1,1)
		glVertex(-1,1,0.1)
		glColor(0.15,0.15,0.15)
		glNormal(-1,1,-0.1)
		glVertex(-1,-1,0.1)	
		glColor(0.3,0.3,0.3)
		glNormal(.1,-.1,1)
		glVertex(1,-1,0.1)
		glColor(0.22,0.22,0.22)
		glNormal(1,-1,0.1)
		glVertex(1,1,0.1)
		glEnd()
		#glPopMatrix()
	
	def __draw_mx_text(self,tx,ty,txtcol,i):
		if self.font_render_mode == EMGUIModule.FTGL:
			
			glEnable(GL_TEXTURE_2D)
			glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
			lighting = glIsEnabled(GL_LIGHTING)
			glDisable(GL_LIGHTING)
			#glEnable(GL_NORMALIZE)
			tagy = ty
			glColor(*txtcol)
			#glMaterial(GL_FRONT,GL_AMBIENT_AND_DIFFUSE,txtcol)
			#glMaterial(GL_FRONT,GL_SPECULAR,txtcol)
			#glMaterial(GL_FRONT,GL_SHININESS,100.0)
			for v in self.valstodisp:
				glPushMatrix()
				glTranslate(tx,tagy,0)
				#bbox = self.bounding_box(str(i))
				glTranslate(4,4,0.2)

				#glTranslate(-(bbox[0]-bbox[3])/2,-(bbox[1]-bbox[4])/2,-(bbox[2]-bbox[5])/2)
				#glRotate(-10,1,0,0)
				#glTranslate((bbox[0]-bbox[3])/2,(bbox[1]-bbox[4])/2,(bbox[2]-bbox[5])/2)
				
				glScale(self.scale/2.0,self.scale/2.0,1)
				if v=="Img #" : 
					#print i,self.img_num_offset,self.max_idx,(i+self.img_num_offset)%self.max_idx,
					idx = i+self.img_num_offset
					if idx != 0: idx = idx%self.max_idx
					self.font_renderer.render_string(str(idx))
				else : 
					av=self.data[i].get_attr(v)
					if isinstance(av,float) : avs="%1.4g"%av
					else: avs=str(av)
					try: self.font_renderer.render_string(str(avs))
					except:	self.font_renderer.render_string("------")
				tagy+=self.font_renderer.get_face_size()*self.scale/2.0
				glPopMatrix()
			if not lighting:
				glDisable(GL_LIGHTING)
			glDisable(GL_TEXTURE_2D)
		elif self.font_render_mode == EMGUIModule.GLUT:
			tagy = ty
			glColor(*txtcol)
			for v in self.valstodisp:
				if v=="Img #" :
					idx = i+self.img_num_offset
					if idx != 0: idx = idx%self.max_idx
					self.render_text(tx,tagy,"%d"%idx)
				else : 
					av=self.data[i].get_attr(v)
					if isinstance(av,float) : avs="%1.4g"%av
					else: avs=str(av)
					try: self.render_text(tx,tagy,str(avs))
					except:	self.render_text(tx,tagy,"------")
				tagy+=16
								
	
	def bounding_box(self,character):
		try: self.text_bbs[character]
		except:
			 self.text_bbs[character] = self.font_renderer.bounding_box(character)
			 
		return self.text_bbs[character]
	
	def texture(self,a,x,y,w,h):
		
		tex_name = glGenTextures(1)
		if ( tex_name <= 0 ):
			raise("failed to generate texture name")
		
		width = w/2.0
		height = h/2.0
		
		glPushMatrix()
		glTranslatef(x+width,y+height,0)
			
		glBindTexture(GL_TEXTURE_2D,tex_name)
		glPixelStorei(GL_UNPACK_ALIGNMENT,4)
		glTexImage2D(GL_TEXTURE_2D,0,GL_LUMINANCE,w,h,0,GL_LUMINANCE,GL_UNSIGNED_BYTE, a)
		
		glEnable(GL_TEXTURE_2D)
		glBindTexture(GL_TEXTURE_2D, tex_name)
		
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
		# using GL_NEAREST ensures pixel granularity
		# using GL_LINEAR blurs textures and makes them more difficult
		# to interpret (in cryo-em)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
		# this makes it so that the texture is impervious to lighting
		glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
		
		
		# POSITIONING POLICY - the texture occupies the entire screen area
		glBegin(GL_QUADS)
		
		glTexCoord2f(0,0)
		glVertex2f(-width,height)
				
		glTexCoord2f(0,1)
		glVertex2f(-width,-height)
			
		glTexCoord2f(1,1)
		glVertex2f(width,-height)
		
		glTexCoord2f(1,0)
		glVertex2f(width,height)
		glEnd()
		
		glDisable(GL_TEXTURE_2D)
		
		glPopMatrix()
		self.tex_names.append(tex_name)
	
	def render_text(self,x,y,s):
#	     print 'in render Text'
		glRasterPos(x+2,y+2)
		for c in s:
			return
			GLUT.glutBitmapCharacter(GLUT.GLUT_BITMAP_9_BY_15,ord(c))

	def resize_event(self, width, height):
		if self.data and len(self.data)>0 :
			if self.data[0].get_xsize()*self.scale != 0:
				self.set_mx_cols(int(self.gl_widget.width()/(self.data[0].get_xsize()*self.scale)))
			else:
				print "error", self.data[0].get_xsize(),self.scale
		#except: pass
		if self.data and len(self.data)>0 and (self.data[0].get_ysize()*self.scale>self.gl_widget.height() or self.data[0].get_xsize()*self.scale>self.gl_widget.width()):
			self.scale=min(float(self.gl_widget.height())/self.data[0].get_ysize(),float(self.gl_widget.width())/self.data[0].get_xsize())
				
	def is_visible(self,n):
		try: return self.coords[n][4]
		except: return False
	
	def scroll_to(self,n,yonly=0):
		"""Moves image 'n' to the center of the display"""
#		print self.origin,self.coords[0],self.coords[1]
#		try: self.origin=(self.coords[n][0]-self.width()/2,self.coords[n][1]+self.height()/2)
#		try: self.origin=(self.coords[8][0]-self.width()/2-self.origin[0],self.coords[8][1]+self.height()/2-self.origin[1])
		if yonly :
			try: 
				self.targetorigin=(0,self.coords[n][1]-self.gl_widget.height()/2+self.data[0].get_ysize()*self.scale/2)
			except: return
		else:
			try: self.targetorigin=(self.coords[n][0]-self.gl_widget.width()/2+self.data[0].get_xsize()*self.scale/2,self.coords[n][1]-self.gl_widget.height()/2+self.data[0].get_ysize()*self.scale/2)
			except: return
		self.targetspeed=hypot(self.targetorigin[0]-self.origin[0],self.targetorigin[1]-self.origin[1])/20.0
#		print n,self.origin
#		self.updateGL()
	
	def set_selected(self,numlist,update_gl=True):
		"""pass an integer or a list/tuple of integers which should be marked as 'selected' in the
		display"""
		real_numlist = []
		for i in numlist:
			t = i-self.get_img_num_offset()
			if t != 0:
				t %= len(self.data)
			real_numlist.append(t)

		if isinstance(numlist,int) : numlist=[real_numlist]
		if isinstance(numlist,list) or isinstance(real_numlist,tuple) : self.selected=real_numlist
		else : self.selected=[]
		self.force_display_update()
		if update_gl: self.updateGL()
	
	def set_display_values(self,v2d,update_gl=True):
		"""Pass in a list of strings describing image attributes to overlay on the image, in order of display"""
		v2d.reverse()
		self.valstodisp=v2d
		self.display_states = []
		if update_gl: self.updateGL()

	def scr_to_img(self,vec):
		"""Converts screen location (ie - mouse event) to pixel coordinates within a single
		image from the matrix. Returns (image number,x,y) or None if the location is not within any
		of the contained images. """ 
		absloc=((vec[0]),(self.gl_widget.height()-(vec[1])))
		for item in self.coords.items():
			index = item[0]+self.img_num_offset
			if index != 0: index %= self.max_idx
			data = item[1]
			if absloc[0]>data[0] and absloc[1]>data[1] and absloc[0]<data[0]+data[2] and absloc[1]<data[1]+data[3] :
				return (index,(absloc[0]-data[0])/self.scale,(absloc[1]-data[1])/self.scale)
		return None
		
	def dragEnterEvent(self,event):
#		f=event.mime_data().formats()
#		for i in f:
#			print str(i)
		
		if event.source()==self:
			event.setDropAction(Qt.MoveAction)
			event.accept()
		elif event.provides("application/x-eman"):
			event.setDropAction(Qt.CopyAction)
			event.accept()

	def save_data(self):
		if self.data==None or len(self.data)==0:
			print "there is no data to save"
			return

		# Get the output filespec
		fsp=QtGui.QFileDialog.getSaveFileName(self, "Select File","","","")
		fsp=str(fsp)
		
		if fsp != '':
			for d in self.data:
				d.write_image(fsp,-1)
		
	def save_lst(self):
		if self.data==None or len(self.data)==0:
			print "there is not data to write"
			return
		
		origname = self.get_image_file_name()
		if origname == None:
			print "error, origname is none. Either the data is not already on disk or there is a bug"
			return

		# Get the output filespec
		fsp=QtGui.QFileDialog.getSaveFileName(self, "Specify lst file to save","","","")
		fsp=str(fsp)
		
		if fsp != '':
			f = file(fsp,'w')
			f.write('#LST\n')
			
			for d in self.data:
				#try:
					f.write(str(d.get_attr('original_number')) +'\t'+origname+'\n')
				#except:
					#pass
						
			f.close()
	
	def dropEvent(self,event):
		lc=self.scr_to_img((event.pos().x(),event.pos().y()))
		if event.source()==self:
#			print lc
			n=int(event.mime_data().text())
			if not lc : lc=[len(self.data)]
			if n>lc[0] : 
				self.data.insert(lc[0],self.data[n])
				del self.data[n+1]
			else : 
				self.data.insert(lc[0]+1,self.data[n])
				del self.data[n]
			event.setDropAction(Qt.MoveAction)
			event.accept()
		elif EMAN2.GUIbeingdragged:
			self.data.append(EMAN2.GUIbeingdragged)
			self.set_data(self.data)
			EMAN2.GUIbeingdragged=None
		elif event.provides("application/x-eman"):
			x=loads(event.mime_data().data("application/x-eman"))
			if not lc : self.data.append(x)
			else : self.data.insert(lc[0],x)
			self.set_data(self.data)
			event.acceptProposedAction()

	def keyPressEvent(self,event):
		ystep = (self.data[0].get_ysize()*self.scale + 2)/2.0
		xstep = (self.data[0].get_xsize()*self.scale + 2)/2.0
		if event.key()==Qt.Key_Up :
			self.origin=(self.origin[0],self.origin[1]+ystep)
			self.updateGL()
		elif event.key()==Qt.Key_Down :
			self.origin=(self.origin[0],self.origin[1]-ystep)
			self.updateGL()
		elif event.key()==Qt.Key_Left :
			self.origin=(self.origin[0]+xstep,self.origin[1])
			self.updateGL()
		elif event.key()==Qt.Key_Right:
			self.origin=(self.origin[0]-xstep,self.origin[1])
			self.updateGL()
			
	def mousePressEvent(self, event):
		if event.button()==Qt.MidButton or (event.button()==Qt.LeftButton and event.modifiers()&Qt.AltModifier):
			self.show_inspector(1)
#			self.emit(QtCore.SIGNAL("inspector_shown"),event)
		elif event.button()==Qt.RightButton or (event.button()==Qt.LeftButton and event.modifiers()&Qt.AltModifier):
			app =  QtGui.QApplication.instance()
			try:
				app.setOverrideCursor(Qt.ClosedHandCursor)
			except: # if we're using a version of qt older than 4.2 than we have to use this...
				app.setOverrideCursor(Qt.SizeAllCursor)
				
			self.mousedrag=(event.x(),event.y())
		else: self.mouse_event_handler.mouse_down(event)
		
	def mouseMoveEvent(self, event):
		if self.mousedrag:
			self.origin=(self.origin[0]+self.mousedrag[0]-event.x(),self.origin[1]-self.mousedrag[1]+event.y())
			self.mousedrag=(event.x(),event.y())
			try:self.gl_widget.updateGL()
			except: pass
		else: self.mouse_event_handler.mouse_move(event)
		
	def mouseReleaseEvent(self, event):
		app =  QtGui.QApplication.instance()
		app.setOverrideCursor(Qt.ArrowCursor)
		lc=self.scr_to_img((event.x(),event.y()))
		if self.mousedrag:
			self.mousedrag=None
		else: self.mouse_event_handler.mouse_up(event)
			
	def wheelEvent(self, event):
		if event.delta() > 0:
			self.set_scale( self.scale * self.mag,False )
		elif event.delta() < 0:
			self.set_scale(self.scale * self.invmag,False)
		self.resize_event(self.gl_widget.width(),self.gl_widget.height())
		# The self.scale variable is updated now, so just update with that
		if self.inspector: self.inspector.set_scale(self.scale)
	
	def mouseDoubleClickEvent(self,event):
		pass
		
		
	def leaveEvent(self):
		if self.mousedrag:
			self.mousedrag=None
			
	def get_frame_buffer(self):
		return self.gl_widget.get_frame_buffer()

class EMImageInspectorMX(QtGui.QWidget):
	def __init__(self,target,allow_col_variation=False,allow_window_variation=False,allow_opt_button=False):
		QtGui.QWidget.__init__(self,None)
		self.target=target
		
		self.vals = QtGui.QMenu()
		self.valsbut = QtGui.QPushButton("Values")
		self.valsbut.setMenu(self.vals)
		
		try:
			self.vals.clear()
			vn=self.target.get_image(0).get_attr_dict().keys()
			vn.sort()
			for i in vn:
				action=self.vals.addAction(i)
				action.setCheckable(1)
				action.setChecked(0)
		except Exception, inst:
			print type(inst)     # the exception instance
			print inst.args      # arguments stored in .args
			print int
		
		action=self.vals.addAction("Img #")
		action.setCheckable(1)
		action.setChecked(1)
		
		self.vbl = QtGui.QVBoxLayout(self)
		self.vbl.setMargin(2)
		self.vbl.setSpacing(6)
		self.vbl.setObjectName("vboxlayout")
		
		self.hbl3 = QtGui.QHBoxLayout()
		self.hbl3.setMargin(0)
		self.hbl3.setSpacing(6)
		self.hbl3.setObjectName("hboxlayout")
		self.vbl.addLayout(self.hbl3)
		
		self.hist = ImgHistogram(self)
		self.hist.setObjectName("hist")
		self.hbl3.addWidget(self.hist)

		self.vbl2 = QtGui.QVBoxLayout()
		self.vbl2.setMargin(0)
		self.vbl2.setSpacing(6)
		self.vbl2.setObjectName("vboxlayout")
		self.hbl3.addLayout(self.vbl2)

		self.bsavedata = QtGui.QPushButton("Save")
		self.vbl2.addWidget(self.bsavedata)
		
		self.bsavelst = QtGui.QPushButton("Save Lst")
		self.vbl2.addWidget(self.bsavelst)

		if allow_opt_button:
			self.opt_fit = QtGui.QPushButton("Opt. Fit")
			self.vbl2.addWidget(self.opt_fit)

		self.bsnapshot = QtGui.QPushButton("Snap")
		self.vbl2.addWidget(self.bsnapshot)

		# This shows the mouse mode buttons
		self.hbl2 = QtGui.QHBoxLayout()
		self.hbl2.setMargin(0)
		self.hbl2.setSpacing(6)
		self.hbl2.setObjectName("hboxlayout")
		self.vbl.addLayout(self.hbl2)
		
		#self.mmeas = QtGui.QPushButton("Meas")
		#self.mmeas.setCheckable(1)
		#self.hbl2.addWidget(self.mmeas)

		self.mapp = QtGui.QPushButton("App")
		self.mapp.setCheckable(1)
		self.hbl2.addWidget(self.mapp)
		
		self.mdel = QtGui.QPushButton("Del")
		self.mdel.setCheckable(1)
		self.hbl2.addWidget(self.mdel)

		self.mdrag = QtGui.QPushButton("Drag")
		self.mdrag.setCheckable(1)
		self.mdrag.setDefault(1)
		self.hbl2.addWidget(self.mdrag)

		self.bg=QtGui.QButtonGroup()
		self.bg.setExclusive(1)
#		self.bg.addButton(self.mmeas)
		self.bg.addButton(self.mapp)
		self.bg.addButton(self.mdel)
		self.bg.addButton(self.mdrag)

		self.hbl = QtGui.QHBoxLayout()
		self.hbl.setMargin(0)
		self.hbl.setSpacing(6)
		self.hbl.setObjectName("hboxlayout")
		self.vbl.addLayout(self.hbl)
		
		self.hbl.addWidget(self.valsbut)
		
		if self.target.using_ftgl():
			self.font_label = QtGui.QLabel("font size:")
			self.font_label.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
			self.hbl.addWidget(self.font_label)
		
			self.font_size = QtGui.QSpinBox(self)
			self.font_size.setObjectName("nrow")
			self.font_size.setRange(1,50)
			self.font_size.setValue(int(self.target.get_font_size()))
			self.hbl.addWidget(self.font_size)
			
			QtCore.QObject.connect(self.font_size, QtCore.SIGNAL("valueChanged(int)"), target.set_font_size)
		
		
		if allow_col_variation:
			self.lbl2 = QtGui.QLabel("#/col:")
			self.lbl2.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
			self.hbl.addWidget(self.lbl2)
			
			self.ncol = QtGui.QSpinBox(self)
			self.ncol.setObjectName("ncol")
			self.ncol.setRange(1,50)
			self.ncol.setValue(self.target.get_rows())
			self.hbl.addWidget(self.ncol)
			
		self.lbl = QtGui.QLabel("#/row:")
		self.lbl.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
		self.hbl.addWidget(self.lbl)
		
		self.nrow = QtGui.QSpinBox(self)
		self.nrow.setObjectName("nrow")
		self.nrow.setRange(1,50)
		self.nrow.setValue(self.target.get_cols())
		self.hbl.addWidget(self.nrow)
		
		if allow_window_variation:
			self.lbl3 = QtGui.QLabel("#/mx:")
			self.lbl3.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
			self.hbl.addWidget(self.lbl3)
			
			self.nmx = QtGui.QSpinBox(self)
			self.nmx.setObjectName("ncol")
			self.nmx.setRange(1,50)
			self.nmx.setValue(self.target.get_mxs())
			self.hbl.addWidget(self.nmx)
		
		self.scale = ValSlider(self,(0.1,5.0),"Mag:")
		self.scale.setObjectName("scale")
		self.scale.setValue(1.0)
		self.vbl.addWidget(self.scale)
		
		self.mins = ValSlider(self,label="Min:")
		minden = self.target.get_density_min()
		maxden = self.target.get_density_max()
		self.mins.setValue(minden)
		self.mins.setRange(minden,maxden)
		self.mins.setObjectName("mins")
		self.vbl.addWidget(self.mins)
		
		self.maxs = ValSlider(self,label="Max:")
		self.maxs.setValue(maxden)
		self.maxs.setRange(minden,maxden)
		self.maxs.setObjectName("maxs")
		self.vbl.addWidget(self.maxs)
		
		self.brts = ValSlider(self,(-1.0,1.0),"Brt:")
		self.brts.setObjectName("brts")
		self.vbl.addWidget(self.brts)
		
		self.conts = ValSlider(self,(0.0,1.0),"Cont:")
		self.conts.setObjectName("conts")
		self.vbl.addWidget(self.conts)
		
		self.gammas = ValSlider(self,(.5,2.0),"Gam:")
		self.gammas.setObjectName("gamma")
		self.gammas.setValue(1.0)
		self.vbl.addWidget(self.gammas)

		self.lowlim=0
		self.highlim=1.0
		
		self.update_brightness_contrast()
		self.hist.set_data(self.target.get_hist(),minden,maxden)
		self.busy=0
		
		QtCore.QObject.connect(self.vals, QtCore.SIGNAL("triggered(QAction*)"), self.newValDisp)
		QtCore.QObject.connect(self.nrow, QtCore.SIGNAL("valueChanged(int)"), target.set_mx_cols)
		if allow_col_variation:
			QtCore.QObject.connect(self.ncol, QtCore.SIGNAL("valueChanged(int)"), target.set_mx_rows)
		if allow_window_variation:
			QtCore.QObject.connect(self.nmx, QtCore.SIGNAL("valueChanged(int)"), target.set_mxs)
		
		QtCore.QObject.connect(self.scale, QtCore.SIGNAL("valueChanged"), target.set_scale)
		QtCore.QObject.connect(self.mins, QtCore.SIGNAL("valueChanged"), self.newMin)
		QtCore.QObject.connect(self.maxs, QtCore.SIGNAL("valueChanged"), self.newMax)
		QtCore.QObject.connect(self.brts, QtCore.SIGNAL("valueChanged"), self.newBrt)
		QtCore.QObject.connect(self.conts, QtCore.SIGNAL("valueChanged"), self.newCont)
		QtCore.QObject.connect(self.gammas, QtCore.SIGNAL("valueChanged"), self.newGamma)
		
		#QtCore.QObject.connect(self.mmeas, QtCore.SIGNAL("clicked(bool)"), self.setMeasMode)
		QtCore.QObject.connect(self.mapp, QtCore.SIGNAL("clicked(bool)"), self.setAppMode)
		QtCore.QObject.connect(self.mdel, QtCore.SIGNAL("clicked(bool)"), self.setDelMode)
		QtCore.QObject.connect(self.mdrag, QtCore.SIGNAL("clicked(bool)"), self.setDragMode)

		QtCore.QObject.connect(self.bsavedata, QtCore.SIGNAL("clicked(bool)"), self.save_data)
		if allow_opt_button:
			QtCore.QObject.connect(self.opt_fit, QtCore.SIGNAL("clicked(bool)"), self.target.optimize_fit)
		QtCore.QObject.connect(self.bsavelst, QtCore.SIGNAL("clicked(bool)"), self.save_lst)
		QtCore.QObject.connect(self.bsnapshot, QtCore.SIGNAL("clicked(bool)"), self.snapShot)
	
	def get_desktop_hint(self):
		return "inspector"
	
	
	def set_scale(self,val):
		if self.busy : return
		self.busy=1
		self.scale.setValue(val)
		self.busy=0
		
	def set_n_cols(self,val):
		self.nrow.setValue(val)
		
	def set_n_rows(self,val):
		self.ncol.setValue(val)
		
	def set_mxs(self,val):
		self.nmx = val
	
	def save_data(self):
		self.target.save_data()
		
	def save_lst(self):
		self.target.save_lst()
			
	def snapShot(self):
		"Save a screenshot of the current image display"
		
		#try:
		qim=self.target.get_frame_buffer()
		#except:
			#QtGui.QMessageBox.warning ( self, "Framebuffer ?", "Could not read framebuffer")
		
		# Get the output filespec
		fsp=QtGui.QFileDialog.getSaveFileName(self, "Select File")
		fsp=str(fsp)
		
		qim.save(fsp,None,90)
		
	def newValDisp(self):
		v2d=[str(i.text()) for i in self.vals.actions() if i.isChecked()]
		self.target.set_display_values(v2d)

	def setAppMode(self,i):
		self.target.set_mouse_mode("app")
	
	#def setMeasMode(self,i):
		#self.target.set_mouse_mode("meas")
	
	def setDelMode(self,i):
		self.target.set_mouse_mode("del")
	
	def setDragMode(self,i):
		self.target.set_mouse_mode("drag")

	def newMin(self,val):
		if self.busy : return
		self.busy=1
		self.target.set_density_min(val)

		self.update_brightness_contrast()
		self.busy=0
		
	def newMax(self,val):
		if self.busy : return
		self.busy=1
		self.target.set_density_max(val)
		self.update_brightness_contrast()
		self.busy=0
	
	def newBrt(self,val):
		if self.busy : return
		self.busy=1
		self.update_min_max()
		self.busy=0
		
	def newCont(self,val):
		if self.busy : return
		self.busy=1
		self.update_min_max()
		self.busy=0
	
	def newGamma(self,val):
		if self.busy : return
		self.busy=1
		self.target.set_gamma(val)
		self.busy=0

	def update_brightness_contrast(self):
		b=0.5*(self.mins.value+self.maxs.value-(self.lowlim+self.highlim))/((self.highlim-self.lowlim))
		c=(self.mins.value-self.maxs.value)/(2.0*(self.lowlim-self.highlim))
		self.brts.setValue(-b)
		self.conts.setValue(1.0-c)
		
	def update_min_max(self):
		x0=((self.lowlim+self.highlim)/2.0-(self.highlim-self.lowlim)*(1.0-self.conts.value)-self.brts.value*(self.highlim-self.lowlim))
		x1=((self.lowlim+self.highlim)/2.0+(self.highlim-self.lowlim)*(1.0-self.conts.value)-self.brts.value*(self.highlim-self.lowlim))
		self.mins.setValue(x0)
		self.maxs.setValue(x1)
		self.target.set_den_range(x0,x1)
		
	def set_hist(self,hist,minden,maxden):
		self.hist.set_data(hist,minden,maxden)

	def set_limits(self,lowlim,highlim,curmin,curmax):
		self.lowlim=lowlim
		self.highlim=highlim
		self.mins.setRange(lowlim,highlim)
		self.maxs.setRange(lowlim,highlim)
		self.mins.setValue(curmin)
		self.maxs.setValue(curmax)


if __name__ == '__main__':
	em_app = EMStandAloneApplication()
	window = EMImageMXModule(application=em_app)
	
	if len(sys.argv)==1 : 
		data = []
		for i in range(0,200):
			e = test_image(Util.get_irand(0,9))
			e.set_attr("excluded",Util.get_irand(0,1))
			data.append(e)
			
		window.set_data(data) 
	else :
		a=EMData.read_images(sys.argv[1])
		window.set_file_name(sys.argv[1])
		window.set_data(a)
		
	em_app.show()
	window.optimally_resize()
	em_app.execute()

