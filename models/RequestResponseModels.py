"""
Collection of Request and Response models used by the ClearSky Vision API
"""

from typing import Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, root_validator
from datetime import date

T = TypeVar("T")


class ErrorModel(BaseModel):
    Message: str
    Code: int


class ServiceResult(BaseModel, Generic[T]):
    Succeeded: bool
    Error: Optional["ErrorModel"]
    Data: Optional[T]


class ServiceResultError(BaseModel):
    Succeeded: bool
    Error: ErrorModel
    Data: Optional[Dict[str, str]]


class GeoJsonModel(BaseModel):
    type: str  # The GeoJSON type (e.g. "Polygon", "MultiPolygon", "GeometryCollection")
    coordinates: Optional[
        Union[
            List[List[List[float]]],  # For "Polygon"
            List[List[List[List[float]]]],  # For "MultiPolygon"
        ]
    ] = None
    geometries: Optional[List["GeoJsonModel"]] = None  # For "GeometryCollection"


# -----------------------------------
# Get API Key Info Models
# -----------------------------------


class ApiKeyData(BaseModel):
    Key: str
    CreditAmount: int
    EuroCreditAmount: int
    CreditLimit: int
    EuroCreditLimit: int
    ContactInfo: str
    Email: Optional[str]
    MaxConcurrentConnections: int
    MaxCompositeAreaKm2: int
    MaxTotalBands: int


class ApiKeyInfoQueryResponseDto(ServiceResult[ApiKeyData]):
    pass


# --------------------------------------------------
# Search Available Imagery Request Model
# --------------------------------------------------


class SearchAvailableImageryQueryDto(BaseModel):
    Wkt: Optional[str]
    GeoJson: Optional[GeoJsonModel]
    From: Optional[date]
    Until: Optional[date]

    @root_validator
    def check_wkt_or_geojson(cls, values):
        wkt, geojson = values.get("Wkt"), values.get("GeoJson")
        if not wkt and not geojson:
            raise ValueError("Either Wkt or GeoJson must be provided.")
        if wkt and geojson:
            raise ValueError("Only one of Wkt or GeoJson must be provided.")
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
    pass


# ----------------------------------------------------
# Process Composite Estimate Query Models
# ----------------------------------------------------


class ProcessCompositeEstimateQueryDto(BaseModel):
    Wkt: Optional[str]
    GeoJson: Optional[GeoJsonModel]
    Resolution: int = 10  # pixel resolution in meters, check api documentation for available options
    FileType: str = "tif"  # check api documentation for available options
    EpsgProjection: int  # 4326, 32632, or any other valid EPSG
    DataType: str = "int16"  # check api documentation for available options
    UtmDataSelectionMode: str = "combined_utm"  # only applicable with UTM EPSGs, check api documentation for available options
    Bandnames: str = "all"  # check api documentation for available options

    @root_validator
    def check_wkt_or_geojson(cls, values):
        wkt, geojson = values.get("Wkt"), values.get("GeoJson")
        if not wkt and not geojson:
            raise ValueError("Either Wkt or GeoJson must be provided.")
        if wkt and geojson:
            raise ValueError("Only one of Wkt or GeoJson must be provided.")
        return values


class ProcessCompositeEstimateData(BaseModel):
    AreaEstimateKm2: float
    CreditEstimate: int


class ProcessCompositeEstimateQueryResponseDto(ServiceResult[ProcessCompositeEstimateData]):
    pass


# -------------------------------------------------
# Process Composite Command Models
# -------------------------------------------------


class ProcessCompositeCommandDto(ProcessCompositeEstimateQueryDto):
    Date: date
    PixelSelectionMode: str  # check api documentation for available options
    SatelliteConstellations: List[str]  # check api documentation for available options
    Model: str  # check api documentation for available options
    UtmGridForcePixelResolutionSize: bool  #


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
    pass


# -------------------------------------------------
# Tasking Orders Query Models
# -------------------------------------------------


class TaskOrderDto(BaseModel):
    TaskOrderGuid: str
    BillingCycle: str  # Monthly or Yearly
    OrderingProcessStatus: str  # check api documentation for available options
    StorageMonths: int
    ApiRequests: int
    ImageFrequency: int
    TaskOrderAreaKm2: float
    Model: str  # check api documentation for available options
    ReferenceDate: date
    From: date
    To: Optional[date]
    SatelliteConstellations: List[str]  # check api documentation for available options
    Tiles: Optional[List[str]]
    Wkt: Optional[str]


class TaskingOrdersData(BaseModel):
    TaskOrders: List[TaskOrderDto]


class TaskingOrdersQueryResponseDto(ServiceResult[TaskingOrdersData]):
    pass


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
    Tiles: Optional[List[str]]
    Wkt: Optional[str]
    GeoJson: Optional[GeoJsonModel]

    @root_validator
    def check_wkt_or_geojson(cls, values):
        wkt, geojson = values.get("Wkt"), values.get("GeoJson")
        if not wkt and not geojson:
            raise ValueError("Either Wkt or GeoJson must be provided.")
        if wkt and geojson:
            raise ValueError("Only one of Wkt or GeoJson must be provided.")
        return values


class TaskingOrderEstimateCostsDto(BaseModel):
    CurrencyCode: str
    HistoricOrderCostEstimate: float
    HistoricStorageCosts: float
    RecurringOrderCostEstimate: float
    RecurringStorageCosts: float


class TaskingOrderEstimateQueryResponseData(BaseModel):
    StorageMonths: int
    ApiRequests: int
    Model: str  # check api documentation for available options
    CancellationDate: date
    AreaKm2: float
    AreaKm2BeforeMinimum1Km2PerAoi: float  # The Area of AoIs following the rule of AoI must be minimum 1 km2
    TotalHistoricCost: float
    NextMonthRecurringCost: float
    Costs: TaskingOrderEstimateCostsDto
    Tiles: Optional[List[str]]
    AreasOfInterestWkt: str
    SatelliteConstellations: List[str]  # check api documentation for available options
    HistoricImageDates: List[date]
    RecurringImageDates: List[date]


class TaskingOrderEstimateQueryResponseDto(ServiceResult[TaskingOrderEstimateQueryResponseData]):
    pass


class TaskingOrderCreateCommandResponseDto(ServiceResult[TaskOrderDto]):
    pass


# -------------------------------------------------
# Tasking Tile Search Models
# -------------------------------------------------


class TaskingTileSearchQueryDto(BaseModel):
    Wkt: Optional[str]
    GeoJson: Optional[GeoJsonModel]

    @root_validator
    def check_wkt_or_geojson(cls, values):
        wkt, geojson = values.get("Wkt"), values.get("GeoJson")
        if not wkt and not geojson:
            raise ValueError("Either Wkt or GeoJson must be provided.")
        if wkt and geojson:
            raise ValueError("Only one of Wkt or GeoJson must be provided.")
        return values


class TaskingTileDto(BaseModel):
    Guid: str
    Epsg: str
    DataGeogWkt: str


class TaskingTileSearchQueryResponseData(BaseModel):
    Tiles: List[TaskingTileDto]


class TaskingTileSearchQueryResponseDto(ServiceResult[TaskingTileSearchQueryResponseData]):
    pass
