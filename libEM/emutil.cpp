/**
 * $Id$
 */
#include "emutil.h"
#include "log.h"
#include "io.h"
#include "transform.h"
#include "portable_fileio.h"
#include "emcache.h"
#include "emdata.h"
#include "ctf.h"

#include <assert.h>

using namespace EMAN;

EMUtil::ImageType EMUtil::get_image_ext_type(string file_ext)
{
	ENTERFUNC;
	static bool initialized = false;
	static map < string, ImageType > imagetypes;

	if (!initialized) {
		imagetypes["mrc"] = IMAGE_MRC;
		imagetypes["MRC"] = IMAGE_MRC;
		
		imagetypes["tnf"] = IMAGE_MRC;
		imagetypes["TNF"] = IMAGE_MRC;
		
		imagetypes["dm3"] = IMAGE_DM3;
		imagetypes["DM3"] = IMAGE_DM3;
		
		imagetypes["spi"] = IMAGE_SPIDER;
		imagetypes["SPI"] = IMAGE_SPIDER;
		
		imagetypes["img"] = IMAGE_IMAGIC;
		imagetypes["IMG"] = IMAGE_IMAGIC;
		
		imagetypes["hed"] = IMAGE_IMAGIC;
		imagetypes["HED"] = IMAGE_IMAGIC;
		
		imagetypes["pgm"] = IMAGE_PGM;
		imagetypes["PGM"] = IMAGE_PGM;
		
		imagetypes["lst"] = IMAGE_LST;
		imagetypes["LST"] = IMAGE_LST;
		
		imagetypes["pif"] = IMAGE_PIF;
		imagetypes["PIF"] = IMAGE_PIF;
		
		imagetypes["png"] = IMAGE_PNG;
		imagetypes["PNG"] = IMAGE_PNG;
		
		imagetypes["h5"] = IMAGE_HDF;
		imagetypes["H5"] = IMAGE_HDF;
		
		imagetypes["hd5"] = IMAGE_HDF;
		imagetypes["HD5"] = IMAGE_HDF;
		
		imagetypes["hdf"] = IMAGE_HDF;
		imagetypes["HDF"] = IMAGE_HDF;
		
		imagetypes["tif"] = IMAGE_TIFF;
		imagetypes["TIF"] = IMAGE_TIFF;
		
		imagetypes["tiff"] = IMAGE_TIFF;
		imagetypes["TIFF"] = IMAGE_TIFF;
		
		imagetypes["vtk"] = IMAGE_VTK;
		imagetypes["VTK"] = IMAGE_VTK;
		
		imagetypes["hdr"] = IMAGE_SAL;
		imagetypes["HDR"] = IMAGE_SAL;
		
		imagetypes["sal"] = IMAGE_SAL;
		imagetypes["SAL"] = IMAGE_SAL;
		
		imagetypes["map"] = IMAGE_ICOS;
		imagetypes["MAP"] = IMAGE_ICOS;

		imagetypes["icos"] = IMAGE_ICOS;
		imagetypes["ICOS"] = IMAGE_ICOS;
		
		imagetypes["am"] = IMAGE_AMIRA;
		imagetypes["AM"] = IMAGE_AMIRA;
		
		imagetypes["amira"] = IMAGE_AMIRA;
		imagetypes["AMIRA"] = IMAGE_AMIRA;
		
		imagetypes["emim"] = IMAGE_EMIM;
		imagetypes["EMIM"] = IMAGE_EMIM;
		
		imagetypes["xplor"] = IMAGE_XPLOR;
		imagetypes["XPLOR"] = IMAGE_XPLOR;
		
		imagetypes["em"] = IMAGE_EM;
		imagetypes["EM"] = IMAGE_EM;
		
		imagetypes["dm2"] = IMAGE_GATAN2;
		imagetypes["DM2"] = IMAGE_GATAN2;

		initialized = true;
	}
	EXITFUNC;
	return imagetypes[file_ext];
}


EMUtil::ImageType EMUtil::fast_get_image_type(string filename, const void *first_block,
											  off_t file_size)
{
	ENTERFUNC;
	char *ext = strrchr(filename.c_str(), '.');
	if (!ext) {
		return IMAGE_UNKNOWN;
	}
	ext++;
	ImageType image_type = get_image_ext_type(ext);

	switch (image_type) {
	case IMAGE_MRC:
		if (MrcIO::is_valid(first_block, file_size)) {
			return IMAGE_MRC;
		}
		break;
	case IMAGE_IMAGIC:
		if (ImagicIO::is_valid(first_block)) {
			return IMAGE_IMAGIC;
		}
		break;
	case IMAGE_DM3:
		if (DM3IO::is_valid(first_block)) {
			return IMAGE_DM3;
		}
		break;
#ifdef EM_HDF5
	case IMAGE_HDF:
		if (HdfIO::is_valid(first_block)) {
			return IMAGE_HDF;
		}
		break;
#endif
	case IMAGE_LST:
		if (LstIO::is_valid(first_block)) {
			return IMAGE_LST;
		}
		break;
#ifdef EM_TIFF
	case IMAGE_TIFF:
		if (TiffIO::is_valid(first_block)) {
			return IMAGE_TIFF;
		}
		break;
#endif
	case IMAGE_SPIDER:
		if (SpiderIO::is_valid(first_block)) {
			return IMAGE_SPIDER;
		}
		break;
	case IMAGE_SINGLE_SPIDER:
		if (SingleSpiderIO::is_valid(first_block)) {
			return IMAGE_SINGLE_SPIDER;
		}
		break;
	case IMAGE_PIF:
		if (PifIO::is_valid(first_block)) {
			return IMAGE_PIF;
		}
		break;
#ifdef EM_PNG
	case IMAGE_PNG:
		if (PngIO::is_valid(first_block)) {
			return IMAGE_PNG;
		}
		break;
#endif
	case IMAGE_VTK:
		if (VtkIO::is_valid(first_block)) {
			return IMAGE_VTK;
		}
		break;
	case IMAGE_PGM:
		if (PgmIO::is_valid(first_block)) {
			return IMAGE_PGM;
		}
		break;
	case IMAGE_EMIM:
		if (EmimIO::is_valid(first_block)) {
			return IMAGE_EMIM;
		}
		break;
	case IMAGE_ICOS:
		if (IcosIO::is_valid(first_block)) {
			return IMAGE_ICOS;
		}
		break;
	case IMAGE_SAL:
		if (SalIO::is_valid(first_block)) {
			return IMAGE_SAL;
		}
		break;
	case IMAGE_AMIRA:
		if (AmiraIO::is_valid(first_block)) {
			return IMAGE_AMIRA;
		}
		break;
	case IMAGE_XPLOR:
		if (XplorIO::is_valid(first_block)) {
			return IMAGE_XPLOR;
		}
		break;
	case IMAGE_GATAN2:
		if (Gatan2IO::is_valid(first_block)) {
			return IMAGE_GATAN2;
		}
		break;
	case IMAGE_EM:
		if (EmIO::is_valid(first_block, file_size)) {
			return IMAGE_EM;
		}
		break;
	default:
		return IMAGE_UNKNOWN;
	}
	EXITFUNC;
	return IMAGE_UNKNOWN;
}


EMUtil::ImageType EMUtil::get_image_type(string filename)
{
	ENTERFUNC;

	size_t ext_pos = filename.find(".img");
	if (ext_pos != string::npos) {
		filename.replace(ext_pos, 4, ".hed");
	}

	FILE *in = fopen(filename.c_str(), "rb");
	if (!in) {
		LOGERR("cannot open image file: '%s'", filename.c_str());
		return IMAGE_UNKNOWN;
	}

	char first_block[1024];
	size_t n = fread(&first_block, sizeof(char), sizeof(first_block), in);
	portable_fseek(in, 0, SEEK_END);
	off_t file_size = portable_ftell(in);

	if (n == 0) {
		LOGERR("file '%s' is an empty file", filename.c_str());
		fclose(in);
		return IMAGE_UNKNOWN;
	}
	fclose(in);

	ImageType image_type = fast_get_image_type(filename, first_block, file_size);
	if (image_type != IMAGE_UNKNOWN) {
		return image_type;
	}

	if (MrcIO::is_valid(&first_block, file_size)) {
		image_type = IMAGE_MRC;
	}
	else if (DM3IO::is_valid(&first_block)) {
		image_type = IMAGE_DM3;
	}
#ifdef EM_HDF5
	else if (HdfIO::is_valid(&first_block)) {
		image_type = IMAGE_HDF;
	}
#endif
	else if (LstIO::is_valid(&first_block)) {
		image_type = IMAGE_LST;
	}
#ifdef EM_TIFF
	else if (TiffIO::is_valid(&first_block)) {
		image_type = IMAGE_TIFF;
	}
#endif
	else if (SpiderIO::is_valid(&first_block)) {
		image_type = IMAGE_SPIDER;
	}
	else if (SingleSpiderIO::is_valid(&first_block)) {
		image_type = IMAGE_SINGLE_SPIDER;
	}
	else if (PifIO::is_valid(&first_block)) {
		image_type = IMAGE_PIF;
	}
#ifdef EM_PNG
	else if (PngIO::is_valid(&first_block)) {
		image_type = IMAGE_PNG;
	}
#endif
	else if (VtkIO::is_valid(&first_block)) {
		image_type = IMAGE_VTK;
	}
	else if (PgmIO::is_valid(&first_block)) {
		image_type = IMAGE_PGM;
	}
	else if (EmimIO::is_valid(&first_block)) {
		image_type = IMAGE_EMIM;
	}
	else if (IcosIO::is_valid(&first_block)) {
		image_type = IMAGE_ICOS;
	}
	else if (SalIO::is_valid(&first_block)) {
		image_type = IMAGE_SAL;
	}
	else if (AmiraIO::is_valid(&first_block)) {
		image_type = IMAGE_AMIRA;
	}
	else if (XplorIO::is_valid(&first_block)) {
		image_type = IMAGE_XPLOR;
	}
	else if (Gatan2IO::is_valid(&first_block)) {
		image_type = IMAGE_GATAN2;
	}
	else if (EmIO::is_valid(&first_block, file_size)) {
		image_type = IMAGE_EM;
	}
	else if (ImagicIO::is_valid(&first_block)) {
		image_type = IMAGE_IMAGIC;
	}
	else {		
		LOGERR("I don't know this image's type: '%s'", filename.c_str());
		throw ImageFormatException("invalid image type");
	}

	EXITFUNC;
	return image_type;
}


int EMUtil::get_image_count(string filename)
{
	ENTERFUNC;
	int nimg = 0;
	ImageIO *imageio = get_imageio(filename, ImageIO::READ_ONLY);

	if (imageio) {
		nimg = imageio->get_nimg();
	}
	EXITFUNC;
	return nimg;
}


ImageIO *EMUtil::get_imageio(string filename, int rw, ImageType image_type)
{
	ENTERFUNC;
	ImageIO *imageio = GlobalCache::instance()->get_imageio(filename, rw);
	if (imageio) {
		return imageio;
	}

	ImageIO::IOMode rw_mode = static_cast < ImageIO::IOMode > (rw);

	if (image_type == IMAGE_UNKNOWN) {
		image_type = get_image_type(filename);
	}

	switch (image_type) {
	case IMAGE_MRC:
		imageio = new MrcIO(filename, rw_mode);
		break;
	case IMAGE_IMAGIC:
		imageio = new ImagicIO(filename, rw_mode);
		break;
	case IMAGE_DM3:
		imageio = new DM3IO(filename, rw_mode);
		break;
#ifdef EM_TIFF
	case IMAGE_TIFF:
		imageio = new TiffIO(filename, rw_mode);
		break;
#endif
#ifdef EM_HDF5
	case IMAGE_HDF:
		imageio = new HdfIO(filename, rw_mode);
		break;
#endif
	case IMAGE_LST:
		imageio = new LstIO(filename, rw_mode);
		break;
	case IMAGE_PIF:
		imageio = new PifIO(filename, rw_mode);
		break;
	case IMAGE_VTK:
		imageio = new VtkIO(filename, rw_mode);
		break;
	case IMAGE_SPIDER:
		imageio = new SpiderIO(filename, rw_mode);
		break;
	case IMAGE_SINGLE_SPIDER:
		imageio = new SingleSpiderIO(filename, rw_mode);
		break;
	case IMAGE_PGM:
		imageio = new PgmIO(filename, rw_mode);
		break;
	case IMAGE_EMIM:
		imageio = new EmimIO(filename, rw_mode);
		break;
	case IMAGE_ICOS:
		imageio = new IcosIO(filename, rw_mode);
		break;
#ifdef EM_PNG
	case IMAGE_PNG:
		imageio = new PngIO(filename, rw_mode);
		break;
#endif
	case IMAGE_SAL:
		imageio = new SalIO(filename, rw_mode);
		break;
	case IMAGE_AMIRA:
		imageio = new AmiraIO(filename, rw_mode);
		break;
	case IMAGE_GATAN2:
		imageio = new Gatan2IO(filename, rw_mode);
		break;
	case IMAGE_EM:
		imageio = new EmIO(filename, rw_mode);
		break;
	case IMAGE_XPLOR:
		imageio = new XplorIO(filename, rw_mode);
		break;
	default:
		break;
	}

	GlobalCache::instance()->add_imageio(filename, rw, imageio);
	EXITFUNC;
	return imageio;
}



const char *EMUtil::get_imagetype_name(ImageType t)
{
	switch (t) {
	case IMAGE_MRC:
		return "MRC";
	case IMAGE_SPIDER:
		return "SPIDER";
	case IMAGE_SINGLE_SPIDER:
		return "Single-SPIDER";
	case IMAGE_IMAGIC:
		return "IMAGIC";
	case IMAGE_PGM:
		return "PGM";
	case IMAGE_LST:
		return "LST";
	case IMAGE_PIF:
		return "PIF";
	case IMAGE_PNG:
		return "PNG";
	case IMAGE_HDF:
		return "HDF5";
	case IMAGE_DM3:
		return "GatanDM3";
	case IMAGE_TIFF:
		return "TIFF";
	case IMAGE_VTK:
		return "VTK";
	case IMAGE_SAL:
		return "HDR";
	case IMAGE_ICOS:
		return "ICOS_MAP";
	case IMAGE_EMIM:
		return "EMIM";
	case IMAGE_GATAN2:
		return "GatanDM2";
	case IMAGE_AMIRA:
		return "AmiraMesh";
	case IMAGE_XPLOR:
		return "XPLOR";
	case IMAGE_EM:
		return "EM";
	case IMAGE_UNKNOWN:
		return "unknown";
	}
	return "unknown";
}

const char *EMUtil::get_datatype_string(EMDataType type)
{
	switch (type) {
	case EM_CHAR:
		return "CHAR";
	case EM_UCHAR:
		return "UNSIGNED CHAR";
	case EM_SHORT:
		return "SHORT";
	case EM_USHORT:
		return "UNSIGNED SHORT";
	case EM_INT:
		return "INT";
	case EM_UINT:
		return "UNSIGNED INT";
	case EM_FLOAT:
		return "FLOAT";
	case EM_DOUBLE:
		return "DOUBLE";
	case EM_SHORT_COMPLEX:
		return "SHORT_COMPLEX";
	case EM_USHORT_COMPLEX:
		return "USHORT_COMPLEX";
	case EM_FLOAT_COMPLEX:
		return "FLOAT_COMPLEX";
	case EM_UNKNOWN:
		return "UNKNOWN";
	}
	return "UNKNOWN";
}

void EMUtil::get_region_dims(const Region * area, int nx, int *area_x,
							 int ny, int *area_y, int nz, int *area_z)
{
	if (!area) {
		*area_x = nx;
		*area_y = ny;
		if (area_z) {
			*area_z = nz;
		}
	}
	else {
		*area_x = (int)area->size.x;
		*area_y = (int)area->size.y;

		if (area_z) {
			if (area->get_ndim() > 2 && nz > 1) {
				*area_z = (int)area->size.z;
			}
			else {
				*area_z = 1;
			}
		}
	}
}

void EMUtil::get_region_origins(const Region * area, int *p_x0, int *p_y0, int *p_z0,
								int nz, int image_index)
{
	if (area) {
		*p_x0 = static_cast < int >(area->origin.x);
		*p_y0 = static_cast < int >(area->origin.y);

		if (p_z0 && nz > 1 && area->get_ndim() > 2) {
			*p_z0 = static_cast < int >(area->origin.z);
		}
	}
	else {
		*p_x0 = 0;
		*p_y0 = 0;
		if (p_z0) {
			*p_z0 = nz > 1 ? 0 : image_index;
		}
	}
}


int EMUtil::get_region_data(unsigned char *cdata, FILE * in, int image_index, size_t mode_size,
							int nx, int ny, int nz, const Region * area, bool need_flip,
							int pre_row, int post_row)
{
	assert(mode_size <= sizeof(float));

	int x0 = 0;
	int y0 = 0;
	int z0 = nz > 1 ? 0 : image_index;

	int xlen, ylen, zlen;
	get_region_dims(area, nx, &xlen, ny, &ylen, nz, &zlen);

	if (area) {
		x0 = static_cast < int >(area->origin.x);
		y0 = static_cast < int >(area->origin.y);
		if (nz > 1 && area->get_ndim() > 2) {
			z0 = static_cast < int >(area->origin.z);
		}
	}

	size_t area_sec_size = xlen * ylen * mode_size;
	size_t img_row_size = nx * mode_size + pre_row + post_row;
	size_t area_row_size = xlen * mode_size;

	size_t x_pre_gap = x0 * mode_size;
	size_t x_post_gap = (nx - x0 - xlen) * mode_size;

	size_t y_pre_gap = y0 * img_row_size;
	size_t y_post_gap = (ny - y0 - ylen) * img_row_size;

	portable_fseek(in, img_row_size * ny * z0, SEEK_CUR);

	for (int k = 0; k < zlen; k++) {
		if (area) {
			portable_fseek(in, y_pre_gap, SEEK_CUR);
		}
		for (int j = 0; j < ylen; j++) {
			if (pre_row > 0) {
				portable_fseek(in, pre_row, SEEK_CUR);
			}

			if (area) {
				portable_fseek(in, x_pre_gap, SEEK_CUR);
			}

			int jj = j;
			if (need_flip) {
				jj = ylen - 1 - j;
			}

			if (fread(&cdata[k * area_sec_size + jj * area_row_size], area_row_size, 1, in) != 1) {
				LOGERR("incomplete data read");
				return 1;
			}
			if (area) {
				portable_fseek(in, x_post_gap, SEEK_CUR);
			}

			if (post_row > 0) {
				portable_fseek(in, post_row, SEEK_CUR);
			}
		}

		if (area) {
			portable_fseek(in, y_post_gap, SEEK_CUR);
		}
	}

	return 0;
}


void EMUtil::dump_dict(const Dict & dict)
{
	vector < string > keys = dict.keys();
	vector < EMObject > values = dict.values();

	for (unsigned int i = 0; i < keys.size(); i++) {
		EMObject obj = values[i];
		string val = obj.to_str();

		if (keys[i] == "datatype") {
			val = get_datatype_string((EMDataType) (int) obj);
		}

		fprintf(stdout, "%25s\t%s\n", keys[i].c_str(), val.c_str());
	}
}

#if 0
bool EMUtil::is_same_size(const EMData & em1, const EMData & em2)
{
	if (em1.get_xsize() == em2.get_xsize() &&
		em1.get_ysize() == em2.get_ysize() && em1.get_zsize() == em2.get_zsize()) {
		return true;
	}
	return false;
}
#endif

bool EMUtil::is_same_size(const EMData * em1, const EMData * em2)
{
	if (em1->get_xsize() == em2->get_xsize() &&
		em1->get_ysize() == em2->get_ysize() && em1->get_zsize() == em2->get_zsize()) {
		return true;
	}
	return false;
}


EMData *EMUtil::vertical_acf(const EMData * image, int maxdy)
{
	EMData *ret = new EMData();
	int nx = image->get_xsize();
	int ny = image->get_ysize();

	if (maxdy <= 1) {
		maxdy = ny / 8;
	}

	ret->set_size(nx, maxdy, 1);

	float *data = image->get_data();
	float *ret_data = ret->get_data();

	for (int x = 0; x < nx; x++) {
		for (int y = 0; y < maxdy; y++) {
			float dot = 0;
			for (int yy = maxdy; yy < ny - maxdy; yy++) {
				dot += data[x + (yy + y) * nx] * data[x + (yy - y) * nx];
			}
			ret_data[x + y * nx] = dot;
		}
	}

	ret->done_data();

	return ret;
}



EMData *EMUtil::make_image_median(const vector < EMData * >&image_list)
{
	if (image_list.size() == 0) {
		return 0;
	}

	EMData *image0 = image_list[0];
	int image0_nx = image0->get_xsize();
	int image0_ny = image0->get_ysize();
	int image0_nz = image0->get_zsize();
	int size = image0_nx * image0_ny * image0_nz;

	EMData *result = new EMData();

	result->set_size(image0_nx, image0_ny, image0_nz);

	float *dest = result->get_data();
	int nitems = static_cast < int >(image_list.size());
	float *srt = new float[nitems];
	float **src = new float *[nitems];

	for (int i = 0; i < nitems; i++) {
		src[i] = image_list[i]->get_data();
	}

	for (int i = 0; i < size; i++) {
		for (int j = 0; j < nitems; j++) {
			srt[j] = src[j][i];
		}

		for (int j = 0; j < nitems; j++) {
			for (int k = j + 1; k < nitems; k++) {
				if (srt[j] < srt[k]) {
					float v = srt[j];
					srt[j] = srt[k];
					srt[k] = v;
				}
			}
		}

		int l = nitems / 2;
		if (nitems < 3) {
			dest[i] = srt[l];
		}
		else {
			dest[i] = (srt[l] + srt[l + 1] + srt[l - 1]) / 3.0;
		}
	}

	result->done_data();
	delete[]srt;
	srt = 0;
	delete[]src;
	src = 0;

	result->update();

	return result;
}

bool EMUtil::is_same_ctf(const EMData * image1, const EMData * image2)
{
	Ctf *ctf1 = image1->get_ctf();
	Ctf *ctf2 = image2->get_ctf();

	if ((!ctf1 && !ctf2) && (image1->has_ctff() == false && image2->has_ctff() == false)) {
		return true;
	}

	if (ctf1 && ctf2) {
		return ctf1->equal(ctf2);
	}
	return false;
}
