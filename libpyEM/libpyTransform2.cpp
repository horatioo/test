
// Boost Includes ==============================================================
#include <boost/python.hpp>
#include <boost/cstdint.hpp>

// Includes ====================================================================
#include <emdata.h>
#include <emdata_pickle.h>
#include <quaternion.h>
#include <transform.h>
#include <vec3.h>

// Using =======================================================================
using namespace boost::python;

// Declarations ================================================================
namespace  {

struct EMAN_Symmetry3D_Wrapper : public EMAN::Symmetry3D
{
    EMAN_Symmetry3D_Wrapper(PyObject* py_self_):
			EMAN::Symmetry3D(), py_self(py_self_) {}
	
	float get_h(const float& prop, const float& altitude) const {
		return call_method< float >(py_self, "get_h", prop, altitude);
	}
	
	int get_nsym() const {
		return call_method< int >(py_self, "get_nsym");
	}
	
	EMAN::Transform3D get_sym(const int n) const {
		return call_method< EMAN::Transform3D >(py_self, "get_sym", n);
	}
	
	EMAN::Dict get_delimiters() const {
		return call_method< EMAN::Dict >(py_self, "get_delimiters");
	}
	
	std::string get_name() const {
		return call_method< std::string >(py_self, "get_name");
	}
	std::string get_desc() const {
		return call_method< std::string >(py_self, "get_desc");
	}
	
	EMAN::TypeDict get_param_types() const {
		return call_method< EMAN::TypeDict >(py_self, "get_param_types");
	}

	PyObject* py_self;
};

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(EMAN_Transform3D_get_rotation_overloads_0_1, get_rotation, 0, 1)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(EMAN_Transform3D_get_pretrans_overloads_0_1, get_pretrans, 0, 1)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(EMAN_Transform3D_get_posttrans_overloads_0_1, get_posttrans, 0, 1)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(EMAN_Transform3D_set_pretrans_overloads_2_3, set_pretrans, 2, 3)

BOOST_PYTHON_MEMBER_FUNCTION_OVERLOADS(EMAN_Transform3D_set_posttrans_overloads_2_3, set_posttrans, 2, 3)
		
}// namespace 


// Module ======================================================================
BOOST_PYTHON_MODULE(libpyTransform2)
{
	def("dump_symmetries", &EMAN::dump_symmetries);
	def("dump_symmetries_list", &EMAN::dump_symmetries_list);
	class_< EMAN::Symmetry3D, boost::noncopyable, EMAN_Symmetry3D_Wrapper >("__Symmetry3D", init<  >())
		.def("get_delimiters", pure_virtual(&EMAN::Symmetry3D::get_delimiters))
		.def("get_sym", pure_virtual(&EMAN::Symmetry3D::get_sym))
		.def("is_in_asym_unit", pure_virtual(&EMAN::Symmetry3D::is_in_asym_unit))
		.def("get_h", pure_virtual(&EMAN::Symmetry3D::get_h))
		.def("get_nsym",pure_virtual(&EMAN::Symmetry3D::get_nsym))
		.def("get_name",pure_virtual(&EMAN::Symmetry3D::get_name))
		.def("is_platonic",pure_virtual(&EMAN::Symmetry3D::is_platonic))
		.def("get_az_alignment_offset", pure_virtual(&EMAN::Symmetry3D::get_az_alignment_offset))
		.def("is_h_sym", &EMAN::Symmetry3D::is_h_sym)
		.def("get_params", &EMAN::Symmetry3D::get_params)
		.def("gen_orientations", &EMAN::Symmetry3D::gen_orientations)
		;

	class_< EMAN::Factory<EMAN::Symmetry3D>, boost::noncopyable >("Symmetries", no_init)
		.def("get", (EMAN::Symmetry3D* (*)(const std::basic_string<char,std::char_traits<char>,std::allocator<char> >&))&EMAN::Factory<EMAN::Symmetry3D>::get, return_value_policy< manage_new_object >())
		.def("get", (EMAN::Symmetry3D* (*)(const std::basic_string<char,std::char_traits<char>,std::allocator<char> >&, const EMAN::Dict&))&EMAN::Factory<EMAN::Symmetry3D>::get, return_value_policy< manage_new_object >())
		.def("get_list", &EMAN::Factory<EMAN::Symmetry3D>::get_list)
		.staticmethod("get_list")
		.staticmethod("get")
		;
	
    class_< EMAN::Vec3f >("Vec3f", init<  >())
    	.def_pickle(Vec3f_pickle_suite())
        .def(init< float, float, optional< float > >())
        .def(init< const std::vector<float,std::allocator<float> >& >())
        .def(init< const EMAN::Vec3i& >())
        .def(init< const EMAN::Vec3f& >())
        .def("normalize", &EMAN::Vec3f::normalize)
        .def("length", &EMAN::Vec3f::length)
        .def("dot", &EMAN::Vec3f::dot)
        .def("cross", &EMAN::Vec3f::cross)
        .def("as_list", &EMAN::Vec3f::as_list)
        .def("set_value", (void (EMAN::Vec3f::*)(const std::vector<float,std::allocator<float> >&) )&EMAN::Vec3f::set_value)
        .def("set_value_at", &EMAN::Vec3f::set_value_at)
        .def("set_value", (void (EMAN::Vec3f::*)(float, float, float) )&EMAN::Vec3f::set_value)
        .def("at", &EMAN::Vec3f::at)
        .def("__getitem__",&EMAN::Vec3f::at)
        .def("__setitem__",&EMAN::Vec3f::set_value_at)
        .def( self + other< EMAN::Vec3i >() )
        .def( other< EMAN::Vec3i >() - self )
        .def( self - other< EMAN::Vec3i >() )
        .def( -self )
        .def( self * other< EMAN::Vec3i >() )
        .def( other< EMAN::Vec3i >() * self )
        .def( other< float >() + self )
        .def( self + other< float >() )
        .def( other< float >() - self )
        .def( self - other< float >() )
        .def( self * other< float >() )
        .def( other< float >() * self )
        .def( self != self )
        .def( self == self )
        .def( self / other< float >() )
        .def( self - self )
        .def( self + self )
        .def( other< EMAN::Vec3i >() + self )
        .def( self * self )
        .def( self += self )
        .def( self += other< EMAN::Vec3i >() )
        .def( self += other< float >() )
        .def( self -= self )
        .def( self -= other< EMAN::Vec3i >() )
        .def( self -= other< float >() )
        .def( self *= other< float >() )
        .def( self /= other< float >() )
    ;

    class_< EMAN::Vec3i >("Vec3i", init<  >())
        .def(init< int, int, optional< int > >())
        .def(init< const std::vector<int,std::allocator<int> >& >())
        .def(init< const EMAN::Vec3i& >())
        .def("normalize", &EMAN::Vec3i::normalize)
        .def("length", &EMAN::Vec3i::length)
        .def("dot", &EMAN::Vec3i::dot)
        .def("cross", &EMAN::Vec3i::cross)
        .def("as_list", &EMAN::Vec3i::as_list)
        .def("set_value", (void (EMAN::Vec3i::*)(const std::vector<int,std::allocator<int> >&) )&EMAN::Vec3i::set_value)
        .def("set_value_at", &EMAN::Vec3i::set_value_at)
        .def("set_value", (void (EMAN::Vec3i::*)(int, int, int) )&EMAN::Vec3i::set_value)
        .def( other< EMAN::Vec3f >() + self )
        .def( self - other< EMAN::Vec3f >() )
        .def( other< EMAN::Vec3f >() - self )
        .def( other< EMAN::Vec3f >() * self )
        .def( self * other< EMAN::Vec3f >() )
        .def( self + other< int >() )
        .def( other< int >() + self )
        .def( self + self )
        .def( other< int >() - self )
        .def( self * self )
        .def( self - self )
        .def( self - other< int >() )
        .def( self * other< int >() )
        .def( other< int >() * self )
        .def( self == self )
        .def( self / other< int >() )
        .def( self != self )
        .def( self + other< EMAN::Vec3f >() )
        .def( self += self )
        .def( self += other< int >() )
        .def( self -= self )
        .def( self -= other< int >() )
        .def( self *= other< int >() )
        .def( self /= other< int >() )
    ;

    class_< EMAN::Quaternion >("Quaternion", init<  >())
        .def(init< const EMAN::Quaternion& >())
        .def(init< float, float, float, float >())
        .def(init< float, const EMAN::Vec3f& >())
        .def(init< const EMAN::Vec3f&, float >())
        .def(init< const std::vector<float,std::allocator<float> >& >())
        .def("norm", &EMAN::Quaternion::norm)
        .def("conj", &EMAN::Quaternion::conj)
        .def("abs", &EMAN::Quaternion::abs)
        .def("normalize", &EMAN::Quaternion::normalize)
        .def("inverse", &EMAN::Quaternion::inverse, return_internal_reference< 1 >())
        .def("create_inverse", &EMAN::Quaternion::create_inverse)
        .def("rotate", &EMAN::Quaternion::rotate)
        .def("to_angle", &EMAN::Quaternion::to_angle)
        .def("to_axis", &EMAN::Quaternion::to_axis)
        .def("to_matrix3", &EMAN::Quaternion::to_matrix3)
        .def("real", &EMAN::Quaternion::real)
        .def("unreal", &EMAN::Quaternion::unreal)
        .def("as_list", &EMAN::Quaternion::as_list)
        .def("interpolate", &EMAN::Quaternion::interpolate)
        .staticmethod("interpolate")
        .def( self + self )
        .def( self - self )
        .def( self * self )
        .def( other< float >() * self )
        .def( self * other< float >() )
        .def( self != self )
        .def( self == self )
        .def( self / self )
        .def( self += self )
        .def( self -= self )
        .def( self *= self )
        .def( self *= other< float >() )
        .def( self /= self )
        .def( self /= other< float >() )
    ;

    scope* EMAN_Transform3D_scope = new scope(
    class_< EMAN::Transform3D >("Transform3D", init<  >())
        .def(init< const EMAN::Transform3D& >())
        .def(init< float, float, float >())
        .def(init< float, float, float, const EMAN::Vec3f& >())
        .def(init< EMAN::Transform3D::EulerType, float, float, float >())
        .def(init< EMAN::Transform3D::EulerType, const EMAN::Dict& >())
        .def(init< const EMAN::Vec3f&, float, float, float, const EMAN::Vec3f& >())
        .def(init< float, float, float, float, float, float, float, float, float >())
        .def_readonly("ERR_LIMIT", &EMAN::Transform3D::ERR_LIMIT)
        .def("set_posttrans", (void (EMAN::Transform3D::*)(float, float, float) )&EMAN::Transform3D::set_posttrans,EMAN_Transform3D_set_posttrans_overloads_2_3())
        .def("set_posttrans", (void (EMAN::Transform3D::*)(const EMAN::Vec3f&) )&EMAN::Transform3D::set_posttrans)
        .def("apply_scale", &EMAN::Transform3D::apply_scale)
        .def("set_scale", &EMAN::Transform3D::set_scale)
        .def("orthogonalize", &EMAN::Transform3D::orthogonalize)
        .def("transpose", &EMAN::Transform3D::transpose)
        .def("set_rotation", (void (EMAN::Transform3D::*)(float, float, float) )&EMAN::Transform3D::set_rotation)
        .def("set_rotation", (void (EMAN::Transform3D::*)(EMAN::Transform3D::EulerType, float, float, float) )&EMAN::Transform3D::set_rotation)
        .def("set_rotation", (void (EMAN::Transform3D::*)(float, float, float, float, float, float, float, float, float) )&EMAN::Transform3D::set_rotation)
        .def("set_rotation", (void (EMAN::Transform3D::*)(EMAN::Transform3D::EulerType, const EMAN::Dict&) )&EMAN::Transform3D::set_rotation)
        .def("set_rotation", (void (EMAN::Transform3D::*)(const EMAN::Vec3f&, const EMAN::Vec3f&, const EMAN::Vec3f&, const EMAN::Vec3f&) )&EMAN::Transform3D::set_rotation)
        .def("get_mag", &EMAN::Transform3D::get_mag)
        .def("get_finger", &EMAN::Transform3D::get_finger)
        .def("get_pretrans", &EMAN::Transform3D::get_pretrans, EMAN_Transform3D_get_pretrans_overloads_0_1())
        .def("get_posttrans", &EMAN::Transform3D::get_posttrans, EMAN_Transform3D_get_posttrans_overloads_0_1())
        .def("get_center", &EMAN::Transform3D::get_center)
        .def("get_matrix3_col", &EMAN::Transform3D::get_matrix3_col)
        .def("get_matrix3_row", &EMAN::Transform3D::get_matrix3_row)
        .def("transform", &EMAN::Transform3D::transform)
        .def("rotate", &EMAN::Transform3D::rotate)
        .def("inverse", &EMAN::Transform3D::inverse)
        .def("get_rotation", &EMAN::Transform3D::get_rotation, EMAN_Transform3D_get_rotation_overloads_0_1())
        .def("printme", &EMAN::Transform3D::printme)
        .def("at", &EMAN::Transform3D::at)
        .def("get_nsym", &EMAN::Transform3D::get_nsym)
        .def("get_sym", &EMAN::Transform3D::get_sym)
        .def("set_center", &EMAN::Transform3D::set_center)
        .def("set_pretrans", (void (EMAN::Transform3D::*)(float,float,float))&EMAN::Transform3D::set_pretrans, EMAN_Transform3D_set_pretrans_overloads_2_3())
        .def("set_pretrans", (void (EMAN::Transform3D::*)(const EMAN::Vec3f&))&EMAN::Transform3D::set_pretrans)
        .def("get_scale", &EMAN::Transform3D::get_scale)
        .def("to_identity", &EMAN::Transform3D::to_identity)
        .def("is_identity", &EMAN::Transform3D::is_identity)
        .def("angles2tfvec", &EMAN::Transform3D::angles2tfvec)
        .staticmethod("angles2tfvec")
        .staticmethod("get_nsym")
        .def( other< EMAN::Vec3f >() * self )
        .def( self * self )
        .def( self * other< EMAN::Vec3f >() )
// 		.def( self + self )
// 		.def( self - self )
    );

    enum_< EMAN::Transform3D::EulerType >("EulerType")
        .value("MATRIX", EMAN::Transform3D::MATRIX)
        .value("UNKNOWN", EMAN::Transform3D::UNKNOWN)
        .value("XYZ", EMAN::Transform3D::XYZ)
        .value("IMAGIC", EMAN::Transform3D::IMAGIC)
        .value("SPIDER", EMAN::Transform3D::SPIDER)
        .value("QUATERNION", EMAN::Transform3D::QUATERNION)
        .value("SGIROT", EMAN::Transform3D::SGIROT)
        .value("MRC", EMAN::Transform3D::MRC)
        .value("SPIN", EMAN::Transform3D::SPIN)
        .value("EMAN", EMAN::Transform3D::EMAN)
    ;
	
	delete EMAN_Transform3D_scope;
}

