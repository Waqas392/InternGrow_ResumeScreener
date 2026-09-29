# Submission Notes

## Commit Plan

```text
feat: scaffold backend project structure
feat: add configuration, logging, and exception handling
feat: add database models and async session
feat: add user authentication with JWT
feat: add job creation and listing API
feat: add resume upload and text extraction service
feat: add OCR fallback for scanned PDFs
feat: add spaCy skill extraction taxonomy
feat: add semantic matching service
feat: add candidate scoring breakdown
feat: add background processing for bulk resume uploads
feat: add candidate ranking and filtering API
feat: add CSV and PDF export endpoints
feat: add evaluation dataset and metrics engine
feat: add evaluation endpoint
feat: scaffold React frontend with Vite and Tailwind
feat: add auth context and protected routing
feat: add dashboard and job creation UI
feat: add job detail candidate ranking UI
feat: add resume upload and extraction UI
feat: add evaluation dashboard UI
test: add backend API and service tests
test: add frontend component tests
docs: add README, deployment guide, and demo script
```

## Demo Video Script

1. Open the login screen and mention that the app uses JWT authentication.
2. Sign in with the seeded demo user.
3. Show the dashboard and the seeded job.
4. Create a new job with required skills.
5. Upload multiple resumes using bulk upload.
6. Return to the job detail screen and show the ranked candidate table.
7. Open one candidate explainability panel and describe the score breakdown.
8. Export candidates as CSV and PDF.
9. Show the Resumes page and extracted skills.
10. Show the Evaluation page and explain model versus baseline metrics.
11. Toggle dark mode and show responsive behavior.
12. End with Docker and deployment commands.

## LinkedIn Post Draft

```text
I built an Intelligent Resume Screening System for the InternGrow AI Track.

The application helps recruiters create jobs, upload resumes in bulk, and rank candidates using a transparent AI scoring pipeline.

Highlights:
- FastAPI backend with JWT auth and async processing
- PDF/DOCX extraction with OCR fallback
- spaCy skill extraction using a curated taxonomy
- Semantic matching with sentence-transformers
- Explainable candidate score breakdown
- Ranked candidate table with filters
- CSV and PDF export
- React dashboard with dark mode, skeletons, and responsive UI
- Evaluation dashboard comparing hybrid scoring against a keyword baseline

Live demo: <LINK>
GitHub: <LINK>

Built with Python, FastAPI, React, TypeScript, Tailwind CSS, spaCy, and sentence-transformers.
```
