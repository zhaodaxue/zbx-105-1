from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
from app.models import Role, ApplicationStatus


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    username: str
    full_name: str
    role: Role


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class ApplicationBase(BaseModel):
    stall_number: str = Field(..., min_length=1, max_length=20, description="摊位编号，格式如 A-01")
    stall_area: str = Field(..., min_length=1, max_length=50, description="摊位所属区域")
    peak_kw: float = Field(..., gt=0, le=100, description="预估峰值千瓦")
    start_time: datetime
    end_time: datetime
    has_open_flame: bool = Field(default=False, description="是否使用明火厨灶")

    @field_validator("end_time")
    def end_time_must_be_after_start_time(cls, v, info):
        if v <= info.data["start_time"]:
            raise ValueError("用电结束时间必须晚于开始时间")
        return v


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationReview(BaseModel):
    status: ApplicationStatus
    reject_reason: Optional[str] = Field(None, max_length=500)
    meter_number: Optional[str] = Field(None, max_length=50)


class ApplicationResponse(ApplicationBase):
    id: int
    status: ApplicationStatus
    reject_reason: Optional[str] = None
    meter_number: Optional[str] = None
    applicant_id: int
    applicant_name: Optional[str] = None
    reviewer_id: Optional[int] = None
    reviewer_name: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ApplicationListResponse(BaseModel):
    items: List[ApplicationResponse]
    total: int


class AreaStats(BaseModel):
    stall_area: str
    total_kw: float
    count: int


class DailyStatsResponse(BaseModel):
    date: str
    areas: List[AreaStats]
    grand_total_kw: float
    grand_total_count: int
