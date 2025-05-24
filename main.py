from fastapi import FastAPI, HTTPException
from routers import ping, auth
from routers.admin.tasks import router as admin_tasks_router
from routers.team.tasks import router as team_tasks_router
from routers.dashboard import router as dashboard_router

app = FastAPI()

app.include_router(ping.router)
app.include_router(auth.router)
app.include_router(admin_tasks_router)
app.include_router(team_tasks_router)
app.include_router(dashboard_router)

@app.get("/", responses={
    200: {"description": "Server is running"},
    500: {"description": "Internal server error"}
})
def root():
    try:
        return {"status": "Server is running"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
