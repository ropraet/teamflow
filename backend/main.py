"""
TeamFlow — Synthetic SaaS Project Manager for QA benchmarking.
Single-file FastAPI backend with SQLite.
"""
from __future__ import annotations

import csv
import io
import json
import os
import sqlite3
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Request, Response, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel

from bug_registry import bug_registry

# ── Config ──────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "teamflow-secret-key-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
DB_PATH = os.getenv("DB_PATH", "teamflow.db")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Database ────────────────────────────────────────────────────────────────
def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'member',
            avatar_url TEXT DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'active',
            owner_id INTEGER NOT NULL REFERENCES users(id),
            color TEXT DEFAULT '#3B82F6',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'todo',
            priority TEXT NOT NULL DEFAULT 'medium',
            assignee_id INTEGER REFERENCES users(id),
            due_date TEXT,
            labels TEXT DEFAULT '[]',
            created_by INTEGER NOT NULL REFERENCES users(id),
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES users(id),
            role TEXT NOT NULL DEFAULT 'member',
            invited_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(project_id, user_id)
        );

        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            project_id INTEGER REFERENCES projects(id),
            action TEXT NOT NULL,
            details TEXT DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """)
    conn.commit()

    # Seed data if empty
    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        seed_data(conn)

    conn.close()


def seed_data(conn: sqlite3.Connection):
    """Insert realistic demo data."""
    # Users: admin + member
    admin_hash = pwd_context.hash("admin123")
    member_hash = pwd_context.hash("member123")

    conn.execute(
        "INSERT INTO users (email, name, password_hash, role, avatar_url) VALUES (?, ?, ?, ?, ?)",
        ("admin@teamflow.dev", "Sarah Chen", admin_hash, "admin", ""),
    )
    conn.execute(
        "INSERT INTO users (email, name, password_hash, role, avatar_url) VALUES (?, ?, ?, ?, ?)",
        ("member@teamflow.dev", "Alex Rivera", member_hash, "member", ""),
    )
    # Extra team members
    for name, email in [
        ("Jordan Park", "jordan@teamflow.dev"),
        ("Priya Sharma", "priya@teamflow.dev"),
        ("Marcus Johnson", "marcus@teamflow.dev"),
    ]:
        conn.execute(
            "INSERT INTO users (email, name, password_hash, role, avatar_url) VALUES (?, ?, ?, ?, ?)",
            (email, name, pwd_context.hash("password123"), "member", ""),
        )

    # Projects
    projects = [
        ("Website Redesign", "Complete overhaul of the company marketing website with new brand guidelines", "active", 1, "#3B82F6"),
        ("Mobile App v2.0", "Native mobile app rebuild with React Native, focusing on performance and offline support", "active", 1, "#10B981"),
        ("Q1 Marketing Campaign", "Multi-channel marketing campaign for product launch including social, email, and PPC", "completed", 2, "#F59E0B"),
    ]
    for title, desc, status, owner, color in projects:
        conn.execute(
            "INSERT INTO projects (title, description, status, owner_id, color, created_at) VALUES (?, ?, ?, ?, ?, datetime('now', ?))",
            (title, desc, status, owner, color, f"-{projects.index((title, desc, status, owner, color)) * 5} days"),
        )

    # Team memberships
    for proj_id in [1, 2, 3]:
        for user_id in [1, 2, 3, 4, 5]:
            role = "admin" if user_id == 1 else "member"
            conn.execute(
                "INSERT OR IGNORE INTO team_members (project_id, user_id, role) VALUES (?, ?, ?)",
                (proj_id, user_id, role),
            )

    # Tasks
    tasks = [
        # Website Redesign (project 1)
        (1, "Design new homepage mockup", "Create Figma mockups for the new homepage layout with hero section", "done", "high", 3, "-10 days", '["design", "homepage"]', 1),
        (1, "Implement responsive navigation", "Build mobile-first responsive nav with hamburger menu", "in_progress", "high", 2, "-5 days", '["frontend", "responsive"]', 1),
        (1, "Set up CI/CD pipeline", "Configure GitHub Actions for auto-deploy to staging", "todo", "medium", 4, "+5 days", '["devops"]', 1),
        (1, "Write API documentation", "Document all REST endpoints with OpenAPI/Swagger", "todo", "low", None, "+14 days", '["docs"]', 1),
        (1, "Performance audit", "Run Lighthouse audit and fix critical performance issues", "todo", "high", 2, "+7 days", '["performance"]', 1),
        (1, "Content migration", "Migrate blog posts and pages from old CMS", "in_progress", "medium", 5, "-2 days", '["content"]', 1),
        (1, "SEO optimization", "Implement meta tags, structured data, and sitemap", "todo", "medium", 3, "+10 days", '["seo"]', 1),
        (1, "Cross-browser testing", "Test on Chrome, Firefox, Safari, and Edge", "todo", "high", None, "+12 days", '["testing", "qa"]', 1),
        (1, "Accessibility review", "WCAG 2.1 AA compliance check", "todo", "high", 4, "+8 days", '["a11y"]', 1),
        (1, "Launch preparation", "Final checklist, DNS config, SSL certificate", "todo", "critical", 1, "+20 days", '["launch"]', 1),

        # Mobile App v2.0 (project 2)
        (2, "Set up React Native project", "Initialize project with TypeScript, configure ESLint and Prettier", "done", "high", 2, "-15 days", '["setup"]', 1),
        (2, "Design system components", "Build reusable component library (buttons, inputs, cards)", "done", "high", 3, "-12 days", '["design-system", "components"]', 2),
        (2, "User authentication flow", "Implement login, register, forgot password with biometrics", "in_progress", "critical", 2, "-3 days", '["auth"]', 1),
        (2, "Offline data sync", "Implement SQLite local storage with background sync", "todo", "high", 4, "+10 days", '["offline", "sync"]', 2),
        (2, "Push notifications", "Set up FCM/APNs with notification preferences", "todo", "medium", 5, "+15 days", '["notifications"]', 2),
        (2, "App store submission", "Prepare screenshots, descriptions, and submit to stores", "todo", "high", 1, "+30 days", '["release"]', 1),
        (2, "Analytics integration", "Integrate Mixpanel for user behavior tracking", "todo", "medium", 3, "+8 days", '["analytics"]', 2),
        (2, "Crash reporting", "Set up Sentry for crash tracking and monitoring", "in_progress", "high", 4, "-1 days", '["monitoring"]', 2),
        (2, "Load testing", "Stress test API endpoints and measure response times", "todo", "medium", None, "+20 days", '["testing", "performance"]', 1),
        (2, "Dark mode support", "Implement system-aware dark mode throughout the app", "todo", "low", 3, "+12 days", '["design", "theme"]', 2),

        # Q1 Marketing Campaign (project 3)
        (3, "Campaign strategy document", "Define target audience, channels, budget, and KPIs", "done", "critical", 1, "-20 days", '["strategy"]', 1),
        (3, "Social media content calendar", "Plan 4 weeks of posts for Twitter, LinkedIn, Instagram", "done", "high", 5, "-14 days", '["social", "content"]', 2),
        (3, "Landing page design", "Design high-converting landing page with A/B test variants", "done", "high", 3, "-10 days", '["design", "conversion"]', 1),
        (3, "Email sequences", "Write 5-email nurture sequence for leads", "done", "medium", 5, "-7 days", '["email"]', 2),
        (3, "PPC campaign setup", "Configure Google Ads and Facebook Ads campaigns", "done", "high", 1, "-5 days", '["paid", "ads"]', 1),
        (3, "Analytics dashboard", "Build campaign tracking dashboard in Google Data Studio", "done", "medium", 4, "-3 days", '["analytics"]', 2),
        (3, "Week 1 performance review", "Analyze first week metrics and adjust targeting", "done", "high", 1, "+2 days", '["review"]', 1),
        (3, "Influencer outreach", "Contact 20 micro-influencers for product reviews", "done", "medium", 5, "-8 days", '["influencer"]', 2),
    ]
    for proj_id, title, desc, status, priority, assignee, date_offset, labels, created_by in tasks:
        conn.execute(
            """INSERT INTO tasks (project_id, title, description, status, priority, assignee_id, due_date, labels, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, date('now', ?), ?, ?, datetime('now', ?))""",
            (proj_id, title, desc, status, priority, assignee, date_offset, labels, created_by, date_offset),
        )

    # Activity log
    activities = [
        (1, 1, "created_project", "Created 'Website Redesign'"),
        (2, 2, "created_project", "Created 'Mobile App v2.0'"),
        (1, 1, "completed_task", "Completed 'Design new homepage mockup'"),
        (3, 2, "assigned_task", "Assigned 'Design system components' to Priya"),
        (2, 1, "commented", "Added comment on 'User authentication flow'"),
        (5, 3, "completed_task", "Completed 'Social media content calendar'"),
        (1, None, "updated_profile", "Updated notification settings"),
        (4, 2, "completed_task", "Completed 'Crash reporting setup'"),
    ]
    for user_id, proj_id, action, details in activities:
        conn.execute(
            "INSERT INTO activity_log (user_id, project_id, action, details) VALUES (?, ?, ?, ?)",
            (user_id, proj_id, action, details),
        )

    conn.commit()


# ── Auth helpers ────────────────────────────────────────────────────────────
def create_token(user_id: int, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    return jwt.encode({"sub": str(user_id), "role": role, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(request: Request) -> dict:
    token = None
    # Check cookie first, then Authorization header
    token = request.cookies.get("teamflow_token")
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
    if not token:
        raise HTTPException(401, "Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
        role = payload.get("role", "member")
    except JWTError:
        raise HTTPException(401, "Invalid token")

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if not user:
        raise HTTPException(401, "User not found")
    return dict(user)


# ── Pydantic models ────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    name: str
    password: str

class ProjectCreate(BaseModel):
    title: str
    description: str = ""
    color: str = "#3B82F6"

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    color: Optional[str] = None

class TaskCreate(BaseModel):
    title: str
    description: str = ""
    status: str = "todo"
    priority: str = "medium"
    assignee_id: Optional[int] = None
    due_date: Optional[str] = None
    labels: list[str] = []

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_id: Optional[int] = None
    due_date: Optional[str] = None
    labels: Optional[list[str]] = None

class InviteMember(BaseModel):
    email: str
    role: str = "member"

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None

class BugToggle(BaseModel):
    bug_id: str

class BugPreset(BaseModel):
    preset: str


# ── App ─────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="TeamFlow", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Security headers middleware ─────────────────────────────────────────────
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    if not bug_registry.is_active("security_no_csp"):
        response.headers["Content-Security-Policy"] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://cdn.jsdelivr.net; img-src 'self' data: https:; font-src 'self' https://fonts.gstatic.com"
    if not bug_registry.is_active("security_no_hsts"):
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


# ── Auth routes ─────────────────────────────────────────────────────────────
@app.post("/api/auth/login")
async def login(data: LoginRequest, response: Response):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (data.email,)).fetchone()
    conn.close()
    if not user or not pwd_context.verify(data.password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    token = create_token(user["id"], user["role"])
    response.set_cookie("teamflow_token", token, httponly=True, samesite="lax", max_age=86400)
    return {"token": token, "user": {"id": user["id"], "email": user["email"], "name": user["name"], "role": user["role"]}}


@app.post("/api/auth/register")
async def register(data: RegisterRequest, response: Response):
    conn = get_db()
    existing = conn.execute("SELECT id FROM users WHERE email = ?", (data.email,)).fetchone()
    if existing:
        conn.close()
        raise HTTPException(400, "Email already registered")
    password_hash = pwd_context.hash(data.password)
    cursor = conn.execute(
        "INSERT INTO users (email, name, password_hash, role) VALUES (?, ?, ?, ?)",
        (data.email, data.name, password_hash, "member"),
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    token = create_token(user_id, "member")
    response.set_cookie("teamflow_token", token, httponly=True, samesite="lax", max_age=86400)
    return {"token": token, "user": {"id": user_id, "email": data.email, "name": data.name, "role": "member"}}


@app.post("/api/auth/logout")
async def logout(response: Response):
    response.delete_cookie("teamflow_token")
    return {"message": "Logged out"}


@app.get("/api/auth/me")
async def get_me(request: Request):
    user = get_current_user(request)
    return {"id": user["id"], "email": user["email"], "name": user["name"], "role": user["role"], "avatar_url": user["avatar_url"], "created_at": user["created_at"]}


@app.post("/api/auth/forgot-password")
async def forgot_password(data: dict):
    # Simulated — always returns success
    return {"message": "If that email exists, a reset link has been sent."}


# ── Profile ─────────────────────────────────────────────────────────────────
@app.put("/api/profile")
async def update_profile(data: ProfileUpdate, request: Request):
    user = get_current_user(request)
    conn = get_db()

    if data.email:
        if not bug_registry.is_active("form_accepts_invalid_email"):
            if "@" not in data.email or "." not in data.email.split("@")[-1]:
                conn.close()
                raise HTTPException(422, "Invalid email address")

    updates = []
    values = []
    if data.name is not None:
        updates.append("name = ?")
        values.append(data.name)
    if data.email is not None:
        updates.append("email = ?")
        values.append(data.email)
    if data.avatar_url is not None:
        updates.append("avatar_url = ?")
        values.append(data.avatar_url)

    if updates:
        values.append(user["id"])
        conn.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", values)
        conn.commit()
    conn.close()
    return {"message": "Profile updated"}


# ── Projects ────────────────────────────────────────────────────────────────
@app.get("/api/projects")
async def list_projects(request: Request):
    user = get_current_user(request)
    conn = get_db()
    projects = conn.execute("""
        SELECT p.*, u.name as owner_name,
            (SELECT COUNT(*) FROM tasks WHERE project_id = p.id) as task_count,
            (SELECT COUNT(*) FROM tasks WHERE project_id = p.id AND status = 'done') as completed_count,
            (SELECT COUNT(*) FROM team_members WHERE project_id = p.id) as member_count
        FROM projects p
        JOIN users u ON p.owner_id = u.id
        JOIN team_members tm ON tm.project_id = p.id AND tm.user_id = ?
        ORDER BY p.updated_at DESC
    """, (user["id"],)).fetchall()
    conn.close()
    return [dict(p) for p in projects]


@app.post("/api/projects")
async def create_project(data: ProjectCreate, request: Request):
    user = get_current_user(request)

    if not bug_registry.is_active("form_missing_title_validation"):
        if not data.title or not data.title.strip():
            raise HTTPException(422, "Title is required")

    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO projects (title, description, owner_id, color) VALUES (?, ?, ?, ?)",
        (data.title, data.description, user["id"], data.color),
    )
    project_id = cursor.lastrowid
    # Add creator as admin member
    conn.execute(
        "INSERT INTO team_members (project_id, user_id, role) VALUES (?, ?, 'admin')",
        (project_id, user["id"]),
    )
    conn.execute(
        "INSERT INTO activity_log (user_id, project_id, action, details) VALUES (?, ?, 'created_project', ?)",
        (user["id"], project_id, f"Created '{data.title}'"),
    )
    conn.commit()
    project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    conn.close()
    return dict(project)


@app.get("/api/projects/{project_id}")
async def get_project(project_id: int, request: Request):
    user = get_current_user(request)
    conn = get_db()
    project = conn.execute("""
        SELECT p.*, u.name as owner_name,
            (SELECT COUNT(*) FROM tasks WHERE project_id = p.id) as task_count,
            (SELECT COUNT(*) FROM tasks WHERE project_id = p.id AND status = 'done') as completed_count,
            (SELECT COUNT(*) FROM team_members WHERE project_id = p.id) as member_count
        FROM projects p
        JOIN users u ON p.owner_id = u.id
        WHERE p.id = ?
    """, (project_id,)).fetchone()
    conn.close()
    if not project:
        raise HTTPException(404, "Project not found")
    return dict(project)


@app.put("/api/projects/{project_id}")
async def update_project(project_id: int, data: ProjectUpdate, request: Request):
    user = get_current_user(request)
    conn = get_db()
    updates = []
    values = []
    if data.title is not None:
        updates.append("title = ?")
        values.append(data.title)
    if data.description is not None:
        updates.append("description = ?")
        values.append(data.description)
    if data.status is not None:
        updates.append("status = ?")
        values.append(data.status)
    if data.color is not None:
        updates.append("color = ?")
        values.append(data.color)
    updates.append("updated_at = datetime('now')")
    values.append(project_id)
    conn.execute(f"UPDATE projects SET {', '.join(updates)} WHERE id = ?", values)
    conn.commit()
    project = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    conn.close()
    return dict(project)


@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: int, request: Request):
    user = get_current_user(request)
    conn = get_db()

    if not bug_registry.is_active("rbac_delete_not_restricted"):
        if user["role"] != "admin":
            member = conn.execute(
                "SELECT role FROM team_members WHERE project_id = ? AND user_id = ?",
                (project_id, user["id"]),
            ).fetchone()
            if not member or member["role"] != "admin":
                conn.close()
                raise HTTPException(403, "Only admins can delete projects")

    if bug_registry.is_active("crud_delete_item_reappears"):
        # Bug: don't actually delete, just pretend
        conn.close()
        return {"message": "Project deleted"}

    conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
    return {"message": "Project deleted"}


# ── Tasks ───────────────────────────────────────────────────────────────────
@app.get("/api/projects/{project_id}/tasks")
async def list_tasks(
    project_id: int,
    request: Request,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee_id: Optional[int] = None,
    search: Optional[str] = None,
    sort: str = "created_at",
    order: str = "desc",
    page: int = 1,
    per_page: int = 10,
):
    user = get_current_user(request)
    conn = get_db()

    where = ["t.project_id = ?"]
    params: list[Any] = [project_id]

    # BUG: filter_resets_on_pagination — ignore filters when page > 1
    if bug_registry.is_active("filter_resets_on_pagination") and page > 1:
        pass  # skip all filters
    else:
        if status:
            where.append("t.status = ?")
            params.append(status)
        if priority:
            where.append("t.priority = ?")
            params.append(priority)
        if assignee_id:
            where.append("t.assignee_id = ?")
            params.append(assignee_id)
        if search:
            where.append("(t.title LIKE ? OR t.description LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])

    where_clause = " AND ".join(where)
    allowed_sorts = {"created_at", "updated_at", "title", "priority", "status", "due_date"}
    sort_col = sort if sort in allowed_sorts else "created_at"
    sort_order = "ASC" if order.lower() == "asc" else "DESC"

    total = conn.execute(f"SELECT COUNT(*) FROM tasks t WHERE {where_clause}", params).fetchone()[0]

    offset = (page - 1) * per_page
    tasks = conn.execute(f"""
        SELECT t.*, u.name as assignee_name
        FROM tasks t
        LEFT JOIN users u ON t.assignee_id = u.id
        WHERE {where_clause}
        ORDER BY t.{sort_col} {sort_order}
        LIMIT ? OFFSET ?
    """, params + [per_page, offset]).fetchall()
    conn.close()

    return {
        "tasks": [dict(t) for t in tasks],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
    }


@app.post("/api/projects/{project_id}/tasks")
async def create_task(project_id: int, data: TaskCreate, request: Request):
    user = get_current_user(request)
    conn = get_db()

    # BUG: crud_create_duplicate_on_doubleclick — no idempotency check
    # (frontend bug — handled in frontend, but backend also doesn't block)

    cursor = conn.execute(
        """INSERT INTO tasks (project_id, title, description, status, priority, assignee_id, due_date, labels, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (project_id, data.title, data.description, data.status, data.priority, data.assignee_id, data.due_date, json.dumps(data.labels), user["id"]),
    )
    task_id = cursor.lastrowid
    conn.execute(
        "INSERT INTO activity_log (user_id, project_id, action, details) VALUES (?, ?, 'created_task', ?)",
        (user["id"], project_id, f"Created '{data.title}'"),
    )
    conn.commit()
    task = conn.execute("SELECT t.*, u.name as assignee_name FROM tasks t LEFT JOIN users u ON t.assignee_id = u.id WHERE t.id = ?", (task_id,)).fetchone()
    conn.close()

    result = dict(task)
    if bug_registry.is_active("form_submit_no_feedback"):
        # Return 200 but with no message field — frontend won't show toast
        return result
    result["message"] = "Task created successfully"
    return result


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: int, request: Request):
    user = get_current_user(request)
    conn = get_db()

    if bug_registry.is_active("console_unhandled_error"):
        # Bug: sometimes return data that causes frontend JS error
        task = conn.execute("""
            SELECT t.*, u.name as assignee_name
            FROM tasks t LEFT JOIN users u ON t.assignee_id = u.id
            WHERE t.id = ?
        """, (task_id,)).fetchone()
        if task:
            result = dict(task)
            result["labels"] = "INVALID_JSON{{"  # Will cause JSON.parse error in frontend
            conn.close()
            return result

    task = conn.execute("""
        SELECT t.*, u.name as assignee_name
        FROM tasks t LEFT JOIN users u ON t.assignee_id = u.id
        WHERE t.id = ?
    """, (task_id,)).fetchone()
    conn.close()
    if not task:
        raise HTTPException(404, "Task not found")
    return dict(task)


@app.put("/api/tasks/{task_id}")
async def update_task(task_id: int, data: TaskUpdate, request: Request):
    user = get_current_user(request)
    conn = get_db()

    if bug_registry.is_active("crud_edit_doesnt_save"):
        # Bug: return success but don't actually save
        task = conn.execute("SELECT t.*, u.name as assignee_name FROM tasks t LEFT JOIN users u ON t.assignee_id = u.id WHERE t.id = ?", (task_id,)).fetchone()
        conn.close()
        if not task:
            raise HTTPException(404, "Task not found")
        # Return the original task as if it was updated
        result = dict(task)
        # Override with "new" values in response so it LOOKS saved
        if data.title is not None:
            result["title"] = data.title
        if data.description is not None:
            result["description"] = data.description
        if data.status is not None:
            result["status"] = data.status
        return result

    updates = []
    values = []
    if data.title is not None:
        updates.append("title = ?")
        values.append(data.title)
    if data.description is not None:
        updates.append("description = ?")
        values.append(data.description)
    if data.status is not None:
        updates.append("status = ?")
        values.append(data.status)
    if data.priority is not None:
        updates.append("priority = ?")
        values.append(data.priority)
    if data.assignee_id is not None:
        updates.append("assignee_id = ?")
        values.append(data.assignee_id)
    if data.due_date is not None:
        updates.append("due_date = ?")
        values.append(data.due_date)
    if data.labels is not None:
        updates.append("labels = ?")
        values.append(json.dumps(data.labels))
    updates.append("updated_at = datetime('now')")
    values.append(task_id)
    conn.execute(f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?", values)
    conn.commit()
    task = conn.execute("SELECT t.*, u.name as assignee_name FROM tasks t LEFT JOIN users u ON t.assignee_id = u.id WHERE t.id = ?", (task_id,)).fetchone()
    conn.close()
    if not task:
        raise HTTPException(404, "Task not found")
    return dict(task)


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int, request: Request):
    user = get_current_user(request)
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return {"message": "Task deleted"}


# ── Team ────────────────────────────────────────────────────────────────────
@app.get("/api/projects/{project_id}/members")
async def list_members(project_id: int, request: Request):
    user = get_current_user(request)
    conn = get_db()
    members = conn.execute("""
        SELECT tm.*, u.name, u.email, u.avatar_url
        FROM team_members tm
        JOIN users u ON tm.user_id = u.id
        WHERE tm.project_id = ?
    """, (project_id,)).fetchall()
    conn.close()
    return [dict(m) for m in members]


@app.post("/api/projects/{project_id}/members")
async def invite_member(project_id: int, data: InviteMember, request: Request):
    user = get_current_user(request)
    conn = get_db()

    target = conn.execute("SELECT id FROM users WHERE email = ?", (data.email,)).fetchone()
    if not target:
        conn.close()
        raise HTTPException(404, "User not found with that email")

    if bug_registry.is_active("share_success_but_no_effect"):
        # Bug: return success but don't actually add member
        conn.close()
        return {"message": "Member invited successfully!"}

    try:
        conn.execute(
            "INSERT INTO team_members (project_id, user_id, role) VALUES (?, ?, ?)",
            (project_id, target["id"], data.role),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(400, "User is already a member")
    conn.close()
    return {"message": "Member invited successfully!"}


@app.delete("/api/projects/{project_id}/members/{user_id}")
async def remove_member(project_id: int, user_id: int, request: Request):
    current = get_current_user(request)
    conn = get_db()
    conn.execute("DELETE FROM team_members WHERE project_id = ? AND user_id = ?", (project_id, user_id))
    conn.commit()
    conn.close()
    return {"message": "Member removed"}


@app.put("/api/projects/{project_id}/members/{user_id}/role")
async def update_member_role(project_id: int, user_id: int, data: dict, request: Request):
    current = get_current_user(request)
    conn = get_db()
    conn.execute(
        "UPDATE team_members SET role = ? WHERE project_id = ? AND user_id = ?",
        (data.get("role", "member"), project_id, user_id),
    )
    conn.commit()
    conn.close()
    return {"message": "Role updated"}


# ── Dashboard ───────────────────────────────────────────────────────────────
@app.get("/api/dashboard")
async def get_dashboard(request: Request):
    user = get_current_user(request)
    conn = get_db()

    project_count = conn.execute("""
        SELECT COUNT(*) FROM projects p
        JOIN team_members tm ON tm.project_id = p.id AND tm.user_id = ?
    """, (user["id"],)).fetchone()[0]

    task_stats = conn.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN t.status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
            SUM(CASE WHEN t.status = 'todo' THEN 1 ELSE 0 END) as todo,
            SUM(CASE WHEN t.due_date < date('now') AND t.status != 'done' THEN 1 ELSE 0 END) as overdue
        FROM tasks t
        JOIN projects p ON t.project_id = p.id
        JOIN team_members tm ON tm.project_id = p.id AND tm.user_id = ?
    """, (user["id"],)).fetchone()

    activities = conn.execute("""
        SELECT al.*, u.name as user_name
        FROM activity_log al
        JOIN users u ON al.user_id = u.id
        ORDER BY al.created_at DESC LIMIT 10
    """).fetchall()

    conn.close()
    return {
        "projects": project_count,
        "tasks": dict(task_stats),
        "recent_activity": [dict(a) for a in activities],
    }


# ── Settings (RBAC bug) ────────────────────────────────────────────────────
@app.get("/api/settings/billing")
async def get_billing(request: Request):
    user = get_current_user(request)

    if not bug_registry.is_active("rbac_member_sees_admin"):
        if user["role"] != "admin":
            raise HTTPException(403, "Admin access required")

    return {
        "plan": "Pro",
        "price": "$29/month",
        "next_billing": "2025-02-01",
        "payment_method": "Visa ending in 4242",
        "invoices": [
            {"date": "2025-01-01", "amount": "$29.00", "status": "paid"},
            {"date": "2024-12-01", "amount": "$29.00", "status": "paid"},
        ],
    }


@app.get("/api/settings/notifications")
async def get_notifications(request: Request):
    user = get_current_user(request)
    return {
        "email_notifications": True,
        "push_notifications": True,
        "weekly_digest": False,
        "mention_alerts": True,
    }


@app.put("/api/settings/notifications")
async def update_notifications(data: dict, request: Request):
    user = get_current_user(request)
    return {"message": "Notification settings updated"}


# ── Export ──────────────────────────────────────────────────────────────────
@app.get("/api/projects/{project_id}/export/csv")
async def export_csv(project_id: int, request: Request):
    user = get_current_user(request)
    conn = get_db()
    tasks = conn.execute("""
        SELECT t.*, u.name as assignee_name
        FROM tasks t LEFT JOIN users u ON t.assignee_id = u.id
        WHERE t.project_id = ?
    """, (project_id,)).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)

    if bug_registry.is_active("export_missing_columns"):
        # Bug: missing assignee and due_date columns
        writer.writerow(["ID", "Title", "Description", "Status", "Priority"])
        for t in tasks:
            writer.writerow([t["id"], t["title"], t["description"], t["status"], t["priority"]])
    else:
        writer.writerow(["ID", "Title", "Description", "Status", "Priority", "Assignee", "Due Date", "Labels"])
        for t in tasks:
            writer.writerow([t["id"], t["title"], t["description"], t["status"], t["priority"], t["assignee_name"] or "", t["due_date"] or "", t["labels"]])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=project_{project_id}_tasks.csv"},
    )


@app.get("/api/projects/{project_id}/export/json")
async def export_json(project_id: int, request: Request):
    user = get_current_user(request)

    if bug_registry.is_active("export_empty_file"):
        # Bug: return empty file
        return StreamingResponse(
            iter([""]),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=project_{project_id}_tasks.json"},
        )

    conn = get_db()
    tasks = conn.execute("""
        SELECT t.*, u.name as assignee_name
        FROM tasks t LEFT JOIN users u ON t.assignee_id = u.id
        WHERE t.project_id = ?
    """, (project_id,)).fetchall()
    conn.close()

    data = [dict(t) for t in tasks]
    return StreamingResponse(
        iter([json.dumps(data, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=project_{project_id}_tasks.json"},
    )


# ── Users list (for assignees, etc.) ───────────────────────────────────────
@app.get("/api/users")
async def list_users(request: Request):
    user = get_current_user(request)
    conn = get_db()
    users = conn.execute("SELECT id, email, name, role, avatar_url FROM users").fetchall()
    conn.close()
    return [dict(u) for u in users]


# ── Bug Registry API ───────────────────────────────────────────────────────
@app.get("/api/bugs")
async def list_bugs():
    return bug_registry.list_bugs()


@app.get("/api/bugs/active")
async def get_active_bugs():
    return {"active": bug_registry.get_active_ids()}


@app.post("/api/bugs/toggle")
async def toggle_bug(data: BugToggle):
    new_state = bug_registry.toggle(data.bug_id)
    return {"bug_id": data.bug_id, "active": new_state}


@app.post("/api/bugs/preset")
async def apply_preset(data: BugPreset):
    bugs = bug_registry.apply_preset(data.preset)
    return {"preset": data.preset, "active_bugs": bugs}


@app.get("/api/bugs/presets")
async def list_presets():
    return {"presets": bug_registry.get_preset_names()}


@app.get("/api/ground-truth")
async def get_ground_truth():
    gt_path = Path(__file__).parent.parent / "bugs" / "ground_truth.json"
    if gt_path.exists():
        return json.loads(gt_path.read_text())
    raise HTTPException(404, "Ground truth file not found")


# ── Error simulation ───────────────────────────────────────────────────────
@app.get("/api/simulate-error")
async def simulate_error(request: Request):
    if bug_registry.is_active("error_generic_500_message"):
        raise HTTPException(500, "Error 500")
    raise HTTPException(500, "An unexpected error occurred. Please try again later or contact support.")


# ── Serve frontend (production) ────────────────────────────────────────────
FRONTEND_DIR = Path(__file__).parent.parent / "frontend" / "dist"

if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")

    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        file_path = FRONTEND_DIR / path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIR / "index.html")
