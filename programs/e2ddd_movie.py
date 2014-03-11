#!/usr/bin/env python

#
# Author: Steven Ludtke, 02/12/2013 (sludtke@bcm.edu)
# Copyright (c) 2000-2013 Baylor College of Medicine
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  2111-1307 USA
#
#

import pprint
from EMAN2 import *
import sys


def main():
	progname = os.path.basename(sys.argv[0])
	usage = """prog [options] <ddd_movie_stack>

	This program will take an image stack from movie mode on a DirectElectron DDD camera and process it in various ways.
	The input stack should be <dark ref> <gain ref> <img 1> ...
	"""
	
	parser = EMArgumentParser(usage=usage,version=EMANVERSION)
	
	parser.add_argument("--align_frames", action="store_true",help="Perform whole-frame alignment of the stack",default=False)
	parser.add_argument("--align_frames_countmode", action="store_true",help="Perform whole-frame alignment of frames collected in counting mode",default=False)
	parser.add_argument("--save_aligned", action="store_true",help="Save aligned stack",default=False)
	parser.add_argument("--dark",type=str,default=None,help="Perform dark image correction using the specified image file")
	parser.add_argument("--gain",type=str,default=None,help="Perform gain image correction using the specified image file")
	parser.add_argument("--step",type=str,default="1,1",help="Specify <first>,<step>,[last]. Processes only a subset of the input data. ie- 0,2 would process all even particles. Same step used for all input files. [last] is exclusive. Default= 1,1 (first image skipped)")
	parser.add_argument("--frames",action="store_true",default=False,help="Save the dark/gain corrected frames")
	parser.add_argument("--movie", type=int,help="Display an n-frame averaged 'movie' of the stack, specify number of frames to average",default=0)
	parser.add_argument("--simpleavg", action="store_true",help="Will save a simple average of the dark/gain corrected frames (no alignment or weighting)",default=False)
	parser.add_argument("--avgs", action="store_true",help="Testing",default=False)
	parser.add_argument("--parallel", default=None, help="parallelism argument. This program supports only thread:<n>")
	parser.add_argument("--ppid", type=int, help="Set the PID of the parent process, used for cross platform PPID",default=-2)
	parser.add_argument("--verbose", "-v", dest="verbose", action="store", metavar="n", type=int, default=0, help="verbose level [0-9], higner number means higher level of verboseness")
	
	(options, args) = parser.parse_args()
	
	if len(args)<1:
		print usage
		parser.error("Specify input DDD stack")

	pid=E2init(sys.argv)

	if options.dark : 
		nd=EMUtil.get_image_count(options.dark)
		dark=EMData(options.dark,0)
		if nd>1:
			sigd=dark.copy()
			sigd.to_zero()
			a=Averagers.get("mean",{"sigma":sigd,"ignore0":1})
			print "Summing dark"
			for i in xrange(0,nd):
				if options.verbose:
					print " {}/{}   \r".format(i+1,nd),
					sys.stdout.flush()
				t=EMData(options.dark,i)
				t.process_inplace("threshold.clampminmax",{"minval":0,"maxval":t["mean"]+t["sigma"]*3.0,"tozero":1})
				a.add_image(t)
			dark=a.finish()
			dark.write_image(options.dark.rsplit(".",1)[0]+"_sum.hdf")
			sigd.write_image(options.dark.rsplit(".",1)[0]+"_sig.hdf")
		#else: dark.mult(1.0/99.0)
		dark.process_inplace("threshold.clampminmax.nsigma",{"nsigma":3.0})
		dark2=dark.process("normalize.unitlen")
	else : dark=None
	if options.gain : 
		nd=EMUtil.get_image_count(options.gain)
		gain=EMData(options.gain,0)
		if nd>1:
			sigg=gain.copy()
			sigg.to_zero()
			a=Averagers.get("mean",{"sigma":sigg,"ignore0":1})
			print "Summing gain"
			for i in xrange(0,nd):
				if options.verbose:
					print " {}/{}   \r".format(i+1,nd),
					sys.stdout.flush()
				t=EMData(options.gain,i)
				#t.process_inplace("threshold.clampminmax.nsigma",{"nsigma":4.0,"tozero":1})
				t.process_inplace("threshold.clampminmax",{"minval":0,"maxval":t["mean"]+t["sigma"]*3.0,"tozero":1})
				a.add_image(t)
			gain=a.finish()
			gain.write_image(options.gain.rsplit(".",1)[0]+"_sum.hdf")
			sigg.write_image(options.gain.rsplit(".",1)[0]+"_sig.hdf")
		#else: gain.mult(1.0/99.0)
		gain.process_inplace("threshold.clampminmax.nsigma",{"nsigma":3.0})
	else : gain=None
	if dark!=None and gain!=None : gain.sub(dark)												# dark correct the gain-reference
	if gain!=None : 
		gain.mult(1.0/gain["mean"])									# normalize so gain reference on average multiplies by 1.0
		gain.process_inplace("math.reciprocal",{"zero_to":1.0})		 
	

	#try: display((dark,gain,sigd,sigg))
	#except: display((dark,gain))

	step=options.step.split(",")
	if len(step)==3 : last=int(step[2])
	else: last=-1
	first=int(step[0])
	step=int(step[1])
	if options.verbose: print "Range={} - {}, Step={}".format(first,last,step)

	# the user may provide multiple movies to process at once
	for fsp in args:
		if options.verbose : print "Processing ",fsp
		
		n=EMUtil.get_image_count(fsp)
		if n<3 : 
			print "ERROR: {} has only {} images. Min 3 required.".format(fsp,n)
			continue
		if last<=0 : flast=n
		else : flast=last
		
		process_movie(fsp,dark,gain,first,flast,step,options)
		
	E2end(pid)

def process_movie(fsp,dark,gain,first,flast,step,options):
		outname=fsp.rsplit(".",1)[0]+"_proc.hdf"		# always output to an HDF file. Output contents vary with options
		
		# bgsub and gain correct the stack
		outim=[]
		for ii in xrange(first,flast,step):
			if options.verbose:
				print " {}/{}   \r".format(ii-first+1,flast-first+1),
				sys.stdout.flush()

			im=EMData(fsp,ii)
			
			if dark!=None : im.sub(dark)
			if gain!=None : im.mult(gain)

			#im.process_inplace("threshold.clampminmax.nsigma",{"nsigma":3.0})
			im.process_inplace("threshold.clampminmax",{"minval":0,"maxval":im["mean"]+im["sigma"]*2.0,"tozero":1})		# TODO - not sure if 2 is really safe here, even on the high end
#			im.mult(-1.0)
			
			if options.frames : im.write_image(outname[:-4]+"_corr.hdf",ii-first)
			outim.append(im)
			#im.write_image(outname,ii-first)

		nx=outim[0]["nx"]
		ny=outim[0]["ny"]

		# show a little movie of 5 averaged frames
		if options.movie>0 :
			mov=[]
			for i in xrange(options.movie+1,len(outim)):
				im=sum(outim[i-options.movie-1:i])
	#			im.process_inplace("normalize.edgemean")
				#im.write_image("movie%d.hdf"%(i/5-1),0)
				#im.process_inplace("filter.lowpass.gauss",{"cutoff_freq":.02})
				mov.append(im)
				
			display(mov)

			#mov2=[]
			#for i in xrange(0,len(outim)-10,2):
				#im=sum(outim[i+5:i+10])-sum(outim[i:i+5])
				#mov2.append(im)
				
			#display(mov2)
			
			#mov=[i.get_clip(Region(1000,500,2048,2048)) for i in mov]
			#s=sum(mov)
#			fsc=[i.calc_fourier_shell_correlation(s)[1025:2050] for i in mov]
#			plot(fsc)
		
		# A simple average
		if options.simpleavg :
			if options.verbose : print "Simple average"
			avgr=Averagers.get("mean")
			for i in xrange(len(outim)):						# only use the first second for the unweighted average
				if options.verbose:
					print " {}/{}   \r".format(i+1,len(outim)),
					sys.stdout.flush()
				avgr.add_image(outim[i])
			print ""

			av=avgr.finish()
			av.write_image(outname[:-4]+"_mean.hdf",0)
			
		
		# Generates different possibilites for resolution-weighted, but unaligned, averages
		xy=XYData()
		xy.set_size(2)
		xy.set_x(0,0)
		xy.set_y(0,1.0)
		xy.set_x(1,0.707)
		xy.set_y(1,0.0)
		if options.avgs :
			if options.verbose : print "Weighted average"
			normim=EMData(nx/2+1,ny)
			avgr=Averagers.get("weightedfourier",{"normimage":normim})
			for i in xrange(min(len(outim),25)):						# only use the first second for the unweighted average
				if options.verbose:
					print " {}/{}   \r".format(i+1,len(outim)),
					sys.stdout.flush()
				xy.set_y(1,1.0)					# no weighting
				outim[i]["avg_weight"]=xy
				avgr.add_image(outim[i])
			print ""

			av=avgr.finish()
			av.write_image(outname[:-4]+"_a.hdf",0)
#			display(normim)

			# linear weighting with shifting 0 cutoff
			xy.set_y(1,0.0)
			for i in xrange(len(outim)):
				if options.verbose:
					print " {}/{}   \r".format(i+1,len(outim)),
					sys.stdout.flush()
				xy.set_x(1,0.025+0.8*(len(outim)-i)/len(outim))
				outim[i]["avg_weight"]=xy
				avgr.add_image(outim[i])
			print ""

			av=avgr.finish()
			av.write_image(outname[:-4]+"_b.hdf",0)

			# exponential falloff with shifting width
			xy.set_size(64)
			for j in xrange(64): xy.set_x(j,0.8*j/64.0)
			for i in xrange(len(outim)):
				if options.verbose:
					print " {}/{}   \r".format(i+1,len(outim)),
					sys.stdout.flush()
				for j in xrange(64) : xy.set_y(j,exp(-j/(3.0+48.0*(len(outim)-i)/float(len(outim)))))
#				plot(xy)
				outim[i]["avg_weight"]=xy
				avgr.add_image(outim[i])
			print ""

			av=avgr.finish()
			av.write_image(outname[:-4]+"_c.hdf",0)


		# we iterate the alignment process several times
		if options.align_frames:
			outim2=[]
#			for im in outim: im.process_inplace("threshold.clampminmax.nsigma",{"nsigma":4,"tomean":True})
#			for im in outim: im.process_inplace("threshold.clampminmax.nsigma",{"nsigma":4})
			av=sum(outim[-5:])
#			av=outim[-1].copy()
#			av.mult(1.0/len(outim))
			fav=[]
			for it in xrange(2):

				for im in outim:
					dx,dy=zonealign(im,av,verbose=options.verbose)
					im2=im.process("xform",{"transform":Transform({"type":"2d","tx":-dx,"ty":-dy})})
					if options.verbose==1 : print "{}, {}".format(dx,dy)
					outim2.append(im2)

				print "-----"
				
				av=sum(outim2)
				av.mult(1.0/len(outim))
				fav.append(av)
				if it!=2 : outim2=[]
							
			av.write_image(outname[:-4]+"_aliavg.hdf",0)
			if options.save_aligned:
				for i,im in enumerate(outim2): im.write_image(outname[:-4]+"_align.hdf",i)
			if options.verbose>1 : display(fav,True)

		# we iterate the alignment process several times
		if options.align_frames_countmode:
			outim2=[]
#			for im in outim: im.process_inplace("threshold.clampminmax.nsigma",{"nsigma":6,"tomean":True})	# nsigma was normally 4, but for K2 images even 6 may not be enough
			av=sum(outim)
#			av.mult(1.0/len(outim))
			fav=[]
			for it in xrange(2):		# K2 data seems to converge pretty much immediately in my tests

				for im in outim:
					if it==0 : av.sub(im)
					dx,dy=zonealign(im,av,verbose=options.verbose)
					im2=im.process("xform",{"transform":Transform({"type":"2d","tx":-dx,"ty":-dy})})
					if options.verbose==1 : print "{}, {}".format(dx,dy)
					if it==0: av.add(im2)
					outim2.append(im2)

				print "-----"
				
				av=sum(outim2)
				av.mult(1.0/len(outim))
				fav.append(av)
				if it!=2 : outim2=[]
							
			av.write_image(outname[:-4]+"_aliavg.hdf",0)
			if options.save_aligned:
				for i,im in enumerate(outim2): im.write_image(outname[:-4]+"_align.hdf",i)
			if options.verbose>2 : display(fav,True)

		# show CCF between first and last frame
		#cf=mov[0].calc_ccf(mov[-1])
		#cf.process_inplace("xform.phaseorigin.tocenter")
		#display(cf)

		## save 10-frame averages without alignment
		#im=sum(outim[:10])
		#im.process_inplace("normalize.edgemean")
		#im.write_image("sum0-10.hdf",0)
		#im=sum(outim[10:20])
		#im.process_inplace("normalize.edgemean")
		#im.write_image("sum10-20.hdf",0)
		#im=sum(outim[20:30])
		#im.process_inplace("normalize.edgemean")
		#im.write_image("sum20-30.hdf",0)
	
	

		#try:
			#dot1=s1.cmp("ccc",dark2,{"negative":0})
			#dot2=s2.cmp("ccc",dark2,{"negative":0})

			##s1.sub(dark2*dot1)
			##s2.sub(dark2*dot2)

			#print dot1,dot2
		#except:
			#print "no dark"

		# alignment
		#ni=len(outim)		# number of input images in movie
		
		#s1=sum(outim[:ni/4])
		#s1.process_inplace("normalize.edgemean")
		#s2=sum(outim[ni*3/4:])
		#s2.process_inplace("normalize.edgemean")
		#dx,dy=align(s1,s2)
		#print "half vs half: ",dx,dy
		
		#dxn=dx/(ni/2.0)		# dx per n
		#dyn=dy/(ni/2.0)mpi_test.py
		
		#s1=sum(outim[:ni/4])
		#s1.process_inplace("normalize.edgemean")
		#s2=sum(outim[ni/4:ni/2])
		#s2.process_inplace("normalize.edgemean")
		#dx,dy=align(s1,s2,(dxn*ni/4.0,dyn*ni/4.0))
		#print dx,dy
		
		#s1=sum(outim[ni/4:ni/2])
		#s1.process_inplace("normalize.edgemean")
		#s2=sum(outim[ni/2:ni*3/4])
		#s2.process_inplace("normalize.edgemean")
		#dx,dy=align(s1,s2,(dxn*ni/4.0,dyn*ni/4.0))
		#print dx,dy
		
		#s1=sum(outim[ni/2:ni*3/4])
		#s1.process_inplace("normalize.edgemean")
		#s2=sum(outim[ni*3/4:])
		#s2.process_inplace("normalize.edgemean")
		#dx,dy=align(s1,s2,(dxn*ni/4.0,dyn*ni/4.0))
		#print dx,dy
		
			

def zonealign(s1,s2,verbose=0):

	# reduce region used for alignment a bit (perhaps a lot for superresolution imaging
	newbx=good_boxsize(min(s1["nx"],s1["ny"],4096)*0.8)
	if s1["nx"]>newbx or s1["ny"]>newbx : 
		s1a=s1.get_clip(Region((s1["nx"]-newbx)/2,(s1["ny"]-newbx)/2,newbx,newbx))
		s2a=s2.get_clip(Region((s2["nx"]-newbx)/2,(s2["ny"]-newbx)/2,newbx,newbx))
	else :
		s1a=s1.copy()
		s2a=s2.copy()


#	s1a.process_inplace("math.xystripefix",{"xlen":200,"ylen":200})
	s1a.process_inplace("filter.xyaxes0")
#	s1a.process_inplace("filter.lowpass.gauss",{"cutoff_abs":.05})
#	s1a.process_inplace("threshold.compress",{"value":0,"range":s1a["sigma"]/2.0})
	s1a.process_inplace("filter.highpass.gauss",{"cutoff_abs":.002})
	
#	s2a.process_inplace("math.xystripefix",{"xlen":200,"ylen":200})
#	s2a.process_inplace("filter.lowpass.gauss",{"cutoff_abs":.05})
	s2a.process_inplace("filter.xyaxes0")
	s2a.process_inplace("filter.highpass.gauss",{"cutoff_abs":.002})

	
	#### Not doing by zone ATM
	#tot=None
	#for x in range(256,s1["nx"]-512,512):
		#for y in range(256,s1["ny"]-512,512):
			#s1b=s1a.get_clip(Region(x,y,512,512))
			#s2b=s2a.get_clip(Region(x,y,512,512))
			
			#c12=s1b.calc_ccf(s2b)
			#c12.process_inplace("xform.phaseorigin.tocenter")
			#c12.process_inplace("normalize.edgemean")
						
			#cm=c12.calc_center_of_mass(0)
			#try: tot.add(cm)
			#except: tot=c12
	
	
	tot=s1a.calc_ccf(s2a)
	tot.process_inplace("xform.phaseorigin.tocenter")
	tot.process_inplace("normalize.edgemean")
	
	#if verbose>1 : 
		#s1a.write_image("s1a.hdf",0)
		#s2a.write_image("s2a.hdf",0)
		#tot.write_image("stot.hdf",0)
			
	if verbose>3 : display((s1a,s2a,tot),force_2d=True)
	
	dx,dy=(tot["nx"]/2,tot["ny"]/2)					# the 'false peak' should always be at the origin, ie - no translation
	for x in xrange(dx-1,dx+2):
		for y in xrange(dy-1,dy+2):
			tot[x,y]=0		# exclude from COM

	# first pass to make sure we find the true peak with a lot of blurring
	tot2=tot.get_clip(Region(tot["nx"]/2-96,tot["ny"]/2-96,192,192))
	tot2.process_inplace("filter.lowpass.gauss",{"cutoff_abs":.04})		# This is an empirical value. Started with 0.04 which also seemed to be blurring out high-res features.
	dx1,dy1,dz=tot2.calc_max_location()
	dx1-=96
	dy1-=96

	# second pass with less blurring to fine tune it
	tot=tot.get_clip(Region(tot["nx"]/2-12+dx1,tot["ny"]/2-12+dy1,24,24))
	tot.process_inplace("filter.lowpass.gauss",{"cutoff_abs":.12})		# This is an empirical value. Started with 0.04 which also seemed to be blurring out high-res features.
	dx,dy,dz=tot.calc_max_location()
	dx-=12
	dy-=12
	#while hypot(dx-tot["nx"]/2,dy-tot["ny"]/2)>64 :
		#tot[dx,dy]=0
		#dx,dy,dz=tot.calc_max_location()

	if verbose>1: print "{},{} + {},{}".format(dx1,dy1,dx,dy)
	if verbose>2: display(tot)
	
	return dx1+dx,dy1+dy
		
	#cl=tot.get_clip(Region(dx-8,dy-8,17,17))
	#cm=cl.calc_center_of_mass(0)
	#return dx+cm[0]-8-256,dy+cm[1]-8-256

def align(s1,s2,hint=None):

	s11=s1.get_clip(Region(1024,500,2048,2048))
#	s11.process_inplace("math.addsignoise",{"noise":0.5})
#	s11.process_inplace("normalize.local",{"radius":6,"threshold":0})
#	s11.process_inplace("math.xystripefix",{"xlen":200,"ylen":200})
	#s11.process_inplace("threshold.compress",{"value":s11["mean"],"range":s11["sigma"]})
	s11.process_inplace("filter.lowpass.gauss",{"cutoff_abs":.02})
	s21=s2.get_clip(Region(1024,500,2048,2048))
#	s21.process_inplace("math.addsignoise",{"noise":0.5})
#	s21.process_inplace("normalize.local",{"radius":6,"threshold":0})
#	s21.process_inplace("math.xystripefix",{"xlen":200,"ylen":200})
	#s21.process_inplace("threshold.compress",{"value":s21["mean"],"range":s21["sigma"]})
	s21.process_inplace("filter.lowpass.gauss",{"cutoff_abs":.02})

	c12=s11.calc_ccf(s21)
	m=c12["minimum"]
#	for x in xrange(c12["nx"]): c12[x,0]=m
	c12.process_inplace("normalize.edgemean")
	c12.process_inplace("xform.phaseorigin.tocenter")

	# This peak is the false peak caused by the imperfect dark noise subtraction
	# we want to wipe this peak out
	#dx,dy,dz=tuple(c12.calc_max_location())		# dz is obviously 0
	dx,dy=(c12["nx"]/2,c12["ny"]/2)					# the 'false peak' should always be at the origin, ie - no translation
	newval=(c12[dx-3,dy]+c12[dx+3,dy]+c12[dx,dy-3]+c12[dx,dy+3])/8		# /4 would be the average, we intentionally downweight it
	for x in xrange(dx-2,dx+3):
		for y in xrange(dy-2,dy+3):
			c12[x,y]=newval
	#c12[dx-1,dy]=(c12[dx-1,dy-1]+c12[dx-1,dy+1])/2.0
	#c12[dx+1,dy]=(c12[dx+1,dy-1]+c12[dx+1,dy+1])/2.0
	#c12[dx,dy+1]=(c12[dx+1,dy+1]+c12[dx-1,dy+1])/2.0
	#c12[dx,dy-1]=(c12[dx+1,dy-1]+c12[dx-1,dy-1])/2.0
	#c12[dx,dy]=(c12[dx-1,dy]+c12[dx+1,dy]+c12[dx,dy+1]+c12[dx,dy-1])/4.0
	
	display((s11,s21,c12))
#	display(c12)
	
	if hint!=None:
		cl=c12.get_clip(Region(1024+hint[0]-4,1024+hint[1]-4,9,9))
		dx,dy,dz=cl.calc_max_location()
		cl=c12.get_clip(Region(1024+dx-3,1024+dy-3,7,7))
		cm=cl.calc_center_of_mass(0)
		return dx+cm[0]-3,dy+cm[1]-3
	else:
		dx,dy,dz=c12.calc_max_location()
		cl=c12.get_clip(Region(dx-8,dy-8,17,17))
		cm=cl.calc_center_of_mass(0)
		return dx+cm[0]-8-1024,dy+cm[1]-8-1024

if __name__ == "__main__":
	main()
