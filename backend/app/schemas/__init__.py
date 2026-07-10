from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


# ============================================================
# Unified Response
# ============================================================

class PaginationMeta(BaseModel):
    page: int = 1
    page_size: int = 20
    total: int = 0
    total_pages: int = 0


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    pagination: Optional[PaginationMeta] = None
    meta: Optional[dict] = None


# ============================================================
# Brand Schemas
# ============================================================

class BrandBase(BaseModel):
    name: str
    slug: str
    country: Optional[str] = None
    founded_year: Optional[int] = None
    parent_company: Optional[str] = None
    headquarters: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True


class BrandCreate(BrandBase):
    pass


class BrandOut(BaseModel):
    id: int
    name: str
    slug: str
    country: Optional[str] = None
    founded_year: Optional[int] = None
    parent_company: Optional[str] = None
    headquarters: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    instagram_url: Optional[str] = None
    twitter_url: Optional[str] = None
    tiktok_url: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    price_tier: Optional[str] = None
    instagram_followers: Optional[int] = None
    monthly_web_visits: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# Dimension sub-schemas

class BrandCategoryOut(BaseModel):
    category_id: int
    category_name: Optional[str] = None
    category_slug: Optional[str] = None
    is_primary: bool = False

    model_config = {"from_attributes": True}


class BrandPositioningOut(BaseModel):
    price_tier: Optional[str] = None
    brand_tone: Optional[str] = None
    core_value_proposition: Optional[str] = None
    usp: Optional[str] = None
    brand_story: Optional[str] = None
    source_url: Optional[str] = None
    source_type: Optional[str] = None
    last_verified_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PricingStrategyOut(BaseModel):
    category_name: Optional[str] = None
    price_range_min: Optional[float] = None
    price_range_max: Optional[float] = None
    avg_price: Optional[float] = None
    discount_frequency: Optional[str] = None
    typical_discount_pct: Optional[float] = None
    has_membership: bool = False
    membership_price: Optional[float] = None
    membership_model: Optional[str] = None
    data_as_of: Optional[date] = None
    source_url: Optional[str] = None
    source_type: Optional[str] = None

    model_config = {"from_attributes": True}


class TargetDemographicsOut(BaseModel):
    age_range: Optional[str] = None
    gender_skew: Optional[str] = None
    income_level: Optional[str] = None
    lifestyle_tags: Optional[Any] = None
    core_scenarios: Optional[Any] = None
    source_url: Optional[str] = None
    source_type: Optional[str] = None

    model_config = {"from_attributes": True}


class ProductStrategyOut(BaseModel):
    hero_products: Optional[Any] = None
    launch_cadence: Optional[str] = None
    sku_count_estimate: Optional[int] = None
    has_sustainable_line: bool = False
    collab_strategy: Optional[str] = None
    recent_collabs: Optional[Any] = None
    tech_innovations: Optional[Any] = None
    category_expansion: Optional[Any] = None
    data_as_of: Optional[date] = None
    source_url: Optional[str] = None
    source_type: Optional[str] = None

    model_config = {"from_attributes": True}


class ChannelStrategyOut(BaseModel):
    dtc_pct: Optional[float] = None
    wholesale_pct: Optional[float] = None
    own_stores_na: Optional[int] = None
    retail_partners: Optional[Any] = None
    ecommerce_platforms: Optional[Any] = None
    international_markets: Optional[Any] = None
    data_as_of: Optional[date] = None
    source_url: Optional[str] = None
    source_type: Optional[str] = None

    model_config = {"from_attributes": True}


class SocialMediaMetricsOut(BaseModel):
    platform: Optional[str] = None
    followers: Optional[int] = None
    engagement_rate: Optional[float] = None
    avg_likes: Optional[int] = None
    avg_comments: Optional[int] = None
    post_frequency: Optional[str] = None
    top_hashtags: Optional[Any] = None
    key_kols: Optional[Any] = None
    data_as_of: Optional[date] = None
    source_url: Optional[str] = None
    source_type: Optional[str] = None

    model_config = {"from_attributes": True}


class DigitalCapabilityOut(BaseModel):
    monthly_web_visits: Optional[int] = None
    app_rating: Optional[float] = None
    app_downloads: Optional[str] = None
    has_personalization: bool = False
    has_virtual_tryon: bool = False
    has_community_feature: bool = False
    has_membership_program: bool = False
    membership_name: Optional[str] = None
    ai_features: Optional[Any] = None
    data_as_of: Optional[date] = None
    source_url: Optional[str] = None
    source_type: Optional[str] = None

    model_config = {"from_attributes": True}


class FinancialPerformanceOut(BaseModel):
    fiscal_year: Optional[int] = None
    revenue: Optional[float] = None
    revenue_growth_pct: Optional[float] = None
    gross_margin_pct: Optional[float] = None
    na_revenue_pct: Optional[float] = None
    is_estimated: bool = False
    data_source: Optional[str] = None

    model_config = {"from_attributes": True}


class CustomerSentimentOut(BaseModel):
    platform: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    positive_themes: Optional[Any] = None
    negative_themes: Optional[Any] = None
    nps_score: Optional[int] = None
    data_as_of: Optional[date] = None
    source_url: Optional[str] = None
    source_type: Optional[str] = None

    model_config = {"from_attributes": True}


class CompetitiveEventOut(BaseModel):
    id: int
    brand_id: int
    brand_name: Optional[str] = None
    brand_slug: Optional[str] = None
    event_type: str
    title: str
    description: Optional[str] = None
    event_date: Optional[date] = None
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    source_quote: Optional[str] = None
    importance: Optional[str] = "medium"
    tags: Optional[Any] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class BrandDetailOut(BrandOut):
    categories: List[BrandCategoryOut] = []
    positioning: Optional[BrandPositioningOut] = None
    pricing: List[PricingStrategyOut] = []
    demographics: Optional[TargetDemographicsOut] = None
    product_strategy: Optional[ProductStrategyOut] = None
    channel_strategy: Optional[ChannelStrategyOut] = None
    social_media: List[SocialMediaMetricsOut] = []
    digital: Optional[DigitalCapabilityOut] = None
    financials: List[FinancialPerformanceOut] = []
    sentiment: List[CustomerSentimentOut] = []
    events: List[CompetitiveEventOut] = []


class BrandListOut(BaseModel):
    items: List[BrandOut]
    total: int


# ============================================================
# Category Schemas
# ============================================================

class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    parent_id: Optional[int] = None
    level: int = 1
    sort_order: int = 0

    model_config = {"from_attributes": True}


class CategoryTreeNode(CategoryOut):
    children: List[CategoryTreeNode] = []


# ============================================================
# Compare Schemas
# ============================================================

class CompareRequest(BaseModel):
    brand_slugs: List[str] = Field(..., min_length=2)
    dimensions: Optional[List[str]] = None


class CompareDimensionData(BaseModel):
    brand_slug: str
    brand_name: str
    dimension: str
    data: Any


class CompareResponse(BaseModel):
    brand_slugs: List[str]
    dimensions: List[str]
    data: List[CompareDimensionData]


class ComparisonGroupOut(BaseModel):
    id: int
    name: str
    brand_ids: Any
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ComparisonGroupCreate(BaseModel):
    name: str
    brand_ids: List[int]


# ============================================================
# Event Schemas
# ============================================================

class EventListOut(BaseModel):
    items: List[CompetitiveEventOut]
    total: int


class EventTimelineItem(BaseModel):
    id: int
    brand_name: str
    event_type: str
    title: str
    event_date: Optional[date] = None
    importance: Optional[str] = "medium"


class EventRefreshOut(BaseModel):
    refreshed_count: int
    new_events: List[CompetitiveEventOut]
    refreshed_at: date
    message: Optional[str] = None

    model_config = {"from_attributes": True}


# ============================================================
# Import Schemas
# ============================================================

class ImportPreviewOut(BaseModel):
    file_name: str
    sheet_name: Optional[str] = None
    total_rows: int
    valid_rows: int
    invalid_rows: int
    columns: List[str]
    sample_data: List[dict]
    errors: List[dict] = []


class ImportExecuteRequest(BaseModel):
    file_name: str
    sheet_name: Optional[str] = None
    data_type: str  # brands, pricing, financials, events, etc.
    skip_invalid: bool = True


class ImportHistoryItem(BaseModel):
    id: int
    file_name: str
    data_type: str
    total_rows: int
    imported_rows: int
    skipped_rows: int
    status: str
    created_at: Optional[datetime] = None


# ============================================================
# Trend Schemas
# ============================================================

class RevenueTrendItem(BaseModel):
    brand_id: int
    brand_name: str
    brand_slug: str
    fiscal_year: int
    revenue: Optional[float] = None
    revenue_growth_pct: Optional[float] = None


class SocialTrendItem(BaseModel):
    brand_id: int
    brand_name: str
    brand_slug: str
    platform: str
    followers: Optional[int] = None
    engagement_rate: Optional[float] = None
    data_as_of: Optional[date] = None


class TrendOverview(BaseModel):
    total_brands: int
    total_categories: int
    avg_revenue_growth: Optional[float] = None
    top_revenue_brands: List[dict] = []
    top_engagement_brands: List[dict] = []


# ============================================================
# Data Source Schemas
# ============================================================

class DataSourceOut(BaseModel):
    id: int
    name: str
    source_type: str
    config: Optional[Any] = None
    last_sync_at: Optional[datetime] = None
    sync_status: Optional[str] = "idle"
    sync_interval: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DataSourceCreate(BaseModel):
    name: str
    source_type: str
    config: Optional[dict] = None
    sync_interval: Optional[str] = None


class DataSourceUpdate(BaseModel):
    name: Optional[str] = None
    source_type: Optional[str] = None
    config: Optional[dict] = None
    sync_interval: Optional[str] = None


# ============================================================
# Search Schemas
# ============================================================

class SearchResult(BaseModel):
    type: str  # brand, category, event
    id: int
    title: str
    subtitle: Optional[str] = None
    slug: Optional[str] = None


# ============================================================
# Stats Schemas
# ============================================================

class StatsOverview(BaseModel):
    total_brands: int
    active_brands: int
    total_categories: int
    total_events: int
    total_financial_records: int
    data_sources_count: int
    events_this_month: Optional[int] = None
    last_updated_at: Optional[datetime] = None


class PriceDistribution(BaseModel):
    tier: str
    count: int


class CountryDistribution(BaseModel):
    country: str
    count: int


# ============================================================
# Export Schemas
# ============================================================

class ExportRequest(BaseModel):
    data_type: str  # brands, financials, events, etc.
    brand_ids: Optional[List[int]] = None
    category_ids: Optional[List[int]] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    format: str = "xlsx"  # xlsx or csv
