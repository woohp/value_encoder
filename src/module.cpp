#include <algorithm>
#include <array>
#include <iomanip>
#include <iostream>
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <sstream>
#include <string_view>
using namespace std;
namespace py = pybind11;

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)


struct ValueEncoder
{
    ValueEncoder& fit(string_view value)
    {
        std::fill(mapping.begin(), mapping.end(), -1);
        std::fill(inverse_mapping.begin(), inverse_mapping.end(), -1);

        array<uint8_t, 256> present;
        present.fill(0);

        for (uint8_t c : value)
            present[c] = 1;

        for (size_t i = 0, j = 0; i < present.size(); i++)
        {
            if (present[i] == 0)
                continue;
            this->classes_.push_back(i);
            mapping[i] = j;
            inverse_mapping[j] = i;
            j++;
        }

        return *this;
    }

    ValueEncoder& fit(py::iterable values)
    {
        std::fill(mapping.begin(), mapping.end(), -1);
        std::fill(inverse_mapping.begin(), inverse_mapping.end(), -1);

        array<uint8_t, 256> present;
        present.fill(0);

        for (py::handle obj : values)
        {
            string_view value;
            try
            {
                value = obj.cast<string_view>();
            }
            catch (const std::runtime_error&)
            {
                throw std::invalid_argument("Invalid type, expected str or bytes");
            }
            for (uint8_t c : value)
                present[c] = 1;
        }

        for (size_t i = 0, j = 0; i < present.size(); i++)
        {
            if (present[i] == 0)
                continue;
            this->classes_.push_back(i);
            mapping[i] = j;
            inverse_mapping[j] = i;
            j++;
        }

        return *this;
    }

    py::array_t<int16_t> transform(string_view characters, bool cap)
    {
        py::array_t<int16_t> result(characters.size() + cap);
        int16_t* result_ptr = reinterpret_cast<int16_t*>(result.request().ptr);

        for (size_t i = 0; i < characters.size(); i++)
        {
            auto mapped_character = mapping[static_cast<uint8_t>(characters[i])];
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

    py::array_t<int16_t> transform(const vector<string_view>& values, int padding_value, bool cap)
    {
        int max_length = 0;
        for (const auto& value : values)
            max_length = std::max<int>(max_length, value.length());
        py::array_t<int16_t> result({ static_cast<int>(values.size()), max_length + cap });
        std::fill_n(reinterpret_cast<int16_t*>(result.request().ptr), result.size(), padding_value);
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

    string inverse_transform(py::array_t<int16_t, py::array::c_style | py::array::forcecast> value)
    {
        py::buffer_info info = value.request();
        int16_t* ptr = reinterpret_cast<int16_t*>(info.ptr);

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

    vector<uint8_t> classes_;
    array<int16_t, 256> mapping;
    array<int16_t, 256> inverse_mapping;
};


PYBIND11_MODULE(value_encoder, m)
{
    using namespace pybind11::literals;

    py::class_<ValueEncoder>(m, "ValueEncoder")
        .def(py::init<>())
        .def_readonly("classes_", &ValueEncoder::classes_)
        .def("fit", py::overload_cast<string_view>(&ValueEncoder::fit), "value"_a)
        .def("fit", py::overload_cast<py::iterable>(&ValueEncoder::fit), "values"_a)
        .def("transform", py::overload_cast<string_view, bool>(&ValueEncoder::transform), "value"_a, "cap"_a = false)
        .def(
            "transform",
            py::overload_cast<const vector<string_view>&, int, bool>(&ValueEncoder::transform),
            "values"_a,
            "padding_value"_a = -1,
            "cap"_a = false)
        .def("inverse_transform", &ValueEncoder::inverse_transform, "value"_a);

#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#endif
}
