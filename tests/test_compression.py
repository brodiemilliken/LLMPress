import unittest
from src.compressor import compress
from src.decompressor import decompress

class TestCompression(unittest.TestCase):

    def setUp(self):
        self.sample_file = 'tests/samples/sample.txt'
        self.compressed_file = 'tests/samples/sample_compressed.txt'
        self.decompressed_file = 'tests/samples/sample_decompressed.txt'

    def test_compression(self):
        compress(self.sample_file, self.compressed_file)
        # Check if the compressed file is created
        self.assertTrue(os.path.exists(self.compressed_file))

    def test_decompression(self):
        compress(self.sample_file, self.compressed_file)
        decompress(self.compressed_file, self.decompressed_file)
        # Check if the decompressed file is created
        self.assertTrue(os.path.exists(self.decompressed_file))
        
        # Verify that the decompressed content matches the original
        with open(self.sample_file, 'r') as original, open(self.decompressed_file, 'r') as decompressed:
            self.assertEqual(original.read(), decompressed.read())

if __name__ == '__main__':
    unittest.main()