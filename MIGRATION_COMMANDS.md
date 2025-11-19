# Backend Migration Commands

Run these commands on your server after the code changes:

```bash
# 1. Make migrations for the new fields
python manage.py makemigrations activities

# 2. Apply migrations
python manage.py migrate

# 3. Create some sample languages if they don't exist (optional)
python manage.py shell
```

Then in the Python shell:
```python
from accounts.models import Language

# Create common languages if they don't exist
languages = [
    ('Azərbaycan dili', 'az'),
    ('İngilis dili', 'en'),
    ('Rus dili', 'ru'),
    ('Türk dili', 'tr'),
]

for name, code in languages:
    Language.objects.get_or_create(name=name, code=code)

exit()
```

## New Fields Added to Activity Model:
- `is_unlimited_participants` (Boolean)
- `dress_code` (CharField)
- `gender_balance_required` (Boolean)
- `duration_hours` (now nullable, auto-calculated)

## New API Endpoints:
- `/api/activities/languages/` - Get all available languages

## Changes Summary:
1. ✅ Fixed image picker deprecation warning
2. ✅ Auto-calculate duration_hours from start/end dates
3. ✅ Added unlimited participants option
4. ✅ Added dress code field
5. ✅ Added gender balance required checkbox
6. ✅ Added required languages selector
7. ✅ Improved step 2 layout (date & time in same row)
8. ✅ Added category search in step 1
9. ✅ Reordered step 1 fields
10. ✅ Made category buttons smaller
11. ✅ Added padding to step indicator

