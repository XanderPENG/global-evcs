import unittest
import codes.utils.tools.plot_tool as pt
import codes.utils.tools.io_tool as uio
import os.path as path


class MyTestCase(unittest.TestCase):
    def test_something(self):
        pt.plot_worldmap()
        upath = uio.global_output_path + "plots/worldmap.png"
        self.assertEqual(path.exists(upath), True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
