from fastapi import FastAPI
from routers.auth.auth import auth_router
from routers.attendance.attendance import attendance_router
from routers.leave.leave import leave_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(attendance_router, prefix="/attendance", tags=["Attendance"])
app.include_router(leave_router, prefix="/leave", tags=["Leaves"])

@app.get("/")
def home():
    '''This is the first and default route for the Attendance System Backend'''
    return {"message": "Hello World!"}

