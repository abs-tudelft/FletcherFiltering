library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
library work;
use work.Array_pkg.all;
entity ff_in is
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
end entity;
architecture Implementation of ff_in is
begin
  pkid_inst : ArrayReader
    generic map (
      BUS_ADDR_WIDTH     => 64,
      BUS_LEN_WIDTH      => 8,
      BUS_DATA_WIDTH     => 512,
      BUS_BURST_STEP_LEN => 1,
      BUS_BURST_MAX_LEN  => 64,
      INDEX_WIDTH        => 32,
      CFG                => "prim(32)",
      CMD_TAG_ENABLE     => true,
      CMD_TAG_WIDTH      => 1
    )
    port map (
      bcd_clk               => bcd_clk,
      bcd_reset             => bcd_reset,
      kcd_clk               => kcd_clk,
      kcd_reset             => kcd_reset,
      bus_rreq_valid        => ff_in_pkid_bus_rreq_valid,
      bus_rreq_ready        => ff_in_pkid_bus_rreq_ready,
      bus_rreq_addr         => ff_in_pkid_bus_rreq_addr,
      bus_rreq_len          => ff_in_pkid_bus_rreq_len,
      bus_rdat_valid        => ff_in_pkid_bus_rdat_valid,
      bus_rdat_ready        => ff_in_pkid_bus_rdat_ready,
      bus_rdat_data         => ff_in_pkid_bus_rdat_data,
      bus_rdat_last         => ff_in_pkid_bus_rdat_last,
      cmd_valid             => ff_in_pkid_cmd_valid,
      cmd_ready             => ff_in_pkid_cmd_ready,
      cmd_firstIdx          => ff_in_pkid_cmd_firstIdx,
      cmd_lastidx           => ff_in_pkid_cmd_lastidx,
      cmd_ctrl              => ff_in_pkid_cmd_ctrl,
      cmd_tag               => ff_in_pkid_cmd_tag,
      unl_valid             => ff_in_pkid_unl_valid,
      unl_ready             => ff_in_pkid_unl_ready,
      unl_tag               => ff_in_pkid_unl_tag,
      out_valid(0)          => ff_in_pkid_valid,
      out_ready(0)          => ff_in_pkid_ready,
      out_data(31 downto 0) => ff_in_pkid,
      out_dvalid(0)         => ff_in_pkid_dvalid,
      out_last(0)           => ff_in_pkid_last
    );
  string1_inst : ArrayReader
    generic map (
      BUS_ADDR_WIDTH     => 64,
      BUS_LEN_WIDTH      => 8,
      BUS_DATA_WIDTH     => 512,
      BUS_BURST_STEP_LEN => 1,
      BUS_BURST_MAX_LEN  => 64,
      INDEX_WIDTH        => 32,
      CFG                => "listprim(8)",
      CMD_TAG_ENABLE     => true,
      CMD_TAG_WIDTH      => 1
    )
    port map (
      bcd_clk                => bcd_clk,
      bcd_reset              => bcd_reset,
      kcd_clk                => kcd_clk,
      kcd_reset              => kcd_reset,
      bus_rreq_valid         => ff_in_string1_bus_rreq_valid,
      bus_rreq_ready         => ff_in_string1_bus_rreq_ready,
      bus_rreq_addr          => ff_in_string1_bus_rreq_addr,
      bus_rreq_len           => ff_in_string1_bus_rreq_len,
      bus_rdat_valid         => ff_in_string1_bus_rdat_valid,
      bus_rdat_ready         => ff_in_string1_bus_rdat_ready,
      bus_rdat_data          => ff_in_string1_bus_rdat_data,
      bus_rdat_last          => ff_in_string1_bus_rdat_last,
      cmd_valid              => ff_in_string1_cmd_valid,
      cmd_ready              => ff_in_string1_cmd_ready,
      cmd_firstIdx           => ff_in_string1_cmd_firstIdx,
      cmd_lastidx            => ff_in_string1_cmd_lastidx,
      cmd_ctrl               => ff_in_string1_cmd_ctrl,
      cmd_tag                => ff_in_string1_cmd_tag,
      unl_valid              => ff_in_string1_unl_valid,
      unl_ready              => ff_in_string1_unl_ready,
      unl_tag                => ff_in_string1_unl_tag,
      out_valid(0)           => ff_in_string1_valid,
      out_valid(1)           => ff_in_string1_chars_valid,
      out_ready(0)           => ff_in_string1_ready,
      out_ready(1)           => ff_in_string1_chars_ready,
      out_data(31 downto 0)  => ff_in_string1_length,
      out_data(32 downto 32) => ff_in_string1_count,
      out_data(40 downto 33) => ff_in_string1_chars_data,
      out_data(41 downto 41) => ff_in_string1_chars_count,
      out_dvalid(0)          => ff_in_string1_dvalid,
      out_dvalid(1)          => ff_in_string1_chars_dvalid,
      out_last(0)            => ff_in_string1_last,
      out_last(1)            => ff_in_string1_chars_last
    );
  string2_inst : ArrayReader
    generic map (
      BUS_ADDR_WIDTH     => 64,
      BUS_LEN_WIDTH      => 8,
      BUS_DATA_WIDTH     => 512,
      BUS_BURST_STEP_LEN => 1,
      BUS_BURST_MAX_LEN  => 64,
      INDEX_WIDTH        => 32,
      CFG                => "listprim(8)",
      CMD_TAG_ENABLE     => true,
      CMD_TAG_WIDTH      => 1
    )
    port map (
      bcd_clk                => bcd_clk,
      bcd_reset              => bcd_reset,
      kcd_clk                => kcd_clk,
      kcd_reset              => kcd_reset,
      bus_rreq_valid         => ff_in_string2_bus_rreq_valid,
      bus_rreq_ready         => ff_in_string2_bus_rreq_ready,
      bus_rreq_addr          => ff_in_string2_bus_rreq_addr,
      bus_rreq_len           => ff_in_string2_bus_rreq_len,
      bus_rdat_valid         => ff_in_string2_bus_rdat_valid,
      bus_rdat_ready         => ff_in_string2_bus_rdat_ready,
      bus_rdat_data          => ff_in_string2_bus_rdat_data,
      bus_rdat_last          => ff_in_string2_bus_rdat_last,
      cmd_valid              => ff_in_string2_cmd_valid,
      cmd_ready              => ff_in_string2_cmd_ready,
      cmd_firstIdx           => ff_in_string2_cmd_firstIdx,
      cmd_lastidx            => ff_in_string2_cmd_lastidx,
      cmd_ctrl               => ff_in_string2_cmd_ctrl,
      cmd_tag                => ff_in_string2_cmd_tag,
      unl_valid              => ff_in_string2_unl_valid,
      unl_ready              => ff_in_string2_unl_ready,
      unl_tag                => ff_in_string2_unl_tag,
      out_valid(0)           => ff_in_string2_valid,
      out_valid(1)           => ff_in_string2_chars_valid,
      out_ready(0)           => ff_in_string2_ready,
      out_ready(1)           => ff_in_string2_chars_ready,
      out_data(31 downto 0)  => ff_in_string2_length,
      out_data(32 downto 32) => ff_in_string2_count,
      out_data(40 downto 33) => ff_in_string2_chars_data,
      out_data(41 downto 41) => ff_in_string2_chars_count,
      out_dvalid(0)          => ff_in_string2_dvalid,
      out_dvalid(1)          => ff_in_string2_chars_dvalid,
      out_last(0)            => ff_in_string2_last,
      out_last(1)            => ff_in_string2_chars_last
    );
end architecture;
