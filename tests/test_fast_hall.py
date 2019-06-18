from tests.utils import TestWithFakeFastHall, TestWithRealFastHall


class TestResets(TestWithFakeFastHall):
    def test_reset_measurement_settings(self):
        self.fake_connection.setup_response('No error')
        self.dut.reset_measurement_settings()
        self.assertIn('SYSTEM:PRESET', self.fake_connection.get_outgoing_message())

    def test_factory_reset(self):
        self.fake_connection.setup_response('No error')
        self.dut.factory_reset()
        self.assertIn('SYSTEM:FACTORYRESET', self.fake_connection.get_outgoing_message())

    def test_contact_check_reset(self):
        self.fake_connection.setup_response('No error')
        self.dut.reset_contact_check_measurement()
        self.assertIn('CCHECK:RESET', self.fake_connection.get_outgoing_message())

    def test_fasthall_reset(self):
        self.fake_connection.setup_response('No error')
        self.dut.reset_fasthall_measurement()
        self.assertIn('FASTHALL:RESET', self.fake_connection.get_outgoing_message())

    def test_four_wire_reset(self):
        self.fake_connection.setup_response('No error')
        self.dut.reset_four_wire_measurement()
        self.assertIn('FWIRE:RESET', self.fake_connection.get_outgoing_message())

    def test_dc_hall_reset(self):
        self.fake_connection.setup_response('No error')
        self.dut.reset_dc_hall_measurement()
        self.assertIn('HALL:DC:RESET', self.fake_connection.get_outgoing_message())

    def test_resisitvity_reset(self):
        self.fake_connection.setup_response('No error')
        self.dut.reset_resistivity_measurement()
        self.assertIn('RESISTIVITY:RESET', self.fake_connection.get_outgoing_message())


class TestRunningStatusFake(TestWithFakeFastHall):
    def test_contact_check_running(self):
        self.fake_connection.setup_response('1;No error')
        response = self.dut.get_contact_check_running_status()
        self.assertAlmostEqual(response, 1)
        self.assertIn('CCHECK:RUNNING?', self.fake_connection.get_outgoing_message())

    def test_fasthall_running(self):
        self.fake_connection.setup_response('0;No error')
        response = self.dut.get_fasthall_running_status()
        self.assertAlmostEqual(response, 0)
        self.assertIn('FASTHALL:RUNNING?', self.fake_connection.get_outgoing_message())

    def test_four_wire_running(self):
        self.fake_connection.setup_response('1;No error')
        response = self.dut.get_four_wire_running_status()
        self.assertAlmostEqual(response, 1)
        self.assertIn('FWIRE:RUNNING?', self.fake_connection.get_outgoing_message())

    def test_dc_hall_running(self):
        self.fake_connection.setup_response('0;No error')
        response = self.dut.get_dc_hall_running_status()
        self.assertAlmostEqual(response, 0)
        self.assertIn('HALL:DC:RUNNING?', self.fake_connection.get_outgoing_message())

    def test_resistivity_running(self):
        self.fake_connection.setup_response('1;No error')
        response = self.dut.get_resistivity_running_status()
        self.assertAlmostEqual(response, 1)
        self.assertIn('RESISTIVITY:RUNNING?', self.fake_connection.get_outgoing_message())


class TestContactCheckRun(TestWithFakeFastHall):
    def test_contact_check_auto_default_parameters(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_contact_check_vdp_auto()
        self.assertIn('CCHECK:START', self.fake_connection.get_outgoing_message())

    def test_contact_check_auto_mixed_parameter(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_contact_check_vdp_auto(number_of_points=13)
        self.assertIn('CCHECK:START DEF,DEF,13,DEF', self.fake_connection.get_outgoing_message())

    def test_contact_check_auto_non_default(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_contact_check_vdp_auto(max_current=50e-3, max_voltage=5, number_of_points=50,
                                            min_r_squared=0.9899)
        self.assertIn('CCHECK:START 0.05,5,50,0.9899', self.fake_connection.get_outgoing_message())

    def test_contact_check_manual_default(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_contact_check_vdp_manual(excitation_type='VOLTAGE', excitation_value_start=-5,
                                              excitation_value_end=5, compliance_limit=10e-3, number_of_points=25)
        self.assertIn('CCHECK:START:MANUAL VOLTAGE,-5,5,AUTO,AUTO,0.01,25',
                      self.fake_connection.get_outgoing_message())

    def test_contact_check_manual_mixed_parameters(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_contact_check_vdp_manual(excitation_type='CURRENT', excitation_value_start=-10e-3,
                                              excitation_value_end=10e-3, excitation_range='AUTO',
                                              measurement_range='AUTO', compliance_limit=1.5, number_of_points=20,
                                              blanking_time='MAX')
        self.assertIn('CCHECK:START:MANUAL CURRENT,-0.01,0.01,AUTO,AUTO,1.5,20,DEF,MAX',
                      self.fake_connection.get_outgoing_message())

    def test_contact_check_manual_non_default(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_contact_check_vdp_manual(excitation_type='CURRENT', excitation_value_start=-10e-6,
                                              excitation_value_end=10e-6, excitation_range=10e-6,
                                              measurement_range=100e-3, compliance_limit=5, number_of_points=50,
                                              min_r_squared=0.9799, blanking_time=3)
        self.assertIn('CCHECK:START:MANUAL CURRENT,-1e-05,1e-05,1e-05,0.1,5,50,0.9799,3',
                      self.fake_connection.get_outgoing_message())

    def test_contact_check_hbar_default(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_contact_check_hbar(excitation_type='VOLTAGE', excitation_value_start=-5,
                                        excitation_value_end=5,
                                        compliance_limit=10e-3, number_of_points=50)
        self.assertIn('CCHECK:HBAR:START VOLTAGE,-5,5,AUTO,AUTO,0.01,50',
                      self.fake_connection.get_outgoing_message())

    def test_contact_check_hbar_non_default(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_contact_check_hbar(excitation_type='CURRENT', excitation_value_start=-10e-6,
                                        excitation_value_end=10e-6, excitation_range=10e-6,
                                        measurement_range=100e-3,
                                        compliance_limit=1.5, number_of_points=20, min_r_squared=0.9899,
                                        blanking_time='MIN')
        self.assertIn('CCHECK:HBAR:START CURRENT,-1e-05,1e-05,1e-05,0.1,1.5,20,0.9899,MIN',
                      self.fake_connection.get_outgoing_message())


class TestFastHallRun(TestWithFakeFastHall):
    def test_run_fasthall_vdp_default_parameters(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_fasthall_vdp(excitation_type='VOLTAGE', excitation_value=1, compliance_limit=10e-6,
                                  user_defined_field=0.5)
        self.assertIn('FASTHALL:START VOLTAGE,1,AUTO,AUTO,AUTO,1e-05,0.5',
                      self.fake_connection.get_outgoing_message())

    def test_run_fasthall_vdp_mixed_parameters(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_fasthall_vdp(excitation_type='CURRENT', excitation_value=10e-3, excitation_range='AUTO',
                                  excitation_measurement_range='AUTO', measurement_range='AUTO', compliance_limit=1.5,
                                  user_defined_field=0.5, max_number_of_samples=200, blanking_time='MAX')
        self.assertIn('FASTHALL:START CURRENT,0.01,AUTO,AUTO,AUTO,1.5,0.5,200,DEF,MAX,DEF,DEF,DEF',
                      self.fake_connection.get_outgoing_message())

    def test_run_fasthall_vdp_non_default(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_fasthall_vdp(excitation_type='CURRENT', excitation_value=10e-3, excitation_range=20e-3,
                                  excitation_measurement_range=30e-3, measurement_range=40e-3, compliance_limit=1.5,
                                  user_defined_field=0.5, max_number_of_samples=200, resistivity=0.216,
                                  blanking_time='MIN', number_of_averaging_voltage_samples=100, sample_thickness=5e-3,
                                  min_hall_voltage_snr=500)
        self.assertIn('FASTHALL:START CURRENT,0.01,0.02,0.03,0.04,1.5,0.5,200,0.216,MIN,100,0.005,500',
                      self.fake_connection.get_outgoing_message())

    def test_run_fasthall_vdp_link_default_parameters(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_fasthall_vdp_link(user_defined_field=0.5)
        self.assertIn('FASTHALL:START:LINK 0.5', self.fake_connection.get_outgoing_message())

    def test_run_fasthall_vdp_link_mixed_parameters(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_fasthall_vdp_link(user_defined_field=0.5, number_of_averaging_voltage_samples=100)
        self.assertIn('FASTHALL:START:LINK 0.5,DEF,DEF,DEF,100,DEF', self.fake_connection.get_outgoing_message())

    def test_run_fasthall_vdp_link_non_default(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_fasthall_vdp_link(user_defined_field=0.5, measurement_range=10e-3, max_number_of_samples=500,
                                       min_hall_voltage_snr=50, number_of_averaging_voltage_samples=100,
                                       sample_thickness=2e-3)
        self.assertIn('FASTHALL:START:LINK 0.5,0.01,500,50,100,0.002', self.fake_connection.get_outgoing_message())


class TestFourWireRun(TestWithFakeFastHall):
    def test_run_four_wire_default_parameters(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_four_wire(contact_point1=1, contact_point2=2, contact_point3=3, contact_point4=4,
                               excitation_type='CURRENT', excitation_value=10e-3, compliance_limit=1.5)
        self.assertIn('FWIRE:START 1,2,3,4,CURRENT,0.01,AUTO,AUTO,AUTO,1.5',
                      self.fake_connection.get_outgoing_message())

    def test_run_four_wire_mixed_parameters(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_four_wire(contact_point1=5, contact_point2=6, contact_point3=3, contact_point4=1,
                               excitation_type='CURRENT', excitation_value=500e-6, excitation_range=1e-3,
                               measurement_range=1.0, excitation_measurement_range=1e-3, compliance_limit=1.5,
                               max_number_of_samples=200, excitation_reversal=False)
        self.assertIn('FWIRE:START 5,6,3,1,CURRENT,0.0005,0.001,1.0,0.001,1.5,DEF,200,DEF,0',
                      self.fake_connection.get_outgoing_message())

    def test_run_four_wire_non_default(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_four_wire(contact_point1=5, contact_point2=6, contact_point3=3, contact_point4=1,
                               excitation_type='CURRENT', excitation_value=500e-6, excitation_range=1e-3,
                               measurement_range=1.0, excitation_measurement_range=1e-3, compliance_limit=1.5,
                               blanking_time='MAX', max_number_of_samples=200, min_snr=50, excitation_reversal=False)
        self.assertIn('FWIRE:START 5,6,3,1,CURRENT,0.0005,0.001,1.0,0.001,1.5,MAX,200,50,0',
                      self.fake_connection.get_outgoing_message())


class TestDCHallRun(TestWithFakeFastHall):
    def test_run_dc_hall_vdp_default_parameters(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_dc_hall_vdp(excitation_type='CURRENT', excitation_value=10e-3, compliance_limit=1.5,
                                 number_of_samples=100, user_defined_field=0.5)
        self.assertIn('HALL:DC:START CURRENT,0.01,AUTO,AUTO,AUTO,1.5,100,0.5',
                      self.fake_connection.get_outgoing_message())

    def test_run_dc_hall_vdp_mixed_parameters(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_dc_hall_vdp(excitation_type='CURRENT', excitation_value=10e-3, excitation_range=10e-3,
                                 excitation_measurement_range=10e-3, measurement_range=1, compliance_limit=1.5,
                                 number_of_samples=100, user_defined_field=0.5, with_field_reversal=False,
                                 blanking_time='MIN', sample_thickness=0.003)
        self.assertIn('HALL:DC:START CURRENT,0.01,0.01,0.01,1,1.5,100,0.5,0,DEF,MIN,0.003',
                      self.fake_connection.get_outgoing_message())

    def test_run_dc_hall_vdp_non_default(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_dc_hall_vdp(excitation_type='CURRENT', excitation_value=10e-3, excitation_range=10e-3,
                                 excitation_measurement_range=10e-3, measurement_range=1, compliance_limit=1.5,
                                 number_of_samples=100, user_defined_field=0.5, with_field_reversal=True,
                                 resistivity=0.216, blanking_time=2.4e-3, sample_thickness=0.002)
        self.assertIn('HALL:DC:START CURRENT,0.01,0.01,0.01,1,1.5,100,0.5,1,0.216,0.0024,0.002',
                      self.fake_connection.get_outgoing_message())

    def test_run_dc_hall_hbar_default_parameters(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_dc_hall_hbar(excitation_type='CURRENT', excitation_value=10e-3, compliance_limit=1.5,
                                  number_of_samples=100, user_defined_field=0.5)
        self.assertIn('HALL:HBAR:DC:START CURRENT,0.01,AUTO,AUTO,AUTO,1.5,100,0.5',
                      self.fake_connection.get_outgoing_message())

    def test_run_dc_hall_hbar_mixed_parameters(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_dc_hall_hbar(excitation_type='CURRENT', excitation_value=10e-3, excitation_range=20e-3,
                                  excitation_measurement_range=30e-3, measurement_range=4, compliance_limit=5,
                                  number_of_samples=200, user_defined_field=0.5, resistivity=0.216, blanking_time='MAX')
        self.assertIn('HALL:HBAR:DC:START CURRENT,0.01,0.02,0.03,4,5,200,0.5,DEF,0.216,MAX,DEF',
                      self.fake_connection.get_outgoing_message())

    def test_run_dc_hall_hbar_non_default(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_dc_hall_hbar(excitation_type='CURRENT', excitation_value=10e-3, excitation_range=20e-3,
                                  excitation_measurement_range=30e-3, measurement_range=4, compliance_limit=5,
                                  number_of_samples=200, user_defined_field=0.5, with_field_reversal=0,
                                  resistivity=0.216, blanking_time=3, sample_thickness=9e-3)
        self.assertIn('HALL:HBAR:DC:START CURRENT,0.01,0.02,0.03,4,5,200,0.5,0,0.216,3,0.009',
                      self.fake_connection.get_outgoing_message())


class TestResistivityRun(TestWithFakeFastHall):
    def test_run_resistivity_vdp_default_parameters(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_resistivity_vdp(excitation_type='CURRENT', excitation_value=10e-3, compliance_limit=5)
        self.assertIn('RESISTIVITY:START CURRENT,0.01,AUTO,AUTO,AUTO,5',
                      self.fake_connection.get_outgoing_message())

    def test_run_resistivity_vdp_mixed_parameters(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_resistivity_vdp(excitation_type='VOLTAGE', excitation_value=1, excitation_range=2,
                                     excitation_measurement_range=3, measurement_range=4e-3, compliance_limit=500e-6,
                                     blanking_time='MIN', min_snr=70)
        self.assertIn('RESISTIVITY:START VOLTAGE,1,2,3,0.004,0.0005,DEF,MIN,DEF,70',
                      self.fake_connection.get_outgoing_message())

    def test_run_resistivity_vdp_non_default(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_resistivity_vdp(excitation_type='VOLTAGE', excitation_value=1, excitation_range=2,
                                     excitation_measurement_range=3, measurement_range=4e-3, compliance_limit=500e-6,
                                     max_number_of_samples=600, blanking_time=7, sample_thickness=8e-3, min_snr=90)
        self.assertIn('RESISTIVITY:START VOLTAGE,1,2,3,0.004,0.0005,600,7,0.008,90',
                      self.fake_connection.get_outgoing_message())

    def test_run_resistivity_vdp_link_default(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_resistivity_vdp_link()
        self.assertIn('RESISTIVITY:START:LINK', self.fake_connection.get_outgoing_message())

    def test_run_resistivity_vdp_link_mixed_parameters(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_resistivity_vdp_link(sample_thickness=5e-3, max_number_of_samples=500)
        self.assertIn('RESISTIVITY:START:LINK DEF,0.005,DEF,500', self.fake_connection.get_outgoing_message())

    def test_run_resistivity_vdp_link_non_default(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_resistivity_vdp_link(measurement_range=10e-3, sample_thickness=2e-3, min_snr=300,
                                          max_number_of_samples=400)
        self.assertIn('RESISTIVITY:START:LINK 0.01,0.002,300,400', self.fake_connection.get_outgoing_message())

    def test_run_resistivity_hbar_default_parameters(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_resistivity_hbar(excitation_type='CURRENT', excitation_value=10e-3, compliance_limit=5, width=1e-3,
                                      separation=2e-3)
        self.assertIn('RESISTIVITY:HBAR:START CURRENT,0.01,AUTO,AUTO,AUTO,5,0.001,0.002',
                      self.fake_connection.get_outgoing_message())

    def test_run_resistivity_hbar_mixed_parameters(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_resistivity_hbar(excitation_type='CURRENT', excitation_value=10e-3, excitation_range='AUTO',
                                      excitation_measurement_range='AUTO', measurement_range='AUTO', compliance_limit=5,
                                      width=6e-3, separation=7e-3, blanking_time='MAX', min_snr=11)
        self.assertIn('RESISTIVITY:HBAR:START CURRENT,0.01,AUTO,AUTO,AUTO,5,0.006,0.007,DEF,MAX,DEF,11',
                      self.fake_connection.get_outgoing_message())

    def test_run_resistivity_hbar_non_default(self):
        self.fake_connection.setup_response('No error')
        self.dut.run_resistivity_hbar(excitation_type='CURRENT', excitation_value=10e-3, excitation_range=20e-3,
                                      excitation_measurement_range=30e-3, measurement_range=4, compliance_limit=5,
                                      width=6e-3, separation=7e-3, max_number_of_samples=800, blanking_time=9,
                                      sample_thickness=10e-4, min_snr=11)
        self.assertIn('RESISTIVITY:HBAR:START CURRENT,0.01,0.02,0.03,4,5,0.006,0.007,800,9,0.001,11',
                      self.fake_connection.get_outgoing_message())
