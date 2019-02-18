/* -*- c++ -*-*/
/*
#-  (c) Copyright 2011-2018 Xilinx, Inc. All rights reserved.
#-
#-  This file contains confidential and proprietary information
#-  of Xilinx, Inc. and is protected under U.S. and
#-  international copyright and other intellectual property
#-  laws.
#-
#-  DISCLAIMER
#-  This disclaimer is not a license and does not grant any
#-  rights to the materials distributed herewith. Except as
#-  otherwise provided in a valid license issued to you by
#-  Xilinx, and to the maximum extent permitted by applicable
#-  law: (1) THESE MATERIALS ARE MADE AVAILABLE "AS IS" AND
#-  WITH ALL FAULTS, AND XILINX HEREBY DISCLAIMS ALL WARRANTIES
#-  AND CONDITIONS, EXPRESS, IMPLIED, OR STATUTORY, INCLUDING
#-  BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, NON-
#-  INFRINGEMENT, OR FITNESS FOR ANY PARTICULAR PURPOSE; and
#-  (2) Xilinx shall not be liable (whether in contract or tort,
#-  including negligence, or under any other theory of
#-  liability) for any loss or damage of any kind or nature
#-  related to, arising under or in connection with these
#-  materials, including for any direct, or any indirect,
#-  special, incidental, or consequential loss or damage
#-  (including loss of data, profits, goodwill, or any type of
#-  loss or damage suffered as a result of any action brought
#-  by a third party) even if such damage or loss was
#-  reasonably foreseeable or Xilinx had been advised of the
#-  possibility of the same.
#-
#-  CRITICAL APPLICATIONS
#-  Xilinx products are not designed or intended to be fail-
#-  safe, or for use in any application requiring fail-safe
#-  performance, such as life-support or safety devices or
#-  systems, Class III medical devices, nuclear facilities,
#-  applications related to the deployment of airbags, or any
#-  other applications that could lead to death, personal
#-  injury, or severe property or environmental damage
#-  (individually and collectively, "Critical
#-  Applications"). Customer assumes the sole risk and
#-  liability of any use of Xilinx products in Critical
#-  Applications, subject only to applicable laws and
#-  regulations governing limitations on product liability.
#-
#-  THIS COPYRIGHT NOTICE AND DISCLAIMER MUST BE RETAINED AS
#-  PART OF THIS FILE AT ALL TIMES. 
#- ************************************************************************

 *
 *
 */

#ifndef X_HLS_STREAM_SYN_H
#define X_HLS_STREAM_SYN_H

/*
 * This file contains a C++ model of hls::stream.
 * It defines AutoESL synthesis model.
 */
#ifndef __cplusplus
#error C++ is required to include this header file

#else

#include "etc/autopilot_enum.h"
#include "etc/autopilot_ssdm_op.h"

namespace hls {

#ifndef INLINE
#define INLINE inline __attribute__((always_inline))
#endif

//////////////////////////////////////////////
// Synthesis models for stream
//////////////////////////////////////////////
template<typename __STREAM_T__>
class stream
{
  public:
    /// Constructors
    INLINE stream() { 
    }

    INLINE stream(const char* name) {
    }

  /// Make copy constructor and assignment operator private
  private:  
    INLINE stream(const stream< __STREAM_T__ >& chn):V(chn.V) {
    }

    INLINE stream& operator= (const stream< __STREAM_T__ >& chn) {
        V = chn.V;
        return *this;
    }

  public:
    /// Overload >> and << operators to implement read() and write()
    INLINE void operator >> (__STREAM_T__& rdata) {
        read(rdata);
    }

    INLINE void operator << (const __STREAM_T__& wdata) {
        write(wdata);
    }

  /// Public API
  public:
#if ((__clang_major__ == 3) && (__clang_minor__ == 1))
    /// Empty & Full
    INLINE bool empty() const {
        bool tmp = _ssdm_StreamCanRead(&V);
        return !tmp;
    }

    INLINE bool full() const {
        bool tmp = _ssdm_StreamCanWrite(&V);
        return !tmp;
    }
#endif

    /// Blocking read
    INLINE void read(__STREAM_T__& dout) {
#if ((__clang_major__ == 3) && (__clang_minor__ == 1))
        __STREAM_T__ tmp;
        _ssdm_StreamRead(&V, &tmp); 
        dout = tmp;
#else
        read_pipe_block(&V, &dout);
#endif
    }

    INLINE __STREAM_T__ read() {
#if ((__clang_major__ == 3) && (__clang_minor__ == 1))
        __STREAM_T__ tmp;
        _ssdm_StreamRead(&V, &tmp); 
        return tmp;
#else
       __STREAM_T__ tmp;
       read_pipe_block(&V, &tmp);
       return tmp;
#endif
    }

#if ((__clang_major__ == 3) && (__clang_minor__ == 1))
    /// Nonblocking read
    INLINE bool read_nb(__STREAM_T__& dout) {
        __STREAM_T__ tmp;
        bool empty_n = _ssdm_StreamNbRead(&V, &tmp); 
        dout = tmp;
        return empty_n;
    }
#endif

    /// Blocking write
    INLINE void write(const __STREAM_T__& din) {
#if ((__clang_major__ == 3) && (__clang_minor__ == 1))
        __STREAM_T__ tmp = din;
        _ssdm_StreamWrite(&V, &tmp);
#else
        write_pipe_block(&V, &din);
#endif
    }

#if ((__clang_major__ == 3) && (__clang_minor__ == 1))
    /// Nonblocking write
    INLINE bool write_nb(const __STREAM_T__& din) {
        __STREAM_T__ tmp = din;
        bool full_n = _ssdm_StreamNbWrite(&V, &tmp);
        return full_n;
    }

    /// Fifo size
    INLINE unsigned size() {
        unsigned size = _ssdm_StreamSize(&V);
        return size;
    }
#endif
    
  public:  
    __STREAM_T__ V; 
};


} // namespace hls

#endif // __cplusplus
#endif  // X_HLS_STREAM_SYN_H


