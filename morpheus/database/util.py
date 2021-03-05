def row2dict(row, ignore_none=False):
    d = {}
    for column in row.__table__.columns:
        if (value := getattr(row, column.name)) is not None:
            d[column.name] = value

    return d