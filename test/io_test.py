import unittest
import codes.utils.tools.io_tool as uio
import geopandas as gpd


class MyTestCase(unittest.TestCase):
    def test_something(self):
        for region in ["world", "china", "usa", "europe"]:
            boundary = uio.load_boundary(region)

            self.assertEqual(isinstance(boundary, gpd.GeoDataFrame), True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
