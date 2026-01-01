from os.path import join

import pytest

from hdx.utilities.zip_crc import (
    find_eocd_signature,
    get_crc_sum,
    get_zip_cd_header,
    get_zip_crcs_buffer,
    get_zip_crcs_fp,
    get_zip_tail_header,
    parse_central_directory,
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

    def test_get_zip_tail_header(self):
        assert get_zip_tail_header(65535) == {"Range": "bytes=0-"}
        assert get_zip_tail_header(1000000) == {"Range": "bytes=934443-"}

    def test_get_zip_cd_header(self, shpfile, xlsxfile):
        with open(shpfile, "rb") as fp:
            data = fp.read()
            assert get_zip_cd_header(data) == (7, {"Range": "bytes=1329685-1330507"})

        with open(xlsxfile, "rb") as fp:
            data = fp.read()
            assert get_zip_cd_header(data) == (18, {"Range": "bytes=12423-13704"})

        assert get_zip_cd_header(b"") == (-1, {})

    def test_get_zip_crcs_buffer(self, shpfile):
        with open(shpfile, "rb") as fp:
            data = fp.read()
            assert get_zip_crcs_buffer(data) == self.expected_crcs
        assert get_zip_crcs_buffer(b"") == {}

    def test_get_zip_crcs_fp(self, shpfile, emptyfile):
        with open(shpfile, "rb") as fp:
            assert get_zip_crcs_fp(fp) == self.expected_crcs

        with open(emptyfile, "rb") as fp:
            assert get_zip_crcs_fp(fp) == {}

    def test_get_crc_sum(self):
        assert get_crc_sum(self.expected_crcs) == "31662cb7"
        assert get_crc_sum({}) == ""

    def test_parse_central_directory(self, shpfile):
        with open(shpfile, "rb") as fp:
            data = fp.read()
            total_records, cd_offset, cd_end = find_eocd_signature(data)
            assert parse_central_directory(data, total_records + 1) == {}
        assert parse_central_directory(b"", 1) == {}
