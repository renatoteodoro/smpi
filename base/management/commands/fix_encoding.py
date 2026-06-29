"""
Management command to repair text fields corrupted by CP437/Latin-1 misinterpretation.

When PostgreSQL was initialized with SQL_ASCII encoding and psycopg3 used a
non-UTF-8 client encoding, multi-byte UTF-8 characters (ç, ã, é, etc.) were
stored as their individual Latin-1 byte values (e.g., ├ + º instead of ç).

This command detects and reverses that corruption by re-encoding as cp437 and
decoding as utf-8, restoring the original Portuguese characters.

Usage:
    python manage.py fix_encoding --dry-run   # preview only
    python manage.py fix_encoding             # apply fixes
"""

from django.core.management.base import BaseCommand


def try_fix(text: str) -> tuple[str, bool]:
    """Attempt to reverse CP437-interpreted-as-unicode corruption.

    Returns (fixed_text, was_changed).
    """
    if not text:
        return text, False
    try:
        fixed = text.encode('cp437').decode('utf-8')
        changed = fixed != text
        return fixed, changed
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text, False


class Command(BaseCommand):
    help = 'Repair UTF-8 text fields corrupted by CP437 misinterpretation in the DB.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without writing to the database.',
        )

    def handle(self, *args, **options):
        dry = options['dry_run']
        total = 0

        # --- Prescriptions ---
        from prescriptions.models import Prescription
        for p in Prescription.objects.exclude(instructions=''):
            fixed, changed = try_fix(p.instructions)
            if changed:
                total += 1
                self.stdout.write(f'  [Prescription #{p.pk}] instructions fixed')
                if not dry:
                    p.instructions = fixed
                    p.save(update_fields=['instructions', 'updated_at'])

        # --- ChatMessages ---
        from ai.models import ChatMessage
        for msg in ChatMessage.objects.exclude(content=''):
            fixed, changed = try_fix(msg.content)
            if changed:
                total += 1
                self.stdout.write(f'  [ChatMessage #{msg.pk}] content fixed')
                if not dry:
                    msg.content = fixed
                    msg.save(update_fields=['content', 'updated_at'])

        # --- KnowledgeDocuments ---
        from knowledge.models import KnowledgeDocument
        for doc in KnowledgeDocument.objects.exclude(description=''):
            fixed, changed = try_fix(doc.description)
            if changed:
                total += 1
                self.stdout.write(f'  [KnowledgeDocument #{doc.pk}] description fixed')
                if not dry:
                    doc.description = fixed
                    doc.save(update_fields=['description', 'updated_at'])

        # --- DocumentChunks (text content) ---
        from knowledge.models import DocumentChunk
        for chunk in DocumentChunk.objects.all():
            fixed, changed = try_fix(chunk.content)
            if changed:
                total += 1
                self.stdout.write(f'  [DocumentChunk #{chunk.pk}] content fixed')
                if not dry:
                    chunk.content = fixed
                    chunk.save(update_fields=['content', 'updated_at'])

        # --- Faults (name and description) ---
        from faults.models import Fault
        for fault in Fault.objects.all():
            changed_any = False
            fixed_name, c1 = try_fix(fault.name)
            fixed_desc, c2 = try_fix(fault.description)
            if c1 or c2:
                total += 1
                self.stdout.write(f'  [Fault #{fault.pk}] name/description fixed')
                if not dry:
                    if c1:
                        fault.name = fixed_name
                    if c2:
                        fault.description = fixed_desc
                    fault.save(update_fields=['name', 'description', 'updated_at'])

        mode = '(DRY RUN — nothing saved)' if dry else '(saved to database)'
        style = self.style.WARNING if dry else self.style.SUCCESS
        self.stdout.write(style(f'\nDone {mode}: {total} record(s) would be/were fixed.'))
        if dry and total:
            self.stdout.write('  Run without --dry-run to apply.')
