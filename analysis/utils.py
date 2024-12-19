from datetime import datetime


def get_start_of_latest_full_month():
    now = datetime.now()
    return datetime(now.year, now.month, 1)


def calculate_num_intervals(start_date):
    """
    Calculate the number of intervals between the start date and the start of the latest full month
    Args:
        start_date: the start date of the study period
    Returns:
        num_intervals (int): the number of intervals between the start date and the start of the latest full month
    """
    start_of_latest_full_month = get_start_of_latest_full_month()

    num_intervals = (
        start_of_latest_full_month.year - datetime.strptime(start_date, "%Y-%m-%d").year
    ) * 12 + (
        start_of_latest_full_month.month
        - datetime.strptime(start_date, "%Y-%m-%d").month
    )

    return num_intervals
