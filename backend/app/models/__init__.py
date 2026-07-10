from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, Date, BigInteger,
    ForeignKey, JSON, TIMESTAMP, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    country = Column(String(50))
    founded_year = Column(Integer)
    parent_company = Column(String(100))
    headquarters = Column(String(200))
    logo_url = Column(String(500))
    website = Column(String(200))
    instagram_url = Column(String(300))
    twitter_url = Column(String(300))
    tiktok_url = Column(String(300))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    brand_categories = relationship("BrandCategory", back_populates="brand", cascade="all, delete-orphan")
    positioning = relationship("BrandPositioning", back_populates="brand", uselist=False, cascade="all, delete-orphan")
    pricing = relationship("PricingStrategy", back_populates="brand", cascade="all, delete-orphan")
    demographics = relationship("TargetDemographics", back_populates="brand", uselist=False, cascade="all, delete-orphan")
    product_strategy = relationship("ProductStrategy", back_populates="brand", uselist=False, cascade="all, delete-orphan")
    channel_strategy = relationship("ChannelStrategy", back_populates="brand", uselist=False, cascade="all, delete-orphan")
    social_media = relationship("SocialMediaMetrics", back_populates="brand", cascade="all, delete-orphan")
    digital = relationship("DigitalCapability", back_populates="brand", uselist=False, cascade="all, delete-orphan")
    financials = relationship("FinancialPerformance", back_populates="brand", cascade="all, delete-orphan")
    sentiment = relationship("CustomerSentiment", back_populates="brand", cascade="all, delete-orphan")
    events = relationship("CompetitiveEvent", back_populates="brand", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    level = Column(Integer, nullable=False, default=1)
    sort_order = Column(Integer, default=0)

    parent = relationship("Category", remote_side=[id], backref="children")
    brand_categories = relationship("BrandCategory", back_populates="category", cascade="all, delete-orphan")


class BrandCategory(Base):
    __tablename__ = "brand_categories"

    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)
    is_primary = Column(Boolean, default=False)

    brand = relationship("Brand", back_populates="brand_categories")
    category = relationship("Category", back_populates="brand_categories")


class BrandPositioning(Base):
    __tablename__ = "brand_positioning"

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, unique=True)
    price_tier = Column(String(20))  # Luxury, Premium, Mid, Mass
    brand_tone = Column(String(50))  # Performance, Lifestyle, Fashion, Outdoor, Hybrid
    core_value_proposition = Column(Text)
    usp = Column(Text)
    brand_story = Column(Text)
    source_url = Column(String(500))
    source_type = Column(String(30), default="manual")
    last_verified_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    brand = relationship("Brand", back_populates="positioning")


class PricingStrategy(Base):
    __tablename__ = "pricing_strategy"

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False)
    category_name = Column(String(50))
    price_range_min = Column(Float)
    price_range_max = Column(Float)
    avg_price = Column(Float)
    discount_frequency = Column(String(30))
    typical_discount_pct = Column(Float)
    has_membership = Column(Boolean, default=False)
    membership_price = Column(Float)
    membership_model = Column(Text)
    data_as_of = Column(Date)
    source_url = Column(String(500))
    source_type = Column(String(30), default="manual")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    brand = relationship("Brand", back_populates="pricing")


class TargetDemographics(Base):
    __tablename__ = "target_demographics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, unique=True)
    age_range = Column(String(20))
    gender_skew = Column(String(30))
    income_level = Column(String(30))
    lifestyle_tags = Column(JSON)
    core_scenarios = Column(JSON)
    source_url = Column(String(500))
    source_type = Column(String(30), default="manual")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    brand = relationship("Brand", back_populates="demographics")


class ProductStrategy(Base):
    __tablename__ = "product_strategy"

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, unique=True)
    hero_products = Column(JSON)
    launch_cadence = Column(String(50))
    sku_count_estimate = Column(Integer)
    has_sustainable_line = Column(Boolean, default=False)
    collab_strategy = Column(Text)
    recent_collabs = Column(JSON)
    tech_innovations = Column(JSON)
    category_expansion = Column(JSON)
    data_as_of = Column(Date)
    source_url = Column(String(500))
    source_type = Column(String(30), default="manual")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    brand = relationship("Brand", back_populates="product_strategy")


class ChannelStrategy(Base):
    __tablename__ = "channel_strategy"

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, unique=True)
    dtc_pct = Column(Float)
    wholesale_pct = Column(Float)
    own_stores_na = Column(Integer)
    retail_partners = Column(JSON)
    ecommerce_platforms = Column(JSON)
    international_markets = Column(JSON)
    data_as_of = Column(Date)
    source_url = Column(String(500))
    source_type = Column(String(30), default="manual")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    brand = relationship("Brand", back_populates="channel_strategy")


class SocialMediaMetrics(Base):
    __tablename__ = "social_media_metrics"
    __table_args__ = (UniqueConstraint("brand_id", "platform", "data_as_of"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String(30), nullable=False)
    followers = Column(BigInteger)
    engagement_rate = Column(Float)
    avg_likes = Column(Integer)
    avg_comments = Column(Integer)
    post_frequency = Column(String(30))
    top_hashtags = Column(JSON)
    key_kols = Column(JSON)
    data_as_of = Column(Date)
    source_url = Column(String(500))
    source_type = Column(String(30), default="manual")
    created_at = Column(TIMESTAMP, server_default=func.now())

    brand = relationship("Brand", back_populates="social_media")


class DigitalCapability(Base):
    __tablename__ = "digital_capability"

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, unique=True)
    monthly_web_visits = Column(BigInteger)
    app_rating = Column(Float)
    app_downloads = Column(String(50))
    has_personalization = Column(Boolean, default=False)
    has_virtual_tryon = Column(Boolean, default=False)
    has_community_feature = Column(Boolean, default=False)
    has_membership_program = Column(Boolean, default=False)
    membership_name = Column(String(100))
    ai_features = Column(JSON)
    data_as_of = Column(Date)
    source_url = Column(String(500))
    source_type = Column(String(30), default="manual")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    brand = relationship("Brand", back_populates="digital")


class FinancialPerformance(Base):
    __tablename__ = "financial_performance"
    __table_args__ = (UniqueConstraint("brand_id", "fiscal_year"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    revenue = Column(Float)
    revenue_growth_pct = Column(Float)
    gross_margin_pct = Column(Float)
    na_revenue_pct = Column(Float)
    is_estimated = Column(Boolean, default=False)
    data_source = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    brand = relationship("Brand", back_populates="financials")


class CustomerSentiment(Base):
    __tablename__ = "customer_sentiment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String(50), nullable=False)
    rating = Column(Float)
    review_count = Column(Integer)
    positive_themes = Column(JSON)
    negative_themes = Column(JSON)
    nps_score = Column(Integer)
    data_as_of = Column(Date)
    source_url = Column(String(500))
    source_type = Column(String(30), default="manual")
    created_at = Column(TIMESTAMP, server_default=func.now())

    brand = relationship("Brand", back_populates="sentiment")


class CompetitiveEvent(Base):
    __tablename__ = "competitive_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    event_date = Column(Date, index=True)
    source_url = Column(String(500))
    source_name = Column(String(100))
    importance = Column(String(20), default="medium")
    tags = Column(JSON)
    source_quote = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    brand = relationship("Brand", back_populates="events")


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    source_type = Column(String(30), nullable=False)
    config = Column(JSON)
    last_sync_at = Column(TIMESTAMP)
    sync_status = Column(String(20), default="idle")
    sync_interval = Column(String(30))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class ComparisonGroup(Base):
    __tablename__ = "comparison_groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    brand_ids = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
