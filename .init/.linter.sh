#!/bin/bash
cd /home/kavia/workspace/code-generation/question-and-answer-platform-3111-3120/qna_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

