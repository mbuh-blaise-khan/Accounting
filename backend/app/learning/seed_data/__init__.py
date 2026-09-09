"""Seed content for the 7-core-lesson learning path (Session 11 Part A).

Grounding: the sequence mirrors ACCA's Foundations in Accountancy (FIA)
introductory progression — accounting context -> the accounting equation ->
debits/credits -> journal entries -> ledger -> trial balance -> financial
statements. It also matches this app's own Sessions 4-10 build order.

All content is plain-language, stored EN+FR in the database, and served
per-request from the API (never bundled as static/downloadable files).
Scoring is straight comparison against stored answers (no AI).
"""
from app.learning.seed_data.lesson_1 import LESSON as _L1
from app.learning.seed_data.lesson_2 import LESSON as _L2
from app.learning.seed_data.lesson_3 import LESSON as _L3
from app.learning.seed_data.lesson_4 import LESSON as _L4
from app.learning.seed_data.lesson_5 import LESSON as _L5
from app.learning.seed_data.lesson_6 import LESSON as _L6
from app.learning.seed_data.lesson_7 import LESSON as _L7

LESSONS = [_L1, _L2, _L3, _L4, _L5, _L6, _L7]