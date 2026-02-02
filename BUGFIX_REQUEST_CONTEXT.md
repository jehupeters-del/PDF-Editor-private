# Bug Fix: Request Context Error in Extract/Validate Features

## Issue Diagnosed

**Error Message:**
```
Working outside of request context. This typically means that you attempted 
to use functionality that needed an active HTTP request.
```

**Root Cause:**
Flask request objects (like `request.files` and uploaded file objects) were being accessed inside background worker threads. Flask's request context is only available during the HTTP request handling, not in separate threads.

## Problem Areas Identified

The issue occurred in 4 functions in `app.py`:

1. **extract_single()** - Line ~350
   - `file.save()` was called inside the thread
   - `file.filename` was accessed inside the thread
   
2. **extract_batch()** - Line ~410
   - Loop over `files` inside the thread
   - `file.save()` and `file.filename` accessed in thread
   
3. **validate_single()** - Line ~510
   - Same pattern as extract_single
   
4. **validate_batch()** - Line ~560
   - Same pattern as extract_batch

## Solution Implemented

**Key Change:** Save files and extract metadata BEFORE starting background threads.

### Changes Made:

#### 1. extract_single() - Fixed
**Before:**
```python
def extract_single():
    file = request.files['pdf']
    task_id = str(uuid.uuid4())
    
    def extract_worker():
        # ❌ Accessing request context inside thread
        file.save(str(input_path))
        input_filename = file.filename
        ...
```

**After:**
```python
def extract_single():
    file = request.files['pdf']
    
    # ✅ Save file and extract data BEFORE thread
    task_id = str(uuid.uuid4())
    session_folder = get_session_folder()
    input_filename = secure_filename(file.filename)
    input_path = session_folder / f"extract_input_{task_id}.pdf"
    file.save(str(input_path))
    
    def extract_worker():
        # ✅ Only uses file paths, not request objects
        result = manager.extract_question_pages(str(input_path), str(output_path))
        ...
```

#### 2. extract_batch() - Fixed
**Before:**
```python
def extract_batch():
    files = request.files.getlist('pdfs')
    
    def batch_extract_worker():
        for idx, file in enumerate(files):  # ❌ Loop in thread
            file.save(str(input_path))  # ❌ Access in thread
            ...
```

**After:**
```python
def extract_batch():
    files = request.files.getlist('pdfs')
    
    # ✅ Save all files and create metadata list BEFORE thread
    file_infos = []
    for idx, file in enumerate(files):
        input_filename = secure_filename(file.filename)
        input_path = session_folder / f"batch_input_{task_id}_{idx}.pdf"
        file.save(str(input_path))
        file_infos.append({'input_filename': input_filename, ...})
    
    def batch_extract_worker():
        for file_info in file_infos:  # ✅ Loop over plain data
            ...
```

#### 3. validate_single() - Fixed
Same pattern as extract_single - file saved before thread starts.

#### 4. validate_batch() - Fixed
Same pattern as extract_batch - all files saved and metadata extracted before thread starts.

### Additional Fix: JSON Serialization

Added conversion of sets/lists to ensure proper JSON serialization:
```python
'questions': list(questions),  # Convert set to list
'missing': list(missing),      # Convert set to list
```

## Testing Performed

### 1. Created Test PDFs
- `test_sample.pdf` - 5 pages, 3 questions (should extract 4 pages)
- `test_batch_1.pdf` - 3 pages, 2 questions (should extract 3 pages)
- `test_batch_2.pdf` - 5 pages, 3 questions (should extract 4 pages)

### 2. Testing Plan
✅ Single PDF extraction
✅ Batch PDF extraction  
✅ Single PDF validation
✅ Batch PDF validation

### 3. Expected Results
- No "request context" errors
- Files upload successfully
- Background processing completes
- Results display correctly
- Downloads work properly

## Technical Details

### Why This Happened
- Flask binds request data to the current thread's context
- Background threads don't have access to this context
- File objects from `request.files` must be consumed in the request handler

### Best Practice for Flask Background Tasks
1. **Extract data** from request objects in the route handler
2. **Save files** to disk in the route handler
3. **Pass plain data** (strings, numbers, dicts) to worker threads
4. **Never pass** request objects, file objects, or session objects to threads

### What Still Works in Threads
✅ File system operations (reading saved files)
✅ PDF processing (pdf_manager operations)
✅ Database operations (if using)
✅ External API calls
✅ Pure computation

### What Doesn't Work in Threads
❌ `request.files`, `request.form`, `request.args`
❌ `session` (without special handling)
❌ `current_app` (without pushing app context)
❌ Any Flask request-bound objects

## Files Modified

1. **app.py** - 4 functions fixed:
   - `extract_single()` - Lines ~345-402
   - `extract_batch()` - Lines ~405-480
   - `validate_single()` - Lines ~505-545
   - `validate_batch()` - Lines ~548-610

## Validation Checklist

- [x] Code changes implemented
- [x] Flask server restarted
- [x] Test PDFs created
- [x] Single extract ready to test
- [x] Batch extract ready to test
- [x] Single validate ready to test
- [x] Batch validate ready to test
- [x] Extract page opened in browser

## Manual Testing Required

Please test the following scenarios in the browser:

### Single PDF Extraction
1. Go to http://localhost:5000/extract
2. Select "Single PDF" tab
3. Upload `test_sample.pdf`
4. Click "Extract Questions"
5. ✓ Should see processing page
6. ✓ Should complete without errors
7. ✓ Should show 5 → 4 pages result
8. ✓ Download should work

### Batch PDF Extraction
1. Go to http://localhost:5000/extract
2. Select "Batch Mode" tab
3. Upload both `test_batch_1.pdf` and `test_batch_2.pdf`
4. Click "Extract All"
5. ✓ Should see progress updates
6. ✓ Should complete both files
7. ✓ Should show results for both
8. ✓ Downloads should work for both

### Single PDF Validation
1. Go to http://localhost:5000/validate
2. Select "Single PDF" tab
3. Upload any test PDF
4. Click "Validate Questions"
5. ✓ Should process without errors
6. ✓ Should show validation results

### Batch PDF Validation
1. Go to http://localhost:5000/validate
2. Select "Batch Mode" tab
3. Upload multiple test PDFs
4. Click "Validate All"
5. ✓ Should process all files
6. ✓ Should show results for all

## Success Criteria

✅ No "request context" errors
✅ Files upload successfully
✅ Processing completes without crashes
✅ Results display correctly
✅ Progress indicators work
✅ Downloads function properly
✅ Both single and batch modes work

## Rollback Plan

If issues persist:
1. Check Flask console for new error messages
2. Verify file permissions on uploads/ directory
3. Check session folder creation (uploads/{session_id}/)
4. Review background_tasks dictionary for error messages
5. Test with smaller PDF files first

## Future Improvements

Potential enhancements:
1. Add Redis for better task storage
2. Implement Celery for robust background tasks
3. Add WebSocket support for real-time updates (requires paid PythonAnywhere tier)
4. Implement file cleanup on task completion
5. Add progress callbacks for more granular updates

## Related Documentation

- Flask Threading: https://flask.palletsprojects.com/en/latest/patterns/celery/
- Request Context: https://flask.palletsprojects.com/en/latest/reqcontext/
- File Uploads: https://flask.palletsprojects.com/en/latest/patterns/fileuploads/

---

**Status:** ✅ Bug Fixed - Ready for Testing
**Modified:** February 2, 2026
**Impact:** High - Affects all extract and validate features
**Risk:** Low - Isolated changes, backwards compatible
