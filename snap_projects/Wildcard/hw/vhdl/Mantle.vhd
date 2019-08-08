library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
library work;
use work.Interconnect_pkg.all;
entity Mantle is
  generic (
    BUS_ADDR_WIDTH : integer := 64
  );
  port (
    bcd_clk            : in  std_logic;
    bcd_reset          : in  std_logic;
    kcd_clk            : in  std_logic;
    kcd_reset          : in  std_logic;
    mmio_awvalid       : in  std_logic;
    mmio_awready       : out std_logic;
    mmio_awaddr        : in  std_logic_vector(31 downto 0);
    mmio_wvalid        : in  std_logic;
    mmio_wready        : out std_logic;
    mmio_wdata         : in  std_logic_vector(31 downto 0);
    mmio_wstrb         : in  std_logic_vector(3 downto 0);
    mmio_bvalid        : out std_logic;
    mmio_bready        : in  std_logic;
    mmio_bresp         : out std_logic_vector(1 downto 0);
    mmio_arvalid       : in  std_logic;
    mmio_arready       : out std_logic;
    mmio_araddr        : in  std_logic_vector(31 downto 0);
    mmio_rvalid        : out std_logic;
    mmio_rready        : in  std_logic;
    mmio_rdata         : out std_logic_vector(31 downto 0);
    mmio_rresp         : out std_logic_vector(1 downto 0);
    rd_mst_rreq_valid  : out std_logic;
    rd_mst_rreq_ready  : in  std_logic;
    rd_mst_rreq_addr   : out std_logic_vector(63 downto 0);
    rd_mst_rreq_len    : out std_logic_vector(7 downto 0);
    rd_mst_rdat_valid  : in  std_logic;
    rd_mst_rdat_ready  : out std_logic;
    rd_mst_rdat_data   : in  std_logic_vector(511 downto 0);
    rd_mst_rdat_last   : in  std_logic;
    wr_mst_wreq_valid  : out std_logic;
    wr_mst_wreq_ready  : in  std_logic;
    wr_mst_wreq_addr   : out std_logic_vector(63 downto 0);
    wr_mst_wreq_len    : out std_logic_vector(7 downto 0);
    wr_mst_wdat_valid  : out std_logic;
    wr_mst_wdat_ready  : in  std_logic;
    wr_mst_wdat_data   : out std_logic_vector(511 downto 0);
    wr_mst_wdat_strobe : out std_logic_vector(63 downto 0);
    wr_mst_wdat_last   : out std_logic
  );
end entity;
architecture Implementation of Mantle is
  component ff_in is
    generic (
      BUS_ADDR_WIDTH : integer := 64
    );
    port (
      bcd_clk                      : in  std_logic;
      bcd_reset                    : in  std_logic;
      kcd_clk                      : in  std_logic;
      kcd_reset                    : in  std_logic;
      ff_in_pkid_valid             : out std_logic;
      ff_in_pkid_ready             : in  std_logic;
      ff_in_pkid_dvalid            : out std_logic;
      ff_in_pkid_last              : out std_logic;
      ff_in_pkid                   : out std_logic_vector(31 downto 0);
      ff_in_pkid_cmd_valid         : in  std_logic;
      ff_in_pkid_cmd_ready         : out std_logic;
      ff_in_pkid_cmd_firstIdx      : in  std_logic_vector(31 downto 0);
      ff_in_pkid_cmd_lastidx       : in  std_logic_vector(31 downto 0);
      ff_in_pkid_cmd_ctrl          : in  std_logic_vector(bus_addr_width-1 downto 0);
      ff_in_pkid_cmd_tag           : in  std_logic_vector(0 downto 0);
      ff_in_pkid_unl_valid         : out std_logic;
      ff_in_pkid_unl_ready         : in  std_logic;
      ff_in_pkid_unl_tag           : out std_logic_vector(0 downto 0);
      ff_in_pkid_bus_rreq_valid    : out std_logic;
      ff_in_pkid_bus_rreq_ready    : in  std_logic;
      ff_in_pkid_bus_rreq_addr     : out std_logic_vector(63 downto 0);
      ff_in_pkid_bus_rreq_len      : out std_logic_vector(7 downto 0);
      ff_in_pkid_bus_rdat_valid    : in  std_logic;
      ff_in_pkid_bus_rdat_ready    : out std_logic;
      ff_in_pkid_bus_rdat_data     : in  std_logic_vector(511 downto 0);
      ff_in_pkid_bus_rdat_last     : in  std_logic;
      ff_in_string1_valid          : out std_logic;
      ff_in_string1_ready          : in  std_logic;
      ff_in_string1_dvalid         : out std_logic;
      ff_in_string1_last           : out std_logic;
      ff_in_string1_length         : out std_logic_vector(31 downto 0);
      ff_in_string1_count          : out std_logic_vector(0 downto 0);
      ff_in_string1_chars_valid    : out std_logic;
      ff_in_string1_chars_ready    : in  std_logic;
      ff_in_string1_chars_dvalid   : out std_logic;
      ff_in_string1_chars_last     : out std_logic;
      ff_in_string1_chars_data     : out std_logic_vector(7 downto 0);
      ff_in_string1_chars_count    : out std_logic_vector(0 downto 0);
      ff_in_string1_cmd_valid      : in  std_logic;
      ff_in_string1_cmd_ready      : out std_logic;
      ff_in_string1_cmd_firstIdx   : in  std_logic_vector(31 downto 0);
      ff_in_string1_cmd_lastidx    : in  std_logic_vector(31 downto 0);
      ff_in_string1_cmd_ctrl       : in  std_logic_vector(2*bus_addr_width-1 downto 0);
      ff_in_string1_cmd_tag        : in  std_logic_vector(0 downto 0);
      ff_in_string1_unl_valid      : out std_logic;
      ff_in_string1_unl_ready      : in  std_logic;
      ff_in_string1_unl_tag        : out std_logic_vector(0 downto 0);
      ff_in_string1_bus_rreq_valid : out std_logic;
      ff_in_string1_bus_rreq_ready : in  std_logic;
      ff_in_string1_bus_rreq_addr  : out std_logic_vector(63 downto 0);
      ff_in_string1_bus_rreq_len   : out std_logic_vector(7 downto 0);
      ff_in_string1_bus_rdat_valid : in  std_logic;
      ff_in_string1_bus_rdat_ready : out std_logic;
      ff_in_string1_bus_rdat_data  : in  std_logic_vector(511 downto 0);
      ff_in_string1_bus_rdat_last  : in  std_logic;
      ff_in_string2_valid          : out std_logic;
      ff_in_string2_ready          : in  std_logic;
      ff_in_string2_dvalid         : out std_logic;
      ff_in_string2_last           : out std_logic;
      ff_in_string2_length         : out std_logic_vector(31 downto 0);
      ff_in_string2_count          : out std_logic_vector(0 downto 0);
      ff_in_string2_chars_valid    : out std_logic;
      ff_in_string2_chars_ready    : in  std_logic;
      ff_in_string2_chars_dvalid   : out std_logic;
      ff_in_string2_chars_last     : out std_logic;
      ff_in_string2_chars_data     : out std_logic_vector(7 downto 0);
      ff_in_string2_chars_count    : out std_logic_vector(0 downto 0);
      ff_in_string2_cmd_valid      : in  std_logic;
      ff_in_string2_cmd_ready      : out std_logic;
      ff_in_string2_cmd_firstIdx   : in  std_logic_vector(31 downto 0);
      ff_in_string2_cmd_lastidx    : in  std_logic_vector(31 downto 0);
      ff_in_string2_cmd_ctrl       : in  std_logic_vector(2*bus_addr_width-1 downto 0);
      ff_in_string2_cmd_tag        : in  std_logic_vector(0 downto 0);
      ff_in_string2_unl_valid      : out std_logic;
      ff_in_string2_unl_ready      : in  std_logic;
      ff_in_string2_unl_tag        : out std_logic_vector(0 downto 0);
      ff_in_string2_bus_rreq_valid : out std_logic;
      ff_in_string2_bus_rreq_ready : in  std_logic;
      ff_in_string2_bus_rreq_addr  : out std_logic_vector(63 downto 0);
      ff_in_string2_bus_rreq_len   : out std_logic_vector(7 downto 0);
      ff_in_string2_bus_rdat_valid : in  std_logic;
      ff_in_string2_bus_rdat_ready : out std_logic;
      ff_in_string2_bus_rdat_data  : in  std_logic_vector(511 downto 0);
      ff_in_string2_bus_rdat_last  : in  std_logic
    );
  end component;
  component ff_out is
    generic (
      BUS_ADDR_WIDTH : integer := 64
    );
    port (
      bcd_clk                        : in  std_logic;
      bcd_reset                      : in  std_logic;
      kcd_clk                        : in  std_logic;
      kcd_reset                      : in  std_logic;
      ff_out_pkid_valid              : in  std_logic;
      ff_out_pkid_ready              : out std_logic;
      ff_out_pkid_dvalid             : in  std_logic;
      ff_out_pkid_last               : in  std_logic;
      ff_out_pkid                    : in  std_logic_vector(31 downto 0);
      ff_out_pkid_cmd_valid          : in  std_logic;
      ff_out_pkid_cmd_ready          : out std_logic;
      ff_out_pkid_cmd_firstIdx       : in  std_logic_vector(31 downto 0);
      ff_out_pkid_cmd_lastidx        : in  std_logic_vector(31 downto 0);
      ff_out_pkid_cmd_ctrl           : in  std_logic_vector(bus_addr_width-1 downto 0);
      ff_out_pkid_cmd_tag            : in  std_logic_vector(0 downto 0);
      ff_out_pkid_unl_valid          : out std_logic;
      ff_out_pkid_unl_ready          : in  std_logic;
      ff_out_pkid_unl_tag            : out std_logic_vector(0 downto 0);
      ff_out_pkid_bus_wreq_valid     : out std_logic;
      ff_out_pkid_bus_wreq_ready     : in  std_logic;
      ff_out_pkid_bus_wreq_addr      : out std_logic_vector(63 downto 0);
      ff_out_pkid_bus_wreq_len       : out std_logic_vector(7 downto 0);
      ff_out_pkid_bus_wdat_valid     : out std_logic;
      ff_out_pkid_bus_wdat_ready     : in  std_logic;
      ff_out_pkid_bus_wdat_data      : out std_logic_vector(511 downto 0);
      ff_out_pkid_bus_wdat_strobe    : out std_logic_vector(63 downto 0);
      ff_out_pkid_bus_wdat_last      : out std_logic;
      ff_out_string1_valid           : in  std_logic;
      ff_out_string1_ready           : out std_logic;
      ff_out_string1_dvalid          : in  std_logic;
      ff_out_string1_last            : in  std_logic;
      ff_out_string1_length          : in  std_logic_vector(31 downto 0);
      ff_out_string1_count           : in  std_logic_vector(0 downto 0);
      ff_out_string1_chars_valid     : in  std_logic;
      ff_out_string1_chars_ready     : out std_logic;
      ff_out_string1_chars_dvalid    : in  std_logic;
      ff_out_string1_chars_last      : in  std_logic;
      ff_out_string1_chars_data      : in  std_logic_vector(7 downto 0);
      ff_out_string1_chars_count     : in  std_logic_vector(0 downto 0);
      ff_out_string1_cmd_valid       : in  std_logic;
      ff_out_string1_cmd_ready       : out std_logic;
      ff_out_string1_cmd_firstIdx    : in  std_logic_vector(31 downto 0);
      ff_out_string1_cmd_lastidx     : in  std_logic_vector(31 downto 0);
      ff_out_string1_cmd_ctrl        : in  std_logic_vector(2*bus_addr_width-1 downto 0);
      ff_out_string1_cmd_tag         : in  std_logic_vector(0 downto 0);
      ff_out_string1_unl_valid       : out std_logic;
      ff_out_string1_unl_ready       : in  std_logic;
      ff_out_string1_unl_tag         : out std_logic_vector(0 downto 0);
      ff_out_string1_bus_wreq_valid  : out std_logic;
      ff_out_string1_bus_wreq_ready  : in  std_logic;
      ff_out_string1_bus_wreq_addr   : out std_logic_vector(63 downto 0);
      ff_out_string1_bus_wreq_len    : out std_logic_vector(7 downto 0);
      ff_out_string1_bus_wdat_valid  : out std_logic;
      ff_out_string1_bus_wdat_ready  : in  std_logic;
      ff_out_string1_bus_wdat_data   : out std_logic_vector(511 downto 0);
      ff_out_string1_bus_wdat_strobe : out std_logic_vector(63 downto 0);
      ff_out_string1_bus_wdat_last   : out std_logic;
      ff_out_string2_valid           : in  std_logic;
      ff_out_string2_ready           : out std_logic;
      ff_out_string2_dvalid          : in  std_logic;
      ff_out_string2_last            : in  std_logic;
      ff_out_string2_length          : in  std_logic_vector(31 downto 0);
      ff_out_string2_count           : in  std_logic_vector(0 downto 0);
      ff_out_string2_chars_valid     : in  std_logic;
      ff_out_string2_chars_ready     : out std_logic;
      ff_out_string2_chars_dvalid    : in  std_logic;
      ff_out_string2_chars_last      : in  std_logic;
      ff_out_string2_chars_data      : in  std_logic_vector(7 downto 0);
      ff_out_string2_chars_count     : in  std_logic_vector(0 downto 0);
      ff_out_string2_cmd_valid       : in  std_logic;
      ff_out_string2_cmd_ready       : out std_logic;
      ff_out_string2_cmd_firstIdx    : in  std_logic_vector(31 downto 0);
      ff_out_string2_cmd_lastidx     : in  std_logic_vector(31 downto 0);
      ff_out_string2_cmd_ctrl        : in  std_logic_vector(2*bus_addr_width-1 downto 0);
      ff_out_string2_cmd_tag         : in  std_logic_vector(0 downto 0);
      ff_out_string2_unl_valid       : out std_logic;
      ff_out_string2_unl_ready       : in  std_logic;
      ff_out_string2_unl_tag         : out std_logic_vector(0 downto 0);
      ff_out_string2_bus_wreq_valid  : out std_logic;
      ff_out_string2_bus_wreq_ready  : in  std_logic;
      ff_out_string2_bus_wreq_addr   : out std_logic_vector(63 downto 0);
      ff_out_string2_bus_wreq_len    : out std_logic_vector(7 downto 0);
      ff_out_string2_bus_wdat_valid  : out std_logic;
      ff_out_string2_bus_wdat_ready  : in  std_logic;
      ff_out_string2_bus_wdat_data   : out std_logic_vector(511 downto 0);
      ff_out_string2_bus_wdat_strobe : out std_logic_vector(63 downto 0);
      ff_out_string2_bus_wdat_last   : out std_logic
    );
  end component;
  component FletcherWildcard is
    generic (
      BUS_ADDR_WIDTH : integer := 64
    );
    port (
      kcd_clk                     : in  std_logic;
      kcd_reset                   : in  std_logic;
      mmio_awvalid                : in  std_logic;
      mmio_awready                : out std_logic;
      mmio_awaddr                 : in  std_logic_vector(31 downto 0);
      mmio_wvalid                 : in  std_logic;
      mmio_wready                 : out std_logic;
      mmio_wdata                  : in  std_logic_vector(31 downto 0);
      mmio_wstrb                  : in  std_logic_vector(3 downto 0);
      mmio_bvalid                 : out std_logic;
      mmio_bready                 : in  std_logic;
      mmio_bresp                  : out std_logic_vector(1 downto 0);
      mmio_arvalid                : in  std_logic;
      mmio_arready                : out std_logic;
      mmio_araddr                 : in  std_logic_vector(31 downto 0);
      mmio_rvalid                 : out std_logic;
      mmio_rready                 : in  std_logic;
      mmio_rdata                  : out std_logic_vector(31 downto 0);
      mmio_rresp                  : out std_logic_vector(1 downto 0);
      ff_in_pkid_valid            : in  std_logic;
      ff_in_pkid_ready            : out std_logic;
      ff_in_pkid_dvalid           : in  std_logic;
      ff_in_pkid_last             : in  std_logic;
      ff_in_pkid                  : in  std_logic_vector(31 downto 0);
      ff_in_pkid_cmd_valid        : out std_logic;
      ff_in_pkid_cmd_ready        : in  std_logic;
      ff_in_pkid_cmd_firstIdx     : out std_logic_vector(31 downto 0);
      ff_in_pkid_cmd_lastidx      : out std_logic_vector(31 downto 0);
      ff_in_pkid_cmd_ctrl         : out std_logic_vector(bus_addr_width-1 downto 0);
      ff_in_pkid_cmd_tag          : out std_logic_vector(0 downto 0);
      ff_in_pkid_unl_valid        : in  std_logic;
      ff_in_pkid_unl_ready        : out std_logic;
      ff_in_pkid_unl_tag          : in  std_logic_vector(0 downto 0);
      ff_in_string1_valid         : in  std_logic;
      ff_in_string1_ready         : out std_logic;
      ff_in_string1_dvalid        : in  std_logic;
      ff_in_string1_last          : in  std_logic;
      ff_in_string1_length        : in  std_logic_vector(31 downto 0);
      ff_in_string1_count         : in  std_logic_vector(0 downto 0);
      ff_in_string1_chars_valid   : in  std_logic;
      ff_in_string1_chars_ready   : out std_logic;
      ff_in_string1_chars_dvalid  : in  std_logic;
      ff_in_string1_chars_last    : in  std_logic;
      ff_in_string1_chars_data    : in  std_logic_vector(7 downto 0);
      ff_in_string1_chars_count   : in  std_logic_vector(0 downto 0);
      ff_in_string1_cmd_valid     : out std_logic;
      ff_in_string1_cmd_ready     : in  std_logic;
      ff_in_string1_cmd_firstIdx  : out std_logic_vector(31 downto 0);
      ff_in_string1_cmd_lastidx   : out std_logic_vector(31 downto 0);
      ff_in_string1_cmd_ctrl      : out std_logic_vector(2*bus_addr_width-1 downto 0);
      ff_in_string1_cmd_tag       : out std_logic_vector(0 downto 0);
      ff_in_string1_unl_valid     : in  std_logic;
      ff_in_string1_unl_ready     : out std_logic;
      ff_in_string1_unl_tag       : in  std_logic_vector(0 downto 0);
      ff_in_string2_valid         : in  std_logic;
      ff_in_string2_ready         : out std_logic;
      ff_in_string2_dvalid        : in  std_logic;
      ff_in_string2_last          : in  std_logic;
      ff_in_string2_length        : in  std_logic_vector(31 downto 0);
      ff_in_string2_count         : in  std_logic_vector(0 downto 0);
      ff_in_string2_chars_valid   : in  std_logic;
      ff_in_string2_chars_ready   : out std_logic;
      ff_in_string2_chars_dvalid  : in  std_logic;
      ff_in_string2_chars_last    : in  std_logic;
      ff_in_string2_chars_data    : in  std_logic_vector(7 downto 0);
      ff_in_string2_chars_count   : in  std_logic_vector(0 downto 0);
      ff_in_string2_cmd_valid     : out std_logic;
      ff_in_string2_cmd_ready     : in  std_logic;
      ff_in_string2_cmd_firstIdx  : out std_logic_vector(31 downto 0);
      ff_in_string2_cmd_lastidx   : out std_logic_vector(31 downto 0);
      ff_in_string2_cmd_ctrl      : out std_logic_vector(2*bus_addr_width-1 downto 0);
      ff_in_string2_cmd_tag       : out std_logic_vector(0 downto 0);
      ff_in_string2_unl_valid     : in  std_logic;
      ff_in_string2_unl_ready     : out std_logic;
      ff_in_string2_unl_tag       : in  std_logic_vector(0 downto 0);
      ff_out_pkid_valid           : out std_logic;
      ff_out_pkid_ready           : in  std_logic;
      ff_out_pkid_dvalid          : out std_logic;
      ff_out_pkid_last            : out std_logic;
      ff_out_pkid                 : out std_logic_vector(31 downto 0);
      ff_out_pkid_cmd_valid       : out std_logic;
      ff_out_pkid_cmd_ready       : in  std_logic;
      ff_out_pkid_cmd_firstIdx    : out std_logic_vector(31 downto 0);
      ff_out_pkid_cmd_lastidx     : out std_logic_vector(31 downto 0);
      ff_out_pkid_cmd_ctrl        : out std_logic_vector(bus_addr_width-1 downto 0);
      ff_out_pkid_cmd_tag         : out std_logic_vector(0 downto 0);
      ff_out_pkid_unl_valid       : in  std_logic;
      ff_out_pkid_unl_ready       : out std_logic;
      ff_out_pkid_unl_tag         : in  std_logic_vector(0 downto 0);
      ff_out_string1_valid        : out std_logic;
      ff_out_string1_ready        : in  std_logic;
      ff_out_string1_dvalid       : out std_logic;
      ff_out_string1_last         : out std_logic;
      ff_out_string1_length       : out std_logic_vector(31 downto 0);
      ff_out_string1_count        : out std_logic_vector(0 downto 0);
      ff_out_string1_chars_valid  : out std_logic;
      ff_out_string1_chars_ready  : in  std_logic;
      ff_out_string1_chars_dvalid : out std_logic;
      ff_out_string1_chars_last   : out std_logic;
      ff_out_string1_chars_data   : out std_logic_vector(7 downto 0);
      ff_out_string1_chars_count  : out std_logic_vector(0 downto 0);
      ff_out_string1_cmd_valid    : out std_logic;
      ff_out_string1_cmd_ready    : in  std_logic;
      ff_out_string1_cmd_firstIdx : out std_logic_vector(31 downto 0);
      ff_out_string1_cmd_lastidx  : out std_logic_vector(31 downto 0);
      ff_out_string1_cmd_ctrl     : out std_logic_vector(2*bus_addr_width-1 downto 0);
      ff_out_string1_cmd_tag      : out std_logic_vector(0 downto 0);
      ff_out_string1_unl_valid    : in  std_logic;
      ff_out_string1_unl_ready    : out std_logic;
      ff_out_string1_unl_tag      : in  std_logic_vector(0 downto 0);
      ff_out_string2_valid        : out std_logic;
      ff_out_string2_ready        : in  std_logic;
      ff_out_string2_dvalid       : out std_logic;
      ff_out_string2_last         : out std_logic;
      ff_out_string2_length       : out std_logic_vector(31 downto 0);
      ff_out_string2_count        : out std_logic_vector(0 downto 0);
      ff_out_string2_chars_valid  : out std_logic;
      ff_out_string2_chars_ready  : in  std_logic;
      ff_out_string2_chars_dvalid : out std_logic;
      ff_out_string2_chars_last   : out std_logic;
      ff_out_string2_chars_data   : out std_logic_vector(7 downto 0);
      ff_out_string2_chars_count  : out std_logic_vector(0 downto 0);
      ff_out_string2_cmd_valid    : out std_logic;
      ff_out_string2_cmd_ready    : in  std_logic;
      ff_out_string2_cmd_firstIdx : out std_logic_vector(31 downto 0);
      ff_out_string2_cmd_lastidx  : out std_logic_vector(31 downto 0);
      ff_out_string2_cmd_ctrl     : out std_logic_vector(2*bus_addr_width-1 downto 0);
      ff_out_string2_cmd_tag      : out std_logic_vector(0 downto 0);
      ff_out_string2_unl_valid    : in  std_logic;
      ff_out_string2_unl_ready    : out std_logic;
      ff_out_string2_unl_tag      : in  std_logic_vector(0 downto 0)
    );
  end component;
  signal ff_in_inst_ff_in_pkid_valid  : std_logic;
  signal ff_in_inst_ff_in_pkid_ready  : std_logic;
  signal ff_in_inst_ff_in_pkid_dvalid : std_logic;
  signal ff_in_inst_ff_in_pkid_last   : std_logic;
  signal ff_in_inst_ff_in_pkid        : std_logic_vector(31 downto 0);
  signal ff_in_inst_ff_in_pkid_unl_valid : std_logic;
  signal ff_in_inst_ff_in_pkid_unl_ready : std_logic;
  signal ff_in_inst_ff_in_pkid_unl_tag   : std_logic_vector(0 downto 0);
  signal ff_in_inst_ff_in_pkid_bus_rreq_valid : std_logic;
  signal ff_in_inst_ff_in_pkid_bus_rreq_ready : std_logic;
  signal ff_in_inst_ff_in_pkid_bus_rreq_addr  : std_logic_vector(63 downto 0);
  signal ff_in_inst_ff_in_pkid_bus_rreq_len   : std_logic_vector(7 downto 0);
  signal ff_in_inst_ff_in_pkid_bus_rdat_valid : std_logic;
  signal ff_in_inst_ff_in_pkid_bus_rdat_ready : std_logic;
  signal ff_in_inst_ff_in_pkid_bus_rdat_data  : std_logic_vector(511 downto 0);
  signal ff_in_inst_ff_in_pkid_bus_rdat_last  : std_logic;
  signal ff_in_inst_ff_in_string1_valid        : std_logic;
  signal ff_in_inst_ff_in_string1_ready        : std_logic;
  signal ff_in_inst_ff_in_string1_dvalid       : std_logic;
  signal ff_in_inst_ff_in_string1_last         : std_logic;
  signal ff_in_inst_ff_in_string1_length       : std_logic_vector(31 downto 0);
  signal ff_in_inst_ff_in_string1_count        : std_logic_vector(0 downto 0);
  signal ff_in_inst_ff_in_string1_chars_valid  : std_logic;
  signal ff_in_inst_ff_in_string1_chars_ready  : std_logic;
  signal ff_in_inst_ff_in_string1_chars_dvalid : std_logic;
  signal ff_in_inst_ff_in_string1_chars_last   : std_logic;
  signal ff_in_inst_ff_in_string1_chars_data   : std_logic_vector(7 downto 0);
  signal ff_in_inst_ff_in_string1_chars_count  : std_logic_vector(0 downto 0);
  signal ff_in_inst_ff_in_string1_unl_valid : std_logic;
  signal ff_in_inst_ff_in_string1_unl_ready : std_logic;
  signal ff_in_inst_ff_in_string1_unl_tag   : std_logic_vector(0 downto 0);
  signal ff_in_inst_ff_in_string1_bus_rreq_valid : std_logic;
  signal ff_in_inst_ff_in_string1_bus_rreq_ready : std_logic;
  signal ff_in_inst_ff_in_string1_bus_rreq_addr  : std_logic_vector(63 downto 0);
  signal ff_in_inst_ff_in_string1_bus_rreq_len   : std_logic_vector(7 downto 0);
  signal ff_in_inst_ff_in_string1_bus_rdat_valid : std_logic;
  signal ff_in_inst_ff_in_string1_bus_rdat_ready : std_logic;
  signal ff_in_inst_ff_in_string1_bus_rdat_data  : std_logic_vector(511 downto 0);
  signal ff_in_inst_ff_in_string1_bus_rdat_last  : std_logic;
  signal ff_in_inst_ff_in_string2_valid        : std_logic;
  signal ff_in_inst_ff_in_string2_ready        : std_logic;
  signal ff_in_inst_ff_in_string2_dvalid       : std_logic;
  signal ff_in_inst_ff_in_string2_last         : std_logic;
  signal ff_in_inst_ff_in_string2_length       : std_logic_vector(31 downto 0);
  signal ff_in_inst_ff_in_string2_count        : std_logic_vector(0 downto 0);
  signal ff_in_inst_ff_in_string2_chars_valid  : std_logic;
  signal ff_in_inst_ff_in_string2_chars_ready  : std_logic;
  signal ff_in_inst_ff_in_string2_chars_dvalid : std_logic;
  signal ff_in_inst_ff_in_string2_chars_last   : std_logic;
  signal ff_in_inst_ff_in_string2_chars_data   : std_logic_vector(7 downto 0);
  signal ff_in_inst_ff_in_string2_chars_count  : std_logic_vector(0 downto 0);
  signal ff_in_inst_ff_in_string2_unl_valid : std_logic;
  signal ff_in_inst_ff_in_string2_unl_ready : std_logic;
  signal ff_in_inst_ff_in_string2_unl_tag   : std_logic_vector(0 downto 0);
  signal ff_in_inst_ff_in_string2_bus_rreq_valid : std_logic;
  signal ff_in_inst_ff_in_string2_bus_rreq_ready : std_logic;
  signal ff_in_inst_ff_in_string2_bus_rreq_addr  : std_logic_vector(63 downto 0);
  signal ff_in_inst_ff_in_string2_bus_rreq_len   : std_logic_vector(7 downto 0);
  signal ff_in_inst_ff_in_string2_bus_rdat_valid : std_logic;
  signal ff_in_inst_ff_in_string2_bus_rdat_ready : std_logic;
  signal ff_in_inst_ff_in_string2_bus_rdat_data  : std_logic_vector(511 downto 0);
  signal ff_in_inst_ff_in_string2_bus_rdat_last  : std_logic;
  signal ff_out_inst_ff_out_pkid_unl_valid : std_logic;
  signal ff_out_inst_ff_out_pkid_unl_ready : std_logic;
  signal ff_out_inst_ff_out_pkid_unl_tag   : std_logic_vector(0 downto 0);
  signal ff_out_inst_ff_out_pkid_bus_wreq_valid  : std_logic;
  signal ff_out_inst_ff_out_pkid_bus_wreq_ready  : std_logic;
  signal ff_out_inst_ff_out_pkid_bus_wreq_addr   : std_logic_vector(63 downto 0);
  signal ff_out_inst_ff_out_pkid_bus_wreq_len    : std_logic_vector(7 downto 0);
  signal ff_out_inst_ff_out_pkid_bus_wdat_valid  : std_logic;
  signal ff_out_inst_ff_out_pkid_bus_wdat_ready  : std_logic;
  signal ff_out_inst_ff_out_pkid_bus_wdat_data   : std_logic_vector(511 downto 0);
  signal ff_out_inst_ff_out_pkid_bus_wdat_strobe : std_logic_vector(63 downto 0);
  signal ff_out_inst_ff_out_pkid_bus_wdat_last   : std_logic;
  signal ff_out_inst_ff_out_string1_unl_valid : std_logic;
  signal ff_out_inst_ff_out_string1_unl_ready : std_logic;
  signal ff_out_inst_ff_out_string1_unl_tag   : std_logic_vector(0 downto 0);
  signal ff_out_inst_ff_out_string1_bus_wreq_valid  : std_logic;
  signal ff_out_inst_ff_out_string1_bus_wreq_ready  : std_logic;
  signal ff_out_inst_ff_out_string1_bus_wreq_addr   : std_logic_vector(63 downto 0);
  signal ff_out_inst_ff_out_string1_bus_wreq_len    : std_logic_vector(7 downto 0);
  signal ff_out_inst_ff_out_string1_bus_wdat_valid  : std_logic;
  signal ff_out_inst_ff_out_string1_bus_wdat_ready  : std_logic;
  signal ff_out_inst_ff_out_string1_bus_wdat_data   : std_logic_vector(511 downto 0);
  signal ff_out_inst_ff_out_string1_bus_wdat_strobe : std_logic_vector(63 downto 0);
  signal ff_out_inst_ff_out_string1_bus_wdat_last   : std_logic;
  signal ff_out_inst_ff_out_string2_unl_valid : std_logic;
  signal ff_out_inst_ff_out_string2_unl_ready : std_logic;
  signal ff_out_inst_ff_out_string2_unl_tag   : std_logic_vector(0 downto 0);
  signal ff_out_inst_ff_out_string2_bus_wreq_valid  : std_logic;
  signal ff_out_inst_ff_out_string2_bus_wreq_ready  : std_logic;
  signal ff_out_inst_ff_out_string2_bus_wreq_addr   : std_logic_vector(63 downto 0);
  signal ff_out_inst_ff_out_string2_bus_wreq_len    : std_logic_vector(7 downto 0);
  signal ff_out_inst_ff_out_string2_bus_wdat_valid  : std_logic;
  signal ff_out_inst_ff_out_string2_bus_wdat_ready  : std_logic;
  signal ff_out_inst_ff_out_string2_bus_wdat_data   : std_logic_vector(511 downto 0);
  signal ff_out_inst_ff_out_string2_bus_wdat_strobe : std_logic_vector(63 downto 0);
  signal ff_out_inst_ff_out_string2_bus_wdat_last   : std_logic;
  signal FletcherWildcard_inst_ff_in_pkid_cmd_valid    : std_logic;
  signal FletcherWildcard_inst_ff_in_pkid_cmd_ready    : std_logic;
  signal FletcherWildcard_inst_ff_in_pkid_cmd_firstIdx : std_logic_vector(31 downto 0);
  signal FletcherWildcard_inst_ff_in_pkid_cmd_lastidx  : std_logic_vector(31 downto 0);
  signal FletcherWildcard_inst_ff_in_pkid_cmd_ctrl     : std_logic_vector(bus_addr_width-1 downto 0);
  signal FletcherWildcard_inst_ff_in_pkid_cmd_tag      : std_logic_vector(0 downto 0);
  signal FletcherWildcard_inst_ff_in_string1_cmd_valid    : std_logic;
  signal FletcherWildcard_inst_ff_in_string1_cmd_ready    : std_logic;
  signal FletcherWildcard_inst_ff_in_string1_cmd_firstIdx : std_logic_vector(31 downto 0);
  signal FletcherWildcard_inst_ff_in_string1_cmd_lastidx  : std_logic_vector(31 downto 0);
  signal FletcherWildcard_inst_ff_in_string1_cmd_ctrl     : std_logic_vector(2*bus_addr_width-1 downto 0);
  signal FletcherWildcard_inst_ff_in_string1_cmd_tag      : std_logic_vector(0 downto 0);
  signal FletcherWildcard_inst_ff_in_string2_cmd_valid    : std_logic;
  signal FletcherWildcard_inst_ff_in_string2_cmd_ready    : std_logic;
  signal FletcherWildcard_inst_ff_in_string2_cmd_firstIdx : std_logic_vector(31 downto 0);
  signal FletcherWildcard_inst_ff_in_string2_cmd_lastidx  : std_logic_vector(31 downto 0);
  signal FletcherWildcard_inst_ff_in_string2_cmd_ctrl     : std_logic_vector(2*bus_addr_width-1 downto 0);
  signal FletcherWildcard_inst_ff_in_string2_cmd_tag      : std_logic_vector(0 downto 0);
  signal FletcherWildcard_inst_ff_out_pkid_valid  : std_logic;
  signal FletcherWildcard_inst_ff_out_pkid_ready  : std_logic;
  signal FletcherWildcard_inst_ff_out_pkid_dvalid : std_logic;
  signal FletcherWildcard_inst_ff_out_pkid_last   : std_logic;
  signal FletcherWildcard_inst_ff_out_pkid        : std_logic_vector(31 downto 0);
  signal FletcherWildcard_inst_ff_out_pkid_cmd_valid    : std_logic;
  signal FletcherWildcard_inst_ff_out_pkid_cmd_ready    : std_logic;
  signal FletcherWildcard_inst_ff_out_pkid_cmd_firstIdx : std_logic_vector(31 downto 0);
  signal FletcherWildcard_inst_ff_out_pkid_cmd_lastidx  : std_logic_vector(31 downto 0);
  signal FletcherWildcard_inst_ff_out_pkid_cmd_ctrl     : std_logic_vector(bus_addr_width-1 downto 0);
  signal FletcherWildcard_inst_ff_out_pkid_cmd_tag      : std_logic_vector(0 downto 0);
  signal FletcherWildcard_inst_ff_out_string1_valid        : std_logic;
  signal FletcherWildcard_inst_ff_out_string1_ready        : std_logic;
  signal FletcherWildcard_inst_ff_out_string1_dvalid       : std_logic;
  signal FletcherWildcard_inst_ff_out_string1_last         : std_logic;
  signal FletcherWildcard_inst_ff_out_string1_length       : std_logic_vector(31 downto 0);
  signal FletcherWildcard_inst_ff_out_string1_count        : std_logic_vector(0 downto 0);
  signal FletcherWildcard_inst_ff_out_string1_chars_valid  : std_logic;
  signal FletcherWildcard_inst_ff_out_string1_chars_ready  : std_logic;
  signal FletcherWildcard_inst_ff_out_string1_chars_dvalid : std_logic;
  signal FletcherWildcard_inst_ff_out_string1_chars_last   : std_logic;
  signal FletcherWildcard_inst_ff_out_string1_chars_data   : std_logic_vector(7 downto 0);
  signal FletcherWildcard_inst_ff_out_string1_chars_count  : std_logic_vector(0 downto 0);
  signal FletcherWildcard_inst_ff_out_string1_cmd_valid    : std_logic;
  signal FletcherWildcard_inst_ff_out_string1_cmd_ready    : std_logic;
  signal FletcherWildcard_inst_ff_out_string1_cmd_firstIdx : std_logic_vector(31 downto 0);
  signal FletcherWildcard_inst_ff_out_string1_cmd_lastidx  : std_logic_vector(31 downto 0);
  signal FletcherWildcard_inst_ff_out_string1_cmd_ctrl     : std_logic_vector(2*bus_addr_width-1 downto 0);
  signal FletcherWildcard_inst_ff_out_string1_cmd_tag      : std_logic_vector(0 downto 0);
  signal FletcherWildcard_inst_ff_out_string2_valid        : std_logic;
  signal FletcherWildcard_inst_ff_out_string2_ready        : std_logic;
  signal FletcherWildcard_inst_ff_out_string2_dvalid       : std_logic;
  signal FletcherWildcard_inst_ff_out_string2_last         : std_logic;
  signal FletcherWildcard_inst_ff_out_string2_length       : std_logic_vector(31 downto 0);
  signal FletcherWildcard_inst_ff_out_string2_count        : std_logic_vector(0 downto 0);
  signal FletcherWildcard_inst_ff_out_string2_chars_valid  : std_logic;
  signal FletcherWildcard_inst_ff_out_string2_chars_ready  : std_logic;
  signal FletcherWildcard_inst_ff_out_string2_chars_dvalid : std_logic;
  signal FletcherWildcard_inst_ff_out_string2_chars_last   : std_logic;
  signal FletcherWildcard_inst_ff_out_string2_chars_data   : std_logic_vector(7 downto 0);
  signal FletcherWildcard_inst_ff_out_string2_chars_count  : std_logic_vector(0 downto 0);
  signal FletcherWildcard_inst_ff_out_string2_cmd_valid    : std_logic;
  signal FletcherWildcard_inst_ff_out_string2_cmd_ready    : std_logic;
  signal FletcherWildcard_inst_ff_out_string2_cmd_firstIdx : std_logic_vector(31 downto 0);
  signal FletcherWildcard_inst_ff_out_string2_cmd_lastidx  : std_logic_vector(31 downto 0);
  signal FletcherWildcard_inst_ff_out_string2_cmd_ctrl     : std_logic_vector(2*bus_addr_width-1 downto 0);
  signal FletcherWildcard_inst_ff_out_string2_cmd_tag      : std_logic_vector(0 downto 0);
begin
  ff_in_inst : ff_in
    generic map (
      BUS_ADDR_WIDTH => 64
    )
    port map (
      bcd_clk                      => bcd_clk,
      bcd_reset                    => bcd_reset,
      kcd_clk                      => kcd_clk,
      kcd_reset                    => kcd_reset,
      ff_in_pkid_valid             => ff_in_inst_ff_in_pkid_valid,
      ff_in_pkid_ready             => ff_in_inst_ff_in_pkid_ready,
      ff_in_pkid_dvalid            => ff_in_inst_ff_in_pkid_dvalid,
      ff_in_pkid_last              => ff_in_inst_ff_in_pkid_last,
      ff_in_pkid                   => ff_in_inst_ff_in_pkid,
      ff_in_pkid_cmd_valid         => FletcherWildcard_inst_ff_in_pkid_cmd_valid,
      ff_in_pkid_cmd_ready         => FletcherWildcard_inst_ff_in_pkid_cmd_ready,
      ff_in_pkid_cmd_firstIdx      => FletcherWildcard_inst_ff_in_pkid_cmd_firstIdx,
      ff_in_pkid_cmd_lastidx       => FletcherWildcard_inst_ff_in_pkid_cmd_lastidx,
      ff_in_pkid_cmd_ctrl          => FletcherWildcard_inst_ff_in_pkid_cmd_ctrl,
      ff_in_pkid_cmd_tag           => FletcherWildcard_inst_ff_in_pkid_cmd_tag,
      ff_in_pkid_unl_valid         => ff_in_inst_ff_in_pkid_unl_valid,
      ff_in_pkid_unl_ready         => ff_in_inst_ff_in_pkid_unl_ready,
      ff_in_pkid_unl_tag           => ff_in_inst_ff_in_pkid_unl_tag,
      ff_in_pkid_bus_rreq_valid    => ff_in_inst_ff_in_pkid_bus_rreq_valid,
      ff_in_pkid_bus_rreq_ready    => ff_in_inst_ff_in_pkid_bus_rreq_ready,
      ff_in_pkid_bus_rreq_addr     => ff_in_inst_ff_in_pkid_bus_rreq_addr,
      ff_in_pkid_bus_rreq_len      => ff_in_inst_ff_in_pkid_bus_rreq_len,
      ff_in_pkid_bus_rdat_valid    => ff_in_inst_ff_in_pkid_bus_rdat_valid,
      ff_in_pkid_bus_rdat_ready    => ff_in_inst_ff_in_pkid_bus_rdat_ready,
      ff_in_pkid_bus_rdat_data     => ff_in_inst_ff_in_pkid_bus_rdat_data,
      ff_in_pkid_bus_rdat_last     => ff_in_inst_ff_in_pkid_bus_rdat_last,
      ff_in_string1_valid          => ff_in_inst_ff_in_string1_valid,
      ff_in_string1_ready          => ff_in_inst_ff_in_string1_ready,
      ff_in_string1_dvalid         => ff_in_inst_ff_in_string1_dvalid,
      ff_in_string1_last           => ff_in_inst_ff_in_string1_last,
      ff_in_string1_length         => ff_in_inst_ff_in_string1_length,
      ff_in_string1_count          => ff_in_inst_ff_in_string1_count,
      ff_in_string1_chars_valid    => ff_in_inst_ff_in_string1_chars_valid,
      ff_in_string1_chars_ready    => ff_in_inst_ff_in_string1_chars_ready,
      ff_in_string1_chars_dvalid   => ff_in_inst_ff_in_string1_chars_dvalid,
      ff_in_string1_chars_last     => ff_in_inst_ff_in_string1_chars_last,
      ff_in_string1_chars_data     => ff_in_inst_ff_in_string1_chars_data,
      ff_in_string1_chars_count    => ff_in_inst_ff_in_string1_chars_count,
      ff_in_string1_cmd_valid      => FletcherWildcard_inst_ff_in_string1_cmd_valid,
      ff_in_string1_cmd_ready      => FletcherWildcard_inst_ff_in_string1_cmd_ready,
      ff_in_string1_cmd_firstIdx   => FletcherWildcard_inst_ff_in_string1_cmd_firstIdx,
      ff_in_string1_cmd_lastidx    => FletcherWildcard_inst_ff_in_string1_cmd_lastidx,
      ff_in_string1_cmd_ctrl       => FletcherWildcard_inst_ff_in_string1_cmd_ctrl,
      ff_in_string1_cmd_tag        => FletcherWildcard_inst_ff_in_string1_cmd_tag,
      ff_in_string1_unl_valid      => ff_in_inst_ff_in_string1_unl_valid,
      ff_in_string1_unl_ready      => ff_in_inst_ff_in_string1_unl_ready,
      ff_in_string1_unl_tag        => ff_in_inst_ff_in_string1_unl_tag,
      ff_in_string1_bus_rreq_valid => ff_in_inst_ff_in_string1_bus_rreq_valid,
      ff_in_string1_bus_rreq_ready => ff_in_inst_ff_in_string1_bus_rreq_ready,
      ff_in_string1_bus_rreq_addr  => ff_in_inst_ff_in_string1_bus_rreq_addr,
      ff_in_string1_bus_rreq_len   => ff_in_inst_ff_in_string1_bus_rreq_len,
      ff_in_string1_bus_rdat_valid => ff_in_inst_ff_in_string1_bus_rdat_valid,
      ff_in_string1_bus_rdat_ready => ff_in_inst_ff_in_string1_bus_rdat_ready,
      ff_in_string1_bus_rdat_data  => ff_in_inst_ff_in_string1_bus_rdat_data,
      ff_in_string1_bus_rdat_last  => ff_in_inst_ff_in_string1_bus_rdat_last,
      ff_in_string2_valid          => ff_in_inst_ff_in_string2_valid,
      ff_in_string2_ready          => ff_in_inst_ff_in_string2_ready,
      ff_in_string2_dvalid         => ff_in_inst_ff_in_string2_dvalid,
      ff_in_string2_last           => ff_in_inst_ff_in_string2_last,
      ff_in_string2_length         => ff_in_inst_ff_in_string2_length,
      ff_in_string2_count          => ff_in_inst_ff_in_string2_count,
      ff_in_string2_chars_valid    => ff_in_inst_ff_in_string2_chars_valid,
      ff_in_string2_chars_ready    => ff_in_inst_ff_in_string2_chars_ready,
      ff_in_string2_chars_dvalid   => ff_in_inst_ff_in_string2_chars_dvalid,
      ff_in_string2_chars_last     => ff_in_inst_ff_in_string2_chars_last,
      ff_in_string2_chars_data     => ff_in_inst_ff_in_string2_chars_data,
      ff_in_string2_chars_count    => ff_in_inst_ff_in_string2_chars_count,
      ff_in_string2_cmd_valid      => FletcherWildcard_inst_ff_in_string2_cmd_valid,
      ff_in_string2_cmd_ready      => FletcherWildcard_inst_ff_in_string2_cmd_ready,
      ff_in_string2_cmd_firstIdx   => FletcherWildcard_inst_ff_in_string2_cmd_firstIdx,
      ff_in_string2_cmd_lastidx    => FletcherWildcard_inst_ff_in_string2_cmd_lastidx,
      ff_in_string2_cmd_ctrl       => FletcherWildcard_inst_ff_in_string2_cmd_ctrl,
      ff_in_string2_cmd_tag        => FletcherWildcard_inst_ff_in_string2_cmd_tag,
      ff_in_string2_unl_valid      => ff_in_inst_ff_in_string2_unl_valid,
      ff_in_string2_unl_ready      => ff_in_inst_ff_in_string2_unl_ready,
      ff_in_string2_unl_tag        => ff_in_inst_ff_in_string2_unl_tag,
      ff_in_string2_bus_rreq_valid => ff_in_inst_ff_in_string2_bus_rreq_valid,
      ff_in_string2_bus_rreq_ready => ff_in_inst_ff_in_string2_bus_rreq_ready,
      ff_in_string2_bus_rreq_addr  => ff_in_inst_ff_in_string2_bus_rreq_addr,
      ff_in_string2_bus_rreq_len   => ff_in_inst_ff_in_string2_bus_rreq_len,
      ff_in_string2_bus_rdat_valid => ff_in_inst_ff_in_string2_bus_rdat_valid,
      ff_in_string2_bus_rdat_ready => ff_in_inst_ff_in_string2_bus_rdat_ready,
      ff_in_string2_bus_rdat_data  => ff_in_inst_ff_in_string2_bus_rdat_data,
      ff_in_string2_bus_rdat_last  => ff_in_inst_ff_in_string2_bus_rdat_last
    );
  ff_out_inst : ff_out
    generic map (
      BUS_ADDR_WIDTH => 64
    )
    port map (
      bcd_clk                        => bcd_clk,
      bcd_reset                      => bcd_reset,
      kcd_clk                        => kcd_clk,
      kcd_reset                      => kcd_reset,
      ff_out_pkid_valid              => FletcherWildcard_inst_ff_out_pkid_valid,
      ff_out_pkid_ready              => FletcherWildcard_inst_ff_out_pkid_ready,
      ff_out_pkid_dvalid             => FletcherWildcard_inst_ff_out_pkid_dvalid,
      ff_out_pkid_last               => FletcherWildcard_inst_ff_out_pkid_last,
      ff_out_pkid                    => FletcherWildcard_inst_ff_out_pkid,
      ff_out_pkid_cmd_valid          => FletcherWildcard_inst_ff_out_pkid_cmd_valid,
      ff_out_pkid_cmd_ready          => FletcherWildcard_inst_ff_out_pkid_cmd_ready,
      ff_out_pkid_cmd_firstIdx       => FletcherWildcard_inst_ff_out_pkid_cmd_firstIdx,
      ff_out_pkid_cmd_lastidx        => FletcherWildcard_inst_ff_out_pkid_cmd_lastidx,
      ff_out_pkid_cmd_ctrl           => FletcherWildcard_inst_ff_out_pkid_cmd_ctrl,
      ff_out_pkid_cmd_tag            => FletcherWildcard_inst_ff_out_pkid_cmd_tag,
      ff_out_pkid_unl_valid          => ff_out_inst_ff_out_pkid_unl_valid,
      ff_out_pkid_unl_ready          => ff_out_inst_ff_out_pkid_unl_ready,
      ff_out_pkid_unl_tag            => ff_out_inst_ff_out_pkid_unl_tag,
      ff_out_pkid_bus_wreq_valid     => ff_out_inst_ff_out_pkid_bus_wreq_valid,
      ff_out_pkid_bus_wreq_ready     => ff_out_inst_ff_out_pkid_bus_wreq_ready,
      ff_out_pkid_bus_wreq_addr      => ff_out_inst_ff_out_pkid_bus_wreq_addr,
      ff_out_pkid_bus_wreq_len       => ff_out_inst_ff_out_pkid_bus_wreq_len,
      ff_out_pkid_bus_wdat_valid     => ff_out_inst_ff_out_pkid_bus_wdat_valid,
      ff_out_pkid_bus_wdat_ready     => ff_out_inst_ff_out_pkid_bus_wdat_ready,
      ff_out_pkid_bus_wdat_data      => ff_out_inst_ff_out_pkid_bus_wdat_data,
      ff_out_pkid_bus_wdat_strobe    => ff_out_inst_ff_out_pkid_bus_wdat_strobe,
      ff_out_pkid_bus_wdat_last      => ff_out_inst_ff_out_pkid_bus_wdat_last,
      ff_out_string1_valid           => FletcherWildcard_inst_ff_out_string1_valid,
      ff_out_string1_ready           => FletcherWildcard_inst_ff_out_string1_ready,
      ff_out_string1_dvalid          => FletcherWildcard_inst_ff_out_string1_dvalid,
      ff_out_string1_last            => FletcherWildcard_inst_ff_out_string1_last,
      ff_out_string1_length          => FletcherWildcard_inst_ff_out_string1_length,
      ff_out_string1_count           => FletcherWildcard_inst_ff_out_string1_count,
      ff_out_string1_chars_valid     => FletcherWildcard_inst_ff_out_string1_chars_valid,
      ff_out_string1_chars_ready     => FletcherWildcard_inst_ff_out_string1_chars_ready,
      ff_out_string1_chars_dvalid    => FletcherWildcard_inst_ff_out_string1_chars_dvalid,
      ff_out_string1_chars_last      => FletcherWildcard_inst_ff_out_string1_chars_last,
      ff_out_string1_chars_data      => FletcherWildcard_inst_ff_out_string1_chars_data,
      ff_out_string1_chars_count     => FletcherWildcard_inst_ff_out_string1_chars_count,
      ff_out_string1_cmd_valid       => FletcherWildcard_inst_ff_out_string1_cmd_valid,
      ff_out_string1_cmd_ready       => FletcherWildcard_inst_ff_out_string1_cmd_ready,
      ff_out_string1_cmd_firstIdx    => FletcherWildcard_inst_ff_out_string1_cmd_firstIdx,
      ff_out_string1_cmd_lastidx     => FletcherWildcard_inst_ff_out_string1_cmd_lastidx,
      ff_out_string1_cmd_ctrl        => FletcherWildcard_inst_ff_out_string1_cmd_ctrl,
      ff_out_string1_cmd_tag         => FletcherWildcard_inst_ff_out_string1_cmd_tag,
      ff_out_string1_unl_valid       => ff_out_inst_ff_out_string1_unl_valid,
      ff_out_string1_unl_ready       => ff_out_inst_ff_out_string1_unl_ready,
      ff_out_string1_unl_tag         => ff_out_inst_ff_out_string1_unl_tag,
      ff_out_string1_bus_wreq_valid  => ff_out_inst_ff_out_string1_bus_wreq_valid,
      ff_out_string1_bus_wreq_ready  => ff_out_inst_ff_out_string1_bus_wreq_ready,
      ff_out_string1_bus_wreq_addr   => ff_out_inst_ff_out_string1_bus_wreq_addr,
      ff_out_string1_bus_wreq_len    => ff_out_inst_ff_out_string1_bus_wreq_len,
      ff_out_string1_bus_wdat_valid  => ff_out_inst_ff_out_string1_bus_wdat_valid,
      ff_out_string1_bus_wdat_ready  => ff_out_inst_ff_out_string1_bus_wdat_ready,
      ff_out_string1_bus_wdat_data   => ff_out_inst_ff_out_string1_bus_wdat_data,
      ff_out_string1_bus_wdat_strobe => ff_out_inst_ff_out_string1_bus_wdat_strobe,
      ff_out_string1_bus_wdat_last   => ff_out_inst_ff_out_string1_bus_wdat_last,
      ff_out_string2_valid           => FletcherWildcard_inst_ff_out_string2_valid,
      ff_out_string2_ready           => FletcherWildcard_inst_ff_out_string2_ready,
      ff_out_string2_dvalid          => FletcherWildcard_inst_ff_out_string2_dvalid,
      ff_out_string2_last            => FletcherWildcard_inst_ff_out_string2_last,
      ff_out_string2_length          => FletcherWildcard_inst_ff_out_string2_length,
      ff_out_string2_count           => FletcherWildcard_inst_ff_out_string2_count,
      ff_out_string2_chars_valid     => FletcherWildcard_inst_ff_out_string2_chars_valid,
      ff_out_string2_chars_ready     => FletcherWildcard_inst_ff_out_string2_chars_ready,
      ff_out_string2_chars_dvalid    => FletcherWildcard_inst_ff_out_string2_chars_dvalid,
      ff_out_string2_chars_last      => FletcherWildcard_inst_ff_out_string2_chars_last,
      ff_out_string2_chars_data      => FletcherWildcard_inst_ff_out_string2_chars_data,
      ff_out_string2_chars_count     => FletcherWildcard_inst_ff_out_string2_chars_count,
      ff_out_string2_cmd_valid       => FletcherWildcard_inst_ff_out_string2_cmd_valid,
      ff_out_string2_cmd_ready       => FletcherWildcard_inst_ff_out_string2_cmd_ready,
      ff_out_string2_cmd_firstIdx    => FletcherWildcard_inst_ff_out_string2_cmd_firstIdx,
      ff_out_string2_cmd_lastidx     => FletcherWildcard_inst_ff_out_string2_cmd_lastidx,
      ff_out_string2_cmd_ctrl        => FletcherWildcard_inst_ff_out_string2_cmd_ctrl,
      ff_out_string2_cmd_tag         => FletcherWildcard_inst_ff_out_string2_cmd_tag,
      ff_out_string2_unl_valid       => ff_out_inst_ff_out_string2_unl_valid,
      ff_out_string2_unl_ready       => ff_out_inst_ff_out_string2_unl_ready,
      ff_out_string2_unl_tag         => ff_out_inst_ff_out_string2_unl_tag,
      ff_out_string2_bus_wreq_valid  => ff_out_inst_ff_out_string2_bus_wreq_valid,
      ff_out_string2_bus_wreq_ready  => ff_out_inst_ff_out_string2_bus_wreq_ready,
      ff_out_string2_bus_wreq_addr   => ff_out_inst_ff_out_string2_bus_wreq_addr,
      ff_out_string2_bus_wreq_len    => ff_out_inst_ff_out_string2_bus_wreq_len,
      ff_out_string2_bus_wdat_valid  => ff_out_inst_ff_out_string2_bus_wdat_valid,
      ff_out_string2_bus_wdat_ready  => ff_out_inst_ff_out_string2_bus_wdat_ready,
      ff_out_string2_bus_wdat_data   => ff_out_inst_ff_out_string2_bus_wdat_data,
      ff_out_string2_bus_wdat_strobe => ff_out_inst_ff_out_string2_bus_wdat_strobe,
      ff_out_string2_bus_wdat_last   => ff_out_inst_ff_out_string2_bus_wdat_last
    );
  FletcherWildcard_inst : FletcherWildcard
    generic map (
      BUS_ADDR_WIDTH => 64
    )
    port map (
      kcd_clk                     => kcd_clk,
      kcd_reset                   => kcd_reset,
      mmio_awvalid                => mmio_awvalid,
      mmio_awready                => mmio_awready,
      mmio_awaddr                 => mmio_awaddr,
      mmio_wvalid                 => mmio_wvalid,
      mmio_wready                 => mmio_wready,
      mmio_wdata                  => mmio_wdata,
      mmio_wstrb                  => mmio_wstrb,
      mmio_bvalid                 => mmio_bvalid,
      mmio_bready                 => mmio_bready,
      mmio_bresp                  => mmio_bresp,
      mmio_arvalid                => mmio_arvalid,
      mmio_arready                => mmio_arready,
      mmio_araddr                 => mmio_araddr,
      mmio_rvalid                 => mmio_rvalid,
      mmio_rready                 => mmio_rready,
      mmio_rdata                  => mmio_rdata,
      mmio_rresp                  => mmio_rresp,
      ff_in_pkid_valid            => ff_in_inst_ff_in_pkid_valid,
      ff_in_pkid_ready            => ff_in_inst_ff_in_pkid_ready,
      ff_in_pkid_dvalid           => ff_in_inst_ff_in_pkid_dvalid,
      ff_in_pkid_last             => ff_in_inst_ff_in_pkid_last,
      ff_in_pkid                  => ff_in_inst_ff_in_pkid,
      ff_in_pkid_cmd_valid        => FletcherWildcard_inst_ff_in_pkid_cmd_valid,
      ff_in_pkid_cmd_ready        => FletcherWildcard_inst_ff_in_pkid_cmd_ready,
      ff_in_pkid_cmd_firstIdx     => FletcherWildcard_inst_ff_in_pkid_cmd_firstIdx,
      ff_in_pkid_cmd_lastidx      => FletcherWildcard_inst_ff_in_pkid_cmd_lastidx,
      ff_in_pkid_cmd_ctrl         => FletcherWildcard_inst_ff_in_pkid_cmd_ctrl,
      ff_in_pkid_cmd_tag          => FletcherWildcard_inst_ff_in_pkid_cmd_tag,
      ff_in_pkid_unl_valid        => ff_in_inst_ff_in_pkid_unl_valid,
      ff_in_pkid_unl_ready        => ff_in_inst_ff_in_pkid_unl_ready,
      ff_in_pkid_unl_tag          => ff_in_inst_ff_in_pkid_unl_tag,
      ff_in_string1_valid         => ff_in_inst_ff_in_string1_valid,
      ff_in_string1_ready         => ff_in_inst_ff_in_string1_ready,
      ff_in_string1_dvalid        => ff_in_inst_ff_in_string1_dvalid,
      ff_in_string1_last          => ff_in_inst_ff_in_string1_last,
      ff_in_string1_length        => ff_in_inst_ff_in_string1_length,
      ff_in_string1_count         => ff_in_inst_ff_in_string1_count,
      ff_in_string1_chars_valid   => ff_in_inst_ff_in_string1_chars_valid,
      ff_in_string1_chars_ready   => ff_in_inst_ff_in_string1_chars_ready,
      ff_in_string1_chars_dvalid  => ff_in_inst_ff_in_string1_chars_dvalid,
      ff_in_string1_chars_last    => ff_in_inst_ff_in_string1_chars_last,
      ff_in_string1_chars_data    => ff_in_inst_ff_in_string1_chars_data,
      ff_in_string1_chars_count   => ff_in_inst_ff_in_string1_chars_count,
      ff_in_string1_cmd_valid     => FletcherWildcard_inst_ff_in_string1_cmd_valid,
      ff_in_string1_cmd_ready     => FletcherWildcard_inst_ff_in_string1_cmd_ready,
      ff_in_string1_cmd_firstIdx  => FletcherWildcard_inst_ff_in_string1_cmd_firstIdx,
      ff_in_string1_cmd_lastidx   => FletcherWildcard_inst_ff_in_string1_cmd_lastidx,
      ff_in_string1_cmd_ctrl      => FletcherWildcard_inst_ff_in_string1_cmd_ctrl,
      ff_in_string1_cmd_tag       => FletcherWildcard_inst_ff_in_string1_cmd_tag,
      ff_in_string1_unl_valid     => ff_in_inst_ff_in_string1_unl_valid,
      ff_in_string1_unl_ready     => ff_in_inst_ff_in_string1_unl_ready,
      ff_in_string1_unl_tag       => ff_in_inst_ff_in_string1_unl_tag,
      ff_in_string2_valid         => ff_in_inst_ff_in_string2_valid,
      ff_in_string2_ready         => ff_in_inst_ff_in_string2_ready,
      ff_in_string2_dvalid        => ff_in_inst_ff_in_string2_dvalid,
      ff_in_string2_last          => ff_in_inst_ff_in_string2_last,
      ff_in_string2_length        => ff_in_inst_ff_in_string2_length,
      ff_in_string2_count         => ff_in_inst_ff_in_string2_count,
      ff_in_string2_chars_valid   => ff_in_inst_ff_in_string2_chars_valid,
      ff_in_string2_chars_ready   => ff_in_inst_ff_in_string2_chars_ready,
      ff_in_string2_chars_dvalid  => ff_in_inst_ff_in_string2_chars_dvalid,
      ff_in_string2_chars_last    => ff_in_inst_ff_in_string2_chars_last,
      ff_in_string2_chars_data    => ff_in_inst_ff_in_string2_chars_data,
      ff_in_string2_chars_count   => ff_in_inst_ff_in_string2_chars_count,
      ff_in_string2_cmd_valid     => FletcherWildcard_inst_ff_in_string2_cmd_valid,
      ff_in_string2_cmd_ready     => FletcherWildcard_inst_ff_in_string2_cmd_ready,
      ff_in_string2_cmd_firstIdx  => FletcherWildcard_inst_ff_in_string2_cmd_firstIdx,
      ff_in_string2_cmd_lastidx   => FletcherWildcard_inst_ff_in_string2_cmd_lastidx,
      ff_in_string2_cmd_ctrl      => FletcherWildcard_inst_ff_in_string2_cmd_ctrl,
      ff_in_string2_cmd_tag       => FletcherWildcard_inst_ff_in_string2_cmd_tag,
      ff_in_string2_unl_valid     => ff_in_inst_ff_in_string2_unl_valid,
      ff_in_string2_unl_ready     => ff_in_inst_ff_in_string2_unl_ready,
      ff_in_string2_unl_tag       => ff_in_inst_ff_in_string2_unl_tag,
      ff_out_pkid_valid           => FletcherWildcard_inst_ff_out_pkid_valid,
      ff_out_pkid_ready           => FletcherWildcard_inst_ff_out_pkid_ready,
      ff_out_pkid_dvalid          => FletcherWildcard_inst_ff_out_pkid_dvalid,
      ff_out_pkid_last            => FletcherWildcard_inst_ff_out_pkid_last,
      ff_out_pkid                 => FletcherWildcard_inst_ff_out_pkid,
      ff_out_pkid_cmd_valid       => FletcherWildcard_inst_ff_out_pkid_cmd_valid,
      ff_out_pkid_cmd_ready       => FletcherWildcard_inst_ff_out_pkid_cmd_ready,
      ff_out_pkid_cmd_firstIdx    => FletcherWildcard_inst_ff_out_pkid_cmd_firstIdx,
      ff_out_pkid_cmd_lastidx     => FletcherWildcard_inst_ff_out_pkid_cmd_lastidx,
      ff_out_pkid_cmd_ctrl        => FletcherWildcard_inst_ff_out_pkid_cmd_ctrl,
      ff_out_pkid_cmd_tag         => FletcherWildcard_inst_ff_out_pkid_cmd_tag,
      ff_out_pkid_unl_valid       => ff_out_inst_ff_out_pkid_unl_valid,
      ff_out_pkid_unl_ready       => ff_out_inst_ff_out_pkid_unl_ready,
      ff_out_pkid_unl_tag         => ff_out_inst_ff_out_pkid_unl_tag,
      ff_out_string1_valid        => FletcherWildcard_inst_ff_out_string1_valid,
      ff_out_string1_ready        => FletcherWildcard_inst_ff_out_string1_ready,
      ff_out_string1_dvalid       => FletcherWildcard_inst_ff_out_string1_dvalid,
      ff_out_string1_last         => FletcherWildcard_inst_ff_out_string1_last,
      ff_out_string1_length       => FletcherWildcard_inst_ff_out_string1_length,
      ff_out_string1_count        => FletcherWildcard_inst_ff_out_string1_count,
      ff_out_string1_chars_valid  => FletcherWildcard_inst_ff_out_string1_chars_valid,
      ff_out_string1_chars_ready  => FletcherWildcard_inst_ff_out_string1_chars_ready,
      ff_out_string1_chars_dvalid => FletcherWildcard_inst_ff_out_string1_chars_dvalid,
      ff_out_string1_chars_last   => FletcherWildcard_inst_ff_out_string1_chars_last,
      ff_out_string1_chars_data   => FletcherWildcard_inst_ff_out_string1_chars_data,
      ff_out_string1_chars_count  => FletcherWildcard_inst_ff_out_string1_chars_count,
      ff_out_string1_cmd_valid    => FletcherWildcard_inst_ff_out_string1_cmd_valid,
      ff_out_string1_cmd_ready    => FletcherWildcard_inst_ff_out_string1_cmd_ready,
      ff_out_string1_cmd_firstIdx => FletcherWildcard_inst_ff_out_string1_cmd_firstIdx,
      ff_out_string1_cmd_lastidx  => FletcherWildcard_inst_ff_out_string1_cmd_lastidx,
      ff_out_string1_cmd_ctrl     => FletcherWildcard_inst_ff_out_string1_cmd_ctrl,
      ff_out_string1_cmd_tag      => FletcherWildcard_inst_ff_out_string1_cmd_tag,
      ff_out_string1_unl_valid    => ff_out_inst_ff_out_string1_unl_valid,
      ff_out_string1_unl_ready    => ff_out_inst_ff_out_string1_unl_ready,
      ff_out_string1_unl_tag      => ff_out_inst_ff_out_string1_unl_tag,
      ff_out_string2_valid        => FletcherWildcard_inst_ff_out_string2_valid,
      ff_out_string2_ready        => FletcherWildcard_inst_ff_out_string2_ready,
      ff_out_string2_dvalid       => FletcherWildcard_inst_ff_out_string2_dvalid,
      ff_out_string2_last         => FletcherWildcard_inst_ff_out_string2_last,
      ff_out_string2_length       => FletcherWildcard_inst_ff_out_string2_length,
      ff_out_string2_count        => FletcherWildcard_inst_ff_out_string2_count,
      ff_out_string2_chars_valid  => FletcherWildcard_inst_ff_out_string2_chars_valid,
      ff_out_string2_chars_ready  => FletcherWildcard_inst_ff_out_string2_chars_ready,
      ff_out_string2_chars_dvalid => FletcherWildcard_inst_ff_out_string2_chars_dvalid,
      ff_out_string2_chars_last   => FletcherWildcard_inst_ff_out_string2_chars_last,
      ff_out_string2_chars_data   => FletcherWildcard_inst_ff_out_string2_chars_data,
      ff_out_string2_chars_count  => FletcherWildcard_inst_ff_out_string2_chars_count,
      ff_out_string2_cmd_valid    => FletcherWildcard_inst_ff_out_string2_cmd_valid,
      ff_out_string2_cmd_ready    => FletcherWildcard_inst_ff_out_string2_cmd_ready,
      ff_out_string2_cmd_firstIdx => FletcherWildcard_inst_ff_out_string2_cmd_firstIdx,
      ff_out_string2_cmd_lastidx  => FletcherWildcard_inst_ff_out_string2_cmd_lastidx,
      ff_out_string2_cmd_ctrl     => FletcherWildcard_inst_ff_out_string2_cmd_ctrl,
      ff_out_string2_cmd_tag      => FletcherWildcard_inst_ff_out_string2_cmd_tag,
      ff_out_string2_unl_valid    => ff_out_inst_ff_out_string2_unl_valid,
      ff_out_string2_unl_ready    => ff_out_inst_ff_out_string2_unl_ready,
      ff_out_string2_unl_tag      => ff_out_inst_ff_out_string2_unl_tag
    );
  BusReadArbiterVec_inst : BusReadArbiterVec
    generic map (
      BUS_ADDR_WIDTH  => 64,
      BUS_LEN_WIDTH   => 8,
      BUS_DATA_WIDTH  => 512,
      ARB_METHOD      => "ROUND-ROBIN",
      MAX_OUTSTANDING => 4,
      RAM_CONFIG      => "",
      SLV_REQ_SLICES  => true,
      MST_REQ_SLICE   => true,
      MST_DAT_SLICE   => true,
      SLV_DAT_SLICES  => true,
      NUM_SLAVE_PORTS => 3
    )
    port map (
      bcd_clk                         => bcd_clk,
      bcd_reset                       => bcd_reset,
      mst_rreq_valid                  => rd_mst_rreq_valid,
      mst_rreq_ready                  => rd_mst_rreq_ready,
      mst_rreq_addr                   => rd_mst_rreq_addr,
      mst_rreq_len                    => rd_mst_rreq_len,
      mst_rdat_valid                  => rd_mst_rdat_valid,
      mst_rdat_ready                  => rd_mst_rdat_ready,
      mst_rdat_data                   => rd_mst_rdat_data,
      mst_rdat_last                   => rd_mst_rdat_last,
      bsv_rreq_valid(0)               => ff_in_inst_ff_in_pkid_bus_rreq_valid,
      bsv_rreq_valid(1)               => ff_in_inst_ff_in_string1_bus_rreq_valid,
      bsv_rreq_valid(2)               => ff_in_inst_ff_in_string2_bus_rreq_valid,
      bsv_rreq_ready(0)               => ff_in_inst_ff_in_pkid_bus_rreq_ready,
      bsv_rreq_ready(1)               => ff_in_inst_ff_in_string1_bus_rreq_ready,
      bsv_rreq_ready(2)               => ff_in_inst_ff_in_string2_bus_rreq_ready,
      bsv_rreq_len(7 downto 0)        => ff_in_inst_ff_in_pkid_bus_rreq_len,
      bsv_rreq_len(15 downto 8)       => ff_in_inst_ff_in_string1_bus_rreq_len,
      bsv_rreq_len(23 downto 16)      => ff_in_inst_ff_in_string2_bus_rreq_len,
      bsv_rreq_addr(63 downto 0)      => ff_in_inst_ff_in_pkid_bus_rreq_addr,
      bsv_rreq_addr(127 downto 64)    => ff_in_inst_ff_in_string1_bus_rreq_addr,
      bsv_rreq_addr(191 downto 128)   => ff_in_inst_ff_in_string2_bus_rreq_addr,
      bsv_rdat_valid(0)               => ff_in_inst_ff_in_pkid_bus_rdat_valid,
      bsv_rdat_valid(1)               => ff_in_inst_ff_in_string1_bus_rdat_valid,
      bsv_rdat_valid(2)               => ff_in_inst_ff_in_string2_bus_rdat_valid,
      bsv_rdat_ready(0)               => ff_in_inst_ff_in_pkid_bus_rdat_ready,
      bsv_rdat_ready(1)               => ff_in_inst_ff_in_string1_bus_rdat_ready,
      bsv_rdat_ready(2)               => ff_in_inst_ff_in_string2_bus_rdat_ready,
      bsv_rdat_last(0)                => ff_in_inst_ff_in_pkid_bus_rdat_last,
      bsv_rdat_last(1)                => ff_in_inst_ff_in_string1_bus_rdat_last,
      bsv_rdat_last(2)                => ff_in_inst_ff_in_string2_bus_rdat_last,
      bsv_rdat_data(511 downto 0)     => ff_in_inst_ff_in_pkid_bus_rdat_data,
      bsv_rdat_data(1023 downto 512)  => ff_in_inst_ff_in_string1_bus_rdat_data,
      bsv_rdat_data(1535 downto 1024) => ff_in_inst_ff_in_string2_bus_rdat_data
    );
  BusWriteArbiterVec_inst : BusWriteArbiterVec
    generic map (
      BUS_ADDR_WIDTH   => 64,
      BUS_LEN_WIDTH    => 8,
      BUS_DATA_WIDTH   => 512,
      BUS_STROBE_WIDTH => 64,
      ARB_METHOD       => "ROUND-ROBIN",
      MAX_OUTSTANDING  => 4,
      RAM_CONFIG       => "",
      SLV_REQ_SLICES   => true,
      MST_REQ_SLICE    => true,
      MST_DAT_SLICE    => true,
      SLV_DAT_SLICES   => true,
      NUM_SLAVE_PORTS  => 3
    )
    port map (
      bcd_clk                         => bcd_clk,
      bcd_reset                       => bcd_reset,
      mst_wreq_valid                  => wr_mst_wreq_valid,
      mst_wreq_ready                  => wr_mst_wreq_ready,
      mst_wreq_addr                   => wr_mst_wreq_addr,
      mst_wreq_len                    => wr_mst_wreq_len,
      mst_wdat_valid                  => wr_mst_wdat_valid,
      mst_wdat_ready                  => wr_mst_wdat_ready,
      mst_wdat_data                   => wr_mst_wdat_data,
      mst_wdat_strobe                 => wr_mst_wdat_strobe,
      mst_wdat_last                   => wr_mst_wdat_last,
      bsv_wreq_valid(0)               => ff_out_inst_ff_out_pkid_bus_wreq_valid,
      bsv_wreq_valid(1)               => ff_out_inst_ff_out_string1_bus_wreq_valid,
      bsv_wreq_valid(2)               => ff_out_inst_ff_out_string2_bus_wreq_valid,
      bsv_wreq_ready(0)               => ff_out_inst_ff_out_pkid_bus_wreq_ready,
      bsv_wreq_ready(1)               => ff_out_inst_ff_out_string1_bus_wreq_ready,
      bsv_wreq_ready(2)               => ff_out_inst_ff_out_string2_bus_wreq_ready,
      bsv_wreq_len(7 downto 0)        => ff_out_inst_ff_out_pkid_bus_wreq_len,
      bsv_wreq_len(15 downto 8)       => ff_out_inst_ff_out_string1_bus_wreq_len,
      bsv_wreq_len(23 downto 16)      => ff_out_inst_ff_out_string2_bus_wreq_len,
      bsv_wreq_addr(63 downto 0)      => ff_out_inst_ff_out_pkid_bus_wreq_addr,
      bsv_wreq_addr(127 downto 64)    => ff_out_inst_ff_out_string1_bus_wreq_addr,
      bsv_wreq_addr(191 downto 128)   => ff_out_inst_ff_out_string2_bus_wreq_addr,
      bsv_wdat_valid(0)               => ff_out_inst_ff_out_pkid_bus_wdat_valid,
      bsv_wdat_valid(1)               => ff_out_inst_ff_out_string1_bus_wdat_valid,
      bsv_wdat_valid(2)               => ff_out_inst_ff_out_string2_bus_wdat_valid,
      bsv_wdat_strobe(63 downto 0)    => ff_out_inst_ff_out_pkid_bus_wdat_strobe,
      bsv_wdat_strobe(127 downto 64)  => ff_out_inst_ff_out_string1_bus_wdat_strobe,
      bsv_wdat_strobe(191 downto 128) => ff_out_inst_ff_out_string2_bus_wdat_strobe,
      bsv_wdat_ready(0)               => ff_out_inst_ff_out_pkid_bus_wdat_ready,
      bsv_wdat_ready(1)               => ff_out_inst_ff_out_string1_bus_wdat_ready,
      bsv_wdat_ready(2)               => ff_out_inst_ff_out_string2_bus_wdat_ready,
      bsv_wdat_last(0)                => ff_out_inst_ff_out_pkid_bus_wdat_last,
      bsv_wdat_last(1)                => ff_out_inst_ff_out_string1_bus_wdat_last,
      bsv_wdat_last(2)                => ff_out_inst_ff_out_string2_bus_wdat_last,
      bsv_wdat_data(511 downto 0)     => ff_out_inst_ff_out_pkid_bus_wdat_data,
      bsv_wdat_data(1023 downto 512)  => ff_out_inst_ff_out_string1_bus_wdat_data,
      bsv_wdat_data(1535 downto 1024) => ff_out_inst_ff_out_string2_bus_wdat_data
    );
end architecture;
