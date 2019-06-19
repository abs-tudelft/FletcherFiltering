#pragma once
#include <inttypes.h>
#include <fletcher/api.h>
#define VAR_LENGTH ${VAR_LENGTH}

//Add valid bit at the end, because data packing in vivado flips the order, and in hardware it needs to be the most significant bit.
//template <typename T>
//struct nullable_tb {
//    friend bool operator<(nullable<T> &lhs, nullable<T> &rhs) {
//        if (lhs.valid && rhs.valid) {
//            if (lhs.value < rhs.value)
//                return true;
//            if (rhs.value < lhs.value)
//                return false;
//        }
//        return false;
//    }
//    nullable<T>& operator=(const T val) {
//        value = val;
//        return *this;
//    }
//    friend bool operator>(nullable<T> &lhs, nullable<T> &rhs) {
//        return rhs < lhs;
//    }
//    friend bool operator<=(nullable<T> &lhs, nullable<T> &rhs) {
//        return !(rhs < lhs);
//    }
//    friend bool operator>=(nullable<T> &lhs, nullable<T> &rhs) {
//        return !(lhs < rhs);
//    }
//    friend nullable<T> operator+(nullable<T> &lhs, nullable<T> &rhs) {
//        return nullable<T>(lhs.value + rhs.value, lhs.valid && rhs.valid);
//    }
//    friend nullable<T> operator+(nullable<T> &rhs) {
//        return nullable<T>(+rhs.value, rhs.valid);
//    }
//    friend nullable<T> operator-(nullable<T> &lhs, nullable<T> &rhs) {
//        return nullable<T>(lhs.value - rhs.value, lhs.valid && rhs.valid);
//    }
//    friend nullable<T> operator-(nullable<T> &rhs) {
//        return nullable<T>(-rhs.value, rhs.valid);
//    }
//    friend nullable<T> operator*(nullable<T> &lhs, nullable<T> &rhs) {
//        return nullable<T>(lhs.value * rhs.value, lhs.valid && rhs.valid);
//    }
//    friend nullable<T> operator/(nullable<T> &lhs, nullable<T> &rhs) {
//        return nullable<T>(lhs.value / rhs.value, lhs.valid && rhs.valid);
//    }
//    friend bool operator==(nullable<T> &lhs, nullable<T> &rhs) {
//        return lhs.value == rhs.value &&
//               lhs.valid == rhs.valid;
//    }
//    friend bool operator!=(nullable<T> &lhs, nullable<T> &rhs) {
//        return !(rhs == lhs);
//    }
//
//    nullable_tb<T>(T _value, bool _valid){
//        value = _value;
//        valid = _valid;
//    }
//
//    explicit nullable_tb<T>(T _value){
//        value = _value;
//        valid = true;
//    }
//
//    nullable_tb<T>(){
//		value = T();
//		valid = true;
//	}
//
//    T data;
//    bool valid;
//};

bool __sql_builtin_like(char* data, int len, const char* pattern_name);

void __sql_builtin_concat(f_uint8* buffer, int* offset, const f_uint8* value, int length);

void __sql_builtin_concat(f_uint8* buffer, int* offset, const f_uint8* value, int length, bool valid);

void __sql_builtin_concat(f_uint8* buffer, int* offset, const char* value, int length, bool valid);

void __sql_builtin_concat(f_uint8* buffer, int* offset, const char* value, int length);
