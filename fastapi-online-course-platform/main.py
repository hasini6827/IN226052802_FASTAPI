from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Course(BaseModel):
    id: int
    title: str
    category: str
    price: float
    rating: float

class User(BaseModel):
    id: int
    name: str

class Enrollment(BaseModel):
    user_id: int
    course_id: int

courses = []
users = []
enrollments = []

def find_course(course_id: int):
    for c in courses:
        if c.id == course_id:
            return c
    return None

@app.get("/")
def home():
    return {"message": "Online Course Platform API"}

@app.get("/courses")
def get_courses():
    return courses

@app.post("/courses", status_code=201)
def add_course(course: Course):
    courses.append(course)
    return {"message": "Course added"}

@app.post("/users", status_code=201)
def add_user(user: User):
    users.append(user)
    return {"message": "User added"}

@app.get("/users")
def get_users():
    return users

@app.get("/courses/category/{category}")
def filter_by_category(category: str):
    return [c for c in courses if c.category.lower() == category.lower()]

@app.get("/courses/price/{price}")
def filter_by_price(price: float):
    return [c for c in courses if c.price <= price]

@app.get("/search")
def search_courses(keyword: str):
    return [c for c in courses if keyword.lower() in c.title.lower()]

@app.get("/courses/{course_id}")
def get_course(course_id: int):
    course = find_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@app.put("/courses/{course_id}")
def update_course(course_id: int, updated: Course):
    course = find_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    courses.remove(course)
    courses.append(updated)
    return {"message": "Course updated"}

@app.delete("/courses/{course_id}")
def delete_course(course_id: int):
    course = find_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    courses.remove(course)
    return {"message": "Course deleted"}

@app.post("/enroll", status_code=201)
def enroll(data: Enrollment):
    course = find_course(data.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    for e in enrollments:
        if e.user_id == data.user_id and e.course_id == data.course_id:
            raise HTTPException(status_code=400, detail="Already enrolled")
    enrollments.append(data)
    return {"message": "User enrolled"}

@app.get("/users/{user_id}/courses")
def user_courses(user_id: int):
    user_course_ids = [e.course_id for e in enrollments if e.user_id == user_id]
    return [c for c in courses if c.id in user_course_ids]

@app.get("/courses/{course_id}/enrollments")
def course_enrollments(course_id: int):
    count = sum(1 for e in enrollments if e.course_id == course_id)
    return {"course_id": course_id, "enrollments": count}

@app.get("/courses/popular")
def popular_courses():
    course_count = {}
    for e in enrollments:
        course_count[e.course_id] = course_count.get(e.course_id, 0) + 1
    sorted_courses = sorted(course_count.items(), key=lambda x: x[1], reverse=True)
    result = []
    for course_id, count in sorted_courses:
        course = find_course(course_id)
        if course:
            result.append({"course": course, "enrollments": count})
    return result

@app.get("/sort")
def sort_courses(by: str = "price"):
    if by == "price":
        return sorted(courses, key=lambda x: x.price)
    elif by == "rating":
        return sorted(courses, key=lambda x: x.rating, reverse=True)
    return courses

@app.get("/paginate")
def paginate(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    end = start + limit
    return courses[start:end]
