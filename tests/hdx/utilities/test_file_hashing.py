from os.path import join

import pytest

from hdx.utilities.file_hashing import (
    crc_zip_buffer,
    crc_zip_fp,
    get_size_and_hash,
    hash_excel_fp,
)


class TestZipCRC:
    expected_crcs = {
        "GHSL2_0_MWD_L1_tile_schema_land.cpg": 243350608,
        "GHSL2_0_MWD_L1_tile_schema_land.dbf": 3146933286,
        "GHSL2_0_MWD_L1_tile_schema_land.prj": 3172151860,
        "GHSL2_0_MWD_L1_tile_schema_land.shp": 2238079868,
        "GHSL2_0_MWD_L1_tile_schema_land.shx": 1240292293,
        "GHSL2_0_MWD_L1_tile_schema_land_Readme.txt": 1146324287,
        "GHSL_Data_Package_2022_light.pdf": 2982083443,
    }

    @pytest.fixture
    def zipfolder(self, fixturesfolder):
        return join(fixturesfolder, "file_hashing")

    @pytest.fixture
    def shpfile(self, zipfolder):
        return join(zipfolder, "test_shapefile.zip")

    @pytest.fixture
    def xlsxfile(self, zipfolder):
        return join(zipfolder, "test.xlsx")

    @pytest.fixture
    def emptyfile(self, zipfolder):
        return join(zipfolder, "empty.zip")

    @pytest.fixture
    def badzipheader(self, zipfolder):
        return join(zipfolder, "bad_header.zip")

    @pytest.fixture
    def valid_sig_invalid_body(self, zipfolder):
        return join(zipfolder, "valid_sig_invalid_body.zip")

    @pytest.fixture
    def bad_index(self, zipfolder):
        return join(zipfolder, "bad_index.xlsx")

    def test_hash_excel_fp(self, xlsxfile):
        with open(xlsxfile, "rb") as fp:
            assert hash_excel_fp(fp) == "55434630784372644438afb5ee5fbc60"

    def test_crc_zip_buffer(self, shpfile):
        with open(shpfile, "rb") as fp:
            data = fp.read()
            assert crc_zip_buffer(data) == "31662cb7"

    def test_crc_zip_fp(self, shpfile):
        with open(shpfile, "rb") as fp:
            assert crc_zip_fp(fp) == "31662cb7"

    def test_get_size_and_hash(
        self,
        shpfile,
        xlsxfile,
        emptyfile,
        badzipheader,
        valid_sig_invalid_body,
        bad_index,
    ):
        assert get_size_and_hash(shpfile, "shp") == (1330530, "31662cb7")
        assert get_size_and_hash(shpfile, "zip") == (1330530, "31662cb7")
        assert get_size_and_hash(shpfile, "xlsx") == (1330530, "31662cb7")

        assert get_size_and_hash(xlsxfile, "xlsx") == (
            13727,
            "55434630784372644438afb5ee5fbc60",
        )
        assert get_size_and_hash(xlsxfile, "zip") == (
            13727,
            "aaf00484",
        )  # treat xlsx as zip

        assert get_size_and_hash(emptyfile, "zip") == (
            0,
            "d41d8cd98f00b204e9800998ecf8427e",
        )
        assert get_size_and_hash(emptyfile, "xlsx") == (
            0,
            "d41d8cd98f00b204e9800998ecf8427e",
        )

        assert get_size_and_hash(badzipheader, "zip") == (
            18,
            "139b47ff14cdcdd9f40fa41b8b02f954",
        )  # MD5 fallback
        assert get_size_and_hash(badzipheader, "xlsx") == (
            18,
            "139b47ff14cdcdd9f40fa41b8b02f954",
        )  # MD5 fallback

        assert get_size_and_hash(valid_sig_invalid_body, "zip") == (
            234,
            "cd5cb49635d192c7693059fad24f0695",
        )  # MD5 fallback
        assert get_size_and_hash(valid_sig_invalid_body, "xlsx") == (
            234,
            "cd5cb49635d192c7693059fad24f0695",
        )  # MD5 fallback

        assert get_size_and_hash(bad_index, "zip") == (
            2830,
            "9a479d24",
        )  # Treat xlsx as zip
        assert get_size_and_hash(bad_index, "xlsx") == (
            2830,
            "9a479d24",
        )  # Fallback to treat xlsx as zip
