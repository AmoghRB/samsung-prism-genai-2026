# Reference material

Source documents from Samsung. Two things override everything else here:

1. **The FAQ overrides the theme guide** where they conflict — notably Q30, which
   says to ignore the JavaScript codebase mentioned in the PPT (the dataset is
   APPS, Python).
2. **Later communications override earlier ones.** The registration email
   (18 Sep) postdates the FAQ and the deck.

| File | What it is |
|---|---|
| `theme1_guidelines.pdf` | **Theme 1: Agentic Code Intelligence — our theme.** The spec. |
| `Samsung_PRISM_GenAI_Hackathon_3_FAQ_v4.docx` | **Read this.** Rules, rubric, naming, tag commands. Theme 1 Q&A at Q30–Q31. |
| `Samsung PRISM_Y2026_GenAI_Hackathon_3rd_Edition.V2(2).pdf` | Main deck: dates, rules, submission process |
| `LangAI3.0_AI_Disclosure.docx` | **Mandatory deliverable.** Needs per-feature AI-usage detail — log as you go. |
| `CollegeName_TeamName_Submission.pptx` | The mandatory PPT template. Rename to `MSRIT_Waypoint_...` |
| `participant-kit-all-themes.zip` | **Theme 5 only** — voice-agent harness. Not ours. Kept for reference. |
| `Theme 2_Troubleshooting_...pdf` | Other theme. No text layer. |
| `Theme 3 - Evaluation Criteria.pdf` | Other theme |
| `Theme 4 Guide_RAG.pdf` | Other theme. No text layer. |
| `Theme 5_Guide.pdf` | Other theme |

> `All theme guidelines.zip` was removed — it contained the same five theme PDFs
> already extracted above.

## Extracting text

The `.docx` files and `theme1_guidelines.pdf` have text layers:

```bash
python3 -c "import zipfile,re,html; z=zipfile.ZipFile('FILE.docx'); x=z.read('word/document.xml').decode(); x=re.sub(r'</w:p>','\n',x); print(html.unescape(re.sub(r'<[^>]+>','',x)))"
```

The Theme 2 and Theme 4 PDFs are scanned and need page rendering — not relevant
to us.
