from ninja import Schema


class AttendanceRequest(Schema):

    rfid_uid: str
    status: int