from app.domain.resume.models import Resume


async def get_resumes_by_name(name: str):
    return (
        await Resume.filter(name__icontains=name)
        .select_related("user")
        .prefetch_related("work_experiences")
        .all()
    )


async def get_all_resumes_query():
    return (
        await Resume.all().select_related("user").prefetch_related("work_experiences")
    )


async def get_resume_by_id(id: int):
    return (
        await Resume.filter(id=id)
        .select_related("user")
        .prefetch_related("work_experiences")
        .first()
    )


async def delete_resume_by_id(id: int):
    await Resume.filter(id=id).delete()
