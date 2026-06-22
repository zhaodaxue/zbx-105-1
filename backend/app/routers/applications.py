from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Application, User, Role, ApplicationStatus
from app.schemas import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationReview,
    ApplicationListResponse,
)
from app.auth import get_current_user, require_roles

router = APIRouter()


def _application_to_response(app: Application) -> dict:
    data = {
        "id": app.id,
        "stall_number": app.stall_number,
        "stall_area": app.stall_area,
        "peak_kw": app.peak_kw,
        "start_time": app.start_time,
        "end_time": app.end_time,
        "has_open_flame": app.has_open_flame,
        "status": app.status,
        "reject_reason": app.reject_reason,
        "meter_number": app.meter_number,
        "applicant_id": app.applicant_id,
        "applicant_name": app.applicant.full_name if app.applicant else None,
        "reviewer_id": app.reviewer_id,
        "reviewer_name": app.reviewer.full_name if app.reviewer else None,
        "created_at": app.created_at,
        "reviewed_at": app.reviewed_at,
    }
    return data


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.VENDOR)),
):
    app = Application(
        **data.model_dump(),
        applicant_id=current_user.id,
        status=ApplicationStatus.PENDING,
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return _application_to_response(app)


@router.get("", response_model=ApplicationListResponse)
def list_applications(
    status: Optional[ApplicationStatus] = Query(None, description="按状态筛选"),
    stall_area: Optional[str] = Query(None, description="按区域筛选"),
    stall_number: Optional[str] = Query(None, description="按摊位号筛选"),
    start_date: Optional[str] = Query(None, description="创建日期开始(YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="创建日期结束(YYYY-MM-DD)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Application)

    if current_user.role == Role.VENDOR:
        query = query.filter(Application.applicant_id == current_user.id)

    if status:
        query = query.filter(Application.status == status)
    if stall_area:
        query = query.filter(Application.stall_area.ilike(f"%{stall_area}%"))
    if stall_number:
        query = query.filter(Application.stall_number.ilike(f"%{stall_number}%"))
    if start_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        query = query.filter(Application.created_at >= start_dt)
    if end_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        import datetime as dt
        end_dt = end_dt + dt.timedelta(days=1)
        query = query.filter(Application.created_at < end_dt)

    total = query.count()
    items = (
        query.order_by(Application.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "items": [_application_to_response(item) for item in items],
        "total": total,
    }


@router.get("/{app_id}", response_model=ApplicationResponse)
def get_application(
    app_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="申报记录不存在")
    if current_user.role == Role.VENDOR and app.applicant_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看他人申报")
    return _application_to_response(app)


@router.put("/{app_id}/review", response_model=ApplicationResponse)
def review_application(
    app_id: int,
    data: ApplicationReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.ELECTRICIAN)),
):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="申报记录不存在")

    if app.status != ApplicationStatus.PENDING:
        raise HTTPException(status_code=400, detail="该申报已审核，不可重复操作")

    if data.status == ApplicationStatus.REJECTED:
        if not data.reject_reason or not data.reject_reason.strip():
            raise HTTPException(status_code=400, detail="驳回必须填写原因")
        app.reject_reason = data.reject_reason.strip()
        app.meter_number = None
    elif data.status == ApplicationStatus.APPROVED:
        if not data.meter_number or not data.meter_number.strip():
            raise HTTPException(status_code=400, detail="批准必须分配临时电表编号")
        app.meter_number = data.meter_number.strip()
        app.reject_reason = None

    app.status = data.status
    app.reviewer_id = current_user.id
    app.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(app)
    return _application_to_response(app)
