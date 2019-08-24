import unittest

import os
import sys

from tests.model.psse.test_psse_model import TestPSSEModel
from tests.model.opendss.model.test_opendss_interface import TestOpenDSSInterface
from tests.model.opendss.model.pvderaggregation.model.test_pvder_aggregated_model import TestPVDERAggregatedModel
from tests.model.opendss.model.pvderaggregation.model.test_pvder_model import TestPVDERModel


def suite():
    """Define a test suite.
    TODO: Include the procedure test
    """ 
    

    suite = unittest.TestSuite()
    
    
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestPSSEModel))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestOpenDSSInterface))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestPVDERAggregatedModel))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestPVDERModel))
    
                                               
    return suite

if __name__ == '__main__':
        
    runner = unittest.TextTestRunner()
    runner.run(suite())
