#include <algorithm>
#include <array>
#include <iomanip>
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <sstream>
using namespace std;
namespace py = pybind11;


struct ValueEncoder
{
    ValueEncoder& fit(const string& characters)
    {
        std::fill(mapping.begin(), mapping.end(), -1);
        std::fill(inverse_mapping.begin(), inverse_mapping.end(), -1);
        classes_ = characters;
        sort(classes_.begin(), classes_.end());
        classes_.erase(unique(classes_.begin(), classes_.end()), classes_.end());

        for (size_t i = 0; i < classes_.size(); i++)
        {
            mapping[classes_[i]] = i;
            inverse_mapping[i] = classes_[i];
        }

        return *this;
    }

    py::array_t<unsigned char> transform(const string& characters, bool cap)
    {
        py::array_t<unsigned char> result(characters.size() + cap);
        unsigned char* result_ptr = reinterpret_cast<unsigned char*>(result.request().ptr);

        for (size_t i = 0; i < characters.size(); i++)
        {
            auto mapped_character = mapping[characters[i]];
            if (mapped_character < 0)
            {
                stringstream ss;
                ss << "invalid character: " << quoted(characters);
                throw std::invalid_argument(ss.str());
            }
            result_ptr[i] = mapped_character;
        }

        if (cap)
            result_ptr[characters.size()] = this->classes_.size();

        return result;
    }

    py::array_t<unsigned char> fit_transform(const string& characters, bool cap)
    {
        fit(characters);
        return transform(characters, cap);
    }

    string inverse_transform(py::array_t<unsigned char, py::array::c_style | py::array::forcecast> value)
    {
        py::buffer_info info = value.request();
        unsigned char* ptr = reinterpret_cast<unsigned char*>(info.ptr);

        string out;
        out.reserve(info.shape[0]);
        for (int i = 0; i < info.shape[0]; i++)
        {
            auto mapped_character = inverse_mapping[ptr[i]];
            if (mapped_character < 0)
                throw std::invalid_argument("invalid character: " + to_string(ptr[i]));
            out.push_back(mapped_character);
        }

        return out;
    }

    string classes_;
    array<char, 128> mapping;
    array<char, 128> inverse_mapping;
};


PYBIND11_MODULE(value_encoder, m)
{
    using namespace pybind11::literals;

    py::class_<ValueEncoder>(m, "ValueEncoder")
        .def(py::init<>())
        .def_readonly("classes_", &ValueEncoder::classes_)
        .def("fit", &ValueEncoder::fit, "characters"_a)
        .def("transform", &ValueEncoder::transform, "characters"_a, "cap"_a = false)
        .def("fit_transform", &ValueEncoder::fit_transform, "characters"_a, "cap"_a = false)
        .def("inverse_transform", &ValueEncoder::inverse_transform, "value"_a);

#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#endif
}
