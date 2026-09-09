"""0014 — Learning engine tables (Session 11 Part A).

Six simple tables: lessons, lesson_sections, questions, answers, attempts,
progress. No AI at this layer — stored plain-language content + straight
comparison scoring; the Lesson 4 practice connector reuses the existing
transactions engine.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "lessons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(80), nullable=False, unique=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("title_en", sa.String(200), nullable=False),
        sa.Column("title_fr", sa.String(200), nullable=False),
        sa.Column("summary_en", sa.Text(), nullable=False),
        sa.Column("summary_fr", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_table(
        "lesson_sections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "lesson_id",
            sa.Integer(),
            sa.ForeignKey("lessons.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("heading_en", sa.String(200), nullable=True),
        sa.Column("heading_fr", sa.String(200), nullable=True),
        sa.Column("body_en", sa.Text(), nullable=False),
        sa.Column("body_fr", sa.Text(), nullable=False),
    )
    op.create_index("ix_lesson_sections_lesson_id", "lesson_sections", ["lesson_id"])
    op.create_table(
        "questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "lesson_id",
            sa.Integer(),
            sa.ForeignKey("lessons.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("question_en", sa.Text(), nullable=False),
        sa.Column("question_fr", sa.Text(), nullable=False),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("explanation_en", sa.Text(), nullable=True),
        sa.Column("explanation_fr", sa.Text(), nullable=True),
        sa.Column("short_answer_en", sa.String(200), nullable=True),
        sa.Column("short_answer_fr", sa.String(200), nullable=True),
        sa.Column(
            "posts_demo_transaction", sa.Boolean(),
            nullable=False, server_default=sa.text("false"),
        ),
        sa.Column("practice_amount", sa.Numeric(16, 2), nullable=True),
    )
    op.create_index("ix_questions_lesson_id", "questions", ["lesson_id"])
    op.create_table(
        "answers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "question_id",
            sa.Integer(),
            sa.ForeignKey("questions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("option_key", sa.String(4), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("text_en", sa.String(300), nullable=False),
        sa.Column("text_fr", sa.String(300), nullable=False),
        sa.Column(
            "is_correct", sa.Boolean(),
            nullable=False, server_default=sa.text("false"),
        ),
    )
    op.create_index("ix_answers_question_id", "answers", ["question_id"])
    op.create_table(
        "attempts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("lesson_id", sa.Integer(), sa.ForeignKey("lessons.id"), nullable=False),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("selected_answer_id", sa.Integer(), sa.ForeignKey("answers.id"), nullable=True),
        sa.Column("submitted_text", sa.String(500), nullable=True),
        sa.Column(
            "is_correct", sa.Boolean(),
            nullable=False, server_default=sa.text("false"),
        ),
        sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=True),
        sa.Column(
            "practice_posted", sa.Boolean(),
            nullable=False, server_default=sa.text("false"),
        ),
        sa.Column("practice_transaction_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_attempts_user_id", "attempts", ["user_id"])
    op.create_index("ix_attempts_lesson_id", "attempts", ["lesson_id"])
    op.create_table(
        "progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("lesson_id", sa.Integer(), sa.ForeignKey("lessons.id"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="not_started"),
        sa.Column("best_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("questions_answered", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("questions_correct", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "practice_posted", sa.Boolean(),
            nullable=False, server_default=sa.text("false"),
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("user_id", "lesson_id", name="uq_progress_user_lesson"),
    )
    op.create_index("ix_progress_user_id", "progress", ["user_id"])
    op.create_index("ix_progress_lesson_id", "progress", ["lesson_id"])


def downgrade() -> None:
    op.drop_index("ix_progress_lesson_id", table_name="progress")
    op.drop_index("ix_progress_user_id", table_name="progress")
    op.drop_table("progress")
    op.drop_index("ix_attempts_lesson_id", table_name="attempts")
    op.drop_index("ix_attempts_user_id", table_name="attempts")
    op.drop_table("attempts")
    op.drop_index("ix_answers_question_id", table_name="answers")
    op.drop_table("answers")
    op.drop_index("ix_questions_lesson_id", table_name="questions")
    op.drop_table("questions")
    op.drop_index("ix_lesson_sections_lesson_id", table_name="lesson_sections")
    op.drop_table("lesson_sections")
    op.drop_table("lessons")