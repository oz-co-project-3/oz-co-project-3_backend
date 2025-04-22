async def paginate_query(query, offset: int, limit: int):
    total = await query.count()
    start = offset * limit
    results = await query.offset(start).limit(limit)

    return total, results
