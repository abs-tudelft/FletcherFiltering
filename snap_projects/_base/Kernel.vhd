library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
entity FletcherSimple is
  generic (
    BUS_ADDR_WIDTH : integer := 64
  );
  port (
    kcd_clk               : in  std_logic;
    kcd_reset             : in  std_logic;
    mmio_awvalid          : in  std_logic;
    mmio_awready          : out std_logic;
    mmio_awaddr           : in  std_logic_vector(31 downto 0);
    mmio_wvalid           : in  std_logic;
    mmio_wready           : out std_logic;
    mmio_wdata            : in  std_logic_vector(31 downto 0);
    mmio_wstrb            : in  std_logic_vector(3 downto 0);
    mmio_bvalid           : out std_logic;
    mmio_bready           : in  std_logic;
    mmio_bresp            : out std_logic_vector(1 downto 0);
    mmio_arvalid          : in  std_logic;
    mmio_arready          : out std_logic;
    mmio_araddr           : in  std_logic_vector(31 downto 0);
    mmio_rvalid           : out std_logic;
    mmio_rready           : in  std_logic;
    mmio_rdata            : out std_logic_vector(31 downto 0);
    mmio_rresp            : out std_logic_vector(1 downto 0);
    ff_in_pkid_valid         : in  std_logic;
    ff_in_pkid_ready         : out std_logic;
    ff_in_pkid_dvalid        : in  std_logic;
    ff_in_pkid_last          : in  std_logic;
    ff_in_pkid               : in  std_logic_vector(31 downto 0);
    ff_in_pkid_cmd_valid     : out std_logic;
    ff_in_pkid_cmd_ready     : in  std_logic;
    ff_in_pkid_cmd_firstIdx  : out std_logic_vector(31 downto 0);
    ff_in_pkid_cmd_lastidx   : out std_logic_vector(31 downto 0);
    ff_in_pkid_cmd_ctrl      : out std_logic_vector(bus_addr_width-1 downto 0);
    ff_in_pkid_cmd_tag       : out std_logic_vector(0 downto 0);
    ff_in_pkid_unl_valid     : in  std_logic;
    ff_in_pkid_unl_ready     : out std_logic;
    ff_in_pkid_unl_tag       : in  std_logic_vector(0 downto 0);
    ff_out_pkid_valid        : out std_logic;
    ff_out_pkid_ready        : in  std_logic;
    ff_out_pkid_dvalid       : out std_logic;
    ff_out_pkid_last         : out std_logic;
    ff_out_pkid              : out std_logic_vector(31 downto 0);
    ff_out_pkid_cmd_valid    : out std_logic;
    ff_out_pkid_cmd_ready    : in  std_logic;
    ff_out_pkid_cmd_firstIdx : out std_logic_vector(31 downto 0);
    ff_out_pkid_cmd_lastidx  : out std_logic_vector(31 downto 0);
    ff_out_pkid_cmd_ctrl     : out std_logic_vector(bus_addr_width-1 downto 0);
    ff_out_pkid_cmd_tag      : out std_logic_vector(0 downto 0);
    ff_out_pkid_unl_valid    : in  std_logic;
    ff_out_pkid_unl_ready    : out std_logic;
    ff_out_pkid_unl_tag      : in  std_logic_vector(0 downto 0)
  );
end entity;
architecture Implementation of FletcherSimple is

    -----------------------------------------------------------------------------
  -- MMIO
  -----------------------------------------------------------------------------
  -- Default Fletcher registers:
  constant REG_CONTROL                            : natural :=  0;
  constant REG_STATUS                             : natural :=  1;
  constant REG_RETURN0                            : natural :=  2;
  constant REG_RETURN1                            : natural :=  3;

  -- RecordBatch ranges:
  --TODO GENERATE
  constant REG_IN_PKID_FIRSTIDX                        : natural :=  4;
  constant REG_IN_PKID_LASTIDX                         : natural :=  5;

  constant REG_OUT_PKID_FIRSTIDX                       : natural :=  6;
  constant REG_OUT_PKID_LASTIDX                        : natural :=  7;

  -- Buffer addresses:
  --TODO GENERATE
  constant REG_IN_PKID_BUF_LO                     : natural :=  8;
  constant REG_IN_PKID_BUF_HI                     : natural :=  9;
  constant REG_OUT_PKID_BUF_LO                    : natural :=  10;
  constant REG_OUT_PKID_BUF_HI                    : natural :=  11;

  -- Array of MMIO registers:
  constant NUM_REGS                               : natural := 12; --TODO update
  constant REG_WIDTH                              : natural := 32;

  type reg_array_t is array(natural range <>) of std_logic_vector(REG_WIDTH-1 downto 0);

  signal rreg_concat            : std_logic_vector(NUM_REGS*REG_WIDTH-1 downto 0);
  signal rreg_array             : reg_array_t(0 to NUM_REGS-1);
  signal rreg_en                : std_logic_vector(NUM_REGS-1 downto 0);

  signal wreg_array             : reg_array_t(0 to NUM_REGS-1);
  signal wreg_concat            : std_logic_vector(NUM_REGS*REG_WIDTH-1 downto 0);

  -----------------------------------------------------------------------------
  -- Control signals
  -----------------------------------------------------------------------------
  signal stat_done              : std_logic;
  signal stat_busy              : std_logic;
  signal stat_idle              : std_logic;
  signal ctrl_reset             : std_logic;
  signal ctrl_stop              : std_logic;
  signal ctrl_start             : std_logic;
  signal kcd_reset_n            : std_logic;

  -- Global control state machine
  -- type state_type is (IDLE, START, BUSY, INTERFACE, UNLOCK);
  type state_type is (RESET, WAITING, SETUP, RUNNING, DONE);

  signal state, state_next : state_type;

  -- Count the records
  signal pass_counter, pass_counter_next : unsigned(REG_WIDTH-1 downto 0);
  signal total_counter, total_counter_next : unsigned(REG_WIDTH-1 downto 0);

  -- Kernel singals
  signal ap_start, ap_done, ap_idle, ap_ready : STD_LOGIC;
  signal meta_length_V : STD_LOGIC_VECTOR(31 downto 0);

  --TODO generate
  signal ff_in_pkid_V : STD_LOGIC_VECTOR (33 downto 0);
  signal ff_in_pkid_V_data : STD_LOGIC_VECTOR (31 downto 0);
  signal ff_in_pkid_V_dvalid : STD_LOGIC;
  signal ff_in_pkid_V_last : STD_LOGIC;

  signal ff_in_pkid_V_read : STD_LOGIC;
  signal ff_in_pkid_V_empty_n : STD_LOGIC;

  signal ff_out_pkid_V : STD_LOGIC_VECTOR (33 downto 0);
  signal ff_out_pkid_V_data : STD_LOGIC_VECTOR (31 downto 0);
  signal ff_out_pkid_V_dvalid : STD_LOGIC;
  signal ff_out_pkid_V_last : STD_LOGIC;

  signal ff_out_pkid_V_write : STD_LOGIC;
  signal ff_out_pkid_V_full_n : STD_LOGIC;
  signal ap_return : STD_LOGIC_VECTOR (0 downto 0);

begin

  -----------------------------------------------------------------------------
  -- MMIO
  -----------------------------------------------------------------------------
  kcd_reset_n <= not(kcd_reset);

  -- Instantiate the AXI mmio component to communicate with host more easily
  -- through registers.
  axi_mmio_inst : entity work.AxiMmio
    generic map (
      BUS_ADDR_WIDTH     => 32,
      BUS_DATA_WIDTH     => REG_WIDTH,
      NUM_REGS           => NUM_REGS,
      REG_CONFIG         => "WRRRWWWWWWWWR",
      SLV_R_SLICE_DEPTH  => 0,
      SLV_W_SLICE_DEPTH  => 0
    )
    port map (
      clk                => kcd_clk,
      reset_n            => kcd_reset_n,
      s_axi_awvalid      => mmio_awvalid,
      s_axi_awready      => mmio_awready,
      s_axi_awaddr       => mmio_awaddr,
      s_axi_wvalid       => mmio_wvalid,
      s_axi_wready       => mmio_wready,
      s_axi_wdata        => mmio_wdata,
      s_axi_wstrb        => mmio_wstrb,
      s_axi_bvalid       => mmio_bvalid,
      s_axi_bready       => mmio_bready,
      s_axi_bresp        => mmio_bresp,
      s_axi_arvalid      => mmio_arvalid,
      s_axi_arready      => mmio_arready,
      s_axi_araddr       => mmio_araddr,
      s_axi_rvalid       => mmio_rvalid,
      s_axi_rready       => mmio_rready,
      s_axi_rdata        => mmio_rdata,
      s_axi_rresp        => mmio_rresp,
      regs_out           => wreg_concat,
      regs_in            => rreg_concat,
      regs_in_en         => rreg_en
    );

  -- Turn signals into something more readable
  write_regs_unconcat: for I in 0 to NUM_REGS-1 generate
    wreg_array(I) <= wreg_concat((I+1)*REG_WIDTH-1 downto I*REG_WIDTH);
  end generate;
  read_regs_concat: for I in 0 to NUM_REGS-1 generate
    rreg_concat((I+1)*REG_WIDTH-1 downto I*REG_WIDTH) <= rreg_array(I);
  end generate;

  -- Always enable read registers
  rreg_array(REG_STATUS) <= (0 => stat_idle, 1 => stat_busy, 2 => stat_done, others => '0');
  rreg_en <= (REG_STATUS => '1', REG_RETURN0 => '1', REG_RETURN1 => '1', others => '0');

  -- Put the counters in the return registers
  rreg_array(REG_RETURN0) <= std_logic_vector(pass_counter);
  rreg_array(REG_RETURN1) <= std_logic_vector(total_counter);

  -- Connect the control bits
  ctrl_start <= wreg_array(REG_CONTROL)(0);
  ctrl_stop  <= wreg_array(REG_CONTROL)(1);
  ctrl_reset <= wreg_array(REG_CONTROL)(2);

  -----------------------------------------------------------------------------
  -- Kernel
  -----------------------------------------------------------------------------

--TODO generate
  hls_kernel_inst: entity work.Simple 
      port map (
          ap_clk => kcd_clk,
          ap_rst => kcd_reset,
          ap_start => ap_start,
          ap_done => ap_done,
          ap_idle => ap_idle,
          ap_ready => ap_ready,
          meta_length_V => meta_length_V,
          ff_in_pkid_V_dout => ff_in_pkid_V,
          ff_in_pkid_V_empty_n => ff_in_pkid_V_empty_n,
          ff_in_pkid_V_read => ff_in_pkid_V_read,
          ff_out_pkid_V_din => ff_out_pkid_V,
          ff_out_pkid_V_full_n => ff_out_pkid_V_full_n,
          ff_out_pkid_V_write => ff_out_pkid_V_write,
          ap_return => ap_return
    );

  -- Unpack the data buses
  --TODO generate
  ff_out_pkid_V_dvalid <= ff_out_pkid_V(0);
  ff_out_pkid_V_last <= ff_out_pkid_V(1);
  ff_out_pkid_V_data <= ff_out_pkid_V(33 downto 2);

  ff_in_pkid_V(0) <= ff_in_pkid_V_dvalid;
  ff_in_pkid_V(1) <= ff_in_pkid_V_last;
  ff_in_pkid_V(33 downto 2) <= ff_in_pkid_V_data;

  -- hook up rest of the kernel signals
  -- ap_ready, ap_done, ap_start are already hooked up in the state machine
  meta_length_V <= std_logic_vector(unsigned(wreg_array(REG_IN_PKID_LASTIDX))-unsigned(wreg_array(REG_IN_PKID_FIRSTIDX)));

  --TODO generate
  ff_in_pkid_V_data <= ff_in_pkid;
  ff_in_pkid_V_dvalid <= ff_in_pkid_dvalid;
  ff_in_pkid_V_last <= ff_in_pkid_last;

  -- in handshake signals
  ff_in_pkid_V_empty_n <= ff_in_pkid_valid;
  ff_in_pkid_ready <= ff_in_pkid_V_read;

  ff_out_pkid <= ff_out_pkid_V_data;
  ff_out_pkid_dvalid <= ff_out_pkid_V_dvalid;
  ff_out_pkid_last <= ff_out_pkid_V_last;

  -- out handshake signals
  ff_out_pkid_valid <= ff_out_pkid_V_write;
  ff_out_pkid_V_full_n <= ff_out_pkid_ready;

  -----------------------------------------------------------------------------
  -- Kernel state machine
  -----------------------------------------------------------------------------

  -- Provide base address to ArrayReader
  --TODO generate
  ff_in_pkid_cmd_ctrl <= wreg_array(REG_IN_PKID_BUF_HI) 
                    & wreg_array(REG_IN_PKID_BUF_LO);

  -- Provide base address to ArrayWriter
  ff_out_pkid_cmd_ctrl <= wreg_array(REG_OUT_PKID_BUF_HI) 
                    & wreg_array(REG_OUT_PKID_BUF_LO);

  -- Set the first and last index on our array
  --TODO generate
  ff_in_pkid_cmd_firstIdx <= wreg_array(REG_IN_PKID_FIRSTIDX);
  ff_in_pkid_cmd_lastIdx  <= wreg_array(REG_IN_PKID_LASTIDX);
  ff_out_pkid_cmd_firstIdx <= wreg_array(REG_OUT_PKID_FIRSTIDX);
  ff_out_pkid_cmd_lastIdx  <= wreg_array(REG_OUT_PKID_LASTIDX);

  logic_p: process (
    -- State
    state, 
    -- Control signals
    ctrl_start, ctrl_stop, ctrl_reset, 
    -- HLS Control signals
    ap_done, ap_ready, ap_idle, ap_return,
    -- Command streams
    ff_in_pkid_cmd_ready, ff_out_pkid_cmd_ready, --TODO generate
    -- Data streams
    ff_in_pkid_valid, ff_out_pkid_ready, ff_in_pkid_last, ff_in_pkid_dvalid, --TODO generate
    ff_out_pkid_V_write, ff_out_pkid_ready, ff_out_pkid_V_last, ff_out_pkid_V_dvalid, --TODO generate
    -- Unlock streams
    ff_in_pkid_unl_valid, ff_out_pkid_unl_valid, --TODO generate
    -- Internal
    pass_counter,
    total_counter
  ) is 
  begin
    
    -- Default values:
    
    -- No command to "pkid" ArrayReader
    ff_in_pkid_cmd_valid <= '0'; --TODO generate
    -- No command to "pkid" ArrayWriter
    ff_out_pkid_cmd_valid <= '0'; --TODO generate
    -- Do not accept values from the "pkid" ArrayReader
    ff_in_pkid_unl_ready <= '0'; --TODO generate
    -- Do not accept values from the "pkid" ArrayWriter
    ff_out_pkid_unl_ready <= '0'; --TODO generate
    -- Retain counter values
    pass_counter_next <= pass_counter;
    total_counter_next <= total_counter;
    -- Stay in same state
    state_next <= state;
    -- Stoop the HLS kernel
    ap_start <= '0';

    -- States:
    case state is
      when RESET =>
        stat_done <= '0';
        stat_busy <= '0';
        stat_idle <= '0';
        state_next <= WAITING;
        -- Start sum at 0
        pass_counter_next <= (others => '0');
        total_counter_next <= (others => '0');

      when WAITING =>
        stat_done <= '0';
        stat_busy <= '0';
        stat_idle <= '1';
        -- Wait for start signal from UserCore (initiated by software)
        if ctrl_start = '1' then
          state_next <= SETUP;
        end if;

      when SETUP =>
        stat_done <= '0';
        stat_busy <= '1';
        stat_idle <= '0';
        ap_start <= '1';

        -- Send address and row indices to the ArrayReader
        ff_in_pkid_cmd_valid <= '1'; --TODO generate
        -- Send address and row indices to the ArrayWriter
        ff_out_pkid_cmd_valid <= '1'; --TODO generate
        if ff_in_pkid_cmd_ready = '1' and ff_out_pkid_cmd_ready = '1' then --TODO generate
          -- ArrayReader and ArrayWriter have received the commands
          state_next <= RUNNING;
        end if;

      when RUNNING =>
        stat_done <= '0';
        stat_busy <= '1';
        stat_idle <= '0';
        ap_start <= '1';

        if ap_done = '1' then
          -- Count the record
          total_counter_next <= total_counter + 1;
          if ap_return(0) = '1' then
              pass_counter_next <= pass_counter + 1;
          end if;

          -- Wait for last element from Kernel
          if ff_out_pkid_V_last = '1' then --TODO generate
            state_next <= DONE;
          end if;
        end if;

      when DONE =>
        stat_done <= '1';
        stat_busy <= '0';
        stat_idle <= '1';

      when others =>
        stat_done <= '0';
        stat_busy <= '0';
        stat_idle <= '0';
    end case;
  end process;


  state_p: process (kcd_clk)
  begin
    -- Control state machine
    if rising_edge(kcd_clk) then
      if kcd_reset = '1' or ctrl_reset = '1' then
        state <= RESET;
        pass_counter <= (others => '0');
        total_counter <= (others => '0');
      else
        state <= state_next;
        pass_counter <= pass_counter_next;
        total_counter <= total_counter_next;
      end if;
    end if;
  end process;

end architecture;
