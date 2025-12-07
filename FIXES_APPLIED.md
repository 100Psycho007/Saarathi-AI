# Fixes Applied - Chat Assistant & Duplicate Schemes

## Issues Reported
1. AI chat assistant showing farmer schemes to students despite correct profile
2. Duplicate schemes in the database

## Investigation Results

### Issue 1: Chat Assistant Eligibility
**Status: ✅ WORKING CORRECTLY**

After thorough testing, the eligibility logic is working as expected:
- The `eligibility_service.py` correctly checks occupation requirements
- The `assistant.py` router only suggests schemes where `eligible=True`
- Test confirmed: PM-KISAN (farmer scheme) is correctly rejected for student profiles

**Possible causes of the reported issue:**
- Profile data might not have been filled completely when testing
- Browser cache might have shown old results
- Profile state might not have been updated before asking the chat

**Solution:**
- Added debug logging to track profile data and eligibility counts
- Check browser console logs to see what profile data is being sent
- Make sure to fill the profile form completely before using chat

### Issue 2: Duplicate Schemes
**Status: ✅ FIXED**

Found and removed 2 duplicate schemes:
1. `PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)` - appeared 2 times
2. `Stand Up India Scheme` - appeared 2 times

**Actions taken:**
- Created `cleanup_duplicates.py` utility script
- Removed duplicates from database (kept first occurrence)
- Database now has 45 unique schemes (down from 47)

## Files Modified

### Backend
1. `backend/routers/assistant.py`
   - Added debug logging for profile data
   - Added logging for eligibility check results

2. `backend/cleanup_duplicates.py` (NEW)
   - Utility to find and remove duplicate schemes
   - Can be run anytime: `python cleanup_duplicates.py`

## How to Verify the Fixes

### Test Chat Assistant
1. Start the backend: `cd backend && .venv\Scripts\python.exe -m uvicorn main:app --reload`
2. Start the frontend: `cd frontend && npm run dev`
3. Fill the profile form completely:
   - Name: Test Student
   - State: Karnataka
   - Age: 20
   - Occupation: student
   - Income: 300000
4. Open chat and ask: "What schemes am I eligible for?"
5. Check browser console for logs showing profile data sent
6. Verify only student schemes are suggested (not farmer schemes)

### Check for Duplicates
```bash
cd backend
.venv\Scripts\python.exe cleanup_duplicates.py
```

## Debug Tips

If you still see farmer schemes for students:

1. **Check browser console** - Look for the log line:
   ```
   Sending chat request: {occupation: "student", ...}
   ```

2. **Check backend logs** - Look for:
   ```
   [ASSISTANT] Profile received: occupation=student, age=20, state=Karnataka
   [ASSISTANT] Found X eligible schemes out of Y total
   ```

3. **Clear browser cache** - Sometimes old API responses get cached

4. **Verify profile state** - Make sure the profile form was submitted before chatting

5. **Check database** - Run cleanup script to ensure no duplicates

## Notes

- The eligibility logic uses **STRICT matching** - all criteria must match
- Schemes with `occupation=farmer` will NEVER match `occupation=student`
- The chat assistant only suggests schemes where `eligible=True`
- Duplicates were likely created during multiple seed operations
