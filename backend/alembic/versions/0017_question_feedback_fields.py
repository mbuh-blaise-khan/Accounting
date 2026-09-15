"""0017 - Question feedback fields (Session 11 Part C1).

Adds, to the existing `questions` table:

- correction_en / correction_fr: authored, learner-safe plain-language
  correction of the reasoning, shown only AFTER an answer is submitted. It says
  what is right without echoing the correct option key, the stored option text,
  or the short-answer accepted text (no answer-key leakage).
- remediation_section_id: OPTIONAL foreign key to `lesson_sections.id` for the
  "Review this concept" action. It always points at a section of the SAME
  lesson as the question; the service verifies that and omits the target when
  no clearly-relevant section exists. ON DELETE SET NULL keeps section edits
  from ever cascading into question loss.

NOT added here (deliberate): `explanation_en` / `explanation_fr`. They already
exist on `questions` (created with the learning tables in 0014) and are already
returned by the scoring endpoint, so re-adding them would be a no-op that breaks
the upgrade.

All three new columns are nullable, so no backfill is required. Content is
supplied by the illustrative seed pack in app/learning/seed_data and synced
in place by learning/service.py (see `_sync_question_feedback`).

downgrade() removes ONLY what this revision added.
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("questions", sa.Column("correction_en", sa.Text(), nullable=True))
    op.add_column("questions", sa.Column("correction_fr", sa.Text(), nullable=True))
    op.add_column(
        "questions", sa.Column("remediation_section_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        "fk_questions_remediation_section_id",
        "questions",
        "lesson_sections",
        ["remediation_section_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_questions_remediation_section_id", "questions", ["remediation_section_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_questions_remediation_section_id", table_name="questions")
    op.drop_constraint(
        "fk_questions_remediation_section_id", "questions", type_="foreignkey"
    )
    op.drop_column("questions", "remediation_section_id")
    op.drop_column("questions", "correction_fr")
    op.drop_column("questions", "correction_en")
