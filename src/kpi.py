from datetime import date, timedelta
import pandas as pd

from src.auth import authenticated_client, current_role


def _iso(day):
    return day.isoformat() if hasattr(day, "isoformat") else str(day)


def default_range(days=30):
    end = date.today()
    return end - timedelta(days=days - 1), end


def my_kpis(start_date, end_date):
    result = authenticated_client().rpc(
        "get_my_kpis",
        {"p_start": _iso(start_date), "p_end": _iso(end_date)},
    ).execute()
    return result.data or {}


def admin_kpis(start_date, end_date):
    if current_role() not in {"reviewer", "admin"}:
        raise PermissionError("No tienes permisos para consultar KPI globales.")
    result = authenticated_client().rpc(
        "get_admin_kpis",
        {"p_start": _iso(start_date), "p_end": _iso(end_date)},
    ).execute()
    return result.data or {}


def my_sessions(limit=50):
    result = (
        authenticated_client()
        .table("sessions")
        .select(
            "id, started_at, ended_at, status, app_version, "
            "results(relationship, dimensions, frequency, duration, impacts, orientation)"
        )
        .order("started_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data or []


def dataframe_from_counts(mapping, label_col="Categoría", value_col="Cantidad"):
    mapping = mapping or {}
    return pd.DataFrame(
        [{label_col: key, value_col: value} for key, value in mapping.items()]
    )
