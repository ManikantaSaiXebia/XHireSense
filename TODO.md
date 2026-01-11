# TODO: Automate Email Extraction from Resumes

## Backend Changes
- [ ] Update Resume model to add name, email, mobile columns
- [ ] Update ResumeResponse schema to include new fields
- [ ] Modify upload endpoint to extract and store contact info during upload

## Frontend Changes
- [ ] Update API types to include name, email, mobile
- [ ] Update ResumeCard component to display extracted info
- [ ] Modify sendScreeningForm to use extracted email instead of prompt

## Testing & Validation
- [ ] Test parsing with sample resume text
- [ ] Verify database schema changes
- [ ] Test UI display and email automation
