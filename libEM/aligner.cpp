/**
 * $Id$
 */

/*
 * Author: Steven Ludtke, 04/10/2003 (sludtke@bcm.edu)
 * Copyright (c) 2000-2006 Baylor College of Medicine
 * 
 * This software is issued under a joint BSD/GNU license. You may use the
 * source code in this file under either license. However, note that the
 * complete EMAN2 and SPARX software packages have some GPL dependencies,
 * so you are responsible for compliance with the licenses of these packages
 * if you opt to use BSD licensing. The warranty disclaimer below holds
 * in either instance.
 * 
 * This complete copyright notice must be included in any revised version of the
 * source code. Additional authorship citations may be added, but existing
 * author citations must be preserved.
 * 
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
 * 
 * */

#include "cmp.h"
#include "aligner.h"
#include "emdata.h"
#include "processor.h"
#include <gsl/gsl_multimin.h>

using namespace EMAN;

template <> Factory < Aligner >::Factory()
{
	force_add(&TranslationalAligner::NEW);
	force_add(&Translational3DAligner::NEW);
	force_add(&RotationalAligner::NEW);
	force_add(&RotatePrecenterAligner::NEW);
	force_add(&RotateCHAligner::NEW);
	force_add(&RotateTranslateAligner::NEW);
	force_add(&RotateTranslateBestAligner::NEW);
	force_add(&RotateTranslateRadonAligner::NEW);
	force_add(&RotateFlipAligner::NEW);
	force_add(&RotateTranslateFlipAligner::NEW);
	force_add(&RTFSlowAligner::NEW);
//	force_add(&RTFSlowestAligner::NEW);
	force_add(&RTFBestAligner::NEW);
	force_add(&RTFRadonAligner::NEW);
	force_add(&RefineAligner::NEW);
}


EMData *TranslationalAligner::align(EMData * this_img, EMData *to, 
					const string&, const Dict&) const
{
	if (!this_img) {
		return 0;
	}

	int nz = this_img->get_zsize();
	if (nz > 1) {
		LOGERR("%s doesn't support 3D alignment", get_name().c_str());
		return 0;
	}


	if (to && !EMUtil::is_same_size(this_img, to)) {
		LOGERR("%s: images must be the same size", get_name().c_str());
		return 0;
	}

	EMData *cf = 0;

	cf = this_img->calc_ccf(to);

	int nx = this_img->get_xsize();
	int ny = this_img->get_ysize();
	int maxshiftx = params["maxshift"];
	int maxshifty = params["maxshift"];
	int nozero = params["nozero"];
	
	if (maxshiftx <= 0) {
		maxshiftx = nx / 8;
		maxshifty = ny / 8;
	}
	if (maxshiftx > nx / 2 - 1) {
		maxshiftx = nx / 2 - 1;
	}

	if (maxshifty > ny / 2 - 1) {
		maxshifty = ny / 2 - 1;
	}


//	cf->write_image("ccf.mrc");
	float *cf_data = cf->get_data();
	if (nozero) {
		cf_data[nx/2+nx*ny/2]=0;
		cf_data[nx/2+nx*ny/2+1]=0;
		cf_data[nx/2+nx*ny/2-1]=0;
		cf_data[nx/2+nx*ny/2+nx]=0;
		cf_data[nx/2+nx*ny/2-nx]=0;
		cf_data[nx/2+nx*ny/2+1+nx]=0;
		cf_data[nx/2+nx*ny/2-1+nx]=0;
		cf_data[nx/2+nx*ny/2+1-nx]=0;
		cf_data[nx/2+nx*ny/2-1-nx]=0;
	}

	float neg = (float)cf->get_attr("mean") - (float)cf->get_attr("minimum");
	float pos = (float)cf->get_attr("maximum") - (float)cf->get_attr("mean");

	int flag = 1;
	if (neg > pos) {
		flag = -1;
	}

	int peak_x = nx / 2+1;
	int peak_y = ny / 2;

	float max_value = -FLT_MAX;
	float min_value = FLT_MAX;

	for (int j = ny / 2 - maxshifty; j < ny / 2 + maxshifty; j++) {
		for (int i = nx / 2 - maxshiftx; i < nx / 2 + maxshiftx; i++) {
			int l = i + j * nx;

			if (cf_data[l] * flag > max_value) {
				max_value = cf_data[l] * flag;
				peak_x = i;
				peak_y = j;
			}
			if (cf_data[l] < min_value) {
				min_value = cf_data[l];
			}
		}
	}

	Vec3f pre_trans = this_img->get_translation();
	Vec3f cur_trans = Vec3f ((float)(nx / 2 - peak_x), (float)(ny / 2 - peak_y), 0);

	Vec3f result;	
	result = cur_trans;

	if (!to) {
		cur_trans /= 2.0f;
	}

	int intonly = params["intonly"];

	if (intonly) {
		cur_trans[0] = floor(cur_trans[0] + 0.5f);
		cur_trans[1] = floor(cur_trans[1] + 0.5f);
	}

	cf->update();
	if( cf )
	{
		delete cf;
		cf = 0;
	}
	cf=this_img->copy();
	cf->translate(cur_trans);

	
	//float score = (float)hypot(result[0], result[1]);
	cf->set_attr("align.score", max_value);
	cf->set_attr("align.dx",result[0]); 
	cf->set_attr("align.dy",result[1]); 

	return cf;
}



EMData *Translational3DAligner::align(EMData * this_img, EMData *to,  
			const string&, const Dict&) const
{
	if (!this_img) {
		return 0;
	}

	params.set_default("intonly", 0);

	if (to && !EMUtil::is_same_size(this_img, to)) {
		LOGERR("%s: images must be same size", get_name().c_str());
		return 0;
	}

	if (!to) {
		LOGWARN("%s: ACF", get_name().c_str());
	}

	EMData *cf = 0;
	cf = this_img->calc_ccf(to);

	float *cf_data = cf->get_data();

	float neg = (float)cf->get_attr("mean") - (float)cf->get_attr("minimum");
	float pos = (float)cf->get_attr("maximum") - (float)cf->get_attr("mean");

	int flag = 1;
	if (neg > pos) {
		flag = -1;
	}

	int nx = this_img->get_xsize();
	int ny = this_img->get_ysize();
	int nz = this_img->get_zsize();

	int peak_x = nx / 2;
	int peak_y = ny / 2;
	int peak_z = nz / 2;

	float max_value = -FLT_MAX;
	float min_value = FLT_MAX;

	int nsec = nx * ny;

	for (int k = nz / 4; k < 3 * nz / 4; k++) {
		for (int j = ny / 4; j < 3 * ny / 4; j++) {
			for (int i = nx / 4; i < 3 * nx / 4; i++) {
				if (cf_data[i + j * nx + k * nsec] * flag > max_value) {
					max_value = cf_data[i + j * nx + k * nsec] * flag;
					peak_x = i;
					peak_y = j;
					peak_z = k;
				}

				if (cf_data[i + j * nx + k * nsec] < min_value) {
					min_value = cf_data[i + j * nx + k * nsec];
				}
			}
		}
	}

	float tx = (float)(nx / 2 - peak_x);
	float ty = (float)(ny / 2 - peak_y);
	float tz = (float)(nz / 2 - peak_z);

	float score = 0;
	score = Util::hypot3(tx, ty, tz);


	if (!to) {
		tx /= 2;
		ty /= 2;
		tz /= 2;
	}

	this_img->translate(tx, ty, tz);

	cf->set_attr("align.score", max_value);
	cf->set_attr("align.dx",tx); 
	cf->set_attr("align.dy",ty); 
	cf->set_attr("align.dz",tz); 

	cf->update();

	return cf;
}


EMData *RotationalAligner::align(EMData * this_img, EMData *to,  
			const string&, const Dict&) const
{
	if (!to) {
		return 0;
	}

	bool premasked = true;
	EMData *this_img2 = this_img->make_rotational_footprint(premasked);
	EMData *to2 = to->make_rotational_footprint(premasked);

//	to2->write_image("temp.hdf",-1); // eliminate later, PRB
	int this_img2_nx = this_img2->get_xsize();

	EMData *cf = this_img2->calc_ccfx(to2, 0, this_img->get_ysize());

	cf->write_image("temp.hdf",-1); // eliminate later, PRB
	delete this_img2;
	delete to2;

	float *data = cf->get_data();
	float peak = 0;
	int peak_index = 0;

	Util::find_max(data, this_img2_nx, &peak, &peak_index);
	
	cf->update();
	if( cf )
	{
		delete cf;
		cf = 0;
	}
	EMData *cfL=this_img->copy();
	float rotateAngle = (float) peak_index * 180.0 / this_img2_nx;
	//printf("rotateAngleInit= %f \n",rotateAngle ); // eliminate later, PRB
	cfL->rotate( rotateAngle, 0, 0);
	EMData *cfR=this_img->copy();
	cfR->rotate( rotateAngle-180, 0, 0);
	float Ldot = cfL->dot(to);
	float Rdot = cfR->dot(to);
	//printf("Ldot = %f, Rdot=%f \n",Ldot, Rdot); // eliminate later, PRB
	if (Ldot>Rdot){
		cf=cfL;
		delete cfR;
	} else {
		cf=cfR;
		delete cfL;
		rotateAngle = rotateAngle-180;
	}
	//printf("rotateAngleFinal= %f \n",rotateAngle ); // eliminate later, PRB
	cf->set_attr("align.score", peak);
	cf->set_attr("rotational", rotateAngle );
	cf->set_attr("align.az",rotateAngle);


	return cf;
}


EMData *RotatePrecenterAligner::align(EMData * this_img, EMData *to,  
			const string&, const Dict&) const
{
	if (!to) {
		return 0;
	}

	int ny = this_img->get_ysize();
	int size = Util::calc_best_fft_size((int) (M_PI * ny * 1.5));
	EMData *e1 = this_img->unwrap(4, ny * 7 / 16, size, 0, 0, 1);
	EMData *e2 = to->unwrap(4, ny * 7 / 16, size, 0, 0, 1);
	EMData *cf = e1->calc_ccfx(e2, 0, ny);

	float *data = cf->get_data();

	float peak = 0;
	int peak_index = 0;
	Util::find_max(data, size, &peak, &peak_index);
	float a = (float) ((1.0f - 1.0f * peak_index / size) * 180. * 2);
	this_img->rotate(a*180./M_PI, 0, 0);

	cf->set_attr("align.score", peak);
	cf->set_attr("align.az",a);
	cf->update();

	if( e1 )
	{
		delete e1;
		e1 = 0;
	}

	if( e2 )
	{
		delete e2;
		e2 = 0;
	}

	return cf;
}


EMData *RotateCHAligner::align(EMData * this_img, EMData *to,  
			const string&, const Dict&) const
{
	static vector < EMData * >ralfp;
	static int rali = 0;
	static int ralo = 0;
	static int rals = 0;

	if (!this_img) {
		return 0;
	}


	int irad = params.set_default("irad", 8);
	int orad = params.set_default("orad", 0);

	int nx = this_img->get_xsize();
	int ny = this_img->get_ysize();

	const int ralrad = 5;
	const int ralang = 8;

	if (nx != ny) {
		return 0;
	}

	if (irad <= 0) {
		irad = 6;
	}

	if (orad <= 2 || orad > nx / 2) {
		orad = nx / 2 - 2;
	}

	float center = 0;
	int max_num = 0;

	if (nx != rals || irad != rali || orad != ralo) {
		for (size_t i = 0; i < ralfp.size(); i++) {
			if( ralfp[i] )
			{
				delete ralfp[i];
				ralfp[i] = 0;
			}
		}
		ralfp.clear();

		rals = nx;
		ralo = orad;
		rali = irad;

		float wid = (float)((ralo - rali) / (ralrad + 1));

		for (int i = 0; i < ralang; i++) {
			for (int j = 0; j < ralrad; j++) {
				float cen = (j + i) * wid + rali;
				int na = 1 << (i + 1);

				if (cen * M_PI >= na) {
					EMData *d1 = new EMData();
					d1->set_size(nx, ny, 1);
					EMData *d2 = new EMData();
					d2->set_size(nx, ny, 1);

					center = cen;
					max_num = na;

					float *dat1 = d1->get_data();
					float *dat2 = d2->get_data();

					for (int x = 0; x < nx; x++) {
						for (int y = 0; y < ny; y++) {
							float a = 0;
							if (y != ny / 2 || x != nx / 2) {
								a = atan2((float) (y - ny / 2), (float) (x - nx / 2));
							}

							float r = (float)hypot((y - ny / 2), (x - nx / 2)) - cen;
							dat1[x + y * nx] = sin(a * na) * exp(-r * r / (wid * wid / 2.4f));
							dat2[x + y * nx] = cos(a * na) * exp(-r * r / (wid * wid / 2.4f));
						}
					}

					d1->update();
					d2->update();

					ralfp.push_back(d1);
					ralfp.push_back(d2);
				}
			}
		}
	}

	unsigned int i = 0;
	float ndot = 0;
	float aa = 0;

	for (i = 0; i < ralfp.size(); i += 2) {
		EMData *d1 = ralfp[i];
		EMData *d2 = ralfp[i + 1];

		float ta = this_img->dot(d1);
		float tb = this_img->dot(d2);
		float p1 = 0;
		if (ta != 0 || tb != 0) {
			p1 = atan2(ta, tb);
		}

		ta = to->dot(d1);
		tb = to->dot(d2);

		float a2 = (float)hypot(ta, tb);
		float p2 = 0;
		if (ta != 0 || tb != 0) {
			p2 = atan2(ta, tb);
		}

		float ca = p2 - p1;
		ca = (float)(ca - floor(ca / (2 * M_PI)) * 2 * M_PI);

		if (ca > M_PI) {
			ca -= (float) (2.0 * M_PI);
		}

		if (ndot > 0) {
			float dl = (float) (2.0 * M_PI / max_num);
			float ep = aa / ndot;
			ep = (float)((ep - floor(ep / dl) * dl) * 2.0 * M_PI / dl);
			ca -= ep;
			ca = (float) (ca - floor(ca / (2.0 * M_PI)) * 2.0 * M_PI);

			if (ca > M_PI) {
				ca -= (float) (2.0 * M_PI);
			}

			ca = aa / ndot + ca / max_num;
		}

		aa += ca * center * a2;
		ndot += center * a2;
#ifdef DEBUG
		printf("%f\t%d\n", ca * 180.0 / M_PI, i);
#endif
	}

#ifdef DEBUG
	printf("%f\t%d\n", aa / ndot * 180.0 / M_PI, i + 5);
#endif

	this_img->rotate(aa * 180. / ndot, 0, 0);
	this_img->set_attr("align.az", aa * 180. / ndot);
	return 0;
}


EMData *RotateTranslateAligner::align(EMData * this_img, EMData *to,  
			const string & cmp_name, const Dict& cmp_params) const
{
	params.set_default("maxshift", -1);
#if 0
	int usedot = params.set_default("usedot", 0);
	if (usedot) {
		cmp_name = "dot";
	}
#endif
	//printf(" This is the one \n");
	EMData *this_copy  = this_img->align("rotational", to);
	
	EMData *this_copy2 = this_copy->copy(); // Now this_copy, this_copy2
	this_copy2->rotate_180();               //  is an aligned version of this_img
	this_copy2->set_attr("align.az",(float)this_copy2->get_attr("rotational")+180.0);

	Dict trans_params;
	
	trans_params["intonly"]  = 1;
	trans_params["maxshift"] = params["maxshift"];
	trans_params["nozero"]   = params["nozero"];
	EMData *tmp = this_copy;
	this_copy=tmp->align("translational", to, trans_params);
	if( tmp )
	{
		delete tmp;
		tmp = 0;
	}
	
	tmp=this_copy2;
	this_copy2=tmp->align("translational", to, trans_params);
	if( tmp )
	{
		delete tmp;
		tmp = 0;
	}
	
	tmp = to;

	float dot1 = 0;
	float dot2 = 0;
	dot1 = this_copy  ->cmp(cmp_name, tmp, cmp_params);
	dot2 = this_copy2 ->cmp(cmp_name, tmp, cmp_params);

	EMData *result = 0;
	if (dot1 < dot2) {			// assumes smaller is better, won't work with Dot !!!
		this_copy->set_attr("align.score", dot1);
		if( this_copy2 )
		{
			delete this_copy2;
			this_copy2 = 0;
		}
		result = this_copy;
	}
	else {
		this_copy2->set_attr("align.score", dot2);
		if( this_copy )
		{
			delete this_copy;
			this_copy = 0;
		}
		result = this_copy2;
	}

	return result;
}


EMData *RotateTranslateBestAligner::align(EMData * this_img, EMData *to,  
			const string & cmp_name, const Dict& cmp_params) const
{
	params.set_default("maxshift", -1);

	EMData *this_copy = this_img->copy();
	this_img->align("rotational", to);
	
	Dict rotation = this_img->get_transform().get_rotation(Transform3D::EMAN);
	float cda = rotation["alt"];

	EMData *this_copy2 = this_copy->copy();

	Dict trans_params;
	
	trans_params["intonly"] = 0;
	trans_params["maxshift"] = params["maxshift"];
	this_copy->align("translational", to, trans_params);

	Vec3f trans_v = this_copy->get_translation();
	float cdx = trans_v[0] * cos(cda) + trans_v[1] * sin(cda);
	float cdy = trans_v[0] * sin(cda) + trans_v[1] * cos(cda);

	Dict refine_params;
	refine_params["alt"] = cda;
	refine_params["dx"] = cdx;
	refine_params["dy"] = cdy;
	if(params.has_key("dz")) {
		refine_params["dz"] = params["dz"];
	}
	if(params.has_key("snr")) {
		refine_params["snr"] = params["snr"];
	}

	this_copy->align("refine", to, refine_params);

	float cda2 = cda + (float)M_PI;
	this_copy2->rotate_180();

	this_copy2->align("translational", to, trans_params);
	Vec3f trans_v2 = this_copy2->get_translation();

	cdx = trans_v2[0] * cos(cda2) + trans_v2[1] * sin(cda2);
	cdy = -trans_v2[0] * sin(cda2) + trans_v2[1] * cos(cda2);

	refine_params["az"] = cda2/M_PI*180.;
	refine_params["dx"] = cdx;
	refine_params["dy"] = cdy;

	this_copy2->align("refine", to, refine_params);
	EMData * with = to;
	float dot1 = this_copy->cmp(cmp_name, with, cmp_params);
	float dot2 = this_copy2->cmp(cmp_name, with, cmp_params);

	EMData *result = 0;
	if (dot1 < dot2) {
		this_copy->set_attr("align.score", dot1);
		if( this_copy2 )
		{
			delete this_copy2;
			this_copy2 = 0;
		}
		result = this_copy;
	}
	else {
		this_copy2->set_attr("align.score", dot2);
		if( this_copy )
		{
			delete this_copy;
			this_copy = 0;
		}
		result = this_copy2;
	}

	return result;
}



EMData *RotateTranslateRadonAligner::align(EMData * this_img, EMData *to,  
			const string&, const Dict&) const
{

	int maxshift = params.set_default("maxshift", -1);
	EMData *radonwith = params.set_default("radonwith", (EMData *) 0);
	EMData *radonthis = params.set_default("radonthis", (EMData *) 0);

	int nx = this_img->get_xsize();
	int ny = this_img->get_ysize();
	int size = nx;

	if (nx != ny) {
		LOGERR("%s: images must be square", get_name().c_str());
		return 0;
	}

	if (to && !EMUtil::is_same_size(this_img, to)) {
		LOGERR("%s: images must be same size", get_name().c_str());
		return 0;
	}

	float *vert = new float[size];
	int drw = 0;
	int drt = 0;

	if (!radonwith) {
		drw = 1;
		radonwith = to->do_radon();
	}
	if (!radonthis) {
		drt = 1;
		radonthis = this_img->do_radon();
	}
	if (maxshift <= 0) {
		maxshift = size / 8;
	}

	EMData *t1 = radonthis->copy();
	radonthis->write_image("radon.hed", 0, EMUtil::IMAGE_IMAGIC);

	float si = 0;
	float co = 0;
	float max = 0;
	float ta = 0;
	int lda = 0;

	for (int j = 0; j < 3; j++) {
		if (j) {
			float *d = radonthis->get_data();
			float *d2 = t1->get_data();

			for (int x = 0; x < size; x++) {
				for (int y = maxshift; y < size - maxshift + 1; y++) {
					d2[x + y * size] =
						d[x + (y + (int) floor(max * sin(x * 2.0 * M_PI / size + ta))) * size];
				}
			}
		}

		t1->write_image("radon.hed", j + 1, EMUtil::IMAGE_IMAGIC);

		EMData *r1 = EMUtil::vertical_acf(t1, maxshift);
		EMData *r2 = EMUtil::vertical_acf(radonwith, maxshift);
		EMData *ccf = r1->calc_ccfx(r2, 0, maxshift);
		r1->write_image("racf.hed", 0, EMUtil::IMAGE_IMAGIC);
		r2->write_image("racf.hed", 1, EMUtil::IMAGE_IMAGIC);

		if( r1 )
		{
			delete r1;
			r1 = 0;
		}
		if( r2 )
		{
			delete r2;
			r2 = 0;
		}

		float *d = ccf->get_data();
		float peak_value = 0;
		int peak_x = 0;

		for (int i = 0; i < size; i++) {
			if (d[i] > peak_value) {
				peak_value = d[i];
				peak_x = i % size;
			}
		}
		
		if( ccf )
		{
			delete ccf;
			ccf = 0;
		}

		lda = peak_x;
		if (peak_x > size / 2) {
			lda = size - peak_x;
		}

#ifdef DEBUG
		printf("R Peak %d\t%g\t%1.2f\n", lda, peak_value, lda * 360.0 / size);
#endif

		d = radonthis->get_data();
		float *d2 = radonwith->get_data();
		int x2 = lda % size;

		for (int x = 0; x < size / 2; x++) {
			float best = 0;
			int besti = 0;
			for (int i = -maxshift; i < maxshift; i++) {
				float dot = 0;
				for (int y = maxshift; y < size - maxshift; y++) {
					dot += d2[x2 + y * size] * d[x + (y + i) * size];
				}

				if (dot > best) {
					best = dot;
					besti = i;
				}
			}

			vert[x] = (float)besti;
#ifdef DEBUG
			printf("%d\t%d\n", x, besti);
#endif
			x2 = (x2 + 1) % size;
		}

		si = co = max = ta = 0;
		for (int x = 0; x < size / 2; x++) {
			si += (float) sin(x * 2.0 * M_PI / size) * vert[x];
			co += (float) cos(x * 2 * M_PI / size) * vert[x];
			if (fabs(vert[x]) > max) {
				max = fabs(vert[x]);
			}
		}

		float inten = (si * si + co * co) / (size * (float)M_PI);
		ta = atan2(co, si);
#ifdef DEBUG
		printf("x, y = %g, %g\ta, p=%g / %g, %g\n", co, si, sqrt(inten), max, 180.0f / (float)M_PI * ta);
#endif
		max = floor(sqrt(inten) + 0.5f);

		t1->update();
		radonwith->update();
	}

	if( t1 )
	{
		delete t1;
		t1 = 0;
	}

	t1 = this_img->copy();

	t1->rotate_translate(-lda * (float)180. * 2.0f / size, 0, 0, -max * cos(ta), -max * sin(ta), 0);

	if (drt) {
		if( radonthis )
		{
			delete radonthis;
			radonthis = 0;
		}
	}

	if (drw) {
		if( radonwith )
		{
			delete radonwith;
			radonwith = 0;
		}
	}

	if( vert )
	{
		delete[]vert;
		vert = 0;
	}

	return t1;
}



EMData *RotateFlipAligner::align(EMData * this_img, EMData *to,  
			const string&, const Dict&) const
{
	EMData *flip = to;
	params.set_default("imask", 0);

	EMData *this_copy = this_img->copy();
	this_copy->align("rotational", to);

	float dot1 = this_copy->dot(to);
	float dot2 = 0;

	EMData *this_copy2 = this_img->copy();

	if (!flip) {
		this_copy2->process_inplace("xform.flip", Dict("axis", "y"));
	}

	this_copy2->align("rotational", to);
	dot2 = this_copy2->dot(to);

	EMData *result = 0;

	if (!this_copy) {
		result = this_copy2;
	}
	else if (!this_copy2) {
		result = this_copy;
	}
	else {
		if (dot1 < dot2) {
			this_copy->set_flipped(0);
			if( this_copy2 )
			{
				delete this_copy2;
				this_copy2 = 0;
			}
			result = this_copy;
		}
		else {
			this_copy2->set_flipped(1);
			if( this_copy )
			{
				delete this_copy;
				this_copy = 0;
			}
			result = this_copy2;
		}
	}

	return result;
}

EMData *RotateTranslateFlipAligner::align(EMData * this_img, EMData *to, 
			const string & given_cmp_name, const Dict& cmp_params) const
{
	EMData *with = to;
	EMData *flip = params.set_default("flip", (EMData *) 0);
	
	params.set_default("maxshift", -1);
	string cmp_name = given_cmp_name;
	int usedot = params.set_default("usedot", 1);
	if (usedot) {
		cmp_name = "dot";
	}

	EMData *this_copy = this_img->align("rotate_translate", to, Dict("maxshift", params["maxshift"]));
	EMData *this_copy2 = 0;

	if (flip) {
		this_copy2 = flip->align("rotate_translate", to, Dict("maxshift", params["maxshift"]));
	}
	else {
		this_img->process_inplace("xform.flip", Dict("axis", "x"));
		this_copy2 = this_img->align("rotate_translate", to, Dict("maxshift", params["maxshift"]));
	}

	if (!this_copy) {
		LOGERR("%s failed", get_name().c_str());
		return this_copy2;
	}
	if (!this_copy2) {
		LOGERR("%s flip failed", get_name().c_str());
		return this_copy;
	}

	float dot1 = 0;
	float dot2 = 0;

	if (usedot) {
		dot1 = this_copy->cmp(cmp_name, with, cmp_params);
		dot2 = this_copy2->cmp(cmp_name, with, cmp_params);

		if (usedot == 2) {
			Vec3f trans = this_copy->get_translation();
			Dict rot = this_copy->get_transform().get_rotation(Transform3D::EMAN);

			Vec3f trans2 = this_copy2->get_translation();
			Dict rot2 = this_copy2->get_transform().get_rotation(Transform3D::EMAN);

			printf("%f vs %f  (%1.1f, %1.1f  %1.2f) (%1.1f, %1.1f  %1.2f)\n",
				   dot1, dot2, trans[0], trans[1], (float)rot["alt"] * 180. / M_PI,
				   trans2[0], trans2[1], (float)rot2["alt"] * 180. / M_PI);
		}
	}
	else {
		cmp_params["keepzero"] = 1;

		dot1 = this_copy->cmp(cmp_name, with, cmp_params);
		dot2 = this_copy2->cmp(cmp_name, with, cmp_params);
	}

	EMData *result = 0;

	if (dot1 < dot2) {
		this_copy->set_attr("align.flip",0);
		this_copy->set_attr("align.score",dot1);
		if (!flip) {
			this_img->process_inplace("xform.flip", Dict("axis", "x"));
		}

		if( this_copy2 )
		{
			delete this_copy2;
			this_copy2 = 0;
		}
		result = this_copy;
	}
	else {
		this_copy2->set_attr("align.flip",1);
		this_copy2->set_attr("align.score",dot2);
		if( this_copy )
		{
			delete this_copy;
			this_copy = 0;
		}
		result = this_copy2;
	}

	return result;
}



EMData *RTFSlowAligner::align(EMData * this_img, EMData *to,  
			const string & cmp_name, const Dict& cmp_params) const
{

	EMData *flip = params.set_default("flip", (EMData *) 0);
	int maxshift = params.set_default("maxshift", -1);

	EMData *to_copy = to->copy();
	int ny = this_img->get_ysize();

	int xst = (int) floor(2 * M_PI * ny);
	xst = Util::calc_best_fft_size(xst);

	to_copy->median_shrink(2);

	int to_copy_r2 = to_copy->get_ysize() / 2 - 2 - maxshift / 2;
	EMData *tmp = to_copy->unwrap(4, to_copy_r2, xst / 2, 0, 0, true);
	if( to_copy )
	{
		delete to_copy;
		to_copy = 0;
	}
	to_copy = tmp;

	EMData *wsc = to_copy->copy();
	to = to->unwrap(4, to->get_ysize() / 2 - 2 - maxshift, xst, 0, 0, true);
	EMData *to_copy2 = to->copy();

	EMData *df = 0;
	if (flip) {
		df = flip->copy();
	}
	else {
		df = this_img->copy();
		df->process_inplace("xform.flip", Dict("axis", "x"));
	}

	EMData *dns = this_img->copy();
	EMData *dfs = df->copy();
	dns->median_shrink(2);
	dfs->median_shrink(2);

	int dflip = 0;
	float bestval = FLT_MAX;
	float bestang = 0;
	int bestflip = 0;
	int bestdx = 0;
	int bestdy = 0;

	int half_maxshift = maxshift / 2;
	for (dflip = 0; dflip < 2; dflip++) {
		EMData *u = 0;

		if (dflip) {
			u = dfs;
		}
		else {
			u = dns;
		}

		int ur2 = u->get_ysize() / 2 - 2 - half_maxshift;
		
		cmp_params["keepzero"] = 1;
		
		for (int dy = -half_maxshift; dy <= half_maxshift; dy++) {
			for (int dx = -half_maxshift; dx <= half_maxshift; dx++) {
				if (hypot(dx, dy) <= half_maxshift) {
					EMData *uw = u->unwrap(4, ur2, xst / 2, dx, dy, true);
					EMData *uwc = uw->copy();
					EMData *a = uw->calc_ccfx(to_copy);

					uwc->rotate_x(a->calc_max_index());

					float cm = uwc->cmp(cmp_name, wsc, cmp_params);

					if (cm < bestval) {
						bestval = cm;
						bestang = (float) (2.0 * M_PI * a->calc_max_index() / a->get_xsize());
						bestdx = dx;
						bestdy = dy;
						bestflip = dflip;
					}
					
					if( a )
					{
						delete a;
						a = 0;
					}
					if( uw )
					{
						delete uw;
						uw = 0;
					}
					if( uwc )
					{
						delete uwc;
						uwc = 0;
					}
				}
			}
		}
	}
	if( dns )
	{
		delete dns;
		dns = 0;
	}
	if( dfs )
	{
		delete dfs;
		dfs = 0;
	}
	if( to_copy )
	{
		delete to_copy;
		to_copy = 0;
	}
	if( wsc )
	{
		delete wsc;
		wsc = 0;
	}

	bestdx *= 2;
	bestdy *= 2;
	bestval = FLT_MAX;

	int bestdx2 = bestdx;
	int bestdy2 = bestdy;


	for (dflip = 0; dflip < 2; dflip++) {
		EMData *u = 0;

		if (dflip) {
			u = df;
			bestdx2 = -bestdx2;
			bestang = -bestang;
		}
		else {
			u = this_img;
		}


		for (int dy = bestdy2 - 3; dy <= bestdy2 + 3; dy++) {
			for (int dx = bestdx2 - 3; dx <= bestdx2 + 3; dx++) {
				if (hypot(dx, dy) <= maxshift) {
					EMData *uw = u->unwrap(4, u->get_ysize() / 2 - 2 - maxshift, xst, dx, dy, true);
					EMData *uwc = uw->copy();
					EMData *a = uw->calc_ccfx(to);

					uwc->rotate_x(a->calc_max_index());
					cmp_params["keepzero"] = 1;
					float cm = uwc->cmp(cmp_name, to_copy2, cmp_params);

					if (cm < bestval) {
						bestval = cm;
						bestang = (float)(2.0 * M_PI * a->calc_max_index() / a->get_xsize());
						bestdx = dx;
						bestdy = dy;
						bestflip = dflip;
					}
					if( a )
					{
						delete a;
						a = 0;
					}
					if( uw )
					{
						delete uw;
						uw = 0;
					}
					if( uwc )
					{
						delete uwc;
						uwc = 0;
					}
				}
			}
		}
	}
	
	if( to )
	{
		delete to;
		to = 0;
	}
	if( to_copy )
	{
		delete to_copy;
		to_copy = 0;
	}

	if (bestflip) {
		df->rotate_translate((float)bestang, 0.0f, 0.0f, (float)-bestdx, (float)-bestdy, 0.0f);
		df->set_flipped(1);
		return df;
	}

	if( df )
	{
		delete df;
		df = 0;
	}

	EMData *dn = 0;
	if (dflip) {
		dn = this_img->copy();
	}
	else {
		dn = this_img->copy();
	}

	dn->rotate_translate((float)bestang, 0.0f, 0.0f, (float)-bestdx, (float)-bestdy, 0.0f);

	return dn;
}

/*
EMData *RTFSlowestAligner::align(EMData * this_img, EMData *to,  
			const string & cmp_name, const Dict& cmp_params) const
{

	EMData *flip = params.set_default("flip", (EMData *) 0);
	int maxshift = params.set_default("maxshift", -1);

	EMData *dn = this_img->copy();
	EMData *df = 0;

	if (flip) {
		df = flip->copy();
	}
	else {
		df = this_img->copy();
		df->process_inplace("xform.flip", Dict("axis", "x"));
		df = df->copy();
	}

	int nx = this_img->get_xsize();

	if (maxshift < 0) {
		maxshift = nx / 10;
	}

	float astep = atan2(2.0f, (float)nx);

	EMData *dns = dn->copy();
	EMData *dfs = df->copy();
	EMData *to_copy = to->copy();

	dns->median_shrink(2);
	dfs->median_shrink(2);
	to_copy->median_shrink(2);
	dns = dns->copy();
	dfs = dfs->copy();

	int bestflip = 0;
	int bestdx = 0;
	int bestdy = 0;

	float bestang = 0;
	float bestval = FLT_MAX;

	int dflip = 0;
	int half_maxshift = maxshift / 2;

	for (dflip = 0; dflip < 2; dflip++) {
		EMData *u = 0;

		if (dflip) {
			u = dfs;
		}
		else {
			u = dns;
		}

		for (int dy = -half_maxshift; dy <= half_maxshift; dy++) {
			for (int dx = -half_maxshift; dx <= half_maxshift; dx++) {
				if (hypot(dx, dy) <= maxshift) {
					for (float ang = -astep * 2.0f; ang <= (float)2 * M_PI; ang += astep * 4.0f) {
						u->rotate_translate(ang, 0.0f, 0.0f, (float)dx, (float)dy, 0.0f);

						float lc = u->cmp(cmp_name, to_copy, cmp_params);

						if (lc < bestval) {
							bestval = lc;
							bestang = ang;
							bestdx = dx;
							bestdy = dy;
							bestflip = dflip;
						}
					}
				}
			}
		}
	}

	if( dns )
	{
		delete dns;
		dns = 0;
	}
	if( dfs )
	{
		delete dfs;
		dfs = 0;
	}
	if( to_copy )
	{
		delete to_copy;
		to_copy = 0;
	}

	bestdx *= 2;
	bestdy *= 2;
	bestval = FLT_MAX;

	int bestdx2 = bestdx;
	int bestdy2 = bestdy;
	float bestang2 = bestang;

	for (dflip = 0; dflip < 2; dflip++) {
		EMData *u = 0;
		if (dflip) {
			u = df;
		}
		else {
			u = dn;
		}

		if (dflip) {
			bestdx2 = -bestdx2;
		}

		for (int dy = bestdy2 - 3; dy <= bestdy2 + 3; dy++) {
			for (int dx = bestdx2 - 3; dx <= bestdx2 + 3; dx++) {
				if (hypot(dx, dy) <= maxshift) {
					for (float ang = bestang2 - astep * 6.0f; ang <= bestang2 + astep * 6.0f;
						 ang += astep) {
						u->rotate_translate(ang, 0.0f, 0.0f, (float)dx, (float)dy, 0.0f);

						cmp_params["keepzero"] = 1;
						float lc = u->cmp(cmp_name, to_copy, cmp_params);

						if (lc < bestval) {
							bestval = lc;
							bestang = ang;
							bestdx = dx;
							bestdy = dy;
							bestflip = dflip;
						}
					}
				}
			}
		}
	}

	if (bestflip) {
		if( dn )
		{
			delete dn;
			dn = 0;
		}

		df->rotate_translate(bestang, 0.0f, 0.0f, (float)bestdx, (float)bestdy, 0.0f);
		df->set_flipped(1);
		return df;
	}

	dn->rotate_translate(bestang, 0.0f, 0.0f, (float)bestdx, (float)bestdy, 0.0f);

	if( df )
	{
		delete df;
		df = 0;
	}

	return dn;
}
*/

EMData *RTFBestAligner::align(EMData * this_img, EMData *to,  
			const string & cmp_name, const Dict& cmp_params) const
{
	EMData *flip = params.set_default("flip", (EMData *) 0);
	params.set_default("maxshift", -1);

	Dict rtb_params;
	rtb_params["maxshift"] = params["maxshift"];
	rtb_params["snr"] = params["snr"];
	
	EMData *this_copy = this_img->align("rotate_translate_best", to, rtb_params);
	EMData *flip_copy = 0;

	if (!flip) {
		this_img->process_inplace("xform.flip", Dict("axis", "x"));
		flip_copy = this_img->align("rotate_translate_best", to, rtb_params);
	}
	else {
		flip_copy = flip->align("rotate_translate_best", to, rtb_params);
	}

	if (!this_copy) {
		LOGERR("%s align failed", get_name().c_str());
		return flip_copy;
	}
	else if (!flip_copy) {
		LOGERR("%s align failed", get_name().c_str());
		return this_copy;
	}

	EMData * with = to;
	float this_cmp = this_copy->cmp(cmp_name, with, cmp_params);
	float flip_cmp = flip_copy->cmp(cmp_name, with, cmp_params);

	EMData *result = 0;

	if (this_cmp > flip_cmp) {
		this_copy->set_flipped(0);
		if (!flip) {
			this_img->process_inplace("xform.flip", Dict("axis", "x"));
		}
		if( flip_copy )
		{
			delete flip_copy;
			flip_copy = 0;
		}
		result = this_copy;
	}
	else {
		flip_copy->set_flipped(1);
		if( this_copy )
		{
			delete this_copy;
			this_copy = 0;
		}
		result = flip_copy;
	}

	return result;
}


EMData *RTFRadonAligner::align(EMData * this_img, EMData *to,  
			const string&, const Dict&) const
{

	params.set_default("maxshift", -1);
	EMData *thisf = params.set_default("thisf", (EMData *) 0);
	EMData *radonwith = params.set_default("radonwith", (EMData *) 0);
	params.set_default("radonthis", (EMData *) 0);
	params.set_default("radonthisf", (EMData *) 0);

	int drw = 0;
	if (!radonwith) {
		drw = 1;
		radonwith = to->do_radon();
		params["radonwith"] = radonwith;
	}

	Dict rtr_params;
	rtr_params["maxshift"] = params["maxshift"];
	rtr_params["radonthis"] = params["radonthis"];
	rtr_params["radonwith"] = params["radonwith"];
	EMData *r1 = this_img->align("rotate_translate_radon", to, rtr_params);
	EMData *r2 = 0;

	if (!thisf) {
		this_img->process_inplace("xform.flip", Dict("axis", "x"));
		r2 = this_img->align("rtf_radon", to, params);
		this_img->process_inplace("xform.flip", Dict("axis", "x"));
	}
	else {
		r2 = thisf->align("rtf_radon", to, params);
	}

	float r1_score = r1->dot(to);
	float r2_score = r2->dot(to);

	if (drw) {
		if(radonwith)
		{
			delete radonwith;
			radonwith = 0;
		}
	}

	EMData *result = 0;
	if (r1_score < r2_score) {
		if(r1)
		{
			delete r1;
			r1 = 0;
		}

		if (!thisf) {
			this_img->process_inplace("xform.flip", Dict("axis", "x"));
		}
		result = r2;
	}
	else {
		if( r2 )
		{
			delete r2;
			r2 = 0;
		}
		result = r1;
	}

	return result;
}


static double refalifn(const gsl_vector * v, void *params)
{
	Dict *dict = (Dict *) params;

	double x = gsl_vector_get(v, 0);
	double y = gsl_vector_get(v, 1);
	double a = gsl_vector_get(v, 2);

	EMData *this_img = (*dict)["this"];
	EMData * with = (*dict)["with"];
	this_img->rotate_translate((float)a, 0.0f, 0.0f, (float)x, (float)y, 0.0f);

	Cmp* c = (Cmp*) ((void*)(*dict)["cmp"]);
	
	return c->cmp(this_img, with);
}

static double refalifnfast(const gsl_vector * v, void *params)
{
	Dict *dict = (Dict *) params;
	EMData *this_img = (*dict)["this"];
	EMData *img_to = (*dict)["with"];

	double x = gsl_vector_get(v, 0);
	double y = gsl_vector_get(v, 1);
	double a = gsl_vector_get(v, 2);

	double r = this_img->dot_rotate_translate(img_to, (float)x, (float)y, (float)a);
	int nsec = this_img->get_xsize() * this_img->get_ysize();
	double result = 1.0 - r / nsec;

	return result;
}


EMData *RefineAligner::align(EMData * this_img, EMData *to, 
	const string & cmp_name, const Dict& cmp_params) const
{

	if (!to) {
		return 0;
	}

	EMData *result = this_img->copy();

//	int ny = this_img->get_ysize();

//	float salt = this_img.get_attr("align.az");
//	float sdx = this_img.get_attr("align.dx");
//	float sdy = this_img.get_attr("align.dy");

//	float dda = atan(2.0f / ny);

	int mode = params.set_default("mode", 0);
	float saz = params.set_default("az",0.0);
	float sdx = params.set_default("dx",0.0);
	float sdy = params.set_default("dy",0.0);
	int np = 3;
	Dict gsl_params;
	gsl_params["this"] = this_img;
	gsl_params["with"] = to;
	gsl_params["snr"]  = params["snr"];
	
	Cmp *c = Factory < Cmp >::get(cmp_name, cmp_params);
	gsl_params["cmp"] = (void *) c;
	
	const gsl_multimin_fminimizer_type *T = gsl_multimin_fminimizer_nmsimplex;
	gsl_vector *ss = gsl_vector_alloc(np);
	gsl_vector_set(ss, 0, 1.0f);
	gsl_vector_set(ss, 1, 1.0f);
	gsl_vector_set(ss, 2, 0.1f);

	gsl_vector *x = gsl_vector_alloc(np);
	gsl_vector_set(x, 0, sdx);
	gsl_vector_set(x, 1, sdy);
	gsl_vector_set(x, 2, saz);

	gsl_multimin_function minex_func;
	if (mode == 2) {
		minex_func.f = &refalifnfast;
	}
	else {
		minex_func.f = &refalifn;
	}
	
	minex_func.n = np;
	minex_func.params = (void *) &gsl_params;

	gsl_multimin_fminimizer *s = gsl_multimin_fminimizer_alloc(T, np);
	gsl_multimin_fminimizer_set(s, &minex_func, x, ss);

	int rval = GSL_CONTINUE;
	int status = GSL_SUCCESS;
	int iter = 1;

	while (rval == GSL_CONTINUE && iter < 28) {
		iter++;
		status = gsl_multimin_fminimizer_iterate(s);
		if (status) {
			break;
		}

		rval = gsl_multimin_test_size(gsl_multimin_fminimizer_size(s), 0.04f);
	}

	result->rotate_translate((float)gsl_vector_get(s->x, 2), 0, 0,
								(float)gsl_vector_get(s->x, 0), (float)gsl_vector_get(s->x, 1), 0);
	
	this_img->set_attr("align.az",(float)gsl_vector_get(s->x, 2));
	this_img->set_attr("align.dx",(float)gsl_vector_get(s->x, 0));
	this_img->set_attr("align.dy",(float)gsl_vector_get(s->x, 1));

	gsl_vector_free(x);
	gsl_vector_free(ss);
	gsl_multimin_fminimizer_free(s);
	
	delete c;
	return result;
}

void EMAN::dump_aligners()
{
	dump_factory < Aligner > ();
}

map<string, vector<string> > EMAN::dump_aligners_list()
{
	return dump_factory_list < Aligner > ();
}
