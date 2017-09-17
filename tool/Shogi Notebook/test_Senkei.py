import unittest
from Senkei import Senkei
from Senkei import SenkeiClassify
from Kifu import Kifu

debug = False


def make_kifu_list(kifu_sfen):
    return kifu_sfen.split(" ")


def large_test(move_list) -> SenkeiClassify:
    kifu = Kifu()
    senkei = Senkei(debug)

    for i, move in enumerate(move_list):
        m_d = kifu.move(move)
        senkei.move(m_d, i+1)
    senkei.get_large_classification()
    return senkei.senkei_classify


class DoubleStaticRookTest(unittest.TestCase):
    def test_1(self):
        kifu_sfen = "7g7f 8c8d 2g2f 8d8e 8h7g 4a3b 6i7h 3c3d 7i6h 2b7g+ " +\
                    "6h7g 3a2b 3i3h 7a6b 5i6h 5a4b 4g4f 9c9d 9g9f 1c1d 1g1f 6c6d 3h4g 6b6c 3g3f 7c7d 4g5f 6c5d"
        result = large_test(make_kifu_list(kifu_sfen))
        self.assertEqual("相居飛車", result.kingdom)
        self.assertEqual("角換わり", result.phylum)

    def test_2(self):
        kifu_sfen = "2g2f 8c8d 2f2e 8d8e 6i7h 4a3b 2e2d 2c2d 2h2d P*2c " +\
                    "2d2h 7a7b 3i3h 9c9d 3h2g 8e8f 8g8f 8b8f P*8g 8f8d 2g3f"
        result = large_test(make_kifu_list(kifu_sfen))
        self.assertEqual("相居飛車", result.kingdom)
        self.assertEqual("相掛かり", result.phylum)

    def test_3(self):
        kifu_sfen = "2g2f 8c8d 7g7f 3c3d 2f2e 8d8e 6i7h 4a3b 2e2d 2c2d 2h2d 8e8f 8g8f " +\
                    "8b8f 2d3d 2b3c 3d3f 3a2b 3f2f 8f8d P*8g 5a5b 5i5h"
        result = large_test(make_kifu_list(kifu_sfen))
        self.assertEqual("相居飛車", result.kingdom)
        self.assertEqual("横歩取り", result.phylum)

    def test_4(self):
        kifu_sfen = "7g7f 8c8d 7i6h 3c3d 6h7g 7a6b 5g5f 3a4b 3i4h 5c5d 6i7h 4a3b 4i5h 5a4a " +\
                    "5i6i 6a5b 6g6f 4b3c 5h6g 2b3a 3g3f 3a6d 4h3g 4c4d 8h7i 5b4c 7i6h 4a3a 6i7i 3a2b 7i8h 7c7d"
        result = large_test(make_kifu_list(kifu_sfen))
        self.assertEqual("相居飛車", result.kingdom)
        self.assertEqual("矢倉", result.phylum)
        self.assertEqual("相矢倉", result.subphylum)


class BlackRangingRookTest(unittest.TestCase):
    def test_1(self):
        kifu_sfen = "7g7f 3c3d 2h6h 8c8d 5i4h 8d8e 8h2b+ 3a2b 7i8h 5a4b 8h7g 4b3b"
        result = large_test(make_kifu_list(kifu_sfen))
        self.assertEqual("先手振り飛車", result.kingdom)
        self.assertEqual("先手角交換四間飛車", result.phylum)

    def test_2(self):
        kifu_sfen = "7g7f 2c2d 6g6f 8c8d 7i6h 8d8e 8h7g 7a6b 6h6g 5a4b 2h6h 4b3b 5i4h 5c5d 6i5h 6a5b"
        result = large_test(make_kifu_list(kifu_sfen))
        self.assertEqual("先手振り飛車", result.kingdom)
        self.assertEqual("先手ノーマル四間飛車", result.phylum)


class WhiteRangingRookTest(unittest.TestCase):
    def test_1(self):
        kifu_sfen = "7g7f 3c3d 2g2f 2b8h+ 7i8h 3a4b 2f2e 4b3c 3i4h 8b2b B*6e B*7d 6e4c+ " + \
                    "4a4b 4c6a 5a6a G*7e 6a7b 5i6h"
        result = large_test(make_kifu_list(kifu_sfen))
        self.assertEqual("後手振り飛車", result.kingdom)
        self.assertEqual("後手角交換向かい飛車", result.phylum)


class DoubleRangingRookTest(unittest.TestCase):
    def test_1(self):
        kifu_sfen = "7g7f 3c3d 7f7e 2b3c 2h7h 8b2b 5i4h 5a6b 4h3h 6b7b 3h2h 7a8b 3i3h 6a6b 6i5h 4a5b"
        result = large_test(make_kifu_list(kifu_sfen))
        self.assertEqual("相振り飛車", result.kingdom)
        self.assertEqual("先手三間飛車後手向かい飛車", result.phylum)


if __name__ == '__main__':
    unittest.main()
