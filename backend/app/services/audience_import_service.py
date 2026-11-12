
import csv
import io

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audience import Audience
from app.schemas.audience import AudienceCreate


async def import_audiences_from_csv(
    file_content: bytes,
    db: AsyncSession,
) -> dict:
    # Read the uploaded CSV file.
    try:
        content = file_content.decode("utf-8-sig")
    except UnicodeDecodeError:
        return {
            "message": "CSV file must use UTF-8 encoding",
            "total_rows": 0,
            "imported": 0,
            "failed": 0,
            "errors": [],
        }

    reader = csv.DictReader(io.StringIO(content))

    required_columns = {
        "full_name",
        "email",
        "phone_number",
        "age",
        "gender",
        "occupation",
        "preferred_language",
        "state",
        "city",
    }

    if not reader.fieldnames:
        return {
            "message": "CSV file is empty or has no header",
            "total_rows": 0,
            "imported": 0,
            "failed": 0,
            "errors": [],
        }

    reader.fieldnames = [
        column.strip().lower() if column else ""
        for column in reader.fieldnames
    ]

    missing_columns = required_columns - set(reader.fieldnames)

    if missing_columns:
        return {
            "message": "CSV file is missing required columns",
            "missing_columns": sorted(missing_columns),
            "total_rows": 0,
            "imported": 0,
            "failed": 0,
            "errors": [],
        }

    rows = list(reader)

    # Load existing contact details to detect duplicates.
    result = await db.execute(select(Audience.email, Audience.phone_number))
    existing_records = result.all()

    existing_emails = {
        email.strip().lower()
        for email, _ in existing_records
        if email
    }

    existing_phones = {
        phone.strip()
        for _, phone in existing_records
        if phone
    }

    imported_records = []
    errors = []

    for row_number, row in enumerate(rows, start=2):
        try:
            cleaned_row = {
                key.strip().lower(): (
                    value.strip() if value else None
                )
                for key, value in row.items()
                if key is not None
            }

            # Validate the audience fields.
            audience_data = AudienceCreate.model_validate(cleaned_row)

            email = (
                str(audience_data.email).strip().lower()
                if audience_data.email
                else None
            )

            phone = (
                audience_data.phone_number.strip()
                if audience_data.phone_number
                else None
            )

            if email and email in existing_emails:
                raise ValueError("Email address already exists")

            if phone and phone in existing_phones:
                raise ValueError("Phone number already exists")

            # Detect duplicates within the same CSV file.
            if email:
                existing_emails.add(email)

            if phone:
                existing_phones.add(phone)

            imported_records.append(
                Audience(**audience_data.model_dump())
            )

        except Exception as exc:
            errors.append({
                "row": row_number,
                "error": str(exc),
            })

    # Save all valid records.
    try:
        if imported_records:
            db.add_all(imported_records)
            await db.commit()

    except Exception:
        await db.rollback()
        raise

    return {
        "message": "CSV import completed",
        "total_rows": len(rows),
        "imported": len(imported_records),
        "failed": len(errors),
        "errors": errors,
    }
