import csv
import io
from datetime import datetime, date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Application, Role, ApplicationStatus
from app.schemas import DailyStatsResponse
from app.auth import require_roles

router = APIRouter()


@router.get("/daily", response_model=DailyStatsResponse)
def get_daily_stats(
    target_date: Optional[str] = Query(None, description="统计日期 YYYY-MM-DD，默认今日"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.PLANNER, Role.ELECTRICIAN)),
):
    if target_date:
        try:
            the_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD")
    else:
        the_date = date.today()

    start_of_day = datetime.combine(the_date, datetime.min.time())
    start_of_next = datetime.combine(the_date + timedelta(days=1), datetime.min.time())

    area_rows = (
        db.query(
            Application.stall_area,
            func.sum(Application.peak_kw).label("total_kw"),
            func.count(Application.id).label("cnt"),
        )
        .filter(
            Application.status == ApplicationStatus.APPROVED,
            Application.reviewed_at >= start_of_day,
            Application.reviewed_at < start_of_next,
        )
        .group_by(Application.stall_area)
        .order_by(Application.stall_area)
        .all()
    )

    areas = []
    grand_total_kw = 0.0
    grand_total_count = 0
    for row in area_rows:
        areas.append({
            "stall_area": row.stall_area,
            "total_kw": float(row.total_kw or 0),
            "count": int(row.cnt or 0),
        })
        grand_total_kw += float(row.total_kw or 0)
        grand_total_count += int(row.cnt or 0)

    return {
        "date": the_date.isoformat(),
        "areas": areas,
        "grand_total_kw": grand_total_kw,
        "grand_total_count": grand_total_count,
    }


@router.get("/export-csv")
def export_daily_csv(
    target_date: Optional[str] = Query(None, description="统计日期 YYYY-MM-DD，默认今日"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(Role.PLANNER, Role.ELECTRICIAN)),
):
    if target_date:
        try:
            the_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD")
    else:
        the_date = date.today()

    start_of_day = datetime.combine(the_date, datetime.min.time())
    start_of_next = datetime.combine(the_date + timedelta(days=1), datetime.min.time())

    approved_apps = (
        db.query(Application)
        .filter(
            Application.status == ApplicationStatus.APPROVED,
            Application.reviewed_at >= start_of_day,
            Application.reviewed_at < start_of_next,
        )
        .order_by(Application.stall_area, Application.stall_number)
        .all()
    )

    area_stats = {}
    for app in approved_apps:
        area = app.stall_area
        if area not in area_stats:
            area_stats[area] = {"total_kw": 0.0, "count": 0}
        area_stats[area]["total_kw"] += app.peak_kw
        area_stats[area]["count"] += 1

    buffer = io.StringIO()
    writer = csv.writer(buffer)

    writer.writerow(["丰收节临时摊位用电申报 - 日度摘要"])
    writer.writerow(["统计日期", the_date.isoformat()])
    writer.writerow([])

    writer.writerow(["一、各区域已批千瓦合计"])
    writer.writerow(["区域", "已批申报数", "合计千瓦(kW)"])
    grand_kw = 0.0
    grand_cnt = 0
    for area in sorted(area_stats.keys()):
        s = area_stats[area]
        writer.writerow([area, s["count"], round(s["total_kw"], 2)])
        grand_kw += s["total_kw"]
        grand_cnt += s["count"]
    writer.writerow(["总计", grand_cnt, round(grand_kw, 2)])
    writer.writerow([])

    writer.writerow(["二、批准申报明细"])
    writer.writerow([
        "ID", "区域", "摊位编号", "峰值千瓦(kW)", "用电开始", "用电结束",
        "是否明火", "电表编号", "申请人", "审核时间",
    ])
    for app in approved_apps:
        writer.writerow([
            app.id,
            app.stall_area,
            app.stall_number,
            app.peak_kw,
            app.start_time.strftime("%Y-%m-%d %H:%M"),
            app.end_time.strftime("%Y-%m-%d %H:%M"),
            "是" if app.has_open_flame else "否",
            app.meter_number or "",
            app.applicant.full_name if app.applicant else "",
            app.reviewed_at.strftime("%Y-%m-%d %H:%M") if app.reviewed_at else "",
        ])

    buffer.seek(0)
    filename = f"用电申报摘要_{the_date.isoformat()}.csv"

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv; charset=utf-8-sig",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{filename}",
        },
    )
