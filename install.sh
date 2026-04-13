#!/usr/bin/env bash
set -euo pipefail

main() {
    SKILL_DIR="${HOME}/.claude/skills/digest"
    REPO_URL="https://github.com/CamilleRoux/tech-digest"
    REPO_TAG="${DIGEST_TAG:-v1.0.0}"

    echo "════════════════════════════════════════"
    echo "  /digest -- Tech Digest for Claude Code"
    echo "════════════════════════════════════════"
    echo ""

    # Prerequisites
    command -v git >/dev/null 2>&1 || { echo "Error: git is required."; exit 1; }
    echo "* git detected"

    # Create skills directory if needed
    mkdir -p "${HOME}/.claude/skills"

    # Download to a temp directory
    TEMP_DIR=$(mktemp -d)
    trap "rm -rf ${TEMP_DIR}" EXIT

    echo "* Downloading (${REPO_TAG})..."
    git clone --depth 1 --branch "${REPO_TAG}" "${REPO_URL}" "${TEMP_DIR}/tech-digest" 2>/dev/null

    # Install skill files
    echo "* Installing files..."
    if [ -d "${SKILL_DIR}" ] && [ ! -L "${SKILL_DIR}" ]; then
        # Preserve a user-modified sources.yml
        if [ -f "${SKILL_DIR}/sources.yml" ]; then
            cp "${SKILL_DIR}/sources.yml" "${TEMP_DIR}/sources.yml.bak"
        fi
    fi

    mkdir -p "${SKILL_DIR}"
    cp -r "${TEMP_DIR}/tech-digest/skills/digest/"* "${SKILL_DIR}/"

    # Restore user's sources.yml if it existed
    if [ -f "${TEMP_DIR}/sources.yml.bak" ]; then
        cp "${TEMP_DIR}/sources.yml.bak" "${SKILL_DIR}/sources.yml"
        echo "* Existing sources.yml preserved"
    fi

    echo ""
    echo "Skill /digest installed successfully!"
    echo ""
    echo "Usage:"
    echo "  1. Launch Claude Code : claude"
    echo "  2. Type :              /digest"
    echo "  3. Or for 3 days :     /digest 3"
    echo ""
    echo "Configure sources: ${SKILL_DIR}/sources.yml"
    echo "To uninstall: curl -fsSL ${REPO_URL}/raw/main/uninstall.sh | bash"
}

main "$@"
