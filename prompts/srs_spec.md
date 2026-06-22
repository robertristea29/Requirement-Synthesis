# SRS Specification (Baseline)

The generated SRS must use this exact section order and headings:

1. `# Software Requirements Specification (SRS)`
2. `## 1. Purpose`
3. `## 2. Scope`
4. `## 3. Stakeholders`
5. `## 4. Functional Requirements`
6. `## 5. Non-Functional Requirements`
7. `## 6. Contradictions and Risks`
8. `## 7. Open Questions`

Functional requirement IDs:

- Use `FR-<number>` format (example: `FR-1`, `FR-2`).

Non-functional requirement IDs:

- Use `NFR-<number>` format (example: `NFR-1`, `NFR-2`).

Contradictions:

- Include each contradiction as `C-<number>` with both conflicting statements.

Output boundaries:

- SRS must be emitted between `BEGIN_SRS` and `END_SRS`.
- Mermaid must be emitted between `BEGIN_MERMAID` and `END_MERMAID`.
- Mermaid section must contain one `C4Context` and one `C4Container` diagram.
