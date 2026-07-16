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

    def test_persistence_api_uses_versioned_local_storage(self):
        self.assertIn("const STORAGE_KEY = 'itinerary-editor-state-v1';", self.html)
        self.assertIn("function loadState()", self.html)
        self.assertIn("function saveState(points)", self.html)
        self.assertIn("schemaVersion: 1", self.html)
        self.assertIn("localStorage.setItem(STORAGE_KEY", self.html)
        self.assertIn("try {", self.html)
        self.assertIn("return false;", self.html)

    def test_transfer_and_reset_controls_are_present(self):
        for control in ("addPointBtn", "exportBtn", "importInput", "resetBtn", "saveStatus"):
            self.assertIn('id="' + control + '"', self.html)
        self.assertIn("function exportJson()", self.html)
        self.assertIn("function importJson(file)", self.html)
        self.assertIn("function resetToBase()", self.html)

    def test_import_validates_before_replacing_points(self):
        import_fn = self.html.split("function importJson(file)", 1)[1].split(
            "function resetToBase()", 1
        )[0]
        self.assertIn("ItineraryCore.parseImport", import_fn)
        self.assertLess(import_fn.index("ItineraryCore.parseImport"),
                        import_fn.index("POIS ="))
        self.assertIn("confirm(", import_fn)
        self.assertIn("catch", import_fn)

    def test_export_downloads_blob_and_releases_url(self):
        export_fn = self.html.split("function exportJson()", 1)[1].split(
            "function importJson(file)", 1
        )[0]
        self.assertIn("new Blob", export_fn)
        self.assertIn("URL.createObjectURL", export_fn)
        self.assertIn("download", export_fn)
        self.assertIn("URL.revokeObjectURL", export_fn)

    def test_reset_removes_saved_state_and_rerenders(self):
        reset_fn = self.html.split("function resetToBase()", 1)[1].split(
            "function boot()", 1
        )[0]
        self.assertIn("localStorage.removeItem(STORAGE_KEY)", reset_fn)
        self.assertIn("BASE_POIS", reset_fn)
        self.assertIn("selectDay(curDay)", reset_fn)

    def test_map_styles_follow_rendered_points_and_empty_itinerary_has_default_center(self):
        marker_styles = self.html.split("function markerStyles(", 1)[1].split(
            "function polylineStyle()", 1
        )[0]
        init_map = self.html.split("function initMap(){", 1)[1].split(
            "function renderTimeline", 1
        )[0]
        render_map = self.html.split("function renderMap(d, list){", 1)[1].split(
            "function selectDay(d){", 1
        )[0]
        self.assertIn("points.forEach", marker_styles)
        self.assertNotIn("BASE_POIS.forEach", marker_styles)
        self.assertIn("POIS[0] ||", init_map)
        self.assertIn("multiMarker.setStyles(markerStyles(list))", render_map)

    def test_import_rolls_back_points_and_exact_storage_snapshot_after_late_failure(self):
        import_fn = self.html.split("function importJson(file)", 1)[1].split(
            "function resetToBase()", 1
        )[0]
        self.assertIn("previousStored = localStorage.getItem(STORAGE_KEY)", import_fn)
        self.assertIn("restoreStoredState(previousStored)", import_fn)
        self.assertIn("POIS = previous", import_fn)
        self.assertLess(import_fn.index("saveState(POIS)"),
                        import_fn.index("document.getElementById('bPoi')"))

    def test_reset_does_not_mutate_points_before_storage_removal_succeeds(self):
        reset_fn = self.html.split("function resetToBase()", 1)[1].split(
            "function boot()", 1
        )[0]
        self.assertIn("try {", reset_fn)
        self.assertIn("catch", reset_fn)
        self.assertIn("恢复失败", reset_fn)
        self.assertLess(reset_fn.index("localStorage.removeItem(STORAGE_KEY)"),
                        reset_fn.index("POIS ="))

    def test_export_revokes_object_url_in_finally(self):
        export_fn = self.html.split("function exportJson()", 1)[1].split(
            "function importJson(file)", 1
        )[0]
        self.assertIn("finally", export_fn)
        self.assertLess(export_fn.index("finally"),
                        export_fn.index("URL.revokeObjectURL"))


if __name__ == "__main__":
    unittest.main()
