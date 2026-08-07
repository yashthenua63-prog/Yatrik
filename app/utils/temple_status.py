from datetime import datetime


def get_temple_status(temple):

    now = datetime.now().time()


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



    if morning_open <= now <= morning_close:

        return {
            "status": "Open Now",
            "color": "green",
            "message": "Morning Darshan is available"
        }


    elif evening_open <= now <= evening_close:

        return {
            "status": "Open Now",
            "color": "green",
            "message": "Evening Darshan is available"
        }


    elif now < evening_open and now > morning_close:

        return {
            "status": "Darshan Break",
            "color": "orange",
            "message": f"Evening Darshan starts at {temple.evening_open}"
        }


    else:

        return {
            "status": "Closed",
            "color": "red",
            "message": f"Next Darshan starts at {temple.morning_open}"
        }
