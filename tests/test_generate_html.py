import pathlib
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
PYTHON = r"C:/Python314/python.exe"


class GeneratedHtmlTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([PYTHON, "generate_html.py"], cwd=ROOT, check=True)
        cls.html = (ROOT / "index.html").read_text(encoding="utf-8")

    def test_inlines_core_and_baidu_map(self):
        self.assertIn("root.ItineraryCore", self.html)
        self.assertIn("api.map.baidu.com/api?v=3.0&ak=", self.html)
        self.assertNotIn("map.qq.com", self.html)
        self.assertNotIn("libraries=service", self.html)

    def test_base_points_have_stable_ids_and_positions(self):
        self.assertIn("const BASE_POIS", self.html)
        self.assertIn('"id": "seed-1-1"', self.html)
        self.assertIn('"position": 1', self.html)

    def test_route_has_numbered_pins(self):
        self.assertIn("buildNumberedPinSvg", self.html)
        self.assertIn("new BMap.Marker", self.html)
        self.assertIn("new BMap.Icon", self.html)

    def test_map_uses_driving_routes_with_straight_fallback(self):
        self.assertIn("BMap.DrivingRoute", self.html)
        self.assertIn("function buildDrivingRoutePath(list)", self.html)
        self.assertIn("function fetchDrivingSegment(from, to)", self.html)
        self.assertIn("buildDrivingRoutePath(list)", self.html)
        self.assertIn("straightSegment", self.html)
        self.assertIn("polylineWithArrows", self.html)
        self.assertIn("BMap.IconSequence", self.html)
        self.assertIn("路线计算中", self.html)
        self.assertIn("驾车路线", self.html)

    def test_day67_includes_heishan_and_yantai_fillers(self):
        self.assertIn("大黑山岛", self.html)
        self.assertIn("南山公园", self.html)
        self.assertIn("西炮台", self.html)
        self.assertIn("门票：免费", self.html)
        self.assertIn("门票约¥", self.html)
        self.assertIn("养马岛+蓬莱+大黑山", self.html)

    def test_day_switch_fits_map_to_current_points(self):
        self.assertIn("function fitMapToPoints(list)", self.html)
        self.assertIn("function scheduleFitMapToPoints(list)", self.html)
        render_map = self.html.split("function renderMap(d, list){", 1)[1].split(
            "function selectDay(d){", 1
        )[0]
        self.assertIn("scheduleFitMapToPoints(list)", render_map)
        fit_fn = self.html.split("function fitMapToPoints(list)", 1)[1].split(
            "function scheduleFitMapToPoints", 1
        )[0]
        self.assertIn("map.setViewport", fit_fn)
        self.assertIn("margins: [80, 80, 80, 80]", fit_fn)

    def test_render_map_handles_zero_and_one_point_days(self):
        fit_fn = self.html.split("function fitMapToPoints(list)", 1)[1].split(
            "function scheduleFitMapToPoints", 1
        )[0]
        self.assertIn("list.length === 0", fit_fn)
        self.assertIn("list.length === 1", fit_fn)

    def test_render_map_clears_overlays_before_fit(self):
        render_map = self.html.split("function renderMap(d, list){", 1)[1].split(
            "function selectDay(d){", 1)[0]
        self.assertIn("clearMapOverlays()", render_map)
        self.assertIn("scheduleFitMapToPoints(list)", render_map)
        self.assertLess(
            render_map.index("clearMapOverlays()"),
            render_map.index("scheduleFitMapToPoints(list)"),
        )

    def test_generator_works_from_project_parent_directory(self):
        subprocess.run([PYTHON, str(ROOT / "generate_html.py")],
                       cwd=ROOT.parent, check=True)
        self.assertTrue((ROOT / "index.html").is_file())

    def test_persistence_api_uses_versioned_local_storage(self):
        self.assertIn("const STORAGE_KEY = 'itinerary-editor-state-v1';", self.html)
        self.assertIn("function loadCachedOrBase()", self.html)
        self.assertIn("function cacheLocal(points, meta)", self.html)
        self.assertIn("function persistPoints(points)", self.html)
        self.assertIn("function saveState(points)", self.html)
        self.assertIn("schemaVersion: 1", self.html)
        self.assertIn("localStorage.setItem(STORAGE_KEY", self.html)
        self.assertIn("try {", self.html)
        self.assertIn("return false;", self.html)

    def test_import_validates_before_replacing_points(self):
        import_fn = self.html.split("async function importJson(file)", 1)[1].split(
            "async function resetToBase()", 1
        )[0]
        self.assertIn("ItineraryCore.parseImport", import_fn)
        self.assertLess(import_fn.index("ItineraryCore.parseImport"),
                        import_fn.index("POIS ="))
        self.assertIn("confirm(", import_fn)
        self.assertIn("catch", import_fn)

    def test_transfer_and_reset_controls_are_present(self):
        for control in ("addPointBtn", "exportBtn", "importInput", "resetBtn", "saveStatus"):
            self.assertIn('id="' + control + '"', self.html)
        self.assertIn("function exportJson()", self.html)
        self.assertIn("async function importJson(file)", self.html)
        self.assertIn("async function resetToBase()", self.html)

    def test_export_downloads_blob_and_releases_url(self):
        export_fn = self.html.split("function exportJson()", 1)[1].split(
            "function restoreStoredState", 1
        )[0]
        self.assertIn("new Blob", export_fn)
        self.assertIn("URL.createObjectURL", export_fn)
        self.assertIn("download", export_fn)
        self.assertIn("URL.revokeObjectURL", export_fn)

    def test_reset_removes_saved_state_and_rerenders(self):
        reset_fn = self.html.split("async function resetToBase()", 1)[1].split(
            "let POIS =", 1
        )[0]
        self.assertIn("localStorage.removeItem(STORAGE_KEY)", reset_fn)
        self.assertIn("basePoints()", reset_fn)
        self.assertIn("selectDay(curDay)", reset_fn)
        self.assertIn("resetRemoteItinerary", reset_fn)

    def test_map_markers_follow_rendered_points_and_empty_itinerary_has_default_center(self):
        init_map = self.html.split("function initMap(){", 1)[1].split(
            "function renderTimeline", 1
        )[0]
        render_map = self.html.split("function renderMap(d, list){", 1)[1].split(
            "function selectDay(d){", 1
        )[0]
        self.assertIn("POIS[0] ||", init_map)
        self.assertIn("list.forEach(function(p)", render_map)
        self.assertIn("new BMap.Marker", render_map)
        self.assertNotIn("BASE_POIS.forEach", render_map)

    def test_import_rolls_back_points_and_exact_storage_snapshot_after_late_failure(self):
        import_fn = self.html.split("async function importJson(file)", 1)[1].split(
            "async function resetToBase()", 1
        )[0]
        self.assertIn("previousStored = localStorage.getItem(STORAGE_KEY)", import_fn)
        self.assertIn("restoreStoredState(previousStored)", import_fn)
        self.assertIn("POIS = previous", import_fn)
        self.assertLess(import_fn.index("persistPoints(POIS)"),
                        import_fn.index("document.getElementById('bPoi')"))

    def test_reset_does_not_mutate_points_before_storage_removal_succeeds(self):
        reset_fn = self.html.split("async function resetToBase()", 1)[1].split(
            "let POIS =", 1
        )[0]
        self.assertIn("try {", reset_fn)
        self.assertIn("catch", reset_fn)
        self.assertIn("恢复失败", reset_fn)
        local_branch = reset_fn.split("const base = basePoints();", 1)[1]
        self.assertLess(local_branch.index("localStorage.removeItem(STORAGE_KEY)"),
                        local_branch.index("POIS = base"))

    def test_export_revokes_object_url_in_finally(self):
        export_fn = self.html.split("function exportJson()", 1)[1].split(
            "function restoreStoredState", 1
        )[0]
        self.assertIn("finally", export_fn)
        self.assertLess(export_fn.index("finally"),
                        export_fn.index("URL.revokeObjectURL"))

    def test_point_editor_contains_required_fields_and_controls(self):
        self.assertIn('id="pointEditor"', self.html)
        for field in ("pointDay", "pointTime", "pointTitle", "pointCity",
                      "pointCategory", "pointLat", "pointLng"):
            self.assertRegex(
                self.html,
                r'id="' + field + r'"[^>]*\brequired\b',
            )
        self.assertIn('id="pointDescription"', self.html)
        self.assertIn('id="placeKeyword"', self.html)
        self.assertIn('id="placeResults"', self.html)
        self.assertIn('id="placeSearchBtn"', self.html)
        self.assertIn('id="mapPickBtn"', self.html)

    def test_point_editor_implements_search_and_single_use_map_pick(self):
        self.assertIn("function openPointEditor()", self.html)
        self.assertIn("function closePointEditor()", self.html)
        self.assertIn("function beginMapPick()", self.html)
        self.assertIn("function searchPlaces(keyword, city)", self.html)
        self.assertIn("new BMap.LocalSearch", self.html)
        self.assertIn("local.setPageCapacity(8)", self.html)
        self.assertIn("map.addEventListener('click', mapPickHandler)", self.html)
        self.assertIn("map.removeEventListener('click', mapPickHandler)", self.html)

    def test_editor_layout_keeps_map_visible_with_preview(self):
        self.assertIn("justify-content:flex-start", self.html)
        self.assertIn("pointer-events:none", self.html)
        self.assertIn("function refreshEditorPreview()", self.html)
        self.assertIn("computeMarkerPixelOffsets", self.html)
        self.assertIn("findTimeNeighbors", self.html)
        self.assertIn('id="previewHint"', self.html)
        self.assertIn("strokeStyle: 'dashed'", self.html)
        open_add = self.html.split("function openPointEditor()", 1)[1].split(
            "function openPointEditorForEdit", 1
        )[0]
        self.assertIn("setMobileView('map')", open_add)
        self.assertIn("refreshEditorPreview()", open_add)

    def test_timeline_and_tabs_survive_map_script_or_initialization_failure(self):
        select_day = self.html.split("function selectDay(d){", 1)[1].split(
            "function flyTo(d, num){", 1
        )[0]
        render_map = self.html.split("function renderMap(d, list){", 1)[1].split(
            "function selectDay(d){", 1
        )[0]
        boot = self.html.split("function boot(){", 1)[1].split(
            "</script>", 1
        )[0]
        self.assertIn("renderTimeline(d, list)", select_day)
        self.assertIn("if (isMapAvailable())", select_day)
        self.assertIn("if (!isMapAvailable())", render_map)
        self.assertIn("selectDay(DAYS[0])", boot)
        self.assertIn("boot();", boot)
        self.assertIn("showMapUnavailable(", boot)
        self.assertIn("'地图不可用：' + message", self.html)

    def test_file_protocol_shows_explicit_unsupported_map_notice(self):
        self.assertIn("location.protocol === 'file:'", self.html)
        self.assertIn("直接双击", self.html)
        self.assertIn("http://localhost:8000/", self.html)

    def test_timeline_card_click_does_not_require_map(self):
        fly_fn = self.html.split("function flyTo(d, num){", 1)[1].split(
            "function boot()", 1
        )[0]
        self.assertIn("if (!isMapAvailable()) return;", fly_fn)
        self.assertLess(
            fly_fn.index("if (!isMapAvailable()) return;"),
            fly_fn.index("map.centerAndZoom"),
        )

    def test_suggestion_uses_baidu_poi_city_fallback(self):
        search_fn = self.html.split("function searchPlaces(keyword, city)", 1)[1].split(
            "async function submitPoint(formData)", 1
        )[0]
        self.assertIn("item.city || city", search_fn)
        self.assertIn("bd09ToGcj02", search_fn)

    def test_submit_point_uses_safe_id_and_atomic_candidate_save(self):
        self.assertIn("async function submitPoint(formData)", self.html)
        submit_fn = self.html.split("async function submitPoint(formData)", 1)[1].split(
            "document.getElementById('pointCancelBtn')", 1
        )[0]
        self.assertIn("crypto.randomUUID", submit_fn)
        self.assertIn("Date.now()", submit_fn)
        self.assertIn("ItineraryCore.insertPointByTime", submit_fn)
        self.assertIn("ItineraryCore.updatePoint", submit_fn)
        self.assertIn("const previousPoints = POIS", submit_fn)
        self.assertIn("persistPoints(candidate)", submit_fn)
        self.assertLess(
            submit_fn.index("persistPoints(candidate)"),
            submit_fn.index("POIS = candidate"),
        )
        self.assertIn("source: pointSource", submit_fn)
        self.assertIn("const latText =", submit_fn)
        self.assertIn("!latText || !lngText", submit_fn)
        self.assertIn(r"/^([01]\d|2[0-3]):[0-5]\d$/.test(time)", submit_fn)
        self.assertNotIn(r"/^\d{2}:\d{2}$/.test(time)", submit_fn)
        self.assertIn("refreshDayView(day)", submit_fn)

    def test_timeline_cards_support_edit_delete_and_time_sorting(self):
        self.assertIn('class="edit-btn"', self.html)
        self.assertIn('class="del-btn"', self.html)
        self.assertIn("function openPointEditorForEdit(pointId)", self.html)
        self.assertIn("function deletePointById(pointId)", self.html)
        self.assertIn("ItineraryCore.deletePoint", self.html)
        self.assertIn("确定删除：", self.html)
        self.assertIn('id="pointId"', self.html)
        self.assertNotIn('draggable="true"', self.html)
        self.assertNotIn("function bindTimelineDrag", self.html)
        select_fn = self.html.split("function selectDay(d){", 1)[1].split(
            "function flyTo(d, num)", 1
        )[0]
        self.assertIn("a.time.localeCompare(b.time)", select_fn)
        timeline_fn = self.html.split("function renderTimeline(d, list){", 1)[1].split(
            "function renderMap", 1
        )[0]
        self.assertIn("openPointEditorForEdit", timeline_fn)
        self.assertIn("deletePointById", timeline_fn)
        self.assertIn("refreshDayView(day)", self.html)

    def test_untrusted_content_is_escaped_in_timeline_info_and_search(self):
        self.assertIn("function escapeHtml(value)", self.html)
        timeline_fn = self.html.split("function renderTimeline(d, list){", 1)[1].split(
            "function renderMap", 1
        )[0]
        fly_fn = self.html.split("function flyTo(d, num){", 1)[1].split(
            "function boot()", 1
        )[0]
        search_fn = self.html.split("function searchPlaces(keyword, city)", 1)[1].split(
            "function submitPoint(formData)", 1
        )[0]
        for expression in ("escapeHtml(p.title)", "escapeHtml(p.desc)"):
            self.assertIn(expression, timeline_fn)
            self.assertIn(expression, fly_fn)
        self.assertIn("escapeHtml(h.addr)", timeline_fn)
        self.assertIn("escapeHtml(h.addr)", fly_fn)
        self.assertIn("textContent", search_fn)

    def test_render_map_escapes_error_message_before_using_inner_html(self):
        render_map = self.html.split("function renderMap(d, list){", 1)[1].split(
            "function selectDay(d){", 1
        )[0]
        catch_block = render_map.split("} catch(e){", 1)[1].split("return;", 1)[0]
        self.assertIn("escapeHtml(e && e.message || e)", catch_block)
        self.assertNotIn(" + e.message", catch_block)

    def test_mobile_layout_uses_list_map_toggle(self):
        self.assertIn('id="mobileBar"', self.html)
        self.assertIn('id="viewListBtn"', self.html)
        self.assertIn('id="viewMapBtn"', self.html)
        self.assertIn("function setMobileView(mode)", self.html)
        self.assertIn("mobile-list", self.html)
        self.assertIn("mobile-map", self.html)
        self.assertIn("visibility:hidden", self.html)
        self.assertIn("不可对地图容器用 display:none", self.html)
        self.assertNotIn(".layout.mobile-list .map-wrap{display:none}", self.html)
        self.assertIn('id="moreBtn"', self.html)

    def test_cloud_sync_hooks_are_present(self):
        self.assertIn('const API_BASE = "', self.html)
        self.assertIn("function cloudEnabled()", self.html)
        self.assertIn("function fetchRemoteItinerary()", self.html)
        self.assertIn("function pushRemoteItinerary(points, title)", self.html)
        self.assertIn("X-Edit-Password", self.html)
        self.assertIn("/api/itinerary", self.html)
        self.assertIn("版本冲突", self.html)
        self.assertIn("将覆盖云端共享数据", self.html)
        self.assertIn("sessionStorage", self.html)
        self.assertIn("startPolling", self.html)
        self.assertIn("persistPoints", self.html)
        self.assertIn('"title": "济南站候车出发"', self.html)
        self.assertIn('"title": "威海住宿·山大路(出发)"', self.html)
        self.assertIn('"title": "烟台住宿·青年南路"', self.html)
        self.assertIn('"title": "威海住宿·时代小驿"', self.html)
        self.assertIn("养马岛", self.html)
        self.assertIn("那香海", self.html)
        self.assertIn("成山头", self.html)
        self.assertIn("5745.65", self.html)
        self.assertNotIn("火炬八街", self.html)
        self.assertNotIn("济南住宿·天桥区", self.html)
        self.assertNotIn("千佛山", self.html)
        self.assertNotIn("山东省博物馆", self.html)
        self.assertNotIn("洪家楼", self.html)


if __name__ == "__main__":
    unittest.main()
