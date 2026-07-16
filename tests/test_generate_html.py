import pathlib
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
PYTHON = r"C:/Python314/python.exe"


class GeneratedHtmlTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([PYTHON, "generate_html.py"], cwd=ROOT, check=True)
        cls.html = (ROOT / "itinerary.html").read_text(encoding="utf-8")

    def test_inlines_core_and_service_library(self):
        self.assertIn("root.ItineraryCore", self.html)
        self.assertIn("libraries=service", self.html)

    def test_base_points_have_stable_ids_and_positions(self):
        self.assertIn("const BASE_POIS", self.html)
        self.assertIn('"id": "seed-1-1"', self.html)
        self.assertIn('"position": 1', self.html)

    def test_route_has_numbered_pins_and_arrows(self):
        self.assertIn("buildNumberedPinSvg", self.html)
        self.assertIn("styles[p.id] = new TMap.MarkerStyle({", self.html)
        self.assertIn("showArrow: true", self.html)
        self.assertIn("arrowOptions: { width: 8, height: 5, space: 60 }", self.html)

    def test_render_map_handles_zero_and_one_point_days(self):
        self.assertIn("if (list.length === 0)", self.html)
        self.assertIn("if (list.length === 1)", self.html)

    def test_render_map_closes_info_window_before_empty_day_returns(self):
        render_map = self.html.split("function renderMap(d, list){", 1)[1].split(
            "function selectDay(d){", 1)[0]
        close_info = "if (infoWin) { infoWin.close(); infoWin = null; }"
        self.assertIn(close_info, render_map)
        self.assertLess(
            render_map.index(close_info),
            render_map.index("if (list.length === 0)"),
        )

    def test_generator_works_from_project_parent_directory(self):
        subprocess.run([PYTHON, "static-itinerary-editor/generate_html.py"],
                       cwd=ROOT.parent, check=True)
        self.assertTrue((ROOT / "itinerary.html").is_file())


if __name__ == "__main__":
    unittest.main()
