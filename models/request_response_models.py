"""
Collection of Request and Response models used by the ClearSKY Vision API
"""

from typing import Dict, Generic, List, Optional, TypeVar, Union
import uuid
from pydantic import BaseModel, TypeAdapter, field_validator, model_validator
from datetime import date

T = TypeVar("T")


class ErrorModel(BaseModel):
    Message: str
    Code: int


class ServiceResult(BaseModel, Generic[T]):
    Succeeded: bool
    Error: Optional["ErrorModel"]
    Data: Optional[T]

    @field_validator("Data", mode="before")
    @classmethod
    def validate_data(cls, value, info):
        generic_type = getattr(cls, "__generic_type__", None)
        if generic_type is None and hasattr(cls, "__parameters__"):
            parameters = cls.__parameters__  # type: ignore
            if parameters and len(parameters) == 1:
                generic_type = parameters[0]

        if generic_type and value is not None:
            type_adapter = TypeAdapter(generic_type)
            return type_adapter.validate_python(value)

        return value


class ServiceResultError(BaseModel):
    Succeeded: bool
    Error: ErrorModel
    Data: Optional[Dict]

    def raise_issues(self):
        issues = [] if not isinstance(self.Data, Dict) else [issue for issue in self.Data.values()]
        raise Exception(self.Error.Message + " " + " ".join([", ".join(issue) for issue in issues]))


class GeoJsonModel(BaseModel):
    type: str  # The GeoJSON type (e.g. "Polygon", "MultiPolygon", "GeometryCollection")
    coordinates: Optional[
        Union[
            List[List[List[float]]],  # For "Polygon"
            List[List[List[List[float]]]],  # For "MultiPolygon"
        ]
    ] = None
    geometries: Optional[List["GeoJsonModel"]] = None  # For "GeometryCollection"

    @staticmethod
    def from_geojson(geojson_data: dict) -> "GeoJsonModel":
        return GeoJsonModel.model_validate(geojson_data)

    def to_geojson(self) -> dict:
        return self.model_dump(exclude_none=True)

    def to_wkt(self) -> str:
        """
        Converts the GeoJsonModel to WKT using Shapely.
        """
        from shapely.geometry import shape

        shapely_geometry = shape(self.to_geojson())
        return shapely_geometry.wkt


# -----------------------------------
# Get API Key Info Models
# -----------------------------------


class ApiKeyData(BaseModel):
    Key: str
    CreditAmount: float
    EuroCreditAmount: float
    CreditLimit: int
    EuroCreditLimit: int
    ContactInfo: str
    Email: Optional[str]
    MaxConcurrentConnections: int
    MaxCompositeAreaKm2: int
    MaxTotalBands: int
    CurrentMonthCosts: float
    NextMonthCosts: float


class ApiKeyInfoQueryResponseDto(ServiceResult[ApiKeyData]):
    __generic_type__ = ApiKeyData


# --------------------------------------------------
# Search Available Imagery Request Model
# --------------------------------------------------


class SearchAvailableImageryQueryDto(BaseModel):
    Wkt: Optional[str] = None
    GeoJson: Optional[GeoJsonModel] = None
    From: Optional[date] = None
    Until: Optional[date] = None

    @model_validator(mode="before")
    def check_only_one_field_set(cls, values):
        wkt = values.get("Wkt")
        geojson = values.get("GeoJson")

        fields_set = sum(bool(field) for field in [wkt, geojson])

        if fields_set == 0:
            raise ValueError("One of Wkt or GeoJson must be provided.")
        if fields_set > 1:
            raise ValueError("Only one of Wkt or GeoJson can be provided at a time.")

        return values


class DatesByGeogModel(BaseModel):
    Wkt: str
    Dates: List[str]


class ModelImageDatesModel(BaseModel):
    Model: str
    SatelliteConstellations: List[str]
    DatesByGeog: List[DatesByGeogModel]


class SearchAvailableImageryData(BaseModel):
    ModelImageDates: List[ModelImageDatesModel]


class SearchAvailableImageryQueryResponseDto(ServiceResult[SearchAvailableImageryData]):
    __generic_type__ = SearchAvailableImageryData


# ----------------------------------------------------
# Process Composite Estimate Query Models
# ----------------------------------------------------


class ProcessCompositeEstimateQueryDto(BaseModel):
    Wkt: Optional[str] = None
    GeoJson: Optional[GeoJsonModel] = None
    Resolution: int = 10  # pixel resolution in meters, check api documentation for available options
    FileType: str = "tif"  # check api documentation for available options
    EpsgProjection: int  # 4326, 32632, or any other valid EPSG
    DataType: str = "int16"  # check api documentation for available options
    UtmDataSelectionMode: str = "combined_utm"  # only applicable with UTM EPSGs, check api documentation for available options
    Bandnames: str = "all"  # check api documentation for available options

    @model_validator(mode="before")
    def check_only_one_field_set(cls, values):
        wkt = values.get("Wkt")
        geojson = values.get("GeoJson")

        fields_set = sum(bool(field) for field in [wkt, geojson])

        if fields_set == 0:
            raise ValueError("One of Wkt or GeoJson must be provided.")
        if fields_set > 1:
            raise ValueError("Only one of Wkt or GeoJson can be provided at a time.")

        return values


class ProcessCompositeEstimateData(BaseModel):
    AreaEstimateKm2: float
    CreditEstimate: float


class ProcessCompositeEstimateQueryResponseDto(ServiceResult[ProcessCompositeEstimateData]):
    __generic_type__ = ProcessCompositeEstimateData


# -------------------------------------------------
# Process Composite Command Models
# -------------------------------------------------


class ProcessCompositeCommandDto(ProcessCompositeEstimateQueryDto):
    """
    The `PixelSelectionMode` parameter controls which pixels are included:

    Intersect: Includes all pixels that intersect the geometry (default).
    Contained: Includes only pixels fully within the geometry.
    """

    Date: date
    PixelSelectionMode: str
    SatelliteConstellations: List[str]  # check documentation for available options
    Model: str  # check documentation for available options
    UtmGridForcePixelResolutionSize: bool  #

    model_config = {
        "json_encoders": {
            date: lambda v: v.isoformat(),  # Serialize dates to ISO 8601 strings
        }
    }


class ProcessCompositeErrorResponseDto(ServiceResultError):
    pass


# -------------------------------------------------
# Tasking Models Query Models
# -------------------------------------------------


class SupportedSatelliteConstellationModel(BaseModel):
    SatelliteConstellation: str
    Optional: bool


class TaskingModelsModel(BaseModel):
    Model: str
    SupportedSatelliteConstellations: List[SupportedSatelliteConstellationModel]


class TaskingModelsData(BaseModel):
    TaskingModels: List[TaskingModelsModel]


class TaskingModelsQueryResponseDto(ServiceResult[TaskingModelsData]):
    __generic_type__ = TaskingModelsData


# -------------------------------------------------
# Tasking Orders Query Models
# -------------------------------------------------


class TaskOrderDto(BaseModel):
    TaskOrderGuid: str
    BillingCycle: str  # Monthly or Yearly
    OrderingProcessStatus: str  # check documentation for available options
    StorageMonths: int
    ApiRequests: int
    ImageFrequency: int
    TaskOrderAreaKm2: float
    Model: str  # check documentation for available options
    ReferenceDate: date
    From: date
    To: Optional[date]
    SatelliteConstellations: List[str]  # check documentation for available options
    Tiles: Optional[List[str]]
    Wkt: Optional[str]


class TaskingOrdersData(BaseModel):
    TaskOrders: List[TaskOrderDto]


class TaskingOrdersQueryResponseDto(ServiceResult[TaskingOrdersData]):
    __generic_type__ = TaskingOrdersData


# -------------------------------------------------
# Tasking Order Create Command and Estimate Query Models
# -------------------------------------------------


class CreateTaskingOrderEstimateQueryAndCreateCommandDto(BaseModel):
    StorageMonths: int
    ApiRequests: int
    ImageFrequency: int
    Model: str  # check api documentation for available options
    ReferenceDate: date
    From: date
    To: Optional[date]
    SatelliteConstellations: List[str]  # check api documentation for available options
    Tiles: Optional[List[uuid.UUID]] = None
    Wkt: Optional[str] = None  # Must be a geometrycollection of polygon and/or multipolygons. Each Polygon or MultiPolygon count as an AOI of minimum 1 km2 w.r.t. pricing
    GeoJson: Optional[GeoJsonModel] = None

    @model_validator(mode="before")
    def check_only_one_field_set(cls, values):
        wkt = values.get("Wkt")
        geojson = values.get("GeoJson")

        fields_set = sum(bool(field) for field in [wkt, geojson])

        if fields_set == 0:
            raise ValueError("One of Wkt or GeoJson must be provided.")
        if fields_set > 1:
            raise ValueError("Only one of Wkt or GeoJson can be provided at a time.")

        return values


class TaskingOrderEstimateCostsDto(BaseModel):
    CurrencyCode: str
    CurrentMonthOrderCostEstimate: float
    CurrentMonthStorageCosts: float
    NextMonthOrderCostEstimate: float
    NextMonthStorageCosts: float


class TaskingOrderEstimateQueryResponseData(BaseModel):
    StorageMonths: int
    ApiRequests: int
    Model: str  # check api documentation for available options
    CancellationDate: date
    AreaKm2: float
    AreaKm2BeforeMinimum1Km2PerAoi: float  # The Area of AoIs following the rule of AoI must be minimum 1 km2
    CurrentMonthCost: float
    NextMonthCost: float
    Costs: TaskingOrderEstimateCostsDto
    Tiles: Optional[List[str]]
    AreasOfInterestWkt: str  # the input GeometryCollection converted to bounding boxes used for the order
    SatelliteConstellations: List[str]  # check api documentation for available options
    ImageDates: List[date]


class TaskingOrderEstimateQueryResponseDto(ServiceResult[TaskingOrderEstimateQueryResponseData]):
    __generic_type__ = TaskingOrderEstimateQueryResponseData


class TaskingOrderCreateCommandResponseDto(ServiceResult[TaskOrderDto]):
    __generic_type__ = TaskOrderDto


# -------------------------------------------------
# Tasking Tile Search Models
# -------------------------------------------------


class TaskingTileSearchQueryDto(BaseModel):
    Wkt: Optional[str] = None
    GeoJson: Optional[GeoJsonModel] = None
    TileGuids: Optional[List[uuid.UUID]] = None

    @model_validator(mode="before")
    def check_only_one_field_set(cls, values):
        wkt = values.get("Wkt")
        geojson = values.get("GeoJson")
        tile_guids = values.get("TileGuids")

        fields_set = sum(bool(field) for field in [wkt, geojson, tile_guids])

        if fields_set == 0:
            raise ValueError("One of Wkt, GeoJson, or TileGuids must be provided.")
        if fields_set > 1:
            raise ValueError("Only one of Wkt, GeoJson, or TileGuids can be provided at a time.")

        return values


class TaskingTileDto(BaseModel):
    Guid: str
    Epsg: str
    DataGeogWkt: str


class TaskingTileSearchQueryResponseData(BaseModel):
    Tiles: List[TaskingTileDto]


class TaskingTileSearchQueryResponseDto(ServiceResult[TaskingTileSearchQueryResponseData]):
    __generic_type__ = TaskingTileSearchQueryResponseData
