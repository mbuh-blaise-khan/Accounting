"""0018 - Spaced-review items + attempt confidence (Session 11 Part C2).

Creates the `review_items` table: ONE deterministic spaced-review card per
(user, question) — the UNIQUE (user_id, question_id) constraint makes
duplicate active cards impossible at the database level; the service resets or
reactivates an existing row instead of inserting another one.

- user_id       — owner; all review endpoints are strictly user-scoped.
- question_id   — the lesson question to re-answer (CASCADE on question loss).
- stage         — index into the deterministic interval ladder: a CORRECT
                  review answer schedules stage 0 -> 1 day, 1 -> 3 days,
                  2 -> 7 days, 3+ -> 14 days; a WRONG one resets the stage to
                  0 and makes the card due immediately.
- due_at        — next due date, timezone-aware UTC.
- is_active     — only active cards are listed/answerable.
- last_outcome  — 'wrong' | 'guessed' (lesson-created) | 'review_correct' |
                  'review_wrong' (the last event on the card).

Also adds `attempts.confidence` (nullable): the optional learner
self-assessment sent with a lesson answer ('understood' | 'guessed'). It never
affects scoring — only whether a review card is created.

Review data deliberately does NOT touch lesson progress, completion or
certificate eligibility (review answers create no `attempts` rows).

downgrade() removes ONLY what this revision added.
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "review_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column(
            "question_id",
            sa.Integer(),
            sa.ForeignKey("questions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("stage", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.true()
        ),
        sa.Column("last_outcome", sa.String(20), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False
        ),
        sa.UniqueConstraint("user_id", "question_id", name="uq_review_user_question"),
    )
    op.create_index("ix_review_items_user_id", "review_items", ["user_id"])
    op.create_index("ix_review_items_question_id", "review_items", ["question_id"])
    op.add_column("attempts", sa.Column("confidence", sa.String(20), nullable=True))


def downgrade() -> None:
    op.drop_column("attempts", "confidence")
    op.drop_index("ix_review_items_question_id", table_name="review_items")
    op.drop_index("ix_review_items_user_id", table_name="review_items")
    op.drop_table("review_items")
