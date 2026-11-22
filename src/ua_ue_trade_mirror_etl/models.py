from pydantic import BaseModel, ConfigDict, Field, model_validator


class UAcustomsRecord(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, frozen=True)

    partner_iso2: str = Field(min_length=2, max_length=2)
    partner_name: str = Field(min_length=1)
    year: int = Field(ge=2000, le=2100)
    hs_chapter: str = Field(min_length=2, max_length=10)
    total_value_usd: float = Field(ge=0)
    export_usd: float = Field(ge=0)
    import_usd: float = Field(ge=0)
    balance_usd: float

    @model_validator(mode="after")
    def check_math_consistency(self) -> "UAcustomsRecord":
        if abs(self.total_value_usd - (self.export_usd + self.import_usd)) > 1.0:
            raise ValueError("total_value_usd != export_usd + import_usd")
        if abs(self.balance_usd - (self.export_usd - self.import_usd)) > 1.0:
            raise ValueError("balance_usd != export_usd - import_usd")
        return self


class MirrorTradeRecord(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, frozen=True)

    partner_iso2: str = Field(min_length=2, max_length=2)
    partner_name: str = Field(min_length=1)
    year: int = Field(ge=2000, le=2100)
    hs_chapter: str = Field(min_length=2, max_length=10)
    ua_export_usd: float = Field(ge=0)
    eu_import_usd: float = Field(ge=0)
    mirror_gap_usd: float
    is_anomaly: bool = False
