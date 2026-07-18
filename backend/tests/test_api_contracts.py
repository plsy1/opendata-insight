import unittest

from fastapi.routing import APIRoute

from routers import api_router


class ApiContractTests(unittest.TestCase):
    def test_core_json_routes_declare_response_models(self):
        routes = {
            route.path: route
            for route in api_router.routes
            if isinstance(route, APIRoute)
        }
        expected_paths = {
            "/avbase/get_index",
            "/avbase/search",
            "/avbase/moviesOfActor",
            "/avbase/actorInformation",
            "/avbase/movieInformation",
            "/avbase/movieInformation/refresh",
            "/avbase/get_release_by_date",
            "/feed/movieSubscribe",
            "/feed/movieDownloaded",
            "/feed/actorSubscribe",
            "/feed/actorCollect",
            "/fc2/details",
            "/fc2/ranking",
            "/emby/get_latest",
            "/emby/get_resume",
            "/emby/get_views",
            "/emby/get_all",
            "/emby/exists",
            "/statistic/overview",
            "/statistic/daily",
            "/statistic/studio",
            "/statistic/actors",
            "/statistic/all",
            "/statistic/makers",
            "/statistic/labels",
            "/statistic/series",
            "/statistic/taxonomy",
            "/statistic/genres",
            "/statistic/tags",
            "/prowlarr/search",
            "/downloader/get_downloading_torrents",
            "/downloader/delete_torrent",
            "/auth/login",
            "/auth/verify",
            "/auth/changepassword",
            "/system/get_environment",
            "/system/version",
            "/system/check_update",
            "/fanza/monthlyactress",
            "/fanza/monthlyworks",
            "/background_task/list",
            "/background_task/run",
        }

        self.assertTrue(expected_paths.issubset(routes))
        for path in expected_paths:
            self.assertIsNotNone(routes[path].response_model, path)


if __name__ == "__main__":
    unittest.main()
