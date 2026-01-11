# TODO: Fix Resume Display by Extracting Contact Info

## Backend Changes
- [x] Update Resume model to add name, email, mobile columns
- [x] Update ResumeResponse schema to include new fields
- [x] Add contact info parsing method to PDFService
- [x] Update upload endpoint to extract and store contact info

## Frontend Changes
- [x] Update API types to include name, email, mobile
- [x] Update ResumeCard component to display extracted info

## Testing & Validation
- [ ] Test parsing with sample resume text
- [ ] Verify database schema changes
- [ ] Test UI display and overflow prevention
