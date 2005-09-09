/**
 * $Id$
 */
#ifndef eman_reconstructor_h__
#define eman_reconstructor_h__ 1

#include "emdata.h"

using std::vector;
using std::map;
using std::string;

namespace EMAN
{

	class Transform3D;
	class EMData;
	
	
	/** Reconstructor class defines a way to do 3D recontruction.
	 * A reconstruction is done by 3 steps:
	 *   - set up.
	 *   - insert all image slices.
	 *   - finish up. The last step will return the result.
	 * 
	 * Reconstructor class is the base class for all reconstructors.
     * Each specific Reconstructor class has a unique ID name. This name
     * is used to create a Reconstructor instance or do a reconstruction.
     *
	 * All Reconstructor classes in EMAN are managed by a Factory
	 * pattern. So each Reconstructor class must define:
	 *   - a unique name to idenfity itself in the factory.
	 *   - a static method to register itself in the factory.
	 *
     * Typical usages of Reconstructors are as follows:
     * 
     *  - How to get all the Reconstructor names:
     *@code
     *    vector<string> all_reconstructors = Factory<Reconstructor>::get_list();
     @endcode
	 *
     *  - How to use a Reconstructor
     *@code 
     *    Reconstructor* r = Factory<Reconstructor>::get("fourier");
     *    r->setup();
     *    r->insert_slice(slice1, euler1);
     *    insert more
     *    EMData* result = r->finish();
     @endcode
	 *
     *  - How to define a new Reconstructor type \n     
     *    A new XYZReconstructor class must implement the following functions:
     *    (Please replace 'XYZ' with your own class name).
	 @code
     *        void setup();
     *        int insert_slice(EMData * slice, const Transform3D & t);
     *        EMData * finish();
     *        string get_name() const { return "xyz"; }
     *        static Reconstructor *NEW() { return new XYZReconstructor(); }
     *        TypeDict get_param_types() const;
	 @endcode
	*/
	class Reconstructor
	{
	  public:
		virtual ~ Reconstructor()
		{
		}

		/** Initialize the reconstructor.
		 * @return 0 if OK. 1 if error.
		 */
		virtual void setup() = 0;

		/** Insert an image slice to the reconstructor. To insert multiple
		 * image slices, call this function multiple times.
		 *
		 * @param slice Image slice.
		 * @param euler Euler angle of this image slice.
		 * @return 0 if OK. 1 if error.
		 */
		virtual int insert_slice(EMData * slice, const Transform3D & euler) = 0;

		/** Finish reconstruction and return the complete model.
		 * @return The result 3D model.
		 */
		virtual EMData *finish() = 0;

		/** Get the Reconstructor's name. Each Reconstructor is
		 * identified by a unique name.
		 * @return The Reconstructor's name.
		 */
		virtual string get_name() const = 0;

		
		virtual string get_desc() const = 0;

		/** Get the Reconstructor's parameters in a key/value dictionary.
		 * @return A key/value pair dictionary containing the parameters.
		 */
		virtual Dict get_params() const
		{
			return params;
		}

		/** Set the Reconstructor's parameters using a key/value dictionary.
		 * @param new_params A dictionary containing the new parameters.
		 */
		virtual void set_params(const Dict & new_params)
		{
			params = new_params;
		}

		/** Get reconstructor parameter information in a dictionary. 
		 * Each parameter has one record in the dictionary. Each 
		 * record contains its name, data-type, and description.
		 *
		 * @return A dictionary containing the parameter info.
		 */	 
		virtual TypeDict get_param_types() const = 0;

	  protected:
		mutable Dict params;
		//tmp_data is the substitute of misused parent in reconstruction
		//the memory will be allocated in setup() and released in finish()
		EMData*		tmp_data;
	};

	/** Fourier space 3D reconstruction
     */
	class FourierReconstructor:public Reconstructor
	{
	  public:
		FourierReconstructor();
		~FourierReconstructor();

		void setup();
		int insert_slice(EMData * slice, const Transform3D & euler);
		EMData *finish();

		string get_name() const
		{
			return "fourier";
		}
		
		string get_desc() const
		{
			return "Reconstruction via direct Fourier methods using a Gaussian kernel";
		}

		static Reconstructor *NEW()
		{
			return new FourierReconstructor();
		}

		TypeDict get_param_types() const
		{
			TypeDict d;
			d.put("size", EMObject::INT);
			d.put("mode", EMObject::INT);
			d.put("weight", EMObject::FLOAT);
			d.put("dlog", EMObject::INT);
			return d;
		}

	  private:
		EMData * image;
		int nx;
		int ny;
		int nz;
	};

	/** Fourier space 3D reconstruction with slices already Wiener filter processed.
     */
	class WienerFourierReconstructor:public Reconstructor
	{
	  public:
		WienerFourierReconstructor();
		~WienerFourierReconstructor();

		void setup();
		int insert_slice(EMData * slice, const Transform3D & euler);
		EMData *finish();

		string get_name() const
		{
			return "wiener_fourier";
		}
		
		string get_desc() const
		{
			return "Experimental - Direct Fourier reconstruction taking into account the Wiener filtration of the individual images.";
		}

		static Reconstructor *NEW()
		{
			return new WienerFourierReconstructor();
		}

		TypeDict get_param_types() const
		{
			TypeDict d;
			d.put("size", EMObject::INT);
			d.put("mode", EMObject::INT);
			d.put("padratio", EMObject::FLOAT);
			d.put("snr", EMObject::FLOATARRAY);
			return d;
		}

	  private:
		EMData * image;
		int nx;
		int ny;
		int nz;
	};

	/** Real space 3D reconstruction using back projection.
     * 
     * Back-projection is a method of 3D reconstruction from 2D
     * projections. It is based on superposing 3D functions
     * ("back-projection bodies") obtained by translating the
     * 2D projections along the directions of projection. 
     */
	class BackProjectionReconstructor:public Reconstructor
	{
	  public:
		BackProjectionReconstructor();
		~BackProjectionReconstructor();

		void setup();
		int insert_slice(EMData * slice, const Transform3D & euler);
		EMData *finish();

		string get_name() const
		{
			return "back_projection";
		}
		
		string get_desc() const
		{
			return "Simple (unfiltered) back-projection reconstruction";
		}

		static Reconstructor *NEW()
		{
			return new BackProjectionReconstructor();
		}

		TypeDict get_param_types() const
		{
			TypeDict d;
			d.put("size", EMObject::INT);
			d.put("weight", EMObject::FLOAT);
			return d;
		}
	  private:
		EMData * image;
		int nx;
		int ny;
		int nz;
	};


	/** Pawel Back Projection Reconstructor
     * 
     */
	class PawelBackProjectionReconstructor:public Reconstructor
	{
	  public:
		PawelBackProjectionReconstructor();
		~PawelBackProjectionReconstructor();

		void setup();
		int insert_slice(EMData * slice, const Transform3D & euler);
		EMData *finish();

		string get_name() const
		{
			return "pawel_back_projection";
		}
		
		string get_desc() const
		{
			return "Fourier back-projection reconstruction routine";
		}

		static Reconstructor *NEW()
		{
			return new PawelBackProjectionReconstructor();
		}

		TypeDict get_param_types() const
		{
			TypeDict d;
			d.put("size", EMObject::INT);
			d.put("npad", EMObject::INT);
			d.put("symmetry", EMObject::STRING);
			return d;
		}

	  private:
		EMData* v;
		MCArray3D* v3dptr;
		MIArray3D* nrptr;
		int vnx, vny, vnz;
		int npad;
		int vnzp, vnyp, vnxp, vnxc;
		void buildFFTVolume();
		void buildNormVolume();
            string symmetry;
            int nsym;
	};

	/** Reverse Gridding Reconstructor
	 *
	 * @see P. A. Penczek, R. Renka, and H. Schomberg, JOSA _21_, 499 (2004).
     * 
     */
	class ReverseGriddingReconstructor:public Reconstructor
	{
	  public:
		ReverseGriddingReconstructor();
		~ReverseGriddingReconstructor();

		void setup();
		int insert_slice(EMData * slice, const Transform3D & euler);
		EMData *finish();

		string get_name() const
		{
			return "reverse_gridding";
		}
		
		string get_desc() const
		{
			return "Reverse gridding reconstruction routine";
		}

		static Reconstructor *NEW()
		{
			return new ReverseGriddingReconstructor();
		}

		TypeDict get_param_types() const
		{
			TypeDict d;
			d.put("size", EMObject::INT);
			d.put("weight", EMObject::FLOAT);
			return d;
		}

	  private:
		EMData* v;
		MCArray3D* v3dptr;
		MIArray3D* nrptr;
		int vnx, vny, vnz;
		int npad;
		int vnzp, vnyp, vnxp, vnxc;
		void cang(float phi, float theta, float psi, float dm[]);
		void buildFFTVolume();
		void buildNormVolume();
		void divkb3();
	};
	template <> Factory < Reconstructor >::Factory();

	void dump_reconstructors();
}

#endif

/* vim: set ts=4 noet: */
