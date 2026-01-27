# clearsky_client.py
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import requests


class ClearSkyAPIError(RuntimeError):
    def __init__(self, message: str, code: Optional[int] = None, status_code: Optional[int] = None):
        self.code = code
        self.status_code = status_code
        super().__init__(f"{message}" + (f" (code={code})" if code is not None else "") + (f" (http={status_code})" if status_code else ""))


@dataclass
class ClearSkyClient:
    api_key: str
    base_url: str = "https://api.clearsky.vision"
    timeout_s: int = 120
    max_retries: int = 5
    backoff_s: float = 1.0

    def _headers(self) -> Dict[str, str]:
        """Return HTTP headers for ClearSky API requests.

        Authentication
        --------------
        ClearSky uses API key authentication via the ``X-API-KEY`` header.

        Returns
        -------
        Dict[str, str]
            Headers containing:
            - ``X-API-KEY``: the API key for the account
            - ``Content-Type``: ``application/json`` (for JSON endpoints)
        """
        return {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        expect_binary: bool = False,
    ) -> requests.Response:
        """Perform an HTTP request with retries and ClearSky error handling.

        This is a low-level helper that:
        - Adds authentication headers (X-API-KEY)
        - Applies a simple retry policy on transient HTTP failures
        - Validates the common ClearSky "ServiceResult" JSON envelope
          (``{Succeeded: bool, Data: ..., Error: {...}}``) and raises
          :class:`ClearSkyAPIError` when ``Succeeded`` is false.

        Parameters
        ----------
        method:
            HTTP method (e.g., ``"GET"``, ``"POST"``, ``"DELETE"``).
        path:
            API path beginning with ``/api/...`` (it will be joined with ``base_url``).
        params:
            Optional query parameters appended to the URL.
        json_body:
            Optional JSON body for POST-like requests.
        stream:
            Set to ``True`` for file downloads / streaming responses. When ``True``,
            callers should read from ``resp.iter_content(...)``.
        expect_binary:
            Set to ``True`` when the successful response is binary (e.g. ``application/octet-stream``).
            When ``False`` (default), JSON responses are inspected for the ServiceResult envelope.

        Returns
        -------
        requests.Response
            The underlying response object. For ServiceResult endpoints, success implies:
            - HTTP status 2xx
            - and if JSON and has ``Succeeded`` key, then ``Succeeded == True``

        Raises
        ------
        ClearSkyAPIError
            If the request fails after retries, or if the API returns a ServiceResult error.
        """
        url = self.base_url.rstrip("/") + path

        for attempt in range(self.max_retries):
            resp = requests.request(
                method=method,
                url=url,
                headers=self._headers(),
                params=params,
                json=json_body,
                timeout=self.timeout_s,
                stream=stream,
            )

            # Basic retry policy for transient failures / throttling
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < self.max_retries - 1:
                time.sleep(self.backoff_s * (2 ** attempt))
                continue

            # Success path
            if 200 <= resp.status_code < 300:
                # If expecting JSON "ServiceResult", validate it here
                if not expect_binary:
                    ct = (resp.headers.get("Content-Type") or "").lower()
                    if "application/json" in ct:
                        payload = resp.json()
                        # Many endpoints return ServiceResult{Succeeded,Data,Error}
                        if isinstance(payload, dict) and "Succeeded" in payload:
                            if not payload.get("Succeeded", False):
                                err = payload.get("Error") or {}
                                raise ClearSkyAPIError(
                                    message=err.get("Message", "Request failed"),
                                    code=err.get("Code"),
                                    status_code=resp.status_code,
                                )
                return resp

            # Error path: try parse ServiceResult error if JSON
            try:
                ct = (resp.headers.get("Content-Type") or "").lower()
                if "application/json" in ct:
                    payload = resp.json()
                    if isinstance(payload, dict) and "Error" in payload:
                        err = payload.get("Error") or {}
                        raise ClearSkyAPIError(
                            message=err.get("Message", resp.text),
                            code=err.get("Code"),
                            status_code=resp.status_code,
                        )
                raise ClearSkyAPIError(resp.text, status_code=resp.status_code)
            except ValueError:
                # Non-JSON error
                raise ClearSkyAPIError(resp.text, status_code=resp.status_code)

        raise ClearSkyAPIError("Request failed after retries")

    # ---------- Convenience wrappers (JSON endpoints) ----------

    def get_account_info(self) -> Dict[str, Any]:
        """Get account limits and quotas for the current API key.

        Endpoint
        --------
        ``GET /api/account/info``

        Purpose
        -------
        Use this endpoint to introspect the account associated with the API key, including:
        - Maximum composite area size allowed
        - Maximum number of concurrent connections
        - Limits that influence what requests your user can make successfully

        Parameters
        ----------
        None

        Returns
        -------
        Dict[str, Any]
            ``Data`` object fields (typical):
            - ``TenantId`` (str): internal tenant identifier for the API key.
            - ``MaxConcurrentConnections`` (int): max simultaneous API connections allowed.
            - ``MaxCompositeAreaKm2`` (int): maximum AOI size allowed for composite processing.
            - ``MaxTotalBands`` (int): maximum number of bands allowed in a single request.
            - ``EuroOverdraftLimit``, ``EuroBalanceCap`` (int): billing-related limits.

        Notes
        -----
        This is a safe “first call” to validate that authentication works.
        """
        resp = self._request("GET", "/api/account/info")
        return resp.json()["Data"]

    def get_tasking_models(self) -> Dict[str, Any]:
        """List available processing/tasking models and their supported satellite constellations.

        Endpoint
        --------
        ``GET /api/tasking/models``

        Purpose
        -------
        Models determine:
        - Which satellite constellations are supported/required
        - Which processing pipeline is used for availability checks and downloads
        - What options are relevant in download endpoints (e.g. some models support Sentinel2 L1)

        Parameters
        ----------
        None

        Returns
        -------
        Dict[str, Any]
            ``Data`` typically contains:
            - ``TaskingModels`` (list[dict]):
                Each item includes:
                - ``Model`` (str): model identifier (e.g. ``"Stratus2"``).
                - ``SupportedSatelliteConstellations`` (list[dict]):
                    Each item:
                    - ``SatelliteConstellation`` (str)
                    - ``Optional`` (bool): whether constellation can be omitted.

        Tips
        ----
        When building UIs, call this once and cache it to populate model/constellation dropdowns.
        """
        resp = self._request("GET", "/api/tasking/models")
        return resp.json()["Data"]

    def optimize_tiles(self, wkt_geometrycollection: str) -> Dict[str, Any]:
        """Optimize a GeometryCollection into a cost-effective set of tiles/minitiles.

        Endpoint
        --------
        ``POST /api/tasking/tile/optimize``

        Purpose
        -------
        Given an AOI expressed as WKT GeometryCollection, this endpoint returns a recommended
        set of tile guids and/or minitile guids that best cover the area with a cost focus.
        It is useful when users want tile ordering but do not want to manually pick tiles.

        Parameters
        ----------
        wkt_geometrycollection:
            WKT **GeometryCollection** string containing polygons/multipolygons that describe the AOI.
            Example: ``"GEOMETRYCOLLECTION (POLYGON(...), POLYGON(...))"``

            The endpoint expects a GeometryCollection for best results; if you only have a polygon,
            you can wrap it in a GeometryCollection.

        Returns
        -------
        Dict[str, Any]
            ``Data`` typically contains:
            - ``Tiles`` (list[str]): tile GUIDs to order.
            - ``MiniTiles`` (list[str]): minitile GUIDs to order.

        Notes
        -----
        The optimization is “best-effort”; exact global optimality is not guaranteed.
        Always run an order estimate afterwards to show the actual price impact.
        """
        resp = self._request(
            "POST",
            "/api/tasking/tile/optimize",
            json_body={"Wkt": wkt_geometrycollection},
        )
        return resp.json()["Data"]

    def search_tiles(self, *, wkt: Optional[str] = None, geojson: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Search for orderable tiles/minitiles intersecting an AOI.

        Endpoint
        --------
        ``POST /api/tasking/search/tiles``

        Purpose
        -------
        Use this endpoint to discover which tiles and/or minitiles can be ordered for a given area.
        It is typically used for a “select tiles” workflow before calling ``create_task_order`` with
        ``TileGuids`` / ``MiniTileGuids``.

        Parameters
        ----------
        wkt:
            AOI geometry in WKT (EPSG:4326 lon/lat).
            Provide either ``wkt`` OR ``geojson`` (not both).
        geojson:
            AOI geometry in GeoJSON (EPSG:4326 lon/lat).
            Provide either ``geojson`` OR ``wkt``.

        Returns
        -------
        Dict[str, Any]
            ``Data`` typically contains:
            - ``Tiles`` (list[dict]): each tile/minitile entry includes:
                - ``Guid`` (str): ID you pass to ordering/download endpoints.
                - ``MiniTile`` (bool): True if this is a minitile.
                - ``Epsg`` (str): EPSG of underlying stored data for the tile (useful for downloads).
                - ``DataGeogWkt`` (str): tile footprint in EPSG:4326, often with nodata areas removed.

        Tips
        ----
        - If you want minitiles for a specific tile, the API supports ``TileGuidForMiniTiles``,
          but this client wrapper does not expose it yet.
        """
        body: Dict[str, Any] = {"Wkt": wkt, "GeoJson": geojson, "TileGuids": None, "MiniTileGuids": None, "TileGuidForMiniTiles": None}
        resp = self._request("POST", "/api/tasking/search/tiles", json_body=body)
        return resp.json()["Data"]

    def create_task_order(
        self,
        *,
        wkt: Optional[str] = None,
        geojson: Optional[Dict[str, Any]] = None,
        tile_guids: Optional[list[str]] = None,
        minitile_guids: Optional[list[str]] = None,
        model: str = "Stratus2",
        satellite_constellations: Optional[list[str]] = None,
        storage_months: int = 3,
        api_requests: int = 5,
        image_frequency: Optional[int] = 2,
        reference_date: Optional[str] = "2024-01-01",
        from_date: str = "2024-01-01",
        to_date: Optional[str] = None,
        tile_deduplication: bool = False,
        geometry_tile_ordering: bool = False,
        automatic_order_guid: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a tasking order (subscription/recurring or fixed period) for an AOI or tiles.

        Endpoint
        --------
        ``POST /api/tasking/orders``

        Purpose
        -------
        Tasking orders define what areas (or tiles/minitiles) a user has access to, and for which
        time period. Orders are required before users can check availability/download data for
        that area and date.

        **Recommended UX:** call ``estimate_task_order`` first, show pricing, and only create the
        order after the user explicitly accepts the estimate.

        Geometry vs tiles
        -----------------
        You can create an order in one of two common ways:

        1) Geometry-based (composite area):
           - Provide ``wkt`` or ``geojson`` (often as a GeometryCollection)
           - Set ``geometry_tile_ordering=True`` to let the service determine tile coverage from geometry

        2) Tile-based:
           - Provide ``tile_guids`` and/or ``minitile_guids`` (typically discovered via ``search_tiles``
             or ``optimize_tiles``)
           - Leave geometry fields empty

        Parameters
        ----------
        wkt / geojson:
            AOI geometry (EPSG:4326). Supply at most one of them.
            - Use GeometryCollection WKT for multi-AOI workflows.
        tile_guids / minitile_guids:
            Explicit tile IDs to order. Use these if users choose tiles manually or via optimization.

        model:
            Processing/tasking model name (e.g. ``"Stratus2"``). Determines supported satellites and
            downstream processing behavior.
        satellite_constellations:
            List of satellite constellations to include (e.g. ``["Sentinel1","Sentinel2","Landsat89"]``).
            Must be compatible with the chosen model.
        storage_months:
            How many months data is retained beyond the initial month (billing/retention control).
        api_requests:
            How many API requests per AOI per month are included/allowed during storage period.

        image_frequency / reference_date:
            Controls the “scheduled image dates” produced by the order (for recurring plans).
            The API describes the schedule with a modulus formula based on ``reference_date`` and frequency.
            Some models require explicitly setting these; others may allow defaults.
        from_date / to_date:
            Define the active period:
            - ``from_date`` is the start month (day should typically be ``01``).
            - ``to_date=None`` means a recurring subscription (open-ended).
            - Set ``to_date`` to end a non-recurring plan at a given month.
        tile_deduplication:
            If True, attempt to deduplicate tile/mini-tile orders against previous tile/mini-tile orders.
        geometry_tile_ordering:
            If True, order tiles based on geometry (``wkt``/``geojson``) rather than explicit tile lists.
        automatic_order_guid:
            Advanced flow: optional query parameter for “automatic order flow” integrations.

        Returns
        -------
        Dict[str, Any]
            ``Data`` (created order) typically includes:
            - ``TaskOrderGuid`` (str): primary identifier used for order status and details.
            - ``OrderingProcessStatus`` (str): initial processing status.
            - Additional metadata (billing cycle, model, area, dates, tile lists, etc.)

        Raises
        ------
        ClearSkyAPIError
            If the API returns a ServiceResult error (e.g. validation errors).
        """
        if satellite_constellations is None:
            satellite_constellations = ["Sentinel1", "Sentinel2", "Landsat89"]

        params = {}
        if automatic_order_guid is not None:
            params["automaticOrderGuid"] = automatic_order_guid

        body = {
            "Wkt": wkt,
            "GeoJson": geojson,
            "TileGuids": tile_guids or [],
            "MiniTileGuids": minitile_guids or [],
            "SatelliteConstellations": satellite_constellations,
            "Model": model,
            "StorageMonths": storage_months,
            "ApiRequests": api_requests,
            "ImageFrequency": image_frequency,
            "ReferenceDate": reference_date,
            "From": from_date,
            "To": to_date,
            "TileDeduplication": tile_deduplication,
            "GeometryTileOrdering": geometry_tile_ordering,
        }

        resp = self._request("POST", "/api/tasking/orders", params=params, json_body=body)
        return resp.json()["Data"]

    def list_orders(self, *, recurring_only: bool = False, get_expired: bool = False) -> Dict[str, Any]:
        """List tasking orders for the current API key.

        Endpoint
        --------
        ``GET /api/tasking/orders``

        Purpose
        -------
        Use this endpoint to show a user all orders on their account and their current statuses.

        Parameters
        ----------
        recurring_only:
            If True, returns only recurring/subscription orders.
        get_expired:
            If True, includes expired orders in the response (useful for auditing/history views).

        Returns
        -------
        Dict[str, Any]
            ``Data`` typically contains:
            - ``TaskOrders`` (list[dict]): each entry commonly includes:
                - ``TaskOrderGuid`` (str)
                - ``OrderingProcessStatus`` (str): see API docs for values like Initialize/Ongoing/Done/etc.
                - ``From`` / ``To`` (date strings)
                - ``Model`` (str)
                - ``SatelliteConstellations`` (list[str])
                - ``Tiles`` / ``MiniTiles`` (list[str]) for tile-based orders
                - ``Wkt`` (str or null) for geometry-based orders

        Notes
        -----
        For more detail (e.g. tile WKT footprints), call :meth:`order_details`.
        """
        resp = self._request("GET", "/api/tasking/orders", params={"recurringOnly": recurring_only, "getExpired": get_expired})
        return resp.json()["Data"]

    def order_details(self, guids: list[str]) -> Dict[str, Any]:
        """Get detailed information for specific tasking orders by GUID.

        Endpoint
        --------
        ``POST /api/tasking/orders/details``

        Purpose
        -------
        Use this endpoint to retrieve details for one or more orders including:
        - Order period, model, constellations
        - Tiles/minitiles, sometimes including per-tile geometry

        Parameters
        ----------
        guids:
            List of order GUID strings (``TaskOrderGuid`` values).

        Returns
        -------
        Dict[str, Any]
            ``Data`` typically contains:
            - ``TaskOrders`` (list[dict]): detailed order objects such as:
                - ``TaskOrderGuid`` (str)
                - ``OrderingProcessStatus`` (str) – the primary “order readiness” signal
                - ``Tiles`` / ``MiniTiles`` (list[dict] or list[str], depending on API version):
                    - May include ``Guid`` and ``Wkt`` for each tile reference.
                - ``Wkt`` (str or null): order AOI (for geometry-based orders)

        Tips
        ----
        If you just need a single status, request one GUID and read ``TaskOrders[0]["OrderingProcessStatus"]``.
        """
        resp = self._request("POST", "/api/tasking/orders/details", json_body={"Guids": guids})
        return resp.json()["Data"]

    def search_available_imagery(self, *, wkt: str, from_utc: str, until_utc: Optional[str] = None) -> Dict[str, Any]:
        """Search which dates have available imagery for an AOI within a time window.

        Endpoint
        --------
        ``POST /api/satelliteimages/search/available``

        Purpose
        -------
        This endpoint helps answer:
        - “Which dates are available for this area (given my current orders)?”
        - “Which parts of my AOI have imagery on which dates?”

        It can be used even when availability depends on multiple underlying orders,
        and it returns results grouped by model/constellations and by geography segments.

        Parameters
        ----------
        wkt:
            AOI polygon (EPSG:4326 WKT). This is the query geometry for which you want availability.
        from_utc:
            Inclusive start timestamp in UTC, ISO-8601 (e.g. ``"2024-05-03T00:00:01Z"``).
        until_utc:
            Optional inclusive end timestamp in UTC. If omitted, the API may return availability
            from ``from_utc`` onward depending on server defaults.

        Returns
        -------
        Dict[str, Any]
            ``Data`` typically contains:
            - ``ModelImageDates`` (list[dict]):
                Each entry contains:
                - ``Model`` (str)
                - ``SatelliteConstellations`` (list[str])
                - ``DatesByGeog`` (list[dict]):
                    - ``Wkt`` (str): a sub-geometry of the AOI tied to the returned date list
                    - ``Dates`` (list[str]): available dates (YYYY-MM-DD)

        Notes
        -----
        This returns “what is available”, not a binary “ready/not-ready” for a specific date.
        For a single date readiness check, use :meth:`composite_available`.
        """
        body = {"Wkt": wkt, "GeoJson": None, "From": from_utc, "Until": until_utc}
        resp = self._request("POST", "/api/satelliteimages/search/available", json_body=body)
        return resp.json()["Data"]

    def composite_available(
        self,
        *,
        wkt: str,
        date_utc: str,
        epsg_projection: int,
        bandnames: str = "all",
        model: str = "Stratus2",
        satellite_constellations: Optional[list[str]] = None,
        utm_data_selection_mode: Optional[str] = "combined_utm",
    ) -> Dict[str, Any]:
        """Check whether a composite request is available for a specific date and AOI.

        Endpoint
        --------
        ``POST /api/satelliteimages/process/composite/available``

        Purpose
        -------
        This endpoint returns a set of boolean flags that explain whether a composite download
        for (AOI, date) is possible *right now*, and why it may not be available.

        It is the best endpoint to use when your workflow is:
        - user has (or just created) an order
        - user wants a specific date
        - you need a single “availability snapshot” before calling ``download_composite``

        Parameters
        ----------
        wkt:
            AOI geometry in WKT (EPSG:4326 lon/lat).
        date_utc:
            Requested imagery date in UTC. Accepts ISO-8601 (e.g. ``"2024-05-03T00:00:00Z"``)
            or a date string (``"2024-05-03"``).
        epsg_projection:
            Output projection EPSG for the availability check context (commonly a UTM EPSG like 32632).
            This should match what you intend to use when downloading, especially for UTM-related rules.
        bandnames:
            Bands requested. Use ``"all"`` for full band set, ``"rgb"`` for visual-only, or a custom
            band expression if supported by your model (e.g. ``"B2, B3, B4, [B8_B4]"``).
            Some band combinations may have specific availability constraints.
        model:
            Processing model identifier (e.g. ``"Stratus2"``).
        satellite_constellations:
            Which constellations should be used to satisfy the request (must be compatible with model).
        utm_data_selection_mode:
            How data is selected across UTM zones (relevant when using UTM EPSGs):
            - ``"single_utm_fully_covered"``: strict; AOI must be fully covered by requested UTM zone
            - ``"single_utm"``: choose pixels from requested zone; keep array shape of combined mode
            - ``"combined_utm"``: fill missing pixels by reprojection from neighboring UTM zones

        Returns
        -------
        Dict[str, Any]
            ``Data`` is a set of boolean flags. Common ones:
            - ``FullyAvailable``: all underlying areas have imagery for the date
            - ``PartiallyAvailable``: some (but not all) underlying areas have imagery
            - ``OrdersCoverPolygon``: whether the union of ordered areas covers the requested AOI
            - ``DataAvailableForUser``: false if access restricted for this date/area
            - ``PolygonInDataArea``: false if AOI is outside data (e.g. entirely water/no-data)
            - ``AllImagesPredicted``: false if not all zones have predictions where expected

        Interpretation
        --------------
        A common “ready” check is:
        - ``FullyAvailable`` AND ``OrdersCoverPolygon`` AND ``DataAvailableForUser``

        Notes
        -----
        This endpoint does not download any data; it only reports readiness.
        """
        if satellite_constellations is None:
            satellite_constellations = ["Sentinel1", "Sentinel2", "Landsat89"]

        body = {
            "Wkt": wkt,
            "GeoJson": None,
            "Date": date_utc,
            "UtmDataSelectionMode": utm_data_selection_mode,
            "SatelliteConstellations": satellite_constellations,
            "Model": model,
            "EpsgProjection": epsg_projection,
            "Bandnames": bandnames,
        }
        resp = self._request("POST", "/api/satelliteimages/process/composite/available", json_body=body)
        return resp.json()["Data"]

    # ---------- Binary endpoints (download) ----------

    def download_composite(
        self,
        *,
        out_path: Path,
        wkt: str,
        date_utc: str,
        resolution: int = 10,
        epsg_projection: int = 32632,
        file_type: str = "tif",
        pixel_selection_mode: str = "contained",
        data_type: str = "INT16",
        utm_data_selection_mode: str = "combined_utm",
        utm_grid_force_pixel_resolution_size: bool = True,
        model: str = "Stratus2",
        satellite_constellations: Optional[list[str]] = None,
        bandnames: str = "all",
        allow_partial_image: bool = False,
        automatic_order_creation: bool = False,
        upload_url: Optional[str] = None,  # if set: API will PUT-upload and return 201
    ) -> None:
        """Download (or upload) a composite image for an AOI and date.

        Endpoint
        --------
        ``POST /api/satelliteimages/process/composite``

        Purpose
        -------
        Produce a GeoTIFF (or other supported file type) for a requested AOI and date, with
        configurable resolution, projection, bands, and pixel selection rules.

        This endpoint can be used for both:
        - Composite-area orders (geometry-based)
        - Tile/minitile orders (the AOI just needs to be covered by the user’s orders)

        Parameters
        ----------
        out_path:
            Local path where the downloaded file will be written (ignored when ``upload_url`` is set).
        wkt:
            AOI geometry in WKT (EPSG:4326 lon/lat).
        date_utc:
            Requested date in UTC (ISO-8601 or YYYY-MM-DD).
        resolution:
            Pixel size. Allowed values include: 10, 20, 40, 80, 160, 320, 640, 1280 (meters for UTM).
        epsg_projection:
            Output projection EPSG. Commonly a UTM EPSG (e.g. 32632) or 4326/3857.
            Using a UTM EPSG enables UTM-specific selection rules.
        file_type:
            Output file type. Currently commonly ``"tif"``.
        pixel_selection_mode:
            Determines which pixels are included relative to the geometry:
            - ``"intersect"``: include pixels that intersect the geometry
            - ``"contained"``: include only pixels fully covered by the geometry
        data_type:
            Pixel datatype (affects nodata values and file size):
            - ``"INT16"`` (nodata -32768)
            - ``"UINT8"`` (nodata 0)
        utm_data_selection_mode:
            Handling of AOIs spanning multiple UTM zones; see :meth:`composite_available` for meaning.
        utm_grid_force_pixel_resolution_size:
            When reprojection is involved:
            - True: keep pixel size exactly equal to ``resolution`` meters (may “twist” image)
            - False: allow slight pixel-size variation (e.g. 9.99m) to reduce reprojection distortion
        model / satellite_constellations:
            The processing model and the satellite sources to incorporate.
        bandnames:
            Which bands and indices to include. Use:
            - ``"all"`` for all available bands
            - ``"rgb"`` for RGB
            - or a custom mix like ``"B2, B3, B4, [B8_B4]"`` for NDVI-like indices.
        allow_partial_image:
            If False (default), the service may require all underlying zones to have imagery for the date.
            If True, allow returning partial coverage when only some zones have imagery.
        automatic_order_creation:
            If True, and the request would fail because the AOI/date is not covered by an order,
            the server may queue an automatic tasking order creation instead of failing immediately.
        upload_url:
            If provided, the API will upload the resulting file via HTTP PUT to this URL and respond with
            HTTP 201. In this mode, no bytes are returned to the client and nothing is written to disk.

        Returns
        -------
        None
            - Writes a file to ``out_path`` when ``upload_url`` is not set.
            - Returns normally after confirming HTTP 201 when ``upload_url`` is set.

        Raises
        ------
        ClearSkyAPIError
            On API errors, including unexpected status code when using ``upload_url``.
        """
        if satellite_constellations is None:
            satellite_constellations = ["Sentinel1", "Sentinel2", "Landsat89"]

        body = {
            "Wkt": wkt,
            "GeoJson": None,
            "Date": date_utc,
            "Resolution": resolution,
            "EpsgProjection": epsg_projection,
            "FileType": file_type,
            "PixelSelectionMode": pixel_selection_mode,
            "DataType": data_type,
            "UtmDataSelectionMode": utm_data_selection_mode,
            "SatelliteConstellations": satellite_constellations,
            "Model": model,
            "UtmGridForcePixelResolutionSize": utm_grid_force_pixel_resolution_size,
            "Bandnames": bandnames,
            "OldPixelSelectionMode": False,
            "AllowPartialImage": allow_partial_image,
            "AutomaticOrderCreation": automatic_order_creation,
            "UploadUrl": upload_url,
        }

        # If UploadUrl is set, many servers respond 201 with no content.
        resp = self._request("POST", "/api/satelliteimages/process/composite", json_body=body, stream=True, expect_binary=True)

        if upload_url:
            if resp.status_code != 201:
                raise ClearSkyAPIError("Expected 201 Created when UploadUrl is provided", status_code=resp.status_code)
            return

        # Otherwise, write stream to disk.
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

    def estimate_task_order(
        self,
        *,
        wkt: Optional[str] = None,
        geojson: Optional[Dict[str, Any]] = None,
        tile_guids: Optional[list[str]] = None,
        minitile_guids: Optional[list[str]] = None,
        model: str = "Stratus2",
        satellite_constellations: Optional[list[str]] = None,
        storage_months: int = 3,
        api_requests: int = 5,
        image_frequency: Optional[int] = 2,
        reference_date: Optional[str] = "2024-01-01",
        from_date: str = "2024-01-01",
        to_date: Optional[str] = None,
        simulated_euro_usage: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Estimate the cost and schedule of a tasking order before creating it.

        Endpoint
        --------
        ``POST /api/tasking/orders/estimate``

        Purpose
        -------
        This endpoint returns a pricing estimate for an order request. Use it to:
        - Show users expected current-month and recurring costs
        - Display the implied image schedule (often via ``ImageDates``)
        - Build “confirm purchase” flows before actually creating the order

        Parameters
        ----------
        wkt / geojson:
            AOI geometry (EPSG:4326). Provide at most one of them.
            Use this form when the user is ordering by area (composite-area ordering).
        tile_guids / minitile_guids:
            Explicit tile/minitile IDs to estimate. Use this form when the user is ordering tiles.
        model:
            Tasking/processing model (e.g. ``"Stratus2"``). Must match downstream usage.
        satellite_constellations:
            List of satellite constellations used for the order. Must be compatible with ``model``.
        storage_months:
            Retention/billing control: number of months data remains available beyond the initial month.
        api_requests:
            Included/allowed API requests per AOI per month while data is stored.
        image_frequency / reference_date:
            Controls which dates are scheduled. These parameters affect how many images/dates are included
            and therefore pricing. Some models require explicitly specifying them.
        from_date / to_date:
            Order active period:
            - ``from_date`` is the first month (often day=01).
            - ``to_date=None`` indicates a recurring subscription estimate.
        simulated_euro_usage:
            Optional advanced parameter for estimating cost under a simulated current usage scenario.

        Returns
        -------
        Dict[str, Any]
            ``Data`` typically includes:
            - ``AreaKm2`` (float): estimated area used for billing.
            - ``CancellationDate`` (date): estimated cancellation cutoff for the current billing logic.
            - ``CurrentMonthCosts`` (dict): current-month cost breakdown (currency + totals).
            - ``RecurringCostsEstimate`` (dict): ongoing cost estimate for subsequent periods.
            - ``ImageDates`` (list[str]): scheduled imagery dates (YYYY-MM-DD) implied by the order.

        Important note about estimates
        ------------------------------
        The API documents that estimates assume:
        - no changes to existing task orders during the month, and
        - the new task order does not overlap existing task orders.
        Real prices may differ if orders overlap or account state changes.

        Recommended usage
        -----------------
        Always require a user confirmation step after showing the estimate and before calling
        :meth:`create_task_order`.
        """
        if satellite_constellations is None:
            satellite_constellations = ["Sentinel1", "Sentinel2", "Landsat89"]

        body: Dict[str, Any] = {
            "Wkt": wkt,
            "GeoJson": geojson,
            "TileGuids": tile_guids or [],
            "MiniTileGuids": minitile_guids or [],
            "SatelliteConstellations": satellite_constellations,
            "Model": model,
            "StorageMonths": storage_months,
            "ApiRequests": api_requests,
            "ImageFrequency": image_frequency,
            "ReferenceDate": reference_date,
            "From": from_date,
            "To": to_date,
            "SimulatedEuroUsage": simulated_euro_usage,
        }

        resp = self._request("POST", "/api/tasking/orders/estimate", json_body=body)
        return resp.json()["Data"]

    def download_tile(
        self,
        *,
        out_path: Path,
        tile_guid: str,
        date_utc: str,
        model: str = "Stratus2",
        satellite_constellations: Optional[list[str]] = None,
        level: Optional[int] = None,
        harmonize: Optional[bool] = None,
        clip_reflectance: Optional[bool] = None,
        upload_url: Optional[str] = None,
    ) -> None:
        """Download (or upload) a single tile image for a given date.

        Endpoint
        --------
        ``POST /api/satelliteimages/process/tile``

        Purpose
        -------
        Fetch imagery for an already-known tile GUID (regular tile, not minitile). This is used when:
        - the user ordered tiles (tile order flow), and
        - they want the full tile footprint for a specific date.

        Parameters
        ----------
        out_path:
            Local file output path (ignored when ``upload_url`` is set).
        tile_guid:
            Tile GUID to download. Obtain from:
            - tile order details, or
            - :meth:`search_tiles`, or
            - :meth:`optimize_tiles` result.
        date_utc:
            Date/time in UTC (ISO-8601 or YYYY-MM-DD). Must be a date that is available for the tile.
        model:
            Processing model (must be compatible with the user’s order and desired data).
        satellite_constellations:
            Constellations used as sources (e.g. Sentinel2/Landsat). Must match the model/order expectations.
        level:
            Optional product level:
            - 1 = Level-1
            - 2 = Level-2 (defaults to 2 if omitted by the API)
        harmonize:
            Optional flag to request harmonization if supported by the selected model (API default is often True).
        clip_reflectance:
            Optional flag (model-dependent) for reflectance clipping behavior.
        upload_url:
            If provided, the API will HTTP PUT-upload the file to this URL and respond with HTTP 201.
            In that case, no content is streamed back and nothing is written to disk.

        Returns
        -------
        None
            Writes a file to ``out_path`` unless ``upload_url`` is provided.

        Raises
        ------
        ClearSkyAPIError
            On API errors, including unexpected status code when using ``upload_url``.
        """
        if satellite_constellations is None:
            satellite_constellations = ["Sentinel1", "Sentinel2", "Landsat89"]

        body = {
            "TileGuid": tile_guid,
            "Date": date_utc,
            "SatelliteConstellations": satellite_constellations,
            "Model": model,
            "Level": level,
            "Harmonize": harmonize,
            "ClipReflectance": clip_reflectance,
            "UploadUrl": upload_url,
        }

        resp = self._request("POST", "/api/satelliteimages/process/tile", json_body=body, stream=True, expect_binary=True)

        if upload_url:
            if resp.status_code != 201:
                raise ClearSkyAPIError("Expected 201 Created when UploadUrl is provided", status_code=resp.status_code)
            return

        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

    def download_minitile(
        self,
        *,
        out_path: Path,
        minitile_guid: str,
        date_utc: str,
        model: str = "Stratus2",
        satellite_constellations: Optional[list[str]] = None,
        level: Optional[int] = None,
        harmonize: Optional[bool] = None,
        clip_reflectance: Optional[bool] = None,
        upload_url: Optional[str] = None,
    ) -> None:
        """Download (or upload) a single minitile image for a given date.

        Endpoint
        --------
        ``POST /api/satelliteimages/process/minitile``

        Purpose
        -------
        Fetch imagery for an already-known *minitile* GUID. Minitiles are smaller-than-tile units
        used for more granular ordering and downloads.

        Parameters
        ----------
        out_path:
            Local file output path (ignored when ``upload_url`` is set).
        minitile_guid:
            Minitile GUID to download. Obtain from:
            - order details (minitile orders), or
            - :meth:`search_tiles` (entries where ``MiniTile=True``), or
            - :meth:`optimize_tiles` (``MiniTiles`` list).
        date_utc:
            Date/time in UTC (ISO-8601 or YYYY-MM-DD). Must be a date that is available for the minitile.
        model:
            Processing model (must be compatible with the user’s order and desired data).
        satellite_constellations:
            Constellations used as sources (e.g. Sentinel2/Landsat).
        level:
            Optional product level (1 or 2). API default is often Level-2.
        harmonize:
            Optional harmonization toggle if supported by the model.
        clip_reflectance:
            Optional reflectance clipping behavior (model-dependent).
        upload_url:
            If provided, the API will HTTP PUT-upload the file to this URL and respond with HTTP 201.
            In that case, no content is streamed back and nothing is written to disk.

        Returns
        -------
        None
            Writes a file to ``out_path`` unless ``upload_url`` is provided.

        Raises
        ------
        ClearSkyAPIError
            On API errors, including unexpected status code when using ``upload_url``.
        """
        if satellite_constellations is None:
            satellite_constellations = ["Sentinel1", "Sentinel2", "Landsat89"]

        body = {
            "MiniTileGuid": minitile_guid,
            "Date": date_utc,
            "SatelliteConstellations": satellite_constellations,
            "Model": model,
            "Level": level,
            "Harmonize": harmonize,
            "ClipReflectance": clip_reflectance,
            "UploadUrl": upload_url,
        }

        resp = self._request("POST", "/api/satelliteimages/process/minitile", json_body=body, stream=True, expect_binary=True)

        if upload_url:
            if resp.status_code != 201:
                raise ClearSkyAPIError("Expected 201 Created when UploadUrl is provided", status_code=resp.status_code)
            return

        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)


def format_order_estimate(est: dict) -> str:
    """Format the output of :meth:`ClearSkyClient.estimate_task_order` for display.

    Purpose
    -------
    The estimate payload can vary slightly across API versions (e.g. total field names).
    This helper renders a stable, human-readable summary that is useful for:
    - CLI tools
    - GitHub examples
    - “confirm purchase” prompts in scripts

    Parameters
    ----------
    est:
        The estimate ``Data`` dict returned by :meth:`ClearSkyClient.estimate_task_order`.

    Output fields shown
    -------------------
    - Area (``AreaKm2``) when available
    - CancellationDate when present
    - CurrentMonthCosts total and currency when present
    - RecurringCostsEstimate total and currency when present
    - ImageDates count and first/last when present

    Returns
    -------
    str
        A multi-line string summary suitable for printing.
    """
    cur = est.get("CurrentMonthCosts") or {}
    rec = est.get("RecurringCostsEstimate") or {}

    def money(costs: dict, key_a: str, key_b: str):
        return costs.get(key_a, costs.get(key_b))

    currency = cur.get("CurrencyCode") or rec.get("CurrencyCode") or "EUR"
    total_now = money(cur, "TotalCost", "TotalCostEuro")
    total_rec = money(rec, "TotalCost", "TotalCostEuro")

    area = est.get("AreaKm2")
    cancel = est.get("CancellationDate")
    img_dates = est.get("ImageDates") or []

    lines = []
    lines.append("=== Tasking Order Estimate ===")
    if area is not None:
        lines.append(f"AreaKm2: {area}")
    if cancel:
        lines.append(f"CancellationDate: {cancel}")
    if total_now is not None:
        lines.append(f"CurrentMonth Total: {total_now} {currency}")
    if total_rec is not None:
        lines.append(f"Recurring Total: {total_rec} {currency}")
    if img_dates:
        lines.append(f"ImageDates (count): {len(img_dates)}")
        lines.append(f"First/Last: {img_dates[0]} .. {img_dates[-1]}")

    return "\n".join(lines)
