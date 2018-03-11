from unittest import TestCase, TestSuite, TextTestRunner, TestResult, makeSuite
from organize import get_file_paths_table, create_subdirectories, organize
from tests.utils import generate_files
import shutil, os


class TestOrganizingNoFiles(TestCase):
    def test_invalid_path(self):
        with self.assertRaises(FileNotFoundError):
            get_file_paths_table("pathThatDoesNotExists")

    def test_empty_dir(self):
        try:
            os.mkdir("emptyDir")
        except:
            pass
        self.assertEqual(get_file_paths_table("emptyDir"), {})
        self.assertEqual(create_subdirectories("emptyDir", {}), 0)
        os.removedirs("emptyDir")


class TestOrganizeSingleFile(TestCase):
    def setUp(self):
        generate_files("testDir", "ENEE408A_HOMEWORK1_")

    def test_get_file_paths_table(self):
        actual = get_file_paths_table("testDir")
        expected = {
            "ENEE408A/HOMEWORK1": {
                "ENEE408A_HOMEWORK1_0.txt"
            }
        }
        self.assertDictEqual(actual, expected)

    def test_directory_creation(self):
        table = get_file_paths_table("testDir")
        create_subdirectories("testDir", table)
        cwd = os.getcwd()
        self.assertTrue(os.path.exists(os.path.join(cwd, "testDir", "ENEE408A", "HOMEWORK1")))
        self.assertTrue(os.path.isdir(os.path.join(cwd, "testDir", "ENEE408A", "HOMEWORK1")))

    def test_organize_same_loc(self):
        organize("testDir", "testDir")
        cwd = os.getcwd()
        expected = os.path.join(cwd, "testDir", "ENEE408A", "HOMEWORK1", "ENEE408A_HOMEWORK1_0.txt")
        self.assertTrue(os.path.isfile(expected))

    def test_organize_diff_loc(self):
        organize("testDir", "newTestDir")
        cwd = os.getcwd()
        expected = os.path.join(cwd, "newTestDir", "ENEE408A", "HOMEWORK1", "ENEE408A_HOMEWORK1_0.txt")
        self.assertTrue(os.path.isfile(expected))

    def tearDown(self):
        shutil.rmtree("testDir")
        if os.path.isdir(os.path.join(os.getcwd(), "newTestDir")):
            shutil.rmtree("newTestDir")


class TestOrganizeManyFiles(TestCase):
    def setUp(self):
        generate_files("testDirMany", "ENEE408A_HOMEWORK1_", 10)

    def test_get_file_paths_table(self):
        actual = get_file_paths_table("testDirMany")
        expected = {
            "ENEE408A/HOMEWORK1": {
                "ENEE408A_HOMEWORK1_0.txt",
                "ENEE408A_HOMEWORK1_1.txt",
                "ENEE408A_HOMEWORK1_2.txt",
                "ENEE408A_HOMEWORK1_3.txt",
                "ENEE408A_HOMEWORK1_4.txt",
                "ENEE408A_HOMEWORK1_5.txt",
                "ENEE408A_HOMEWORK1_6.txt",
                "ENEE408A_HOMEWORK1_7.txt",
                "ENEE408A_HOMEWORK1_8.txt",
                "ENEE408A_HOMEWORK1_9.txt"
            }
        }
        self.assertDictEqual(actual, expected)

    def test_dir_creation(self):
        table = get_file_paths_table("testDirMany")
        cwd = os.getcwd()
        create_subdirectories("testDirMany", table)
        self.assertTrue(os.path.exists(os.path.join(cwd, "testDirMany", "ENEE408A", "HOMEWORK1")))
        self.assertTrue(os.path.isdir(os.path.join(cwd, "testDirMany", "ENEE408A", "HOMEWORK1")))

    def test_organize_same_dir(self):
        table = get_file_paths_table("testDirMany")
        organize("testDirMany", "testDirMany")
        base_path = os.path.join(os.getcwd(), "testDirMany", "ENEE408A", "HOMEWORK1")
        for files in table.values():
            for file in files:
                path = os.path.join(base_path, file)
                self.assertTrue(os.path.exists(path))
                self.assertTrue(os.path.isfile(path))

    def test_organize_diff_dir(self):
        table = get_file_paths_table("testDirMany")
        organize("testDirMany", "newTestDirMany")
        base_path = os.path.join(os.getcwd(), "newTestDirMany", "ENEE408A", "HOMEWORK1")
        for files in table.values():
            for file in files:
                path = os.path.join(base_path, file)
                self.assertTrue(os.path.exists(path))
                self.assertTrue(os.path.isfile(path))

    def test_organize_multiple_subdir(self):
        generate_files("testDirMany", "ENEE408A_HOMEWORK2_", numFiles=10)
        table = get_file_paths_table("testDirMany")
        organize("testDirMany", "testDirMany")
        base_path = os.path.join(os.getcwd(), "testDirMany")
        for path, files in table.items():
            subdir_path = os.path.join(base_path, path)
            for file in files:
                file_path = os.path.join(subdir_path, file)
                self.assertTrue(os.path.exists(file_path))
                self.assertTrue(os.path.isfile(file_path))

    def tearDown(self):
        shutil.rmtree("testDirMany")
        if os.path.isdir("newTestDirMany"):
            shutil.rmtree("newTestDirMany")


if __name__ == "__main__":
    if __name__ == '__main__':
        suite = TestSuite()
        result = TestResult()
        runner = TextTestRunner()
        suite.addTest(makeSuite(TestOrganizingNoFiles))
        suite.addTest(makeSuite(TestOrganizeSingleFile))
        suite.addTest(makeSuite(TestOrganizeManyFiles))
        print(runner.run(suite))