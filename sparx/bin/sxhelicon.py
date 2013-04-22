#!/usr/bin/env python
#
# Author: Pawel A.Penczek and Edward H. Egelman 05/27/2009 (Pawel.A.Penczek@uth.tmc.edu)
# Copyright (c) 2000-2006 The University of Texas - Houston Medical School
# Copyright (c) 2008-Forever The University of Virginia
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
#


def main():
	import os
	import sys
	from optparse import OptionParser
	from global_def import SPARXVERSION
	import global_def
        arglist = []
        for arg in sys.argv:
        	arglist.append( arg )
	progname = os.path.basename(arglist[0])
	usage = progname + " stack ref_vol outdir  <maskfile> --ir=inner_radius --ou=outer_radius --rs=ring_step --xr=x_range --ynumber=y_numbers  --txs=translational_search_stepx  --delta=angular_step --an=angular_neighborhood --center=1 --maxit=max_iter --CTF --snr=1.0  --ref_a=S --sym=c1 --datasym=symdoc --new"
	
	parser = OptionParser(usage,version=SPARXVERSION)
	parser.add_option("--delta",              type="string",		 default= " 10 6 4  3   2",   help="angular step of reference projections")
	parser.add_option("--maxit",              type="int",            default= 30,                 help="maximum number of iterations performed for each angular step (set to 30) ")
	parser.add_option("--CTF",                action="store_true",   default=False,      		  help="CTF correction")
	parser.add_option("--snr",                type="float",          default= 1.0,                help="Signal-to-Noise Ratio of the data")	
	parser.add_option("--MPI",                action="store_true",   default=False,               help="use MPI version")
	#parser.add_option("--fourvar",           action="store_true",   default=False,               help="compute Fourier variance")
	parser.add_option("--apix",               type="float",			 default= -1.0,               help="pixel size in Angstroms")   
	parser.add_option("--dp",                 type="float",			 default= -1.0,               help="delta z - translation in Angstroms")   
	parser.add_option("--dphi",               type="float",			 default= -1.0,               help="delta phi - rotation in degrees")  
	
	parser.add_option("--psi_max",            type="float", 		 default= 10.0,               help="maximum psi - how far rotation in plane can can deviate from 90 or 270 degrees")   
	parser.add_option("--rmin",               type="float", 		 default= 0.0,                help="minimal radius for hsearch (Angstroms)")   
	parser.add_option("--rmax",               type="float", 		 default= 80.0,               help="maximal radius for hsearch (Angstroms)")
	parser.add_option("--fract",              type="float", 		 default= 0.7,                help="fraction of the volume used for helical search")
	parser.add_option("--sym",                type="string",		 default= "c1",               help="symmetry of the structure")
	parser.add_option("--function",           type="string",		 default="helical",  	      help="name of the reference preparation function")
	parser.add_option("--npad",               type="int",   		 default= 4,                  help="padding size for 3D reconstruction")
	parser.add_option("--debug",              action="store_true",   default=False,               help="debug")
	
	parser.add_option("--searchxshift",       type="float",		     default= 0.0,                help="search range for x-shift determination: +/- searchxshift (Angstroms)")
	parser.add_option("--xwobble",             type="float",		     default= 6.0,                help="neighborhood within which to search for peaks in 1D ccf for x-shift search (Angstroms)")

	#  ehelix
	parser.add_option("--ehelix",             action="store_true",   default=False,               help="Use consistent helical refinement")
	parser.add_option("--ywobble",            type="float",          default=0.0,                 help="wobble in y-directions (default = 0.0) in Angstroms")
	parser.add_option("--nopsisearch",        action="store_true",   default=False,               help="Block searching for in-plane angle (default False)")

	(options, args) = parser.parse_args(arglist[1:])
	if len(args) < 3 or len(args) > 4:
		print "usage: " + usage + "\n"
		print "Please run '" + progname + " -h' for detailed options"
	else:
		
		# Convert input arguments in the units/format as expected by ihrsr_MPI in applications.
		if options.apix < 0:
			print "Please enter pixel size"
			sys.exit()

		rminp = int((float(options.rmin)/options.apix) + 0.5)
		rmaxp = int((float(options.rmax)/options.apix) + 0.5)
		ywobble = int(options.ywobble/options.apix+0.5)  # this should be full real.

		from utilities import get_input_from_string, get_im

		searchxshiftp = int( (options.searchxshift/options.apix) + 0.5)
		xwobblep = int( (options.xwobble/options.apix) + 0.5)

		if options.MPI:
			from mpi import mpi_init, mpi_finalize
			sys.argv = mpi_init(len(sys.argv), sys.argv)

		if global_def.CACHE_DISABLE:
			from utilities import disable_bdb_cache
			disable_bdb_cache()

		
		if len(args) < 4:  mask = None
		else:               mask = args[3]
		from development import ehelix_MPI
		global_def.BATCH = True
		ehelix_MPI(args[0], args[1], args[2], options.delta, options.psi_max, searchxshiftp, xwobblep, ywobble, options.apix, options.dp, options.dphi, options.fract, rmaxp, rminp, not options.nopsisearch, mask, options.maxit, options.CTF, options.snr, options.sym,  options.function, options.npad, options.debug)
		global_def.BATCH = False

		if options.MPI:
			from mpi import mpi_finalize
			mpi_finalize()

if __name__ == "__main__":
	main()