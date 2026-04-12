#!/usr/bin/env bash
# Print structured overview of plugins, skills, agents, and references.
set -euo pipefail
cd "$(dirname "$0")"

extract_field() {
  local file="$1" field="$2"
  awk -v f="$field" '
    /^---$/ { block++; next }
    block==1 && $0 ~ "^"f": " {
      sub("^"f": *\"?", ""); sub("\"$", ""); print; exit
    }
  ' "$file"
}

for plugin_json in plugins/*/.claude-plugin/plugin.json; do
  plugin_dir="$(dirname "$(dirname "$plugin_json")")"
  plugin_name="$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['name'])" "$plugin_json")"
  plugin_desc="$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['description'])" "$plugin_json")"

  echo "Plugin: ${plugin_name}"
  echo "  ${plugin_desc}"

  for skill_md in "$plugin_dir"/skills/*/SKILL.md; do
    [ -f "$skill_md" ] || continue
    skill_name="$(extract_field "$skill_md" "name")"
    skill_desc="$(extract_field "$skill_md" "description")"
    # Truncate long descriptions
    if [ "${#skill_desc}" -gt 120 ]; then
      skill_desc="${skill_desc:0:117}..."
    fi
    echo "  Skill: /${skill_name}"
    echo "    ${skill_desc}"

    skill_dir="$(dirname "$skill_md")"

    # Agents
    if [ -d "$skill_dir/agents" ]; then
      agents=("$skill_dir"/agents/*)
      if [ ${#agents[@]} -gt 0 ]; then
        names=()
        for a in "${agents[@]}"; do
          [ -d "$a" ] && names+=("$(basename "$a")")
        done
        if [ ${#names[@]} -gt 0 ]; then
          echo "    Agents: $(IFS=','; echo "${names[*]}" | sed 's/,/, /g')"
        fi
      fi
    fi

    # References
    refs=()
    while IFS= read -r -d '' f; do
      refs+=("$(echo "$f" | sed "s|${skill_dir}/||")")
    done < <(find "$skill_dir" -path '*/references/*.md' -print0 2>/dev/null)
    if [ ${#refs[@]} -gt 0 ]; then
      echo "    References: $(IFS=','; echo "${refs[*]}" | sed 's/,/, /g')"
    fi
  done
  echo
done
