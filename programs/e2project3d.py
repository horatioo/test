#!/usr/bin/env python

#
# Author: Steven Ludtke, 04/10/2003 (sludtke@bcm.edu)
# David Woolford 05/14/2007 (woolford@bcm.edu)
#
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  2111-1307 USA
#
#

# initial version of project3d; more features/documentation to come
# try "e2project3d --help"

# References
# 1. Baldwin, P.R. and Penczek, P.A. 2007. The Transform Class in SPARX and EMAN2. J. Struct. Biol. 157, 250-261.
# 2. http://blake.bcm.edu/emanwiki/EMAN2/Symmetry

# 
# 1. Asymmetric units are accurately demarcated and covered by the projection algorithm. This can
# be tested using 3D plotting in Matlab.
# 2. By default the entire asymmetric is projected over, but excluding the mirror portion is supported.
# The accuracy of the demarcation of the asymmetric unit can be tested by using the --verifymirror
# argument, which subtracts (mirrored) mirror projections in the local asymmetric unit from the 
# the equivalent original projections - the result should be zero but this is not the case due
# to interpolation differences, however the images should have a mean of about zero and a standard
# deviation that is relatively small. Visual inspection of the results (in default output files) can also help.
# 3. Random orientation generation is supported - all three euler angles are random
# 4. Perturbation of projections generated in the asymmetric unit is supported in regular reconstructions runs.
# 5. The user is able to generate projections that include in-plane or "phi" rotations
# and this is achieved using the phitoo argument
# 6. The user can smear in-plane projections when the "smear" argument is specified in addition to the "phitoo" argument
# what else..????

import sys, math, os, random
from EMAN2 import *
from optparse import OptionParser
deg2rad = math.pi / 180.0
rad2deg = 180.0 / math.pi
DEBUG = False
WEN_JIANG = False
EMAN1_OCT = False
MIRROR_DEBUG = True
NO_MIRROR = False

def main():
	progname = os.path.basename(sys.argv[0])
	usage = """%prog image [options] 
	Projects in real space over the asymmetric unit using the angular separation as specified by prop and the symmetry as specified by sym."""
	parser = OptionParser(usage=usage,version=EMANVERSION)
	
	parser.add_option("--prop", dest = "prop", type = "float", help = "The proportional angular separation of projections in degrees")
	parser.add_option("--sym", dest = "sym", help = "Specify symmetry - choices are: c<n>, d<n>, h<n>, tet, oct, icos")
	parser.add_option("--out", dest = "outfile", default = "e2proj.img", help = "Output file. Default is 'e2proj.img'")
	parser.add_option("--phitoo", dest="phitoo", type = "float", default = 0.0,help = "In conjunction with the --sym argument, this will additionally iterate phi on the interval [0,360] for each azimuth and altitude pair, using the specified argument as the angular separation (in degrees)")
	parser.add_option("--random", dest = "random", type = "int", default = 0.0, help = "This will generate a set number of randomly distributed projections (all 3 euler angles are random)")
	# add --perturb
	parser.add_option("--nomirror",action="store_true",help="Stops projection over the mirror portion of the asymmetric unit",default=False)
	parser.add_option("--smear", dest = "smear", type = "int", default=0,help="Used in conjunction with --phitoo, this will rotationally smear between phi steps. The user must specify the amount of smearing (typically 2-10)")
	parser.add_option("--perturb",action="store_true",help="In conjunction with the --sym argument, perturbs orientations when projecting over the asymmetric unit",default=False)
	parser.add_option("--projector", dest = "projector", default = "standard",help = "Projector to use")
	parser.add_option("--verifymirror",action="store_true",help="Used for testing the accuracy of mirror projects",default=False)
	parser.add_option("--numproj", dest = "numproj", type = "float",help = "The number of projections to generate - this is opposed to using the prop argument")
	parser.add_option("--force", "-f",dest="force",default=False, action="store_true",help="Force overwrite the output file if it exists")
	parser.add_option("--append", "-a",dest="append",default=False, action="store_true",help="Append to the output file")
	parser.add_option("--verbose","-v", dest="verbose", default=False, action="store_true",help="Toggle verbose mode - prints extra infromation to the command line while executing")
	parser.add_option("--check","-c", default=False, action="store_true",help="Checks to see if the command line arguments will work.")
	parser.add_option("--nofilecheck",action="store_true",help="Turns file checking off in the check functionality - used by e2refine.py.",default=False)
	
	(options, args) = parser.parse_args()
	
	
	if ( options.check ): options.verbose = True
	
	if len(args) < 1:
		parser.error("Error: No input file given")
	
	options.model = args[0]
	error = check(options,options.verbose)
	
	if ( options.verbose ):
		if (error):
			print "e2project3d.py command line arguments test.... FAILED"
		else:
			if (options.verbose):
				print "e2project3.py command line arguments test.... PASSED"
			
	if error : exit(1)
	if options.check: exit(0)
	
	# just remove the file - if the user didn't specify force then the error should have been found in the check function
	if ( os.path.exists(options.outfile )):
		if ( options.force ):
			remove_file(options.outfile)

	logger=E2init(sys.argv)
	eulers = []
	
	if ( options.random ):
		eulers = get_random_orientations( options.random, options.nomirror )
	else:
		if (options.prop):
				eulers = get_asym_unit_orientations( options.sym, options.prop, options.nomirror, options.perturb )
		else:
			if (options.numproj):
				eulers = get_asym_unit_orientations_numproj( options.sym, options.numproj, options.nomirror, options.perturb )
			else:
				print "Error, this error should have been caught before now, the user has not specified a valid prop or numproj argument"
				exit(1)

		# check for the phitoo argument.
		if (options.phitoo):	
			eulers = include_phi_rotations(eulers, options.phitoo)

	data = EMData()
	data.read_image(args[0])
	# generate and save all the projections to disk - that's it, that main job is done
	if ( options.verbose ):
		print "Generating and saving projections..."
		
	if (DEBUG):
		tally = 0
		for i in eulers:
			print tally,i[0] * rad2deg, i[1] * rad2deg, i[2] * rad2deg
			tally += 1
		exit(1)
	generate_and_save_projections(options, data, eulers, options.smear, options.phitoo)
	if ( options.verbose ):
		print "%s...done" %progname
		
	if options.verifymirror:
		if options.sym:
			verify_mirror_test(data, eulers, options.sym, options.projector)
		else:
			print "Warning: verify mirror only works when a symmetry has been specified. No action taken."

	E2end(logger)
	
def include_phi_rotations(eulers, phiprop):
	
	limit = math.pi * 2. - phiprop * deg2rad / 2.0	
	return_eulers = []
	
	for euler in eulers:
		phi_iterator = phiprop * deg2rad
		return_eulers.append(euler)
		while (phi_iterator < limit):
		# have to use a tmp az_iterator because of 
			return_eulers.append([euler[0],euler[1],phi_iterator])
		
			phi_iterator = phi_iterator + phiprop

	return return_eulers
		
def get_random_orientations( totalprojections, nomirror ):
		
	i = 0
	eulers = []
	while ( i < totalprojections ):
		#get a random 3D vector on [-1,1]
		x = 2*random.random() - 1
		y = 2*random.random() - 1
		if nomirror:
			# if no mirroring is specified, then only consider projections in positive z
			print "no mirroring"
			z = random.random()
		else:
			z = 2*random.random() - 1
		
		length = math.sqrt( x**2 + y**2 + z**2)
		
		#if the point is beyond the unit sphere then we should not 
		#consider it, or else the sampling of Euler angles will be
		#biased
		if length > 1:
			continue
		
		#normalize
		x = x/length
		y = y/length
		z = z/length
		
		# because the point is randomly distributed over the unit sphere,
		# its associated eulers will also be random.
		# note that a point on the unit sphere only implies two angles:
		az = math.atan2(y,x)
		alt = math.acos(z)
			
		randomphi = random.random()*2*math.pi
		eulers.append([alt,az,randomphi])
		
		i += 1
	
	return eulers
		
def get_asym_unit_orientations_numproj(symmetry, num_proj, nomirror, perturb = False):
	
	prop_soln = 360
	prop_upper_bound = 360
	prop_lower_bound = 0
	
	#This is an example of a divide and conquer approach, the possible values of the angle are searched
	#like a binary tree
	
	soln_found = False
	eulers = []
	while ( soln_found == False ):
		eulers = get_asym_unit_orientations(symmetry,prop_soln,nomirror,perturb)
		if (len(eulers) == num_proj):
			soln_found = True
		else:
			if ( (prop_upper_bound - prop_lower_bound) < 0.000001 ): 
				# If this is the case, the requested number of projections is practically infeasible
				# in which case just return the nearest guess
				soln_found = True
				eulers = get_asym_unit_orientations(symmetry,(prop_upper_bound+prop_lower_bound)/2.0,nomirror,perturb)
			
			else:
				if (len(eulers) < num_proj):
					prop_upper_bound = prop_soln;
					prop_soln = prop_soln - (prop_soln-prop_lower_bound)/2.0
				else:
					prop_lower_bound = prop_soln;
					prop_soln = prop_soln  + (prop_upper_bound-prop_soln)/2.0
		
	print "Using an angular distribution of %f, this will give you %d projections" %(prop_soln,len(eulers))
	return eulers

def get_asym_unit_orientations(symmetry, prop, nomirror, perturb = False):

	#sym_object = get_sym_object( symmetry, nomirror)
	sym_object = parsesym(symmetry)
	delimiters = sym_object.get_delimiters()
	altmax = delimiters["alt_max"]
	azmax = delimiters["az_max"]

	if (DEBUG):
		print "for symmetry %s altitude max is %f, azimuth max is %f" %(sym.get_name(), altmax, azmax)

	alt_iterator = 0.0
	
	#If it's a h symmetry then the alt iterator starts at very close
	#to the altmax... the object is a h symmetry then it knows its alt_min...
	if sym_object.is_h_sym():
		alt_iterator = delimiters["alt_min"]
		inc_mirror = sym_object.get_params()["inc_mirror"]
	
	print alt_iterator,altmax
	
	eulers = []
	while ( alt_iterator <= altmax ):
		# get h		
		h = sym_object.get_h(prop,alt_iterator)

		#not sure what this does code taken from EMAN1 - FIXME original author add comments
		if (alt_iterator > 0) and ( (azmax/h) < 2.8):
			h = rad2deg*((deg2rad*azmax) / (2.1))
		elif (alt_iterator == 0):
			h = azmax
			
		az_iterator = 0.0;
		while ( az_iterator < azmax - h / 4.0 ):
			# FIXME: add an intelligent comment - this was copied from old code	
			if ( az_iterator > 180.0 and alt_iterator > 180.0/(2.0-0.001) and alt_iterator < 180.0/(2.0+0.001) ):
				az_iterator = az_iterator + h
				continue
			
			localEuler = ([alt_iterator, az_iterator, 0])
			

			if sym_object.is_platonic():
				if sym_object.is_in_asym_unit(alt_iterator, az_iterator) == False:
					az_iterator = az_iterator + h
					continue
				
				localEuler[1] = localEuler[1] + sym_object.get_az_alignment_offset()
				
			if perturb and localEuler[0] != 0:
				# this perturbation scheme is copied from EMAN1
				if localEuler[0] < (180.0-.01):
					localEuler[0] += gaussian_rand(0.0,.25*prop)
				
				localEuler[1] += gaussian_rand(0.0,h/4.0)
				
				if localEuler[0] > altmax: 
					localEuler[0] = altmax
					
				if localEuler[1] > azmax:
					localEuler[1] > azmax
				elif localEuler[1] < 0:
					localEuler[1] = 0
					
			eulers.append(localEuler)
			if sym_object.is_h_sym() and inc_mirror and alt_iterator != delimiters["alt_min"]:
				eulers.append( [2*delimiters["alt_min"]-localEuler[0],localEuler[1], localEuler[2]] )

			az_iterator = az_iterator + h

		alt_iterator = alt_iterator + prop
	
	return eulers

def get_h(prop,altitude,maxcsym):
		h = float(math.floor(360. / (prop * 1.1547)))
		h = int(math.floor(h * math.sin(altitude) + .5))
		if (h == 0):
			h = 1.0
		h = float(maxcsym) * math.floor(float(h) / float(maxcsym) + .5)
		#this is a temporary hack - i get h == 0, this problem
		# must occur in EMAN1, but division by zero does not throw in C++
		# while it does here
		if ( h == 0 ) :
			h = 1.0
		h = math.pi * 2.0 / h

		return h
	
def generate_and_save_projections(options,data,eulers,smear=0, phiprop=0):
	t3d = Transform3D()
	b = {"t3d": t3d }
	for i,euler in enumerate(eulers):
		#if i == 0 : continue
		#a = {"alt" : euler[0] * rad2deg,"az" : euler[1] * rad2deg,"phi" : euler[2] * rad2deg}
		t3d.set_rotation(EULER_EMAN, euler[0], euler[1], euler[2])
		p=data.project(options.projector,b)
		
		#FIXME:: In EMAN2 everything should be set in degrees but atm radians are being used in error!
		# this problem is being fixed by Phil Baldwin, and when fixed, the arguments here should change to radians
		p.set_rotation(euler[1],euler[0],euler[2])
		# this values reads as "particles_represented"
		#p.set_attr("ptcl_repr", int( random.random() * 50 ) + 1)
		p.set_attr("ptcl_repr", 1)
		# FIXME, this should be optional etc.
		#p.process_inplace("mask.sharp", {"outer_radius":options.mask})
		
		if smear:
			if not phiprop:
				print "ERROR: can not perform smearing operation without a valid phi angle"
				exit(1)
			smear_iterator = deg2rad*euler[2] + deg2rad*phiprop/(smear+1)
			while ( smear_iterator < euler[2] + phiprop*deg2rad ):
				ptmp=data.project(options.projector,{"alt" : euler[0],"az" : euler[1],"phi" : smear_iterator * rad2deg})
				
				p.add(ptmp)
				smear_iterator +=  deg2rad*phiprop/(smear+1)
				
		try: 
			p.write_image(options.outfile,-1)
		except:
			print "Error: Cannot write to file %s"%options.outfile
			exit(1)
		
		pcopy = p;
		
		if (options.verbose):
			print "%d\t%4.2f\t%4.2f\t%4.2f" % (i, euler[0], euler[1], euler[2])


def verify_mirror_test(data, eulers, symmetry, projector):
	
	sym_object = get_sym_object( symmetry )
	
	for i,euler in enumerate(eulers) :
		a = {"alt" : euler[0] * rad2deg,"az" : euler[1] * rad2deg,"phi" : euler[2] * rad2deg}
		t3d = Transform3D(EULER_EMAN, a)
		b = {"t3d": t3d }
		p=data.project(options.projector,b)
		
		mirrorEuler = sym_object.asym_unit_mirror_orientation(euler)
			
		
		#Get the projection in this orientations
		p_mirror = data.project(projector,{"alt" : mirrorEuler[0] * rad2deg,"az" : mirrorEuler[1]* rad2deg,"phi" : mirrorEuler[2] * rad2deg})
		
		## Actually do the mirroring
		if sym_object.is_d_symmetry():
			p_mirror.process_inplace("mirror", {"axis":'y'})
		elif sym_object.is_c_symmetry():
			p_mirror.process_inplace("mirror", {"axis":'x'})
		#FIXME: The mirror orientation is dependent on the platonic symmetry see http://blake.bcm.edu/emanwiki/EMAN2/Symmetry
		elif sym_object.is_platonic_symmetry():
			p_mirror.process_inplace("mirror", {"axis":'y'})
			
		
		## Calculate and write the difference to disk
		p_difference = p_mirror-p
		p_difference.write_image(symmetry+"mirror_debug_difference.img",-1)
		p_mirror.write_image(symmetry+"mirror_debug.img",-1)
		
		## Print debug information
		print "Orientation %d\t%4.2f\t%4.2f\t%4.2f" % (i, euler[0] * rad2deg, euler[1] * rad2deg, euler[2] * rad2deg)
		print "Mirror %d\t%4.2f\t%4.2f\t%4.2f" % (i, mirrorEuler[0] * rad2deg, mirrorEuler[1] * rad2deg, mirrorEuler[2] * rad2deg)

# A base class that encapsulates many of the  things common to all of the symmetries
# it also stores useful information such as the symmetry itself.
class asym_unit:
	def __init__(self, symmetry, nomirror= False):
		self.symmetry = symmetry
		self.nomirror = nomirror
		
		if (self.symmetry == "icos"):
			self.maxcsym = 5
		elif (self.symmetry == "oct"):
			self.maxcsym = 4
		elif (self.symmetry == "tet"):
			self.maxcsym = 3
		elif (self.symmetry[0] in ["c","d","h"]):
			self.maxcsym = int(symmetry[1:])
		else:
			print "ERROR: In get_maxcsym - unknown symmetry type: %s"%self.symmetry
			exit(1)
	
	def asym_unit_alt_max(self):
		return self.altmax
	def asym_unit_az_max(self):
		return self.azmax
	
	def get_maxcsym(self):
		return self.maxcsym

	#FIXME: These "is_whatever_symmetry" functions could be abstracted.
	def is_platonic_symmetry(self):
		if (self.symmetry in ["tet","oct","icos"]):
			return True
		else:
			return False

	def is_c_d_symmetry(self):
		if (self.symmetry[0] in ["c","d"]):
			return True
		else:
			return False
	
	def is_c_symmetry(self):
		if (self.symmetry[0] == "c"):
			return True
		else:
			return False

	def is_d_symmetry(self):
		if (self.symmetry[0] == "d"):
			return True
		else:
			return False

	def is_h_symmetry(self):
		if (self.symmetry[0] == "h"):
			return True
		else:
			return False

class h_asym_unit(asym_unit):
	# symmetry is a string, c1,d1,c2,d2,etc..class c_odd_asymm_unit:
	def __init__(self, symmetry, nomirror = False):
		asym_unit.__init__(self,symmetry, nomirror)
		
		self.azmax = self.maxcsym * math.pi/180.0
		self.altmin = 80.0 * math.pi/180.0
		self.altmax = math.pi/2.0

	def asym_unit_alt_min(self):
		return self.altmin

# A class the encapsulates things common or similar in c and d symmetries
class c_d_asym_unit(asym_unit):
	# symmetry is a string, c1,d1,c2,d2,etc..class c_odd_asym_unit:
	def __init__(self, symmetry, nomirror = False):
		asym_unit.__init__(self,symmetry, nomirror)
		if symmetry[0]=="c":
		
			if nomirror:
				self.altmax = math.pi / 2.0
			else:
				self.altmax = math.pi
				
			self.azmax = 2.0*math.pi/self.get_maxcsym()
		
		elif symmetry[0]=="d":
		
			self.altmax = math.pi / 2.0
		
			if nomirror:
				self.azmax = math.pi/self.get_maxcsym()
			else:
				self.azmax = 2.0*math.pi/self.get_maxcsym()
				
		else:
			print "ERROR: In get_c_d_asym_unit_bounds - unknown symmetry type: %s"%symmetry
			exit(1)
	
# a class to encapsulate specific information attributed to d symmetries
class d_asym_unit(c_d_asym_unit):
	def __init__(self, symmetry, nomirror = False):
		c_d_asym_unit.__init__(self,symmetry, nomirror)
	
	def asym_unit_mirror_orientation(self, euler):
		equiv_asym_unit_az = euler[1] % self.azmax
		az_offset = euler[1] - equiv_asym_unit_az
		mirrorEuler = ([euler[0], self.azmax - equiv_asym_unit_az +  az_offset, euler[2]])
		
		return mirrorEuler


# c odd and even symmetries have different ways of getting mirror orientations, which
# is reflected here in these two separate classes
class c_odd_asym_unit(c_d_asym_unit):
	def __init__(self, symmetry, nomirror = False):
		c_d_asym_unit.__init__(self,symmetry, nomirror)
	
	def asym_unit_mirror_orientation(self, euler):
		equiv_asym_unit_az = euler[1] % self.azmax
		if equiv_asym_unit_az < self.azmax/2.0:
			mirrorAz = self.azmax/2.0 + euler[1]
		else:
			mirrorAz = euler[1] - self.azmax/2.0
			
		mirrorEuler = ([self.altmax - euler[0], mirrorAz, euler[2]])
		
		return mirrorEuler

class c_even_asym_unit(c_d_asym_unit):
	def __init__(self, symmetry, nomirror = False):
		c_d_asym_unit.__init__(self,symmetry, nomirror)
	
	def asym_unit_mirror_orientation(self, euler):
		
		mirrorEuler = ([self.altmax - euler[0], euler[1], euler[2]])
		
		return mirrorEuler

# a class the encapsulates data and tools common to platon symmetry asym units
class platonic_asym_unit(asym_unit):
	def __init__(self, symmetry, nomirror = False):
		asym_unit.__init__(self,symmetry, nomirror)
		# FIXME: doing WEN_JIANG icosahedral and EMAN1 octahedral projection is only here
		# because we are cross checking against the original EMAN1 implementation.
		# Once everything is verified, WEN_JIANG and EMAN1_OCT support can be removed
		# it turns out that in EMAN1 it looks like they were projecting
		# over the entire asymmetric unit, and not accounting for mirror symmetry. Infact, the EMAN1 oct approach produces the EMAN2 oct 
		# approach... remove all references to EMAN1_OCT once these routines have been verified.
		if ( WEN_JIANG or EMAN1_OCT ):
			if ( symmetry == "icos" ):
				self.azmax =  2.0 * math.pi / 10.0
				self.altmax = 37.3773681406497 * math.pi / 180. #this is the angle between a 5fold axis and the nearest 3fold axis of symmetry
			elif ( symmetry == "oct" ):
				self.azmax = 2.0 * math.pi / 4.0
				self.altmax = 54.736 * math.pi / 180.#this is the angle between a 4fold axis and the nearest 3fold axis of symmetry
			else:
				print "DEBUG ERROR: In platonic_asym_unit - current debug mode does not support symmetry type: %s" %symmetry 
				exit(1)	
		else:
			# See the manuscript "The Transform Class in Sparx and EMAN2", Baldwin & Penczek 2007. J. Struct. Biol. 157 (250-261)
			# In particular see pages 257-259
			# capSig is capital sigma in the Baldwin paper
			self.capSig = 2.0*math.pi/ self.get_maxcsym()
			# capSig is left here incase anyone ever tries to interpret what's happening here in terms of the Baldwin paper
			self.azmax = self.capSig;
			
			
			# Alpha is the angle between (immediately) neighborhing 3 fold axes of symmetry
			# This follows the conventions in the Baldwin paper
			self.alpha = math.acos(1.0/(math.sqrt(3.0)*math.tan(self.capSig/2)))
			# As in capsig here, alpha is here just for clarity, incase you try to interpret this code in terms of the Baldwin paper
			self.altmax = self.alpha;
			
			# This is half of "theta_c" as in the conventions of the Balwin paper. See also http://blake.bcm.edu/emanwiki/EMAN2/Symmetry.
			self.thetacontwo = 1.0/2.0*math.acos( math.cos(self.capSig)/(1.0-math.cos(self.capSig)))

	# Tetrahedral symmetry is the only instance that uses alpha != self.alpha, so the 
	# second argument accomodates this - tetrahedral only does this when its discluding
	# mirror symmetries!
	def platonic_boundary_alt(self, azimuth, alpha):
		
		baldwin_boundary_alt = math.sin(self.capSig/2.0 - azimuth)/math.tan(self.thetacontwo)
		baldwin_boundary_alt += math.sin( azimuth )/math.tan(alpha)
		baldwin_boundary_alt *= 1/math.sin(self.capSig/2.0)
		baldwin_boundary_alt = math.atan(1/baldwin_boundary_alt)

		return baldwin_boundary_alt

# this class encapsulates what is common to icosahedral and octahedral symmetry
# in terms of the mirror portions of the asym unit
class icos_oct_asym_unit(platonic_asym_unit):
	def __init__(self, symmetry, nomirror = False):
		platonic_asym_unit.__init__(self,symmetry, nomirror)

	def asym_unit_mirror_orientation(self, euler):
		# nb, this function will only work for projections in the asymmetric
		# unit generated by e2project3d.py
		if self.get_az_alignment_offset() != 0 : # also the same as self.symmetry == "icos"
			equiv_asym_unit_az = euler[1] % self.get_az_alignment_offset()
			az_offset = euler[1] - equiv_asym_unit_az
			mirrorAz = self.azmax + az_offset - equiv_asym_unit_az 
		else: # also the same as self.symmetry == "oct"
			mirrorAz = self.azmax - euler[1]
		
		# returning only euler[0] for this function restrict might restrict 
		# its use to only five of the asymmetric units
		mirrorEuler = (euler[0], mirrorAz, euler[2])
		
		return mirrorEuler
	
	def is_in_asym_unit(self, euler):
			
		# This represents the angle between maxcysm-fold axis and the nearest 
		# 2fold axis. This is the Badwin "theta_c" divided by two, hence the name.
		
		azimuth = euler[1]
		
		if ( azimuth > self.capSig/2.0 ):
			azimuth = self.capSig - azimuth
	
		baldwin_boundary_alt_lower = self.platonic_boundary_alt(azimuth, self.alpha)
	
		if ( baldwin_boundary_alt_lower > euler[0] ):
			if ( self.nomirror ):
				if ( self.azmax/2.0 < euler[1] ):
					return False
				else:
					return True
			else:
				return True
		else:
			return False
		
class icos_asym_unit(icos_oct_asym_unit):
	def __init__(self, symmetry, nomirror = False):
		icos_oct_asym_unit.__init__(self,symmetry, nomirror)

	# this is required to ensure that projection occurs
	# over the proper portion of the icosahedron and is related
	# to the fact that make3d generates icosahdral structures
	# in a very specific orientation
	def get_az_alignment_offset(self):
		return 3.0*math.pi/2.0 - math.pi/5.0

class oct_asym_unit(icos_oct_asym_unit):
	def __init__(self, symmetry, nomirror = False):
		icos_oct_asym_unit.__init__(self,symmetry, nomirror)

	# unfortunately returning zero implies redundance, but this
	# is needed to ensure abstract handling of the symmetries
	# in the euler generation loop. This could be fixable if
	# make3d is adapted to avoid the need for azimuthal offsets.
	def get_az_alignment_offset(self):
		return 0.0


# the tetrahedral asymmetric unit is more complicated in terms of its mirror symmetry
# it needs special consideration
class tet_asym_unit(platonic_asym_unit):
	def __init__(self, symmetry, nomirror = False):
		platonic_asym_unit.__init__(self,symmetry, nomirror)

	def get_az_alignment_offset(self):
		return math.pi

	# nb, this function will only work for projections in the asymmetric
	# unit generated by e2project3d.py - there are 12 asymm units in all,
	# and special consideration would have to be given to generalize the
	# approach used here
	
	def asym_unit_mirror_orientation(self, euler):
		
		c = ([math.sin(self.thetacontwo), 0, math.cos(self.thetacontwo)])
		f = ([math.sin(self.alpha)*math.cos(self.capSig/2.0), math.sin(self.alpha)*math.sin(self.capSig/2.0), math.cos(self.alpha)])
		
		n_fc = ([0,0,0])
		for i in [0,1,2]:
			n_fc[i] = (f[i]*math.sin(self.thetacontwo-euler[0]) + c[i]*math.sin(euler[0]))/math.sin(self.thetacontwo)
		
		mirrorAz = math.atan2(n_fc[1],n_fc[0]) + euler[1]
		mirrorAlt = math.acos(n_fc[2])
		
		mirrorEuler = (mirrorAlt, mirrorAz, euler[2])
		
		return mirrorEuler

	# This function tells the orientaton generating component in e2project2d.py
	# whether or not the euler angle is inside the asymmetric unit. 
	# This is required because the bounds created in the platonic_asymm_unit constructor
	# go beyond the asymmetric unit borders, and as the orientation generation algorithm
	# loops it simply iterates to the extremes permissible values of self.altmax and 
	# self.azmax, which will cause overlap unless those orientations beyond the 
	# asymmetric unit boundary are disregarded.
	def is_in_asym_unit(self, euler):
			
		# This represents the angle between maxcysm-fold axis and the nearest 
		# 2fold axis. This is the Badwin "theta_c" divided by two, hence the name.
		
		azimuth = euler[1]
		
		if ( azimuth > self.capSig/2.0 ):
			azimuth = self.capSig - azimuth
	
		baldwin_boundary_alt_lower = self.platonic_boundary_alt(azimuth, self.alpha)
	
		if ( baldwin_boundary_alt_lower > euler[0] ):
			if ( self.nomirror ):
				baldwin_boundary_alt_upper = self.platonic_boundary_alt( azimuth, self.alpha/2.0)
				# you could change the "<" to a ">" here to get the other mirror part of the asym unit
				# however this approach makes sure that the generated asymmetric unit projects look nice
				# and contiguous
				if ( baldwin_boundary_alt_upper < euler[0] ):
					return False
				else:
					return True
			else:
				return True
		else:
			return False

def get_sym_object( symmetry, nomirror=False ):
	
	if (symmetry == "icos"):
		return icos_asym_unit(symmetry, nomirror)
	elif (symmetry == "oct"):
		return oct_asym_unit(symmetry, nomirror)
	elif (symmetry == "tet"):
		return tet_asym_unit(symmetry, nomirror)
	elif (symmetry[0] =="c"):
		maxcsym = int(symmetry[1:])
		if (maxcsym %2) == 1:
			return c_odd_asym_unit(symmetry, nomirror)
		else:
			return c_even_asym_unit(symmetry, nomirror)
	elif (symmetry[0] =="d"):
		return d_asym_unit(symmetry, nomirror)
	elif (symmetry[0] =="h"):
		return h_asym_unit(symmetry, nomirror)
	else:
		print "ERROR: In get_sym_object - unknown symmetry type: %s" %symmetry
		exit(1)
	
# this is copied from EMAN1 util.C (it's called "grand" there)
def gaussian_rand(mean, sigma):
		
	r = 0
	while ( r == 0 or r > 1.0):
		x = 2*random.random() - 1
		y = 2*random.random() - 1
		r = x**2 + y**2;

	f = math.sqrt(-2.0*math.log(r)/r);

	return x*f*sigma+mean
	
# this is copied from EMAN1 util.C (it's called "frand" there)
def random_on_interval(low,high):

	if ( high < low ):
		print "ERROR: can not call random_on_interval when the the left argument is greater than the right argument"
		# or do this?
		# return (low-high)*random.random() + high
		exit(1)

	return (high-low)*random.random() + low

def check(options, verbose=False):
	
	error = False
	if ( not options.prop and not options.numproj ):
		if verbose:
			print "Error: you must specify one of either --prop or --numproj"
		error = True
	
	if ( not options.sym ):
		if verbose:
			print "Error: you must specify the sym argument"
		error = True
		
	if ( check_eman2_type(options.projector,Projectors,"Projector") == False ):
		error = True

	if not os.path.exists(options.model):
		if verbose:
			print "Error: 3D image %s does not exist" %options.model
		error = True
	
	if ( options.force and options.append):
		if verbose:
			print "Error: cannot specify both append and force"
		error = True
		
	if ( os.path.exists(options.outfile )):
		if ( not options.force ):
			if verbose:
				print "Error: output file exists, use -f to overwrite or -a to append. No action taken"
			error = True
	
	if options.sym and options.random:
		if verbose:
			print "Error: cannot handle both the sym and random arguments simultaneously"
		error = True
	
	if options.numproj and options.numproj < 0:
		print "Error: numproj must be greater than 0"
		error = True
	
	elif options.sym:
		try: sym = parsesym(options.sym)
		except Exception, inst:
			print type(inst)     # the exception instance
			print inst.args      # arguments stored in .args:
			error = True
			
		#name = sym.get_name()
		#if (name in ["c","d", "h"]):
			#if not(options.sym[1:].isdigit()):
				#if verbose:
					#print "Error: %s is an invalid symmetry type. You must specify the --sym argument"%options.sym
				#error = True
		#else :
			#if not (options.sym in ["tet","oct","icos"]):
				#if verbose:
					#print "Error: %s is an invalid symmetry type. You must specify the --sym argument"%options.sym
				#error = True
	
	if (options.phitoo):	
		if (options.phitoo <= 0):
			if verbose:
				print "Error: %f is an invalid value for phitoo (must be greater than zero)"%options.phitoo
			error = True
	
	if ( options.random ):
		if (options.random <= 0):
			if verbose:
				print "Error: %i is an invalid value for random (must be greater than zero)"%options.random
			error = True
			
	
	return error

if __name__=="__main__":
	main()
