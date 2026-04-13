#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="${HOME}/.claude/skills/digest"

if [ -d "${SKILL_DIR}" ]; then
    rm -rf "${SKILL_DIR}"
    echo "/digest skill uninstalled."
else
    echo "/digest skill not found at ${SKILL_DIR}."
fi
