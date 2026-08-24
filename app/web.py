"""Small Flask web interface for support automation and human review."""

import json
from pathlib import Path

from flask import Flask, render_template, request

from .database import get_requests, initialize_database, save_request
from .pipeline import run_pipeline
from .review import review_draft


DEFAULT_KB = Path(__file__).parent.parent / "data" / "knowledge_base.json"


def create_app(
    knowledge_base: str | Path = DEFAULT_KB,
    database_path: str | Path | None = None,
) -> Flask:

    template_dir = Path(__file__).resolve().parent.parent / "templates"

    app = Flask(
        __name__,
        template_folder=template_dir,
    )

    app.config["KNOWLEDGE_BASE"] = str(knowledge_base)
    app.config["DRAFTS"] = {}

    if database_path is not None:
        app.config["DATABASE"] = database_path
    else:
        app.config["DATABASE"] = None

    if app.config["DATABASE"] is None:
        initialize_database()
    else:
        initialize_database(app.config["DATABASE"])

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/history")
    def history():
        if app.config["DATABASE"] is None:
            rows = get_requests()
        else:
            rows = get_requests(app.config["DATABASE"])

        requests = []

        for row in rows:
            row = list(row)

            try:
                row[5] = json.loads(row[5])
            except (TypeError, json.JSONDecodeError):
                row[5] = []

            requests.append(tuple(row))

        return render_template(
            "history.html",
            requests=requests,
        )

    @app.post("/support")
    def support():
        message = request.form.get("message", "").strip()

        if not message:
            return (
                render_template(
                    "index.html",
                    error="Please enter a support request.",
                ),
                400,
            )

        result = run_pipeline(
            message,
            app.config["KNOWLEDGE_BASE"],
        )

        if app.config["DATABASE"] is None:
            save_request(result)
        else:
            save_request(
                result,
                app.config["DATABASE"],
            )

        draft_id = str(len(app.config["DRAFTS"]) + 1)

        app.config["DRAFTS"][draft_id] = {
            "result": result,
            "status": "pending",
        }

        return render_template(
            "review.html",
            result=result,
            draft_id=draft_id,
        )

    @app.post("/review/<draft_id>")
    def review(draft_id: str):
        draft = app.config["DRAFTS"].get(draft_id)

        if draft is None:
            return (
                render_template(
                    "index.html",
                    error="Draft not found. Please submit the request again.",
                ),
                404,
            )

        result = draft["result"]

        action = request.form.get(
            "action",
            "",
        ).strip().lower()

        edited_response = request.form.get(
            "edited_response",
        )

        try:
            decision = review_draft(
                action,
                result.draft.response,
                edited_response,
            )
        except ValueError as exc:
            return (
                render_template(
                    "review.html",
                    result=result,
                    draft_id=draft_id,
                    error=str(exc),
                ),
                400,
            )

        return render_template(
            "decision.html",
            decision=decision,
        )

    return app


app = create_app()