from categorize import reverse_dict_kv, create_file_table, categorize
from .utils import generate_files
from unittest import TestCase, TestResult, TestSuite, TextTestRunner, makeSuite
import os, shutil

import logging
logging.disable(logging.CRITICAL)

class UtilityFunctionTest(TestCase):
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
        actual = reverse_dict_kv(d)
        self.assertDictEqual(actual, expected)

    def test_invalid_parse_inputs(self):
        with self.assertRaises(TypeError):
            reverse_dict_kv({"This": "should fail"})
            reverse_dict_kv("This should fail")


class CatergorizeSingleFileCase(TestCase):
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
        generate_files(test_dir, "clips", extension="avi", numFiles=2)

    def test_create_table(self):
        mapping = {
            ".txt": "documents",
            ".mp3": "audio",
            ".png": "images",
            ".avi": "videos"
        }
        expected = {
            "images": {"pic0.png", "pic1.png"},
            "documents": {"notes0.txt", "notes1.txt"},
            "audio": {"audioFile0.mp3", "audioFile1.mp3"},
            "videos": {"clips0.avi", "clips1.avi"}
        }
        actual = create_file_table("testDir", mapping)

    def test_categorize(self):
        categorize("testDir", "testDirDest")
        self.assertTrue(os.path.exists(os.path.join("testDirDest", "media", "images")))

    def test_categorize_duplicates(self):
        test_dir = "testDir"
        categorize(test_dir, "testDirDest")
        generate_files(test_dir, "audioFile", extension="mp3", numFiles=2)
        generate_files(test_dir, "notes", numFiles=2)
        generate_files(test_dir, "pic", extension="png", numFiles=2)
        generate_files(test_dir, "clips", extension="avi", numFiles=2)
        files_before = os.listdir("testDir")
        categorize(test_dir, "testDirDest")
        files_after = os.listdir("testDir")
        # duplicates should note overwrite
        self.assertEqual(files_before, files_after)

    def test_categorize_existing_dir(self):
        test_dir = "testDir"
        categorize(test_dir, "testDirDest")
        generate_files(test_dir, "newAudioFile", extension="mp3", numFiles=2)
        generate_files(test_dir, "newNotes", numFiles=2)
        generate_files(test_dir, "newPic", extension="png", numFiles=2)
        generate_files(test_dir, "newClips", extension="avi", numFiles=2)
        categorize(test_dir, "testDirDest")
        audioPath = os.path.join("testDirDest", "media", "images")
        num_files = len(os.listdir(audioPath))
        self.assertEqual(num_files, 4)


    def tearDown(self):
        shutil.rmtree("testDir")
        if os.path.exists("testDirDest"):
            shutil.rmtree("testDirDest")


class CategorizeNestedDirectoryCase(TestCase):
    def setUp(self):
        self.testPath = "testDir"
        self.config = {
            "EXTENSION": {
                "dir0": {".nest"}
            },
            "DIRECTORY": {
                "dir1": {"dir0"},
                "dir2": {"dir1"},
                "dir3": {"dir2"},
                "dir4": {"dir3"},
                "dir5": {"dir4"}
            }
        }
        generate_files(self.testPath, "nestFile", extension="nest")

    def test_categorize_nested(self):
        categorize(self.testPath, self.testPath, config_dict=self.config)
        path = os.path.join(self.testPath, *["dir"+str(i) for i in range(5, -1, -1)])
        self.assertTrue(os.path.exists(path))
        self.assertTrue(os.path.isdir(path))

    def tearDown(self):
        shutil.rmtree(self.testPath)


if __name__ == "__main__":
    suite = TestSuite()
    result =TestResult()
    suite.addTest(makeSuite(UtilityFunctionTest))
    suite.addTest(makeSuite(CatergorizeSingleFileCase))
    suite.addTest(makeSuite(CategorizeMultipleFileCase))
    suite.addTest(makeSuite(CategorizeNestedDirectoryCase))
    print(TextTestRunner().run(suite))