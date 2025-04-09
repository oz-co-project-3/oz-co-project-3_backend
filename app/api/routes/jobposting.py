from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.jobposting_schemas import JobPostingCreateUpdate, JobPostingResponse
