/**
 * $Id$
 */

#ifndef eman__testutil_h__
#define eman__testutil_h__

#include "geometry.h"
#include "vec3.h"
#include "emobject.h"
#include "emdata.h"

#include <map>
#include <vector>
#include <string>

using std::map;
using std::vector;
using std::string;

namespace EMAN
{
	/**TestUtil defines function assisting testing of EMAN2.
	 */

	class Dict;
	
	class TestUtil
	{
	public:
		static const char * EMDATA_HEADER_EXT;
		static const char * EMDATA_DATA_EXT;
		
		static int get_debug_int(int i);
		static float get_debug_float(int i);
		static string get_debug_string(int i);
		
		static string get_debug_image(const string & imagename);
		static string get_golden_image(const string & imagename);
		
		static void to_emobject(const Dict & d);

		static EMObject emobject_to_py(int n);
		static EMObject emobject_to_py(float f);
		static EMObject emobject_to_py(double f);
		static EMObject emobject_to_py(const string& str);
		static EMObject emobject_to_py(EMData * emdata);
		static EMObject emobject_to_py(XYData * xydata);
		static EMObject emobject_to_py(const vector<float> & farray);
		static EMObject emobject_to_py(const vector<string> & strarray);
		
		static IntPoint test_IntPoint(const IntPoint & p);
		static FloatPoint test_FloatPoint(const FloatPoint & p);
		static IntSize test_IntSize(const IntSize & p);
		static FloatSize test_FloatSize(const FloatSize & p);
		static Vec3i test_Vec3i(const Vec3i & p);
		static Vec3f test_Vec3f(const Vec3f & p);

		static vector<int> test_vector_int(const vector<int> & v);
		static vector<float> test_vector_float(const vector<float> & v);
		static vector<long> test_vector_long(const vector<long> & v);
		static vector<string> test_vector_string(const vector<string> & v);
		static vector<EMData*> test_vector_emdata(const vector<EMData*> & v);
		static vector<Pixel> test_vector_pixel(const vector<Pixel> & v);

		static map<string, int> test_map_int(const map<string, int>& d);
		static map<string, long> test_map_long(const map<string, long>& d);
		static map<string, float> test_map_float(const map<string, float>& d);
		static map<string, string> test_map_string(const map<string, string>& d);
		static map<string, EMObject> test_map_emobject(const map<string, EMObject>& d);
		static map<string, vector<string> > test_map_vecstring(const map<string,
															   vector<string> >& d);

		static Dict test_dict(const Dict & d);

		static void dump_image_from_file(const string & filename);
		static void dump_emdata(EMData * image, const string & filename);
		static int check_image(const string& imagefile, EMData * image = 0);
        static void set_progname(const string & cur_progname);
        
        static void make_image_file(const string & filename,
									EMUtil::ImageType image_type,
									EMUtil::EMDataType datatype = EMUtil::EM_FLOAT,
									int nx = 16, int ny = 16, int nz = 1)
        {
            make_image_file_by_mode(filename, image_type, 1, datatype, nx, ny, nz);
        }

		static int verify_image_file(const string & filename,
									 EMUtil::ImageType image_type,
									 EMUtil::EMDataType datatype = EMUtil::EM_FLOAT,
									 int nx = 16, int ny = 16, int nz = 1)
        {
            return verify_image_file_by_mode(filename, image_type, 1, datatype, nx, ny, nz);
        }

        static void make_image_file2(const string & filename,
									 EMUtil::ImageType image_type,
									 EMUtil::EMDataType datatype = EMUtil::EM_FLOAT,
									 int nx = 16, int ny = 16, int nz = 1)
        {
            make_image_file_by_mode(filename, image_type, 2, datatype,nx, ny, nz);
        }

		static int verify_image_file2(const string & filename,
									  EMUtil::ImageType image_type,
									  EMUtil::EMDataType datatype = EMUtil::EM_FLOAT,
									  int nx = 16, int ny = 16, int nz = 1)
        {            
            return verify_image_file_by_mode(filename, image_type, 2,
											 datatype, nx, ny, nz);
        }

        
        
		
	private:
		static float tf[10];
		static int ti[10];
		static string progname;
        
        static void make_image_file_by_mode(const string & filename,
											EMUtil::ImageType image_type, int mode,
											EMUtil::EMDataType datatype = EMUtil::EM_FLOAT,
											int nx = 16, int ny = 16, int nz = 1);
        
		static int verify_image_file_by_mode(const string & filename,
											 EMUtil::ImageType image_type, int mode,
											 EMUtil::EMDataType datatype = EMUtil::EM_FLOAT,
											 int nx = 16, int ny = 16, int nz = 1);
        
        
		static float get_pixel_value_by_dist1(int nx, int ny, int nz, int x, int y, int z)
		{
            int x2 = x;
            int y2 = y;
            int z2 = z;

            x2 = abs(nx/2-x);
            y2 = abs(ny/2-y);

            if (z > nz/2) {
                z2 = nz-z;
            }
            
            if (nz == 1) {
                return (x2*x2 + y2*y2);
            }
            else {
                int areax = (int)((float)nx * z2 / nz);
                int areay = (int)((float)ny * z2 / nz);
                if ((abs(x-nx/2) <= areax) && (abs(y-ny/2) <= areay)) {
                    return (x2*x2 + y2*y2);
                }
                else {
                    return 0;
                }
            }
		}

        static float get_pixel_value_by_dist2(int nx, int ny, int nz, int x, int y, int z)
		{
            int x2 = x;
            int y2 = y;
            int z2 = z;


            if (x > nx/2) {
                x2 = nx-x;
            }
            if (y > ny/2) {
                y2 = ny-y;
            }

            if (z > nz/2) {
                z2 = nz-z;
            }
            
            if (nz == 1) {
                return (x2*x2 + y2*y2);
            }
            else {
                int areax = (int)((float)nx * z2 / nz);
                int areay = (int)((float)ny * z2 / nz);
                if ((abs(x-nx/2) <= areax) && (abs(y-ny/2) <= areay)) {
                    return (x2*x2 + y2*y2);
                }
                else {
                    return 0;
                }
            }
        }
	};


	
	
    
}

#endif


