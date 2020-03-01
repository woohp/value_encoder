#include <algorithm>
#include <array>
#include <iomanip>
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <sstream>
#include <string_view>
using namespace std;
namespace py = pybind11;


struct ValueEncoder
{
    ValueEncoder& fit(string_view characters)
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

    py::array_t<char> transform(string_view characters, bool cap)
    {
        py::array_t<char> result(characters.size() + cap);
        char* result_ptr = reinterpret_cast<char*>(result.request().ptr);

        for (size_t i = 0; i < characters.size(); i++)
        {
            auto mapped_character = mapping[characters[i]];
            if (mapped_character < 0)
            {
                stringstream ss;
                ss << "invalid character: " << quoted(string { characters });
                throw std::invalid_argument(ss.str());
            }
            result_ptr[i] = mapped_character;
        }

        if (cap)
            result_ptr[characters.size()] = this->classes_.size();

        return result;
    }

    py::array_t<char> transform(const vector<string_view>& values, int missing_value, bool cap)
    {
        int max_length = 0;
        for (const auto& value : values)
            max_length = std::max<int>(max_length, value.length());
        py::array_t<char> result({ static_cast<int>(values.size()), max_length + cap });
        std::fill_n(reinterpret_cast<char*>(result.request().ptr), result.nbytes(), missing_value);
        auto result_a = result.mutable_unchecked<2>();

        for (size_t batch_idx = 0; batch_idx < values.size(); batch_idx++)
        {
            const auto& value = values[batch_idx];
            for (size_t i = 0; i < value.size(); i++)
            {
                auto mapped_character = mapping[value[i]];
                if (mapped_character < 0)
                {
                    stringstream ss;
                    ss << "invalid character: " << quoted(string { value });
                    throw std::invalid_argument(ss.str());
                }
                result_a(batch_idx, i) = mapped_character;
            }

            if (cap)
                result_a(batch_idx, value.size()) = this->classes_.size();
        }

        return result;
    }

    string inverse_transform(py::array_t<char, py::array::c_style | py::array::forcecast> value)
    {
        py::buffer_info info = value.request();
        char* ptr = reinterpret_cast<char*>(info.ptr);

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
        .def("transform", py::overload_cast<string_view, bool>(&ValueEncoder::transform), "value"_a, "cap"_a = false)
        .def(
            "transform",
            py::overload_cast<const vector<string_view>&, int, bool>(&ValueEncoder::transform),
            "values"_a,
            "missing_value"_a = -1,
            "cap"_a = false)
        .def("inverse_transform", &ValueEncoder::inverse_transform, "value"_a);

#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#endif
}
