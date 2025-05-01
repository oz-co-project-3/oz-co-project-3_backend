async def paginate_query(query, offset: int, limit: int, schema):
    total = await query.count()
    start = offset * limit
    raw_results = await query.offset(start).limit(limit)

    results = [schema.from_orm(item) for item in raw_results]

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "data": results,
    }
