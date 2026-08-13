from datetime import datetime
from zoneinfo import ZoneInfo


# India Standard Time
INDIA_TZ = ZoneInfo("Asia/Kolkata")


def get_temple_status(temple):

    # Current Indian time
    now = datetime.now(INDIA_TZ).time()

    # Convert database timings to time objects
    morning_open = datetime.strptime(
        temple.morning_open,
        "%I:%M %p"
    ).time()

    morning_close = datetime.strptime(
        temple.morning_close,
        "%I:%M %p"
    ).time()

    evening_open = datetime.strptime(
        temple.evening_open,
        "%I:%M %p"
    ).time()

    evening_close = datetime.strptime(
        temple.evening_close,
        "%I:%M %p"
    ).time()


    # -----------------------------------------
    # MORNING DARSHAN
    # -----------------------------------------

    if morning_open <= now <= morning_close:
        return {
            "status": "Open Now",
            "color": "green",
            "message": "Morning Darshan is available",
            "next_darshan": "Currently Open",
            "recommended_arrival": "Now"
        }


    # -----------------------------------------
    # BETWEEN MORNING & EVENING
    # -----------------------------------------

    elif morning_close < now < evening_open:
        return {
            "status": "Darshan Break",
            "color": "orange",
            "message": f"Evening Darshan starts at {temple.evening_open}",
            "next_darshan": f"Today {temple.evening_open}",
            "recommended_arrival": "15 mins before evening opening"
        }


    # -----------------------------------------
    # EVENING DARSHAN
    # -----------------------------------------

    elif evening_open <= now <= evening_close:
        return {
            "status": "Open Now",
            "color": "green",
            "message": "Evening Darshan is available",
            "next_darshan": "Currently Open",
            "recommended_arrival": "Now"
        }


    # -----------------------------------------
    # AFTER EVENING DARSHAN
    # -----------------------------------------

    else:

        return {
            "status": "Closed",
            "color": "red",
            "message": f"Next Darshan starts tomorrow at {temple.morning_open}",
            "next_darshan": f"Tomorrow {temple.morning_open}",
            "recommended_arrival": "Tomorrow early morning"
        }