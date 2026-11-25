from datetime import date

MIN_YEAR = 1900
MAX_YEAR = 2100


def selected_year(requested_year, fallback_year):
    try:
        year = int(requested_year)
    except (TypeError, ValueError):
        return fallback_year
    return year if MIN_YEAR <= year <= MAX_YEAR else fallback_year


def year_context(requested_year, fallback_year):
    current_year = date.today().year
    year = selected_year(requested_year, fallback_year)
    return {
        "view_year": year,
        "current_year": current_year,
        "prev_year": max(MIN_YEAR, year - 1),
        "next_year": min(MAX_YEAR, year + 1),
        "year_options": sorted(set(range(current_year - 5, current_year + 6)) | {year}),
    }
