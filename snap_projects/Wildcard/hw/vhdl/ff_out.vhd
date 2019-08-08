library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
library work;
use work.Array_pkg.all;
entity ff_out is
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
end entity;
architecture Implementation of ff_out is
begin
  pkid_inst : ArrayWriter
    generic map (
      BUS_ADDR_WIDTH     => 64,
      BUS_LEN_WIDTH      => 8,
      BUS_DATA_WIDTH     => 512,
      BUS_STROBE_WIDTH   => 64,
      BUS_BURST_STEP_LEN => 1,
      BUS_BURST_MAX_LEN  => 64,
      INDEX_WIDTH        => 32,
      CFG                => "prim(32)",
      CMD_TAG_ENABLE     => true,
      CMD_TAG_WIDTH      => 1
    )
    port map (
      bcd_clk              => bcd_clk,
      bcd_reset            => bcd_reset,
      kcd_clk              => kcd_clk,
      kcd_reset            => kcd_reset,
      bus_wreq_valid       => ff_out_pkid_bus_wreq_valid,
      bus_wreq_ready       => ff_out_pkid_bus_wreq_ready,
      bus_wreq_addr        => ff_out_pkid_bus_wreq_addr,
      bus_wreq_len         => ff_out_pkid_bus_wreq_len,
      bus_wdat_valid       => ff_out_pkid_bus_wdat_valid,
      bus_wdat_ready       => ff_out_pkid_bus_wdat_ready,
      bus_wdat_data        => ff_out_pkid_bus_wdat_data,
      bus_wdat_strobe      => ff_out_pkid_bus_wdat_strobe,
      bus_wdat_last        => ff_out_pkid_bus_wdat_last,
      cmd_valid            => ff_out_pkid_cmd_valid,
      cmd_ready            => ff_out_pkid_cmd_ready,
      cmd_firstIdx         => ff_out_pkid_cmd_firstIdx,
      cmd_lastidx          => ff_out_pkid_cmd_lastidx,
      cmd_ctrl             => ff_out_pkid_cmd_ctrl,
      cmd_tag              => ff_out_pkid_cmd_tag,
      unl_valid            => ff_out_pkid_unl_valid,
      unl_ready            => ff_out_pkid_unl_ready,
      unl_tag              => ff_out_pkid_unl_tag,
      in_valid(0)          => ff_out_pkid_valid,
      in_ready(0)          => ff_out_pkid_ready,
      in_data(31 downto 0) => ff_out_pkid,
      in_dvalid(0)         => ff_out_pkid_dvalid,
      in_last(0)           => ff_out_pkid_last
    );
  string1_inst : ArrayWriter
    generic map (
      BUS_ADDR_WIDTH     => 64,
      BUS_LEN_WIDTH      => 8,
      BUS_DATA_WIDTH     => 512,
      BUS_STROBE_WIDTH   => 64,
      BUS_BURST_STEP_LEN => 1,
      BUS_BURST_MAX_LEN  => 64,
      INDEX_WIDTH        => 32,
      CFG                => "listprim(8)",
      CMD_TAG_ENABLE     => true,
      CMD_TAG_WIDTH      => 1
    )
    port map (
      bcd_clk               => bcd_clk,
      bcd_reset             => bcd_reset,
      kcd_clk               => kcd_clk,
      kcd_reset             => kcd_reset,
      bus_wreq_valid        => ff_out_string1_bus_wreq_valid,
      bus_wreq_ready        => ff_out_string1_bus_wreq_ready,
      bus_wreq_addr         => ff_out_string1_bus_wreq_addr,
      bus_wreq_len          => ff_out_string1_bus_wreq_len,
      bus_wdat_valid        => ff_out_string1_bus_wdat_valid,
      bus_wdat_ready        => ff_out_string1_bus_wdat_ready,
      bus_wdat_data         => ff_out_string1_bus_wdat_data,
      bus_wdat_strobe       => ff_out_string1_bus_wdat_strobe,
      bus_wdat_last         => ff_out_string1_bus_wdat_last,
      cmd_valid             => ff_out_string1_cmd_valid,
      cmd_ready             => ff_out_string1_cmd_ready,
      cmd_firstIdx          => ff_out_string1_cmd_firstIdx,
      cmd_lastidx           => ff_out_string1_cmd_lastidx,
      cmd_ctrl              => ff_out_string1_cmd_ctrl,
      cmd_tag               => ff_out_string1_cmd_tag,
      unl_valid             => ff_out_string1_unl_valid,
      unl_ready             => ff_out_string1_unl_ready,
      unl_tag               => ff_out_string1_unl_tag,
      in_valid(0)           => ff_out_string1_valid,
      in_valid(1)           => ff_out_string1_chars_valid,
      in_ready(0)           => ff_out_string1_ready,
      in_ready(1)           => ff_out_string1_chars_ready,
      in_data(31 downto 0)  => ff_out_string1_length,
      in_data(32 downto 32) => ff_out_string1_count,
      in_data(40 downto 33) => ff_out_string1_chars_data,
      in_data(41 downto 41) => ff_out_string1_chars_count,
      in_dvalid(0)          => ff_out_string1_dvalid,
      in_dvalid(1)          => ff_out_string1_chars_dvalid,
      in_last(0)            => ff_out_string1_last,
      in_last(1)            => ff_out_string1_chars_last
    );
  string2_inst : ArrayWriter
    generic map (
      BUS_ADDR_WIDTH     => 64,
      BUS_LEN_WIDTH      => 8,
      BUS_DATA_WIDTH     => 512,
      BUS_STROBE_WIDTH   => 64,
      BUS_BURST_STEP_LEN => 1,
      BUS_BURST_MAX_LEN  => 64,
      INDEX_WIDTH        => 32,
      CFG                => "listprim(8)",
      CMD_TAG_ENABLE     => true,
      CMD_TAG_WIDTH      => 1
    )
    port map (
      bcd_clk               => bcd_clk,
      bcd_reset             => bcd_reset,
      kcd_clk               => kcd_clk,
      kcd_reset             => kcd_reset,
      bus_wreq_valid        => ff_out_string2_bus_wreq_valid,
      bus_wreq_ready        => ff_out_string2_bus_wreq_ready,
      bus_wreq_addr         => ff_out_string2_bus_wreq_addr,
      bus_wreq_len          => ff_out_string2_bus_wreq_len,
      bus_wdat_valid        => ff_out_string2_bus_wdat_valid,
      bus_wdat_ready        => ff_out_string2_bus_wdat_ready,
      bus_wdat_data         => ff_out_string2_bus_wdat_data,
      bus_wdat_strobe       => ff_out_string2_bus_wdat_strobe,
      bus_wdat_last         => ff_out_string2_bus_wdat_last,
      cmd_valid             => ff_out_string2_cmd_valid,
      cmd_ready             => ff_out_string2_cmd_ready,
      cmd_firstIdx          => ff_out_string2_cmd_firstIdx,
      cmd_lastidx           => ff_out_string2_cmd_lastidx,
      cmd_ctrl              => ff_out_string2_cmd_ctrl,
      cmd_tag               => ff_out_string2_cmd_tag,
      unl_valid             => ff_out_string2_unl_valid,
      unl_ready             => ff_out_string2_unl_ready,
      unl_tag               => ff_out_string2_unl_tag,
      in_valid(0)           => ff_out_string2_valid,
      in_valid(1)           => ff_out_string2_chars_valid,
      in_ready(0)           => ff_out_string2_ready,
      in_ready(1)           => ff_out_string2_chars_ready,
      in_data(31 downto 0)  => ff_out_string2_length,
      in_data(32 downto 32) => ff_out_string2_count,
      in_data(40 downto 33) => ff_out_string2_chars_data,
      in_data(41 downto 41) => ff_out_string2_chars_count,
      in_dvalid(0)          => ff_out_string2_dvalid,
      in_dvalid(1)          => ff_out_string2_chars_dvalid,
      in_last(0)            => ff_out_string2_last,
      in_last(1)            => ff_out_string2_chars_last
    );
end architecture;
