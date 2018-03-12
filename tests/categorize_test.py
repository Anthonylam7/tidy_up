from categorize import parse_config_dict, create_file_table
from .utils import generate_files
from unittest import TestCase, TestResult, TestSuite, TextTestRunner, makeSuite
import os, shutil


class CategorizeBaseCase(TestCase):
    def test_parse_config_dict(self):
        d = {
            "music": [".mp3", ".wav", ".midi", ".mid"]
        }
        expected = {
            ".mp3": "music",
            ".wav": "music",
            ".midi": "music",
            ".mid": "music"
        }
        actual = parse_config_dict(d)
        self.assertDictEqual(actual, expected)

    def test_invalid_parse_inputs(self):
        with self.assertRaises(TypeError):
            parse_config_dict({"This": "should fail"})
            parse_config_dict("This should fail")


class CatergorizeSingleFileTest(TestCase):
    def setUp(self):
        generate_files("testDir", "testFile")

    def test_create_table(self):
        expected = {"document": {"testFile0.txt"}}
        actual = create_file_table("testDir", {".txt": "document"})
        self.assertDictEqual(expected, actual)

    def tearDown(self):
        shutil.rmtree("testDir")
        pass


class CategorizeMultipleFileCase(TestCase):
    def setUp(self):
        test_dir = "testDir"
        generate_files(test_dir, "audioFile", extension="mp3", numFiles=2)
        generate_files(test_dir, "notes", numFiles=2)
        generate_files(test_dir, "pic", extension="png", numFiles=2)

    def test_create_table(self):
        mapping = {
            ".txt": "documents",
            ".mp3": "audio",
            ".png": "images"
        }
        expected = {
            "images": {"pic0.png", "pic1.png"},
            "documents": {"notes0.txt", "notes1.txt"},
            "audio": {"audioFile0.mp3", "audioFile1.mp3"}
        }
        actual = create_file_table("testDir", mapping)

    def tearDown(self):
        shutil.rmtree("testDir")


if __name__ == "__main__":
    suite = TestSuite()
    result =TestResult()
    suite.addTest(makeSuite(CategorizeBaseCase))
    suite.addTest(makeSuite(CatergorizeSingleFileTest))
    print(TextTestRunner().run(suite))