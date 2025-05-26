from fastapi import FastAPI, HTTPException
from routers import ping, auth
from routers.admin.tasks import router as admin_tasks_router
from routers.team.tasks import router as team_tasks_router
from routers.dashboard import router as dashboard_router
from routers.team import ws_status
from db_connect import get_connection
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI()

# Разрешаем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(ping.router)
app.include_router(auth.router)
app.include_router(admin_tasks_router)
app.include_router(team_tasks_router)
app.include_router(dashboard_router)
app.include_router(ws_status.router)

@app.on_event("startup")
async def start_background_task():
    asyncio.create_task(verify_solutions_periodically())

async def verify_solutions_periodically():
    while True:
        try:
            conn = await get_connection()

            # Получаем все решения, которые нужно проверить
            rows = await conn.fetch("""
                SELECT s.solution_id, s.task_id, s.team_id, s.answer AS solution_answer, t.answer AS task_answer
                FROM solution s
                JOIN task t ON s.task_id = t.task_id
                WHERE s.condition IN ('sent', 'verification')
            """)

            for row in rows:
                sid = row["solution_id"]
                task_answer = row["task_answer"]
                solution_answer = row["solution_answer"]

                if task_answer == solution_answer:
                    # Ответ совпадает — зачёт
                    await conn.execute("""
                        UPDATE solution SET condition = 'approve', approved_at = NOW()
                        WHERE solution_id = $1
                    """, sid)
                else:
                    # Ответ не совпадает — отклонено
                    await conn.execute("""
                        UPDATE solution SET condition = 'reject', approved_at = NULL
                        WHERE solution_id = $1
                    """, sid)

        except Exception as e:
            print(f"[!] Ошибка при автоматической проверке решений: {e}")
        finally:
            if 'conn' in locals() and conn:
                await conn.close()

        await asyncio.sleep(60)  # 1 час

# Асинхронная корневая проверка
@app.get("/", responses={
    200: {"description": "Server is running"},
    500: {"description": "Internal server error"}
})
async def root():
    try:
        return {"status": "Server is running"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
